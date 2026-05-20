"""Tests for codechu_cli.table.Table."""

from __future__ import annotations

import pytest

from codechu_cli import Table


def test_plain_default_render():
    t = Table(["A", "B"])
    t.add_row(["1", "22"])
    t.add_row(["333", "4"])
    out = str(t)
    lines = out.split("\n")
    assert lines[0] == "A    B "
    assert lines[1] == "1    22"
    assert lines[2] == "333  4 "


def test_alignment_right():
    t = Table(["x", "y"])
    t.add_row(["a", "1"])
    t.add_row(["bb", "22"])
    t.align(1, "right")
    out = str(t).split("\n")
    # Column 1 right-aligned to width 2
    assert out[1].endswith(" 1")
    assert out[2].endswith("22")


def test_alignment_center():
    t = Table(["h"])
    t.add_row(["x"])
    t.add_row(["aaaaa"])
    t.align(0, "center")
    out = str(t).split("\n")
    # "x" centered in width 5 → "  x  "
    assert out[1] == "  x  "
    assert out[2] == "aaaaa"


def test_alignment_invalid_mode():
    t = Table(["a"])
    with pytest.raises(ValueError):
        t.align(0, "diagonal")  # type: ignore[arg-type]


def test_alignment_out_of_range():
    t = Table(["a"])
    with pytest.raises(IndexError):
        t.align(5, "left")


def test_style_box():
    t = Table(["A", "B"])
    t.add_row(["1", "2"])
    out = str(t.style("box")).split("\n")
    assert out[0].startswith("┌") and out[0].endswith("┐")
    assert "│" in out[1]
    assert out[2].startswith("├") and out[2].endswith("┤")
    assert out[-1].startswith("└") and out[-1].endswith("┘")


def test_style_github():
    t = Table(["A", "B"])
    t.add_row(["1", "2"])
    t.align(1, "right")
    out = str(t.style("github")).split("\n")
    assert out[0].startswith("|") and out[0].endswith("|")
    # Right-align hint
    assert out[1].rstrip().endswith(":|") or out[1].endswith(": |")
    assert "1" in out[2]


def test_style_unknown():
    t = Table(["a"])
    with pytest.raises(ValueError):
        t.style("bogus")


def test_color_callback_does_not_inflate_width():
    def red(s: str) -> str:
        return f"\x1b[31m{s}\x1b[0m"

    t = Table(["x", "y"])
    t.add_row(["a", "1"])
    t.add_row(["b", "22"])
    t.color_col(0, red)
    t.align(1, "right")
    out = str(t).split("\n")
    # Column 0 width = 1 (no ANSI inflation); plain separator '  '
    assert "\x1b[31ma\x1b[0m" in out[1]
    # Row " 1" → padding still aligns
    assert out[1].endswith(" 1")
    assert out[2].endswith("22")


def test_color_col_out_of_range():
    t = Table(["a"])
    with pytest.raises(IndexError):
        t.color_col(9, str)


def test_add_row_normalizes_length():
    t = Table(["a", "b", "c"])
    t.add_row(["1"])  # short
    t.add_row(["1", "2", "3", "4"])  # long
    out = str(t).split("\n")
    # 4 lines: header + 2 rows = 3 (plain style)
    assert len(out) == 3


def test_auto_widths_from_header_and_rows():
    t = Table(["short", "x"])
    t.add_row(["a", "looooong"])
    out = str(t).split("\n")
    # Header column 0 width ≥ 5, column 1 ≥ 8
    assert out[0].startswith("short")
    assert "looooong" in out[1]


def test_chained_builders_return_self():
    t = Table(["a", "b"])
    r = t.add_row(["1", "2"]).align(0, "right").style("box").color_col(1, str)
    assert r is t


def test_multi_column_box():
    t = Table(["File", "Size", "Risk"])
    t.add_row(["foo.log", "1.2 GB", "high"])
    t.align(1, "right")
    out = str(t.style("box"))
    assert "File" in out and "Size" in out and "Risk" in out
    assert "foo.log" in out and "1.2 GB" in out
