# vesta-claude

Populates a [Vestaboard](https://www.vestaboard.com) split-flap display with AI-generated content via Claude.

The script runs as a short-lived container: it calls Claude, converts the response to Vestaboard character codes, and sends it to the Vestaboard Cloud API — then exits. Run it on a schedule (cron, Kubernetes CronJob, etc.) to keep the board fresh.

## How it works

1. Claude is prompted with a description of the board's constraints and what you'd like it to display (edit `vesta_claude/prompt.py` to change the content).
2. Claude returns a plain text string — no line-breaking required from the model.
3. The script word-wraps, centers, and encodes the text as Vestaboard character codes (6 × 22 grid).
4. The encoded board is POSTed to the Vestaboard Cloud API.

## Requirements

- Python 3.13+
- [Poetry](https://python-poetry.org/) (dev)
- [Finch](https://runfinch.com/) or Docker (production)
- Claude credentials — either an Anthropic API key **or** AWS credentials for Bedrock
- A Vestaboard Cloud API token (cloud.vestaboard.com → Settings → API Tokens) — not required for dry runs

## Setup

```bash
# Install dependencies
poetry install

# Copy and fill in environment variables
cp .env.example .env

# Install pre-commit hooks
poetry run pre-commit install
```

## Running locally

`DRY_RUN` defaults to `true`, so you can test without a Vestaboard connected.

```bash
# Dry run via Anthropic — renders the board in your terminal
ANTHROPIC_API_KEY=sk-ant-... poetry run vesta-claude

# Dry run via AWS Bedrock
AWS_ACCESS_KEY_ID=... \
AWS_SECRET_ACCESS_KEY=... \
AWS_DEFAULT_REGION=us-east-1 \
poetry run vesta-claude

# Send to the board (requires DRY_RUN=false and a Vestaboard token)
DRY_RUN=false \
ANTHROPIC_API_KEY=sk-ant-... \
VESTABOARD_API_TOKEN=your-cloud-token \
poetry run vesta-claude
```

## Docker

```bash
# Build
finch build --platform linux/amd64 -t vesta-claude .

# Dry run via Anthropic
finch run --rm \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  vesta-claude

# Dry run via AWS Bedrock
finch run --rm \
  -e AWS_ACCESS_KEY_ID=... \
  -e AWS_SECRET_ACCESS_KEY=... \
  -e AWS_DEFAULT_REGION=us-east-1 \
  vesta-claude

# Send to board
finch run --rm \
  -e DRY_RUN=false \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e VESTABOARD_API_TOKEN=your-cloud-token \
  vesta-claude
```

## Environment variables

Exactly one of the two credential options below must be configured.

### Credentials

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Anthropic API key. When set, the Anthropic API is used. |
| `AWS_ACCESS_KEY_ID` | AWS access key. When set (and `ANTHROPIC_API_KEY` is absent), AWS Bedrock is used. |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key. Required when using Bedrock. |
| `AWS_SESSION_TOKEN` | AWS session token. Required only for temporary credentials. |
| `AWS_DEFAULT_REGION` | AWS region for Bedrock. Defaults to `us-east-1`. |

If both `ANTHROPIC_API_KEY` and `AWS_ACCESS_KEY_ID` are set, the Anthropic API takes precedence.

### Application

| Variable | Default | Description |
|---|---|---|
| `DRY_RUN` | `true` | Print board to terminal instead of sending to device. Set to `false` to send. |
| `VESTABOARD_API_TOKEN` | — | Vestaboard Cloud API token. Required when `DRY_RUN=false`. |
| `VESTABOARD_FORCED` | `false` | Override Vestaboard quiet hours. |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` (Anthropic) / `us.anthropic.claude-sonnet-4-6` (Bedrock) | Claude model ID. Bedrock requires cross-region inference profile IDs. |

## Customising the content

Open `vesta_claude/prompt.py` and edit the `CONTENT_DESCRIPTION` string at the top of the file. The system prompt (board dimensions, character constraints, response format) is kept separate and does not need to be changed.

## Running tests

```bash
poetry run pytest
```

## Linting and type-checking

```bash
poetry run black vesta_claude tests
poetry run isort vesta_claude tests
poetry run mypy vesta_claude
poetry run pylint vesta_claude
poetry run bandit -c pyproject.toml -r vesta_claude
```

## Vestaboard character codes

The board accepts integer codes per cell:

| Range | Meaning |
|---|---|
| 0 | Blank |
| 1–26 | A–Z |
| 27–35 | Digits 1–9 |
| 36 | Digit 0 |
| 37–60 | Punctuation (see `board.py`) |
| 63–70 | Colour tiles (RED → BLACK) |

> **Note:** Colour codes are documented in `board.py`. Verify them against your device's firmware version if colours appear incorrect.
