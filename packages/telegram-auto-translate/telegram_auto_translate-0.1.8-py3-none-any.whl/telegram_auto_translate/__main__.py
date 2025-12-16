#!/usr/bin/env python3
import argparse
import asyncio
import inspect
import logging
import os
from dataclasses import dataclass
from collections.abc import Awaitable, Callable
from enum import Enum
from typing import cast

import anthropic
import httpx
import openai
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from pydantic import BaseModel, Field
from telethon import TelegramClient, events

logger = logging.getLogger(__name__)


def configure_logging(debug: bool = False) -> None:
    """Configure logging level and format based on debug flag."""
    level = logging.DEBUG if debug else logging.INFO
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        # Update level on existing handlers
        for handler in logger.handlers:
            handler.setLevel(level)


@dataclass(frozen=True)
class AppConfig:
    api_id: int
    api_hash: str
    session_name: str
    anthropic_model: str
    openai_model: str
    openai_api_key: str | None
    openai_base_url: str
    use_token_provider: bool
    context_messages: int
    dry_run: bool
    debug: bool
    bedrock_profile: str
    bedrock_region: str | None


@dataclass
class Clients:
    telegram: TelegramClient
    anthropic_client: anthropic.AsyncAnthropicBedrock
    openai_client: openai.AsyncOpenAI


class CleanedMessage(BaseModel):
    """Schema for cleaned translation output."""
    message: str = Field(min_length=1, description="The cleaned text output", title="Final Message")


