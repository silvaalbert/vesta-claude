"""Tests for board.py — character encoding, wrapping, and board construction."""

from __future__ import annotations

from vesta_claude.board import (
    COLOR_CODES,
    COLS,
    ROWS,
    build_board,
    center_line,
    encode_char,
    format_lines,
    render_terminal,
    wrap_text,
)


class TestEncodeChar:
    def test_letters_uppercase(self) -> None:
        assert encode_char("A") == 1
        assert encode_char("Z") == 26

    def test_letters_lowercase_normalized(self) -> None:
        assert encode_char("a") == 1
        assert encode_char("z") == 26

    def test_digit_zero(self) -> None:
        assert encode_char("0") == 36

    def test_digit_one(self) -> None:
        assert encode_char("1") == 27

    def test_digit_nine(self) -> None:
        assert encode_char("9") == 35

    def test_space(self) -> None:
        assert encode_char(" ") == 0

    def test_unsupported_char_returns_blank(self) -> None:
        assert encode_char("£") == 0
        assert encode_char("ñ") == 0

    def test_punctuation_period(self) -> None:
        assert encode_char(".") == 56

    def test_punctuation_question(self) -> None:
        assert encode_char("?") == 60


class TestWrapText:
    def test_short_text_no_wrap(self) -> None:
        assert wrap_text("HELLO WORLD") == ["HELLO WORLD"]

    def test_wraps_at_word_boundary(self) -> None:
        # 22-char line: "AAAAAAAAAA BBBBBBBBBB" = 21 chars, fits
        # Adding one more word should wrap
        result = wrap_text("AAAAAAAAAA BBBBBBBBBB CCCC", width=22)
        assert result == ["AAAAAAAAAA BBBBBBBBBB", "CCCC"]

    def test_does_not_break_word_mid_line(self) -> None:
        result = wrap_text("THE QUICK BROWN FOX", width=10)
        for line in result:
            assert len(line) <= 10

    def test_long_word_is_hard_split(self) -> None:
        result = wrap_text("ABCDEFGHIJKLMNOPQRSTUVWXYZ", width=10)
        assert result[0] == "ABCDEFGHIJ"
        assert result[1] == "KLMNOPQRST"

    def test_empty_string(self) -> None:
        assert not wrap_text("")

    def test_multiple_spaces_collapsed(self) -> None:
        result = wrap_text("A  B  C")
        assert result == ["A B C"]


class TestCenterLine:
    def test_centers_within_default_cols(self) -> None:
        result = center_line("HI")
        assert len(result) == COLS
        assert result.strip() == "HI"

    def test_exact_width_unchanged(self) -> None:
        text = "A" * COLS
        assert center_line(text) == text

    def test_truncates_to_width(self) -> None:
        text = "A" * (COLS + 5)
        result = center_line(text, COLS)
        assert len(result) == COLS


class TestBuildBoard:
    def test_empty_board_is_all_zeros(self) -> None:
        board = build_board([])
        assert board == [[0] * COLS for _ in range(ROWS)]

    def test_dimensions(self) -> None:
        board = build_board(["HELLO"])
        assert len(board) == ROWS
        assert all(len(row) == COLS for row in board)

    def test_first_row_encoded(self) -> None:
        board = build_board(["A"])
        assert board[0][0] == 1  # A
        assert board[0][1] == 0  # blank

    def test_extra_lines_ignored(self) -> None:
        lines = ["LINE"] * (ROWS + 3)
        board = build_board(lines)
        assert len(board) == ROWS

    def test_color_tile_placed_on_blank_cell(self) -> None:
        # "A" occupies col 0; col 1 is blank — tile goes on col 1
        color_tiles: list[dict[str, int | str]] = [{"row": 0, "col": 1, "color": "RED"}]
        board = build_board(["A"], color_tiles=color_tiles)
        assert board[0][1] == COLOR_CODES["RED"]

    def test_color_tile_does_not_overwrite_character(self) -> None:
        # Placing a tile on col 0 where "A" is encoded — should be silently ignored
        color_tiles: list[dict[str, int | str]] = [{"row": 0, "col": 0, "color": "RED"}]
        board = build_board(["A"], color_tiles=color_tiles)
        assert board[0][0] == 1  # A is preserved

    def test_invalid_color_tile_ignored(self) -> None:
        color_tiles: list[dict[str, int | str]] = [
            {"row": 0, "col": 0, "color": "PINK"}
        ]
        board = build_board(["A"], color_tiles=color_tiles)
        assert board[0][0] == 1  # A is still encoded

    def test_out_of_bounds_color_tile_ignored(self) -> None:
        color_tiles: list[dict[str, int | str]] = [
            {"row": 99, "col": 99, "color": "RED"}
        ]
        board = build_board(["A"], color_tiles=color_tiles)
        # Should not raise; board unchanged
        assert board[0][0] == 1

    def test_no_color_tiles_is_none_safe(self) -> None:
        board = build_board(["HI"], color_tiles=None)
        assert board[0][0] == 8  # H


