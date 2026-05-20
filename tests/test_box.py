"""Tests for codechu_cli.box.box()."""

from __future__ import annotations

import pytest

from codechu_cli import box


def test_single_style_default():
    out = box("hi").split("\n")
    assert out[0].startswith("┌") and out[0].endswith("┐")
    assert out[1].startswith("│") and out[1].endswith("│")
    assert "hi" in out[1]
    assert out[-1].startswith("└") and out[-1].endswith("┘")


def test_double_style():
    out = box("ok", style="double").split("\n")
    assert out[0].startswith("╔") and out[0].endswith("╗")
    assert out[1].startswith("║")
    assert out[-1].startswith("╚") and out[-1].endswith("╝")


def test_rounded_style():
    out = box("ok", style="rounded").split("\n")
    assert out[0].startswith("╭") and out[0].endswith("╮")
    assert out[-1].startswith("╰") and out[-1].endswith("╯")


def test_title_in_top_border():
    out = box("content", title="warning").split("\n")
    assert "warning" in out[0]
    assert out[0].startswith("┌") and out[0].endswith("┐")


def test_multi_line_input():
    out = box("a\nbb\nccc").split("\n")
    # 3 content lines + top + bottom = 5
    assert len(out) == 5
    assert "a" in out[1]
    assert "bb" in out[2]
    assert "ccc" in out[3]
    # All inner lines same length
    assert len({len(line) for line in out[1:-1]}) == 1


def test_padding_zero():
    out = box("x", padding=0).split("\n")
    # Inner width = 1, top border = ┌─┐
    assert out[0] == "┌─┐"
    assert out[1] == "│x│"


def test_padding_default_one():
    out = box("x").split("\n")
    # Inner width = 1 + 2 padding = 3
    assert out[0] == "┌───┐"
    assert out[1] == "│ x │"


def test_padding_negative_rejected():
    with pytest.raises(ValueError):
        box("x", padding=-1)


def test_unknown_style_rejected():
    with pytest.raises(ValueError):
        box("x", style="hex")


def test_empty_text():
    out = box("").split("\n")
    # Still renders top + 1 line + bottom
    assert len(out) == 3