class Confidence(str, Enum):
    """Confidence level for language detection."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ReplyTargetLanguage(BaseModel):
    """Detect target language based on reply context."""
    target_language: str | None = Field(description="The language to translate into")
    confidence: Confidence = Field(description="Confidence in the detection")


class ConversationLanguage(BaseModel):
    """Detect primary language in conversation (excluding user's messages)."""
    primary_language: str = Field(description="The primary language used by other participants")
    confidence: Confidence = Field(description="Confidence in the detection")


class UserMessageLanguage(BaseModel):
    """Detect the language of the user's outgoing message."""
    language: str = Field(description="The language the user's message is written in")
    confidence: Confidence = Field(description="Confidence in the detection")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Telegram auto-translation userbot")
    use_token_provider_default = os.getenv("OPENAI_USE_TOKEN_PROVIDER", "").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    parser.add_argument(
        "--api-id",
        default=os.getenv("TG_API_ID"),
        help="Telegram API ID (overrides TG_API_ID env var)",
    )
    parser.add_argument(
        "--api-hash",
        default=os.getenv("TG_API_HASH"),
        help="Telegram API hash (overrides TG_API_HASH env var)",
    )
    parser.add_argument(
        "--session-name",
        default=os.getenv("TG_SESSION_NAME", "translator_session"),
        help="Telethon session file name",
    )
    parser.add_argument(
        "--anthropic-model",
        default=os.getenv("ANTHROPIC_MODEL", "global.anthropic.claude-opus-4-5-20251101-v1:0"),
        help="Anthropic Bedrock model used for translation",
    )
    parser.add_argument(
        "--openai-model",
        default=os.getenv("OPENAI_MODEL", "gpt-5-mini-2025-08-07"),
        help="OpenAI model used to clean the translation output",
    )
    parser.add_argument(
        "--openai-api-key",
        default=os.getenv("OPENAI_API_KEY"),
        help="OpenAI API key (required unless --use-token-provider is set; overrides OPENAI_API_KEY env var)",
    )
    parser.add_argument(
        "--openai-base-url",
        default=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/"),
        help="Base URL for the OpenAI API (overrides OPENAI_BASE_URL env var)",
    )
    parser.add_argument(
        "--use-token-provider",
        action=argparse.BooleanOptionalAction,
        default=use_token_provider_default,
        help="Use Azure AD bearer token provider instead of OPENAI_API_KEY (overrides OPENAI_USE_TOKEN_PROVIDER env var)",
    )
    parser.add_argument(
        "--context-messages",
        type=int,
        default=int(os.getenv("CONTEXT_MESSAGES", "10")),
        help="Number of previous messages to include as context for translation (default: 10)",
    )
    parser.add_argument(
        "--bedrock-profile",
        default=os.getenv("BEDROCK_AWS_PROFILE"),
        help="AWS profile name for Amazon Bedrock (overrides BEDROCK_AWS_PROFILE env var)",
    )
    parser.add_argument(
        "--bedrock-region",
        default=os.getenv("BEDROCK_AWS_REGION", "us-east-1"),
        help="AWS region for Amazon Bedrock (overrides BEDROCK_AWS_REGION env var)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without sending translations to Telegram",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable verbose debug logging (logs raw API responses)",
    )
    return parser.parse_args()


def build_config(args: argparse.Namespace) -> AppConfig:
    api_id_raw = args.api_id
    api_hash = args.api_hash
    if not api_id_raw or not api_hash:
        raise SystemExit(
            "TG_API_ID and TG_API_HASH are required (set env vars or use --api-id/--api-hash)."
        )
    if not args.use_token_provider and not args.openai_api_key:
        raise SystemExit(
            "OPENAI_API_KEY is required unless --use-token-provider is set "
            "(set env var or pass --openai-api-key)."
        )
    try:
        api_id = int(api_id_raw)
    except ValueError as exc:
        raise SystemExit("TG_API_ID must be an integer.") from exc

    return AppConfig(
        api_id=api_id,
        api_hash=api_hash,
        session_name=args.session_name,
        anthropic_model=args.anthropic_model,
        openai_model=args.openai_model,
        openai_api_key=args.openai_api_key,
        openai_base_url=args.openai_base_url,
        use_token_provider=args.use_token_provider,
        context_messages=args.context_messages,
        dry_run=args.dry_run,
        debug=args.debug,
        bedrock_profile=args.bedrock_profile,
        bedrock_region=args.bedrock_region,
    )


def create_clients(config: AppConfig, http_client: httpx.AsyncClient) -> Clients:
    bedrock_profile = config.bedrock_profile
    bedrock_region = config.bedrock_region

    if not bedrock_profile:
        raise SystemExit(
            "BEDROCK_AWS_PROFILE is required to use Amazon Bedrock (set env var or --bedrock-profile)."
        )

    openai_api_key: str | Callable[[], Awaitable[str]]
    if config.use_token_provider:
        sync_token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://cognitiveservices.azure.com/.default"
        )

        async def token_provider() -> str:
            return sync_token_provider()

        openai_api_key = token_provider
    else:
        if config.openai_api_key is None:
            raise SystemExit(
                "OPENAI_API_KEY is required unless --use-token-provider is set "
                "(set env var or pass --openai-api-key)."
            )
        openai_api_key = config.openai_api_key

    openai_client = openai.AsyncOpenAI(
        base_url=config.openai_base_url,
        api_key=openai_api_key,
        http_client=http_client,
        max_retries=5,
    )
    anthropic_client = anthropic.AsyncAnthropicBedrock(
        aws_profile=bedrock_profile,
        aws_region=bedrock_region,
        http_client=http_client,
        max_retries=3,
    )
    telegram_client = TelegramClient(
        config.session_name, config.api_id, config.api_hash
    )
    return Clients(
        telegram=telegram_client,
        anthropic_client=anthropic_client,
        openai_client=openai_client,
    )


def should_skip_message(text: str) -> bool:
    """Check if a message should be skipped (empty or whitespace-only)."""
    return not text.strip()


def format_conversation_context(messages: list[dict[str, str | bool]]) -> str:
    """Format messages into a context block with (YOU) prefix for outgoing messages."""
    lines = []
    for msg in messages:
        prefix = "(YOU) " if msg["is_outgoing"] else ""
        lines.append(f"{prefix}[{msg['sender']}]: {msg['text']}")
    return "\n".join(lines)