class TestRenderTerminal:
    def test_returns_string(self) -> None:
        board = build_board(["HELLO"])
        result = render_terminal(board)
        assert isinstance(result, str)

    def test_has_border_lines(self) -> None:
        board = build_board([])
        result = render_terminal(board)
        lines = result.splitlines()
        assert lines[0].startswith("+")
        assert lines[-1].startswith("+")

    def test_row_count(self) -> None:
        board = build_board([])
        lines = render_terminal(board).splitlines()
        # 2 border lines + ROWS data lines
        assert len(lines) == ROWS + 2

    def test_color_tile_in_output(self) -> None:
        color_tiles: list[dict[str, int | str]] = [{"row": 0, "col": 0, "color": "RED"}]
        board = build_board([], color_tiles=color_tiles)
        result = render_terminal(board)
        # ANSI escape code should appear for the red tile
        assert "\033[" in result


class TestFormatLines:
    def test_returns_exactly_rows_lines(self) -> None:
        result = format_lines(["HELLO"])
        assert len(result) == ROWS

    def test_each_line_is_cols_wide(self) -> None:
        result = format_lines(["HI", "THERE"])
        assert all(len(line) == COLS for line in result)

    def test_single_line_vertically_centered(self) -> None:
        result = format_lines(["HI"])
        # 1 line → 2 blank above, 1 content, 3 blank below (or 2/3)
        top_pad = (ROWS - 1) // 2  # 2
        assert result[top_pad].strip() == "HI"

    def test_three_lines_vertically_centered(self) -> None:
        result = format_lines(["A", "B", "C"])
        top_pad = (ROWS - 3) // 2  # 1
        assert result[top_pad].strip() == "A"
        assert result[top_pad + 1].strip() == "B"
        assert result[top_pad + 2].strip() == "C"

    def test_strips_leading_trailing_spaces_before_centering(self) -> None:
        result = format_lines(["  HELLO  "])
        # After stripping, "HELLO" should be centered, not left-padded
        line = result[(ROWS - 1) // 2]
        assert line == "HELLO".center(COLS)

    def test_long_line_is_rewrapped_not_truncated(self) -> None:
        # A line longer than 22 chars should be split at a word boundary
        long_line = "THE QUICK BROWN FOX JUMPS"  # 25 chars
        result = format_lines([long_line])
        # All lines should be ≤ COLS wide (after stripping centering spaces)
        assert all(len(r.strip()) <= COLS for r in result)
        # The full content should still be present
        joined = " ".join(r.strip() for r in result if r.strip())
        assert "THE QUICK BROWN FOX" in joined
        assert "JUMPS" in joined

    def test_six_lines_fills_board(self) -> None:
        lines = ["LINE"] * ROWS
        result = format_lines(lines)
        assert len(result) == ROWS
        assert all(r.strip() == "LINE" for r in result)

    def test_extra_lines_beyond_rows_truncated(self) -> None:
        lines = ["X"] * (ROWS + 5)
        result = format_lines(lines)
        assert len(result) == ROWS
