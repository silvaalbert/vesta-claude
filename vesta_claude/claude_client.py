"""Claude API client — fetches board content from the model."""

from __future__ import annotations

import json
import logging

import anthropic

from vesta_claude.config import Config
from vesta_claude.prompt import SYSTEM_PROMPT, get_user_message

logger = logging.getLogger(__name__)


def fetch_content(config: Config) -> str:
    """
    Ask Claude what to display on the Vestaboard.

    Returns:
        The raw message text (uppercase). Line-wrapping is left to the caller.
    """
    client: anthropic.Anthropic | anthropic.AnthropicBedrock
    if config.backend == "bedrock":
        client = anthropic.AnthropicBedrock(aws_region=config.aws_region)
        logger.info(
            "Requesting content from model: %s (via Bedrock, region: %s)",
            config.model,
            config.aws_region,
        )
    else:
        client = anthropic.Anthropic(api_key=config.anthropic_api_key)
        logger.info("Requesting content from model: %s", config.model)

    message = client.messages.create(
        model=config.model,
        max_tokens=512,
        temperature=1.0,
        system=SYSTEM_PROMPT,
        messages=[
            {
                "role": "user",
                "content": get_user_message(),
            }
        ],
    )

    block = message.content[0]
    if not isinstance(block, anthropic.types.TextBlock):
        raise ValueError(f"Unexpected response block type: {type(block).__name__}")
    raw = block.text.strip()
    logger.debug("Raw Claude response: %s", raw)

    try:
        data: dict[str, object] = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Claude returned invalid JSON: {raw!r}") from exc

    if "text" not in data or not isinstance(data["text"], str):
        raise ValueError(f"Claude response missing valid 'text' field: {data!r}")

    return str(data["text"]).upper()