def format_sender_name(sender: object) -> str:
    """Format sender information into a readable string."""
    parts: list[str] = []

    first_name = getattr(sender, "first_name", None)
    last_name = getattr(sender, "last_name", None)
    username = getattr(sender, "username", None)
    title = getattr(sender, "title", None)  # For channels/groups

    if first_name:
        parts.append(first_name)
    if last_name:
        parts.append(last_name)

    # Use title for channels/groups if no name
    if not parts and title:
        parts.append(title)

    if username:
        if parts:
            return f"{' '.join(parts)} (@{username})"
        return f"@{username}"

    if parts:
        return " ".join(parts)

    return "Unknown"


async def fetch_previous_messages(
    event: events.NewMessage.Event,
    limit: int = 10,
) -> list[dict[str, str | bool]]:
    """Fetch previous messages from the chat for translation context."""
    client = event.client
    if client is None:
        return []

    previous = await client.get_messages(
        event.chat_id,
        limit=limit,
        max_id=event.id,  # Exclude current message
    )

    context: list[dict[str, str | bool]] = []
    for msg in reversed(previous):  # Oldest first
        if msg and msg.message:
            sender_entity = await msg.get_sender()
            sender = format_sender_name(sender_entity) if sender_entity else "Unknown"
            context.append({
                "sender": sender,
                "text": msg.message,
                "is_outgoing": bool(msg.out),
            })
    return context


async def detect_reply_target_language(
    previous_messages: list[dict[str, str | bool]],
    current_text: str,
    current_user_name: str,
    config: AppConfig,
    clients: Clients,
) -> ReplyTargetLanguage | None:
    """Detect the language of the person the user is likely replying to."""
    logger.debug("[OpenAI] Starting reply target language detection")

    context_block = format_conversation_context(previous_messages)

    try:
        response = await clients.openai_client.beta.chat.completions.parse(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You analyze conversation context to determine what language to translate the user's message into. "
                        f"The user is '{current_user_name}' and their messages are prefixed with '(YOU)'. "
                        "Look at the conversation history and the user's new message to determine who they are likely replying to. "
                        "Return the language that person uses. If it's unclear who they're replying to, return null for target_language with low confidence."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Conversation history:\n{context_block}\n\nUser's new message to translate:\n{current_text}",
                },
            ],
            response_format=ReplyTargetLanguage,
            service_tier='flex',
            store=config.debug,
        )
        logger.debug("[OpenAI] Reply target detection response: %r", response.model_dump())

        choice = response.choices[0]
        if choice.finish_reason in ("length", "content_filter"):
            logger.warning("OpenAI reply detection failed: %s", choice.finish_reason)
            return None

        message = choice.message
        if getattr(message, "refusal", None):
            logger.warning("OpenAI refused reply detection: %s", message.refusal)
            return None

        return message.parsed
    except Exception as exc:
        logger.warning("Reply target language detection failed: %s", exc)
        return None


async def detect_conversation_language(
    previous_messages: list[dict[str, str | bool]],
    config: AppConfig,
    clients: Clients,
) -> ConversationLanguage | None:
    """Detect the primary language in the conversation (excluding user's messages)."""
    logger.debug("[OpenAI] Starting conversation language detection")

    context_block = format_conversation_context(previous_messages)

    try:
        response = await clients.openai_client.beta.chat.completions.parse(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You analyze conversation context to determine the primary language used by other participants. "
                        "Messages from the current user are prefixed with '(YOU)' - exclude these when identifying the language. "
                        "Focus on what language the other people in the conversation are writing in."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Conversation history:\n{context_block}",
                },
            ],
            response_format=ConversationLanguage,
            service_tier='flex',
            store=config.debug,
        )
        logger.debug("[OpenAI] Conversation language detection response: %r", response.model_dump())

        choice = response.choices[0]
        if choice.finish_reason in ("length", "content_filter"):
            logger.warning("OpenAI conversation detection failed: %s", choice.finish_reason)
            return None

        message = choice.message
        if getattr(message, "refusal", None):
            logger.warning("OpenAI refused conversation detection: %s", message.refusal)
            return None

        return message.parsed
    except Exception as exc:
        logger.warning("Conversation language detection failed: %s", exc)
        return None


