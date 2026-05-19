"""Emoji capability + lookup tests."""

from __future__ import annotations

import io

import pytest

from codechu_cli import capabilities, e

from conftest import TTYStringIO


def test_capabilities_lang_c(monkeypatch):
    monkeypatch.setenv("LANG", "C")
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("CODECHU_CLI_EMOJI", raising=False)
    caps = capabilities(TTYStringIO())
    assert "unicode" not in caps
    assert "emoji" not in caps


def test_capabilities_unicode_locale(monkeypatch):
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("CODECHU_CLI_EMOJI", raising=False)
    caps = capabilities(TTYStringIO())
    assert "unicode" in caps
    assert "color" in caps
    assert "emoji" in caps


def test_capabilities_term_dumb_drops_color_and_emoji(monkeypatch):
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.setenv("TERM", "dumb")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("CODECHU_CLI_EMOJI", raising=False)
    caps = capabilities(TTYStringIO())
    assert "color" not in caps
    assert "emoji" not in caps


def test_capabilities_force_never(monkeypatch):
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.setenv("CODECHU_CLI_EMOJI", "never")
    caps = capabilities(TTYStringIO())
    assert "emoji" not in caps


def test_capabilities_force_always(monkeypatch):
    monkeypatch.setenv("LANG", "C")
    monkeypatch.setenv("TERM", "dumb")
    monkeypatch.setenv("CODECHU_CLI_EMOJI", "always")
    caps = capabilities(io.StringIO())
    assert "emoji" in caps


def test_capabilities_non_tty_no_color(monkeypatch):
    monkeypatch.setenv("LANG", "en_US.UTF-8")
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("NO_COLOR", raising=False)
    monkeypatch.delenv("CODECHU_CLI_EMOJI", raising=False)
    caps = capabilities(io.StringIO())
    assert "color" not in caps
    assert "emoji" not in caps


def test_e_emoji_when_capable(monkeypatch):
    monkeypatch.setenv("CODECHU_CLI_EMOJI", "always")
    assert e("ok") == "✓"
    assert e("fail") == "✗"


def test_e_fallback_when_not_capable(monkeypatch):
    monkeypatch.setenv("CODECHU_CLI_EMOJI", "never")
    assert e("ok") == "+"
    assert e("fail") == "x"
    assert e("ok", fallback="OK") == "OK"


def test_e_unknown_name_raises(monkeypatch):
    monkeypatch.setenv("CODECHU_CLI_EMOJI", "always")
    with pytest.raises(KeyError):
        e("nope")
