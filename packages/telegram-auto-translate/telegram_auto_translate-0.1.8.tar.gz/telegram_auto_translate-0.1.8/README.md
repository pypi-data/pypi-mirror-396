# Telegram Auto-Translate

[![PyPI version](https://img.shields.io/pypi/v/telegram-auto-translate.svg)](https://pypi.org/project/telegram-auto-translate/)

**A Telegram userbot that automatically translates your outgoing messages using conversation context.**

| Before | After |
|--------|-------|
| ![Before translation](screenshot-before.png) | ![After translation](screenshot-after.png) |

---

## How It Works

```
Your message → Detect languages → Translate with Claude → Clean output → Edit in place
```

1. **Watch** - Monitors your outgoing messages
2. **Analyze** - Gathers recent chat context (default: 10 messages)
3. **Detect** - Uses GPT-5 to identify the target language based on who you're replying to
4. **Skip if unnecessary** - Won't translate if your message is already in the target language
5. **Translate** - Claude translates with full conversation context, matching the chat's tone and style
6. **Clean** - Strips any LLM artifacts (preambles, quotes) from the output
7. **Edit** - Replaces your original message with the translation

---

## Installation

### Via PyPI (Recommended)

```bash
pip install telegram-auto-translate
```

### From Source

```bash
git clone https://github.com/aimoda/telegram-auto-translate
cd telegram-auto-translate
pip install -e .
```

---

## Quick Start

```bash
# Set required environment variables
# Get TG_API_ID and TG_API_HASH from https://my.telegram.org/apps
export TG_API_ID="your_api_id"
export TG_API_HASH="your_api_hash"
export BEDROCK_AWS_PROFILE="your_aws_profile"
export OPENAI_API_KEY="your_azure_openai_key"

# Run
telegram-auto-translate
```

On first run, Telethon will prompt for your phone number and login code.

---

## Prerequisites

- **Python 3.10+**
- **Telegram API credentials** - Get `API_ID` and `API_HASH` from [my.telegram.org](https://my.telegram.org)
- **AWS account** with Bedrock access and appropriate IAM permissions
- **Azure OpenAI resource** (or standard OpenAI API key)

---

## Configuration

### Telegram

| Variable | Description |
|----------|-------------|
| `TG_API_ID` | Your Telegram API ID (required) |
| `TG_API_HASH` | Your Telegram API hash (required) |
| `TG_SESSION_NAME` | Session file name (default: `translator_session`) |

### AWS Bedrock (Claude)

1. **[Create an IAM user](https://us-east-1.console.aws.amazon.com/iam/home#/users/create)** with programmatic access, then attach an IAM policy with Bedrock invoke permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AllowBedrockModelInvocationInAUSCANNZUKUS",
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:InvokeModelWithResponseStream"
            ],
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": [
                        "us-east-1",
                        "us-east-2",
                        "us-west-1",
                        "us-west-2",
                        "ca-central-1",
                        "ca-west-1",
                        "eu-west-2",
                        "ap-southeast-2",
                        "ap-southeast-4",
                        "unspecified"
                    ]
                }
            },
            "Resource": [
                "arn:aws:bedrock:*::foundation-model/*",
                "arn:aws:bedrock:*:*:provisioned-model/*",
                "arn:aws:bedrock:*:*:imported-model/*",
                "arn:aws:bedrock:*:*:inference-profile/*"
            ]
        }
    ]
}
```

2. **Add credentials** to `~/.aws/credentials`:

```ini
[telegram-translator-bedrock]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

3. **Set the profile**:

```bash
export BEDROCK_AWS_PROFILE="telegram-translator-bedrock"
export BEDROCK_AWS_REGION="us-east-1"  # optional, us-east-1 is default
```

### Azure OpenAI (Recommended)

**Option A: Azure AD Authentication**
```bash
export OPENAI_USE_TOKEN_PROVIDER=1
export OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/v1/"
# Authenticate via: az login
```

**Option B: API Key**
```bash
export OPENAI_API_KEY="your_azure_openai_key"
export OPENAI_BASE_URL="https://your-resource.openai.azure.com/openai/v1/"
```