async def detect_user_message_language(
    text: str,
    config: AppConfig,
    clients: Clients,
) -> UserMessageLanguage | None:
    """Detect the language of the user's outgoing message."""
    logger.debug("[OpenAI] Starting user message language detection")

    try:
        response = await clients.openai_client.beta.chat.completions.parse(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Identify the language the user's message is written in. "
                    ),
                },
                {"role": "user", "content": text},
            ],
            response_format=UserMessageLanguage,
            service_tier="flex",
            store=config.debug,
        )
        logger.debug("[OpenAI] User message language detection response: %r", response.model_dump())

        choice = response.choices[0]
        if choice.finish_reason in ("length", "content_filter"):
            logger.warning("OpenAI user language detection failed: %s", choice.finish_reason)
            return None

        message = choice.message
        if getattr(message, "refusal", None):
            logger.warning("OpenAI refused user language detection: %s", message.refusal)
            return None

        return message.parsed
    except Exception as exc:
        logger.warning("User message language detection failed: %s", exc)
        return None


async def translate_with_anthropic(
    text: str,
    target_language: str,
    current_user_name: str,
    config: AppConfig,
    clients: Clients,
    previous_messages: list[dict[str, str | bool]],
) -> str:
    logger.debug("[Anthropic] Starting translation request")
    logger.debug("[Anthropic] Input text: %r", text)
    logger.debug("[Anthropic] Target language: %s", target_language)
    system_prompt = (
        f"You are a native {target_language} speaker doing transcreation—rebuilding a message "
        f"as you'd naturally say it, not translating words. You are NOT a translator; "
        f"you ARE the speaker, expressing what they mean in your native tongue.\n\n"
        f"The speaker is '{current_user_name}' (marked '(YOU)' in conversation history).\n\n"
        "CORE PRINCIPLES:\n"
        "- Transcreate the MEANING, FEELING, and ENERGY—never translate word-for-word\n"
        "- Write what you'd actually text to a friend in this situation\n"
        "- Adapt idioms and cultural references to target-culture equivalents "
        "(a joke should land, not be explained)\n"
        "- If a literal translation sounds 'translated,' rewrite it completely\n"
        "- Match the vibe: casual stays casual, formal stays formal\n"
        "- The reader should have NO idea this was originally in another language\n\n"
        "AVOID:\n"
        "- Word-for-word literal translation\n"
        "- Translationese (unnatural constructions borrowed from the source language)\n"
        "- Overly formal/stiff phrasing for casual messages\n"
        "- Generic or 'safe' word choices when a more vivid expression fits\n\n"
        f"REGISTER: Mirror the conversation. For languages with formal/informal distinctions "
        f"(tu/vous, du/Sie, etc.), match what others use in the chat.\n\n"
        "Preserve emojis, markdown formatting, URLs, and @mentions exactly.\n\n"
        "Output only the final message. No commentary."
    )
    logger.debug("[Anthropic] System prompt: %s", system_prompt)
    logger.debug("[Anthropic] Model: %s", config.anthropic_model)

    context_block = format_conversation_context(previous_messages)
    content = f"Conversation so far:\n\n{context_block}\n\n---\n\nNow express this in {target_language}:\n\n{text}"
    logger.debug("[Anthropic] Including %d context messages", len(previous_messages))

    response = await clients.anthropic_client.messages.create(
        model=config.anthropic_model,
        max_tokens=16000,
        thinking={"type": "enabled", "budget_tokens": 10000},
        system=system_prompt,
        messages=[
            {"role": "user", "content": content},
        ],
    )
    logger.debug("[Anthropic] Raw response: %r", response.model_dump())
    logger.debug(
        "[Anthropic] Usage: input_tokens=%d, output_tokens=%d",
        response.usage.input_tokens,
        response.usage.output_tokens,
    )
    translated = "".join(
        block.text for block in response.content if block.type == "text"
    ).strip()
    logger.debug("[Anthropic] Extracted translation: %r", translated)
    return translated


