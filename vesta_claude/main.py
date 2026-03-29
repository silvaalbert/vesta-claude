"""Entry point — fetch content from Claude and send it to the Vestaboard."""

from __future__ import annotations

import logging
import sys

from vesta_claude.board import build_board, format_lines, render_terminal, wrap_text
from vesta_claude.claude_client import fetch_content
from vesta_claude.config import load_config
from vesta_claude.vestaboard_client import send_board

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """Fetch content from Claude and display it on the Vestaboard (or terminal)."""
    try:
        config = load_config()
    except ValueError as exc:
        logger.error("Configuration error: %s", exc)
        sys.exit(1)

    try:
        content = fetch_content(config)
    except Exception as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
        logger.error("Failed to fetch content from Claude: %s", exc)
        sys.exit(1)

    board = build_board(format_lines(wrap_text(content)))

    if config.dry_run:
        print("\n[DRY RUN] Board preview:\n")
        print(render_terminal(board))
        print()
    else:
        try:
            send_board(board, config)
        except (
            Exception
        ) as exc:  # noqa: BLE001  # pylint: disable=broad-exception-caught
            logger.error("Failed to send board to Vestaboard: %s", exc)
            sys.exit(1)


if __name__ == "__main__":
    main()
