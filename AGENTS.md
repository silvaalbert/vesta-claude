# AGENTS.md — guidance for AI agents working on this repo

## Project overview

`vesta-claude` is a short-lived Python script that:
1. Calls the Anthropic Claude API to generate content (a plain text string).
2. Word-wraps, centers, and encodes the text as Vestaboard character codes (6 × 22 integer grid).
3. POSTs the encoded board to the Vestaboard Cloud API (`https://cloud.vestaboard.com/`).
4. Exits.

## Repository layout

```
vesta_claude/
  config.py           — env var loading & validation
  board.py            — character encoding, wrapping, board construction
  prompt.py           — Claude prompts (CONTENT_DESCRIPTION is the easy edit point)
  claude_client.py    — Anthropic SDK calls
  vestaboard_client.py— httpx calls to the Vestaboard Cloud API
  main.py             — entry point; wires everything together
tests/
  test_board.py
  test_config.py
  test_claude_client.py
  test_vestaboard_client.py
```

## How to run

```bash
poetry install
DRY_RUN=true ANTHROPIC_API_KEY=sk-ant-... poetry run vesta-claude
```

## Container runtime

Use Docker (or any OCI-compatible runtime). The target deployment architecture is **linux/amd64** — always pass `--platform linux/amd64` when building.

```bash
docker build --platform linux/amd64 -t vesta-claude .
docker run --rm -e DRY_RUN=true -e ANTHROPIC_API_KEY=sk-ant-... vesta-claude
```

## Key constraints

- **Board dimensions**: exactly 6 rows × 22 columns.
- **Character codes**: integers per `CHAR_CODES` dict in `board.py`. Unknown chars map to 0 (blank).
- **Colour codes**: 63–70 (`board.py::COLOR_CODES`). Supported but not currently used by the prompt.
- **Text must be uppercase** — the board has no lowercase flaps. `fetch_content` uppercases automatically.
- **Word wrapping**: never break a word mid-line; `board.py::wrap_text` handles this.
- **Claude response format**: JSON with a single `text` field (plain string). Line-breaking is done in code, not by Claude.

## Environment variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_API_KEY` | Yes | — | Anthropic API key |
| `VESTABOARD_API_TOKEN` | Yes* | — | Vestaboard Cloud API token |
| `DRY_RUN` | No | `false` | Print board to terminal instead of sending to device |
| `VESTABOARD_FORCED` | No | `false` | Override Vestaboard quiet hours |
| `CLAUDE_MODEL` | No | `claude-sonnet-4-6` | Claude model ID |

\* Not required when `DRY_RUN=true`.

## Making changes

### To change what Claude displays
Edit `CONTENT_DESCRIPTION` in `vesta_claude/prompt.py`. Do not edit `SYSTEM_PROMPT` unless the board spec changes.

### To change the board dimensions
Update `ROWS` and `COLS` in `board.py`. Adjust the system prompt in `prompt.py` to match.

### To add new character mappings
Add entries to `CHAR_CODES` in `board.py` and update the "AVAILABLE CHARACTERS" section of `SYSTEM_PROMPT` in `prompt.py`.

### To change the Claude model
Set the `CLAUDE_MODEL` environment variable, or change the default in `config.py`.

## Testing

```bash
poetry run pytest
```

All external calls (Anthropic SDK, httpx) are mocked in tests. Do not make real network calls in tests.

## Code style

- Formatter: `black` (line length 88)
- Import order: `isort` (black profile)
- Type checker: `mypy --strict`
- Linter: `pylint`
- Security: `bandit`

Run all checks: `poetry run pre-commit run --all-files`

## Dependency management

Add runtime deps: `poetry add <package>`
Add dev deps: `poetry add --group dev <package>`
Always commit an updated `poetry.lock`.
