"""Tests for codechu_cli.markdown.render_markdown()."""

from __future__ import annotations

import io

from codechu_cli import Color, render_markdown


def test_plain_passthrough_when_disabled():
    out = render_markdown("just text", enabled=False)
    assert out == "just text"


def test_bold():
    out = render_markdown("hello **world**", enabled=True)
    assert "\x1b[1m" in out
    assert "world" in out
    # Disabled strips formatting markers but keeps text.
    out2 = render_markdown("hello **world**", enabled=False)
    assert out2 == "hello world"


def test_italic():
    out = render_markdown("an *emphasized* word", enabled=True)
    assert "\x1b[3m" in out
    assert "emphasized" in out
    out2 = render_markdown("an *emphasized* word", enabled=False)
    assert out2 == "an emphasized word"


def test_code_span():
    out = render_markdown("run `pytest -q`", enabled=True)
    assert "\x1b[36m" in out  # cyan default
    assert "pytest -q" in out
    out2 = render_markdown("run `pytest -q`", enabled=False)
    assert out2 == "run pytest -q"


def test_h1():
    out = render_markdown("# Title", enabled=True)
    assert "Title" in out
    assert "\x1b[" in out  # some ANSI applied
    out2 = render_markdown("# Title", enabled=False)
    assert out2 == "Title"


def test_h2():
    out = render_markdown("## Sub", enabled=True)
    assert "Sub" in out
    assert "\x1b[1m" in out
    out2 = render_markdown("## Sub", enabled=False)
    assert out2 == "Sub"


def test_list_dash():
    out = render_markdown("- one\n- two", enabled=False)
    lines = out.split("\n")
    assert "one" in lines[0] and "•" in lines[0]
    assert "two" in lines[1] and "•" in lines[1]


def test_list_star():
    out = render_markdown("* a", enabled=False)
    assert "•" in out and "a" in out


def test_link():
    out = render_markdown("see [docs](https://x.io)", enabled=False)
    assert out == "see docs (https://x.io)"
    out2 = render_markdown("see [docs](https://x.io)", enabled=True)
    assert "docs" in out2 and "https://x.io" in out2


def test_plain_text_passthrough():
    out = render_markdown("nothing special here.", enabled=True)
    assert out == "nothing special here."


def test_color_instance_drives_enabled():
    c = Color(io.StringIO(), enabled=True)
    out = render_markdown("**x**", color=c)
    assert "\x1b[1m" in out
    c2 = Color(io.StringIO(), enabled=False)
    out2 = render_markdown("**x**", color=c2)
    assert out2 == "x"


def test_enabled_overrides_color():
    c = Color(io.StringIO(), enabled=True)
    out = render_markdown("**x**", color=c, enabled=False)
    assert out == "x"


def test_multi_line_mixed():
    src = "# Title\n\nSome **bold** and `code`.\n- item 1\n- item 2"
    out = render_markdown(src, enabled=False)
    lines = out.split("\n")
    assert lines[0] == "Title"
    assert lines[1] == ""
    assert lines[2] == "Some bold and code."
    assert "item 1" in lines[3]
    assert "item 2" in lines[4]
