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


def test_e_emoji_when_capable():
    caps = {"emoji"}
    assert e("ok", caps) == "✓"
    assert e("fail", caps) == "✗"


def test_e_fallback_when_not_capable():
    caps: set[str] = set()
    assert e("ok", caps) == "+"
    assert e("fail", caps) == "x"
    assert e("ok", caps, fallback="OK") == "OK"


def test_e_caps_none_returns_fallback():
    # Explicit-config rule: omitting caps must NOT silently consult the
    # environment. It returns the ASCII fallback.
    assert e("ok") == "+"
    assert e("fail") == "x"


def test_e_unknown_name_raises():
    with pytest.raises(KeyError):
        e("nope", {"emoji"})


def test_register_adds_glyph():
    from codechu_cli import emoji as _emoji

    _emoji.register("snap", "📦", "snap")
    try:
        assert e("snap", {"emoji"}) == "📦"
        assert e("snap", set()) == "snap"
    finally:
        # cleanup so other tests don't see this glyph
        _emoji._GLYPHS.pop("snap", None)


def test_register_overrides_existing():
    from codechu_cli import emoji as _emoji

    original = _emoji._GLYPHS["ok"]
    _emoji.register("ok", "Y", "y")
    try:
        assert e("ok", {"emoji"}) == "Y"
    finally:
        _emoji._GLYPHS["ok"] = original


def test_update_bulk():
    from codechu_cli import emoji as _emoji

    _emoji.update({
        "rocket": ("🚀", "^"),
        "star": ("⭐", "*"),
    })
    try:
        assert e("rocket", {"emoji"}) == "🚀"
        assert e("star", {"emoji"}) == "⭐"
    finally:
        _emoji._GLYPHS.pop("rocket", None)
        _emoji._GLYPHS.pop("star", None)


def test_known_lists_registered_names():
    from codechu_cli import emoji as _emoji

    names = _emoji.known()
    assert isinstance(names, list)
    # The built-in defaults should always be in there.
    assert "ok" in names
    assert "fail" in names
