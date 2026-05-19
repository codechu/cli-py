"""Format detection + epilog rendering tests."""

from __future__ import annotations

import io

from codechu_cli import format_examples, resolve_format

from conftest import TTYStringIO


def test_resolve_format_pipe_default():
    assert resolve_format(io.StringIO()) == "json"


def test_resolve_format_tty_default():
    assert resolve_format(TTYStringIO()) == "table"


def test_resolve_format_custom_defaults():
    assert resolve_format(io.StringIO(), tty_default="x", pipe_default="y") == "y"
    assert resolve_format(TTYStringIO(), tty_default="x", pipe_default="y") == "x"


def test_resolve_format_broken_isatty():
    class B:
        def isatty(self):
            raise RuntimeError("boom")

    assert resolve_format(B()) == "json"


def test_format_examples_empty():
    assert format_examples([]) == ""


def test_format_examples_aligns_columns():
    out = format_examples([("foo", "do foo"), ("bar baz", "do bar")])
    lines = out.splitlines()
    assert lines[0] == "Examples:"
    assert "foo" in lines[1]
    assert "do foo" in lines[1]
    assert "bar baz" in lines[2]


def test_format_examples_long_command_wraps():
    long = "x" * 70
    out = format_examples([(long, "desc")])
    assert long in out
    assert "desc" in out
