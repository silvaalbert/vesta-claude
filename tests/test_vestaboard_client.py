"""Tests for vestaboard_client.py — Cloud API communication."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import httpx
import pytest

from vesta_claude.config import Config
from vesta_claude.vestaboard_client import _API_URL, send_board


def _make_config(forced: bool = False) -> Config:
    return Config(
        vestaboard_api_token="my-token",
        anthropic_api_key="sk-test",
        model="claude-sonnet-4-6",
        dry_run=False,
        forced=forced,
        backend="anthropic",
        aws_region="us-east-1",
    )


def _blank_board() -> list[list[int]]:
    return [[0] * 22 for _ in range(6)]


class TestSendBoard:
    def test_posts_to_cloud_url(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch("vesta_claude.vestaboard_client.httpx.Client") as mock_cls:
            mock_client_instance = mock_cls.return_value.__enter__.return_value
            mock_client_instance.post.return_value = mock_response
            send_board(_blank_board(), _make_config())

        url = mock_client_instance.post.call_args[0][0]
        assert url == _API_URL

    def test_sends_auth_header(self) -> None:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        with patch("vesta_claude.vestaboard_client.httpx.Client") as mock_cls:
            mock_client_instance = mock_cls.return_value.__enter__.return_value
            mock_client_instance.post.return_value = mock_response
            send_board(_blank_board(), _make_config())

        headers = mock_client_instance.post.call_args[1]["headers"]
        assert headers["X-Vestaboard-Token"] == "my-token"

    def test_wraps_board_in_characters_key(self) -> None:
        board = _blank_board()
        board[0][0] = 1  # 'A'

        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch("vesta_claude.vestaboard_client.httpx.Client") as mock_cls:
            mock_client_instance = mock_cls.return_value.__enter__.return_value
            mock_client_instance.post.return_value = mock_response
            send_board(board, _make_config())

        sent_json = mock_client_instance.post.call_args[1]["json"]
        assert "characters" in sent_json
        assert sent_json["characters"][0][0] == 1

    def test_forced_false_by_default(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch("vesta_claude.vestaboard_client.httpx.Client") as mock_cls:
            mock_client_instance = mock_cls.return_value.__enter__.return_value
            mock_client_instance.post.return_value = mock_response
            send_board(_blank_board(), _make_config(forced=False))

        sent_json = mock_client_instance.post.call_args[1]["json"]
        assert sent_json.get("forced") is False

    def test_forced_true_when_configured(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()

        with patch("vesta_claude.vestaboard_client.httpx.Client") as mock_cls:
            mock_client_instance = mock_cls.return_value.__enter__.return_value
            mock_client_instance.post.return_value = mock_response
            send_board(_blank_board(), _make_config(forced=True))

        sent_json = mock_client_instance.post.call_args[1]["json"]
        assert sent_json.get("forced") is True

    def test_http_error_propagates(self) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "403", request=MagicMock(), response=MagicMock()
        )

        with patch("vesta_claude.vestaboard_client.httpx.Client") as mock_cls:
            mock_client_instance = mock_cls.return_value.__enter__.return_value
            mock_client_instance.post.return_value = mock_response
            with pytest.raises(httpx.HTTPStatusError):
                send_board(_blank_board(), _make_config())