async def clean_translation_with_openai(
    text: str, target_language: str, config: AppConfig, clients: Clients
) -> str:
    logger.debug("[OpenAI] Starting cleanup request")
    logger.debug("[OpenAI] Input text: %r", text)
    logger.debug("[OpenAI] Model: %s", config.openai_model)
    try:
        response = await clients.openai_client.beta.chat.completions.parse(
            model=config.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You receive text that has ALREADY been translated into {target_language}. "
                        "Your job is to extract ONLY the actual translated content, removing any LLM artifacts. "
                        "Remove: preamble like 'Here is the translation:', 'Translation:', 'Sure, here you go:'; "
                        "closing remarks like 'Let me know if you need anything else'; "
                        "matching leading/trailing quotes or backticks; surrounding whitespace. "
                        "Do NOT translate, paraphrase, autocorrect, normalize, or change the actual translated content itself. "
                        "Preserve all newlines, emojis, markdown, URLs, and mentions within the translated content exactly as given. "
                        "If the input appears to be ONLY the translated content with no artifacts, return it unchanged. "
                        "Return JSON with a single field `message` containing the cleaned translation—no prefixes, suffixes, or commentary."
                    ),
                },
                {"role": "user", "content": text},
            ],
            response_format=CleanedMessage,
            service_tier='flex',
            store=config.debug,
        )
        logger.debug("[OpenAI] Raw response: %r", response.model_dump())
        if response.usage:
            logger.debug(
                "[OpenAI] Usage: prompt_tokens=%d, completion_tokens=%d, total_tokens=%d",
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                response.usage.total_tokens,
            )
        choice = response.choices[0]
        if choice.finish_reason == "length":
            logger.warning("OpenAI response truncated (hit token limit)")
            return text
        if choice.finish_reason == "content_filter":
            logger.warning("OpenAI response filtered due to content restrictions")
            return text

        message = choice.message
        if getattr(message, "refusal", None):
            logger.warning("OpenAI refused to clean translation: %s", message.refusal)
            logger.debug("[OpenAI] Refusal details: %r", message.refusal)
            return text

        parsed = message.parsed
        cleaned = parsed.message.strip() if parsed else text
        logger.debug("[OpenAI] Cleaned output: %r", cleaned)
        return cleaned
    except Exception as exc:
        logger.warning("OpenAI cleanup failed: %s", exc)
        logger.debug("[OpenAI] Exception details: %r", exc)
        return text


