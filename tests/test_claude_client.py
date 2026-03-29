"""Tests for claude_client.py — Claude API interaction."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import anthropic
import pytest

from vesta_claude.claude_client import fetch_content
from vesta_claude.config import Config


def _make_config(backend: str = "anthropic") -> Config:
    return Config(
        vestaboard_api_token="token",
        anthropic_api_key="sk-test" if backend == "anthropic" else "",
        model="claude-sonnet-4-6",
        dry_run=False,
        forced=False,
        backend=backend,  # type: ignore[arg-type]
        aws_region="us-east-1",
    )


def _make_mock_message(text: str) -> MagicMock:
    msg = MagicMock()
    block = MagicMock(spec=anthropic.types.TextBlock, text=text)
    msg.content = [block]
    return msg


class TestFetchContent:
    def test_valid_response_returns_text(self) -> None:
        payload = {"text": "EVERY CLOCK IS JUST A SMALL ARGUMENT ABOUT WHAT MATTERS."}
        raw = json.dumps(payload)

        with patch("vesta_claude.claude_client.anthropic.Anthropic") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.messages.create.return_value = _make_mock_message(raw)
            result = fetch_content(_make_config())

        assert result == "EVERY CLOCK IS JUST A SMALL ARGUMENT ABOUT WHAT MATTERS."

    def test_text_uppercased(self) -> None:
        payload = {"text": "lowercase text here"}
        raw = json.dumps(payload)

        with patch("vesta_claude.claude_client.anthropic.Anthropic") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.messages.create.return_value = _make_mock_message(raw)
            result = fetch_content(_make_config())

        assert result == "LOWERCASE TEXT HERE"

    def test_invalid_json_raises(self) -> None:
        with patch("vesta_claude.claude_client.anthropic.Anthropic") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.messages.create.return_value = _make_mock_message("not json")
            with pytest.raises(ValueError, match="invalid JSON"):
                fetch_content(_make_config())

    def test_missing_text_field_raises(self) -> None:
        raw = json.dumps({"lines": ["oops"]})

        with patch("vesta_claude.claude_client.anthropic.Anthropic") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.messages.create.return_value = _make_mock_message(raw)
            with pytest.raises(ValueError, match="missing valid 'text'"):
                fetch_content(_make_config())

    def test_non_string_text_field_raises(self) -> None:
        raw = json.dumps({"text": 42})

        with patch("vesta_claude.claude_client.anthropic.Anthropic") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.messages.create.return_value = _make_mock_message(raw)
            with pytest.raises(ValueError, match="missing valid 'text'"):
                fetch_content(_make_config())

    def test_bedrock_client_used_when_backend_is_bedrock(self) -> None:
        payload = {"text": "HELLO FROM BEDROCK"}
        raw = json.dumps(payload)

        with patch("vesta_claude.claude_client.anthropic.AnthropicBedrock") as mock_cls:
            mock_client = mock_cls.return_value
            mock_client.messages.create.return_value = _make_mock_message(raw)
            result = fetch_content(_make_config(backend="bedrock"))

        mock_cls.assert_called_once_with(aws_region="us-east-1")
        assert result == "HELLO FROM BEDROCK"
