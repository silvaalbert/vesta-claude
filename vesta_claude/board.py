"""Vestaboard character encoding, dimensions, and board construction."""

from __future__ import annotations

ROWS: int = 6
COLS: int = 22

# fmt: off
# Character → Vestaboard character code
# Source: Vestaboard Local API documentation
CHAR_CODES: dict[str, int] = {
    " ": 0,
    "A": 1,  "B": 2,  "C": 3,  "D": 4,  "E": 5,
    "F": 6,  "G": 7,  "H": 8,  "I": 9,  "J": 10,
    "K": 11, "L": 12, "M": 13, "N": 14, "O": 15,
    "P": 16, "Q": 17, "R": 18, "S": 19, "T": 20,
    "U": 21, "V": 22, "W": 23, "X": 24, "Y": 25,
    "Z": 26,
    # Digits: 1-9 map to 27-35, 0 maps to 36
    "1": 27, "2": 28, "3": 29, "4": 30, "5": 31,
    "6": 32, "7": 33, "8": 34, "9": 35, "0": 36,
    # Punctuation
    "!": 37, "@": 38, "#": 39, "$": 40,
    "(": 41, ")": 42,
    "-": 44, "+": 46, "&": 47, "=": 48,
    ";": 49, ":": 50,
    "'": 52, '"': 53, "%": 54, ",": 55, ".": 56,
    "/": 59, "?": 60,
}

# Color tile codes for the White Vestaboard.
# Note: verify these against your device's firmware version if colors appear wrong.
COLOR_CODES: dict[str, int] = {
    "RED":    63,
    "ORANGE": 64,
    "YELLOW": 65,
    "GREEN":  66,
    "BLUE":   67,
    "VIOLET": 68,
    "WHITE":  69,
    "BLACK":  70,
}
# fmt: on

# Reverse lookup used by the terminal renderer
_CODE_TO_CHAR: dict[int, str] = {v: k for k, v in CHAR_CODES.items()}
_CODE_TO_COLOR: dict[int, str] = {v: k for k, v in COLOR_CODES.items()}

# ANSI escape codes for terminal color rendering (dry-run)
_ANSI_BG: dict[str, str] = {
    "RED": "\033[41m",
    "ORANGE": "\033[48;5;208m",
    "YELLOW": "\033[43m",
    "GREEN": "\033[42m",
    "BLUE": "\033[44m",
    "VIOLET": "\033[45m",
    "WHITE": "\033[47m",
    "BLACK": "\033[40m",
}
_ANSI_RESET = "\033[0m"


def encode_char(char: str) -> int:
    """Convert a single character to its Vestaboard code. Unknown chars → blank (0)."""
    return CHAR_CODES.get(char.upper(), 0)


def wrap_text(text: str, width: int = COLS) -> list[str]:
    """Word-wrap text into lines no wider than *width* characters."""
    words = text.split()
    lines: list[str] = []
    current = ""

    for word in words:
        if len(word) > width:
            # Word longer than the board width — hard-split it
            if current:
                lines.append(current)
                current = ""
            while len(word) > width:
                lines.append(word[:width])
                word = word[width:]
            current = word
        elif current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip() if current else word

    if current:
        lines.append(current)

    return lines


def center_line(text: str, width: int = COLS) -> str:
    """Return *text* centered within *width* characters (padded with spaces)."""
    return text.center(width)[:width]


def format_lines(lines: list[str]) -> list[str]:
    """
    Vertically and horizontally center a block of lines on the board.

    Strips any manual padding Claude may have applied, centers each line
    horizontally within COLS, then pads with blank rows above and below
    to vertically center the block within ROWS.

    Returns exactly ROWS strings, each exactly COLS characters wide.
    """
    # Strip manual padding, then re-wrap any line that exceeds COLS
    rewrapped: list[str] = []
    for line in lines:
        stripped = line.strip()
        if len(stripped) > COLS:
            rewrapped.extend(wrap_text(stripped))
        else:
            rewrapped.append(stripped)

    cleaned = rewrapped[:ROWS]
    n = len(cleaned)
    top_pad = (ROWS - n) // 2
    bottom_pad = ROWS - n - top_pad
    padded = [""] * top_pad + cleaned + [""] * bottom_pad
    return [center_line(line) for line in padded]


def build_board(
    lines: list[str],
    color_tiles: list[dict[str, int | str]] | None = None,
) -> list[list[int]]:
    """
    Build a 6×22 board of Vestaboard character codes.

    Args:
        lines: Up to 6 strings, each at most 22 characters, uppercase.
        color_tiles: Optional list of color accents.  Each entry is a dict with
            keys ``row`` (0-5), ``col`` (0-21), and ``color`` (e.g. ``"RED"``).

    Returns:
        A list of 6 rows, each containing 22 integer character codes.
    """
    board: list[list[int]] = [[0] * COLS for _ in range(ROWS)]

    for row_idx, line in enumerate(lines[:ROWS]):
        for col_idx, char in enumerate(line[:COLS]):
            board[row_idx][col_idx] = encode_char(char)

    if color_tiles:
        for tile in color_tiles:
            row = int(tile["row"])
            col = int(tile["col"])
            color = str(tile["color"]).upper()
            if 0 <= row < ROWS and 0 <= col < COLS and color in COLOR_CODES:
                # Only place on blank cells — never overwrite an encoded character
                if board[row][col] == 0:
                    board[row][col] = COLOR_CODES[color]

    return board


def render_terminal(board: list[list[int]]) -> str:
    """
    Render a board as a human-readable string for dry-run output.

    Colored tiles are displayed using ANSI background colours.
    """
    border = "+" + "-" * COLS + "+"
    output_lines = [border]

    for row in board:
        row_str = "|"
        for code in row:
            if code in _CODE_TO_COLOR:
                color_name = _CODE_TO_COLOR[code]
                ansi = _ANSI_BG.get(color_name, "")
                row_str += f"{ansi} {_ANSI_RESET}"
            else:
                row_str += _CODE_TO_CHAR.get(code, " ")
        row_str += "|"
        output_lines.append(row_str)

    output_lines.append(border)
    return "\n".join(output_lines)