### Using Standard OpenAI Instead

```bash
export OPENAI_API_KEY="your_openai_key"
export OPENAI_BASE_URL="https://api.openai.com/v1"
```

---

## Usage

```bash
telegram-auto-translate [options]
```

### Command-Line Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--dry-run` | Log translations without editing messages | Off |
| `--debug` | Verbose logging of API calls | Off |
| `--context-messages N` | Number of previous messages for context | 10 |
| `--bedrock-profile NAME` | AWS profile for Bedrock | `$BEDROCK_AWS_PROFILE` |
| `--bedrock-region REGION` | AWS region for Bedrock | `us-east-1` |
| `--use-token-provider` | Use Azure AD instead of API key | Off |
| `--anthropic-model MODEL` | Claude model ID | `global.anthropic.claude-sonnet-4-5-20250929-v1:0` |
| `--openai-model MODEL` | GPT model for detection/cleaning | `gpt-5-mini-2025-08-07` |

### Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `TG_API_ID` | Yes | Telegram API ID |
| `TG_API_HASH` | Yes | Telegram API hash |
| `BEDROCK_AWS_PROFILE` | Yes | AWS credentials profile |
| `OPENAI_API_KEY` | Yes* | Azure/OpenAI API key |
| `OPENAI_BASE_URL` | No | API endpoint URL |
| `OPENAI_USE_TOKEN_PROVIDER` | No | Use Azure AD auth (`1`/`true`) |
| `BEDROCK_AWS_REGION` | No | AWS region (default: `us-east-1`) |
| `TG_SESSION_NAME` | No | Session file name |
| `ANTHROPIC_MODEL` | No | Claude model override |
| `OPENAI_MODEL` | No | GPT model override |
| `CONTEXT_MESSAGES` | No | Context message count |

*Not required if `OPENAI_USE_TOKEN_PROVIDER=1`

---

## Examples

**Test without editing messages:**
```bash
telegram-auto-translate --dry-run --debug
```

**Use more context for better translations:**
```bash
telegram-auto-translate --context-messages 20
```

**Use standard OpenAI API:**
```bash
OPENAI_BASE_URL="https://api.openai.com/v1" telegram-auto-translate
```

---

## Troubleshooting

### "TG_API_ID and TG_API_HASH are required"
Set both environment variables or pass `--api-id` and `--api-hash` flags.

### "OPENAI_API_KEY is required"
Either set `OPENAI_API_KEY` or use `--use-token-provider` for Azure AD auth.

### "BEDROCK_AWS_PROFILE is required"
Set `BEDROCK_AWS_PROFILE` to your AWS credentials profile name.

### Translation not happening
- Check that there are previous messages in the chat (the bot needs context)
- Your message might already be in the detected target language
- Use `--debug` to see detection results

### "AccessDeniedException" from Bedrock
Verify your IAM policy includes `bedrock:InvokeModel` permission and the model is enabled in your region.

### First run hangs
Telethon is waiting for your phone number. Enter it in the terminal.

---

## Development Setup

For local development and contributions:

### Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install the package
```bash
# Install in editable mode for development
pip install -e .
```

### Run the application
```bash
# Option 1: Use the installed command
telegram-auto-translate

# Option 2: Run as module (without installing)
PYTHONPATH=src python -m telegram_auto_translate
```

---

## Why Bedrock and Azure?

This bot uses **Claude via AWS Bedrock** for translation and **GPT-5 via Azure OpenAI** for language detection and output cleaning.

| Task | Model | Why |
|------|-------|-----|
| Translation | Claude (Bedrock) | Extended thinking for nuanced, context-aware translations |
| Language Detection | GPT-5 | Excellent structured output performance |
| Output Cleaning | GPT-5 | Reliable artifact removal |

We prefer these services for their data handling policies:
- **AWS Bedrock** - [Inputs and outputs are not logged by default](https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html)
- **Azure OpenAI** - [Your data is not used to train models](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/openai/data-privacy)

You can use standard OpenAI instead of Azure by setting `OPENAI_BASE_URL=https://api.openai.com/v1`.
