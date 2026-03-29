"""Configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Config:
    vestaboard_api_token: str
    anthropic_api_key: str
    model: str
    dry_run: bool
    forced: bool
    backend: Literal["anthropic", "bedrock"]
    aws_region: str


def load_config() -> Config:
    """Load and validate configuration from environment variables."""
    vestaboard_api_token = os.environ.get("VESTABOARD_API_TOKEN", "")
    anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    dry_run = os.environ.get("DRY_RUN", "true").lower() not in ("0", "false", "no", "")
    forced = os.environ.get("VESTABOARD_FORCED", "false").lower() in (
        "1",
        "true",
        "yes",
    )

    backend: Literal["anthropic", "bedrock"]
    if anthropic_api_key:
        backend = "anthropic"
    elif os.environ.get("AWS_ACCESS_KEY_ID"):
        backend = "bedrock"
    else:
        raise ValueError(
            "No credentials found: set ANTHROPIC_API_KEY or AWS_ACCESS_KEY_ID"
        )

    _model_defaults = {
        "anthropic": "claude-sonnet-4-6",
        "bedrock": "us.anthropic.claude-sonnet-4-6",
    }
    model = os.environ.get("CLAUDE_MODEL", _model_defaults[backend])

    aws_region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    if not dry_run and not vestaboard_api_token:
        raise ValueError("VESTABOARD_API_TOKEN is required when DRY_RUN is not enabled")

    return Config(
        vestaboard_api_token=vestaboard_api_token,
        anthropic_api_key=anthropic_api_key,
        model=model,
        dry_run=dry_run,
        forced=forced,
        backend=backend,
        aws_region=aws_region,
    )
