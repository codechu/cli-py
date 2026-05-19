"""Prompt tests — confirm, prompt, select, multiselect (fallback path)."""

from __future__ import annotations

import io

import pytest

from codechu_cli import confirm, multiselect, prompt, select

from conftest import TTYStringIO


def test_confirm_assume_yes_short_circuits():
    assert confirm("ok?", assume_yes=True) is True


def test_confirm_non_tty_returns_default():
    s = io.StringIO()
    assert confirm("ok?", default=True, stream=s, in_stream=io.StringIO()) is True
    assert confirm("ok?", default=False, stream=s, in_stream=io.StringIO()) is False


def test_confirm_yes():
    s = TTYStringIO()
    assert confirm("ok?", stream=s, in_stream=io.StringIO("y\n")) is True


def test_confirm_no():
    s = TTYStringIO()
    assert confirm("ok?", stream=s, in_stream=io.StringIO("n\n")) is False


def test_confirm_empty_uses_default():
    s = TTYStringIO()
    assert confirm("ok?", default=True, stream=s, in_stream=io.StringIO("\n")) is True
    assert confirm("ok?", default=False, stream=s, in_stream=io.StringIO("\n")) is False


def test_prompt_default_used_when_blank_input():
    s = TTYStringIO()
    out = prompt("name", default="alice", stream=s, in_stream=io.StringIO("\n"))
    assert out == "alice"


def test_prompt_returns_user_input():
    s = TTYStringIO()
    out = prompt("name", stream=s, in_stream=io.StringIO("bob\n"))
    assert out == "bob"


def test_prompt_validate_loops_on_tty():
    s = TTYStringIO()

    def v(x: str) -> None:
        if not x.isdigit():
            raise ValueError("must be number")

    out = prompt("n", validate=v, stream=s, in_stream=io.StringIO("abc\n42\n"))
    assert out == "42"


def test_prompt_validate_raises_on_non_tty():
    s = io.StringIO()

    def v(x: str) -> None:
        raise ValueError("never ok")

    with pytest.raises(ValueError):
        prompt("n", validate=v, stream=s, in_stream=io.StringIO("hi\n"))


def test_select_fallback_numbered():
    s = TTYStringIO()
    # in_stream is a plain StringIO (not a TTY) — forces fallback even
    # though `stream` reports TTY.
    result = select(
        "Pick",
        ["alpha", "beta", "gamma"],
        default=1,
        stream=s,
        in_stream=io.StringIO("3\n"),
    )
    assert result == "gamma"
    assert "alpha" in s.getvalue()
    assert "beta" in s.getvalue()


def test_select_fallback_empty_uses_default():
    s = TTYStringIO()
    result = select(
        "Pick",
        [("A", 1), ("B", 2), ("C", 3)],
        default=1,
        stream=s,
        in_stream=io.StringIO("\n"),
    )
    assert result == 2


def test_select_empty_choices_raises():
    with pytest.raises(ValueError):
        select("Pick", [])


def test_multiselect_fallback_blank_returns_defaults():
    s = TTYStringIO()
    result = multiselect(
        "Pick",
        ["a", "b", "c"],
        defaults=(0, 2),
        stream=s,
        in_stream=io.StringIO("\n"),
    )
    assert result == ["a", "c"]


def test_multiselect_fallback_parses_indices():
    s = TTYStringIO()
    result = multiselect(
        "Pick",
        [("a", 10), ("b", 20), ("c", 30)],
        stream=s,
        in_stream=io.StringIO("1,3\n"),
    )
    assert result == [10, 30]


def test_multiselect_empty_choices_returns_empty():
    assert multiselect("x", []) == []
