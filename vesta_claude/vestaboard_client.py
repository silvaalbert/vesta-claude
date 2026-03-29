"""Vestaboard Cloud API client."""

from __future__ import annotations

import logging

import httpx

from vesta_claude.config import Config

logger = logging.getLogger(__name__)

_API_URL = "https://cloud.vestaboard.com/"
_AUTH_HEADER = "X-Vestaboard-Token"


def send_board(board: list[list[int]], config: Config) -> None:
    """
    Send a 6×22 board of character codes to the Vestaboard Cloud API.

    Args:
        board:  6×22 list of Vestaboard character codes.
        config: Application configuration.

    Raises:
        httpx.HTTPStatusError: If the API returns a non-2xx response.
        httpx.RequestError:    On network / connection errors.
    """
    headers = {
        _AUTH_HEADER: config.vestaboard_api_token,
        "Content-Type": "application/json",
    }

    logger.info("Sending board to Vestaboard Cloud API")

    with httpx.Client(timeout=10.0) as client:
        response = client.post(
            _API_URL,
            json={"characters": board, "forced": config.forced},
            headers=headers,
        )
        response.raise_for_status()

    logger.info("Board sent successfully (HTTP %s)", response.status_code)