async def handle_outgoing_message(
    event: events.NewMessage.Event,
    config: AppConfig,
    clients: Clients,
) -> None:
    text = event.raw_text or ""

    logger.debug(
        "[Handler] Received outgoing message: chat_id=%s, message_id=%s",
        event.chat_id,
        event.id,
    )
    logger.debug("[Handler] Raw text: %r", text)

    if should_skip_message(text):
        logger.debug("[Handler] Skipping empty message")
        return

    # Get current user's name
    if event.client is None:
        logger.debug("[Handler] No client available, skipping")
        return
    me = await event.client.get_me()
    current_user_name = format_sender_name(me) if me else "Me"
    logger.debug("[Handler] Current user: %s", current_user_name)

    # Fetch previous messages for context
    previous_messages = await fetch_previous_messages(event, limit=config.context_messages)
    logger.debug("[Handler] Fetched %d previous messages for context", len(previous_messages))

    # Skip if no previous messages to analyze
    if not previous_messages:
        logger.debug("[Handler] No previous messages, skipping translation")
        return

    # Detect target language
    target_language: str | None = None

    conversation_task = asyncio.create_task(
        detect_conversation_language(previous_messages, config, clients)
    )
    user_language_task = asyncio.create_task(
        detect_user_message_language(text, config, clients)
    )

    # First, try to detect based on who user is replying to
    reply_detection = await detect_reply_target_language(
        previous_messages, text, current_user_name, config, clients
    )
    if reply_detection and reply_detection.target_language:
        if reply_detection.confidence in (Confidence.HIGH, Confidence.MEDIUM):
            target_language = reply_detection.target_language
            logger.debug(
                "[Handler] Reply detection: %s (confidence: %s)",
                target_language,
                reply_detection.confidence.value,
            )

    conversation_detection, user_language_detection = await asyncio.gather(
        conversation_task, user_language_task
    )

    # Fallback: detect primary language in conversation
    if not target_language and conversation_detection:
        target_language = conversation_detection.primary_language
        logger.debug(
            "[Handler] Conversation detection: %s (confidence: %s)",
            target_language,
            conversation_detection.confidence.value,
        )

    if user_language_detection:
        logger.debug(
            "[Handler] User language detection: %s (confidence: %s)",
            user_language_detection.language,
            user_language_detection.confidence.value,
        )

    # Skip if no language detected
    if not target_language:
        logger.debug("[Handler] Could not detect target language, skipping translation")
        return

    if (
        user_language_detection
        and user_language_detection.confidence in (Confidence.HIGH, Confidence.MEDIUM)
        and target_language.casefold() == user_language_detection.language.casefold()
    ):
        logger.info(
            "Detected same language for user message (%s); skipping translation",
            target_language,
        )
        return

    logger.info("Translating to: %s", target_language)

    logger.debug("[Handler] Processing message for translation")
    try:
        translated = await translate_with_anthropic(
            text, target_language, current_user_name, config, clients, previous_messages
        )
    except Exception as exc:
        logger.error("Translation failed: %s", exc)
        logger.debug("[Handler] Translation exception: %r", exc)
        return

    if not translated:
        logger.debug("[Handler] Translation returned empty result, skipping")
        return

    logger.debug("[Handler] Translation complete, starting cleanup")
    cleaned = await clean_translation_with_openai(translated, target_language, config, clients)

    logger.debug("[Handler] Final translated text: %r", cleaned)
    try:
        if config.dry_run:
            logger.info("Dry-run: would edit message to: %s", cleaned)
        else:
            logger.debug("[Handler] Editing message in Telegram")
            await event.edit(cleaned)
            logger.debug("[Handler] Message edited successfully")
    except Exception as exc:
        logger.error("Failed to edit translation: %s", exc)
        logger.debug("[Handler] Edit exception: %r", exc)


def register_handlers(
    telegram_client: TelegramClient,
    config: AppConfig,
    clients: Clients,
) -> None:
    @telegram_client.on(events.NewMessage(outgoing=True))
    async def _(event: events.NewMessage.Event) -> None:
        await handle_outgoing_message(event, config, clients)


async def run_bot(config: AppConfig) -> None:
    logger.debug("[Bot] Initializing HTTP client")
    async with httpx.AsyncClient(http2=True, timeout=60.0, headers={"Sec-GPC": "1", "DNT": "1", "Cache-Control": "no-store"}, limits=httpx.Limits(max_connections=245, max_keepalive_connections=None, keepalive_expiry=None)) as http_client:
        logger.debug("[Bot] Creating API clients")
        clients = create_clients(config, http_client)
        logger.debug("[Bot] API clients created successfully")

        logger.debug("[Bot] Registering event handlers")
        register_handlers(clients.telegram, config, clients)
        logger.debug("[Bot] Event handlers registered")

        logger.info(
            "Starting Telegram translator (anthropic=%s, openai=%s, dry_run=%s)",
            config.anthropic_model,
            config.openai_model,
            config.dry_run,
        )
        logger.debug("[Bot] Starting Telegram client")
        start_result = clients.telegram.start()
        if inspect.isawaitable(start_result):
            await cast(Awaitable[object], start_result)
        logger.debug("[Bot] Telegram client started, entering main loop")

        run_future = clients.telegram.run_until_disconnected()
        if inspect.isawaitable(run_future):
            await cast(Awaitable[object], run_future)
        logger.debug("[Bot] Telegram client disconnected")


def main() -> None:
    args = parse_args()
    configure_logging(debug=args.debug)
    config = build_config(args)
    try:
        asyncio.run(run_bot(config))
    except KeyboardInterrupt:
        logger.info("Translator stopped by user.")


if __name__ == "__main__":
    main()
