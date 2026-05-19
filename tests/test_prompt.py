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


def test_confirm_custom_yes_no_chars_turkish():
    # "e" / "h" + full words "evet" / "hayır"
    s = TTYStringIO()
    assert confirm(
        "Devam?",
        stream=s,
        in_stream=io.StringIO("e\n"),
        yes_chars=("e", "evet"),
        no_chars=("h", "hayır"),
    ) is True
    s2 = TTYStringIO()
    assert confirm(
        "Devam?",
        stream=s2,
        in_stream=io.StringIO("hayır\n"),
        yes_chars=("e", "evet"),
        no_chars=("h", "hayır"),
    ) is False


def test_confirm_custom_suffix_format_renders():
    s = TTYStringIO()
    confirm(
        "Tamam mı?",
        stream=s,
        in_stream=io.StringIO("e\n"),
        yes_chars=("e", "evet"),
        no_chars=("h", "hayır"),
        suffix_format="({yes}/{no})",
    )
    out = s.getvalue()
    assert "(e/H)" in out  # default=False uppercases no


def test_confirm_translate_wraps_suffix():
    s = TTYStringIO()
    seen: list[str] = []

    def fake_t(msg: str) -> str:
        seen.append(msg)
        return msg.upper()

    confirm(
        "ok?",
        stream=s,
        in_stream=io.StringIO("y\n"),
        translate=fake_t,
    )
    out = s.getvalue()
    # Translator was called with the suffix template before formatting? No —
    # we wrap the formatted suffix. Verify it ran on the suffix string.
    assert any("[" in m and "]" in m for m in seen)
    # The translated (uppercased) suffix lands in output.
    assert "[Y/N]" in out


def test_prompt_translate_wraps_validator_error():
    s = TTYStringIO()

    def v(x: str) -> None:
        if not x.isdigit():
            raise ValueError("must be number")

    # Translator that prefixes [tr] so we can see it landed
    def t(msg: str) -> str:
        return "[tr] " + msg

    out = prompt(
        "n",
        validate=v,
        stream=s,
        in_stream=io.StringIO("abc\n42\n"),
        translate=t,
    )
    assert out == "42"
    assert "[tr] Invalid input: must be number" in s.getvalue()
