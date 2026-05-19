"""Color tests — enable/disable, NO_COLOR, TTY detection."""

from __future__ import annotations

import io

from codechu_cli import Color

from conftest import TTYStringIO


def test_disabled_on_non_tty():
    s = io.StringIO()
    c = Color(s)
    assert c.enabled is False
    assert c("low", "ok") == "ok"


def test_enabled_on_tty(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    s = TTYStringIO()
    c = Color(s)
    assert c.enabled is True
    out = c("low", "ok")
    assert out.startswith("\033[32m")
    assert out.endswith("\033[0m")


def test_no_color_env_disables(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    c = Color(TTYStringIO())
    assert c.enabled is False
    assert c("high", "bad") == "bad"


def test_unknown_code_passthrough(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    c = Color(TTYStringIO())
    assert c("notacode", "text") == "text"


def test_isatty_raises_is_treated_as_non_tty():
    class Broken:
        def isatty(self):
            raise RuntimeError("nope")

    c = Color(Broken())
    assert c.enabled is False


def test_custom_palette_extends_defaults(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    c = Color(TTYStringIO(), palette={"snap-edge": "\033[35m"})
    out = c("snap-edge", "edge")
    assert out.startswith("\033[35m")
    assert out.endswith("\033[0m")
    # Defaults still present
    assert c("low", "ok").startswith("\033[32m")


def test_custom_palette_overrides_default(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    c = Color(TTYStringIO(), palette={"low": "\033[95m"})
    assert c("low", "x").startswith("\033[95m")


def test_force_true_overrides_no_color(monkeypatch):
    monkeypatch.setenv("NO_COLOR", "1")
    c = Color(io.StringIO(), force=True)
    assert c.enabled is True
    assert c("low", "ok").startswith("\033[32m")


def test_force_false_disables_on_tty(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    c = Color(TTYStringIO(), force=False)
    assert c.enabled is False
    assert c("low", "ok") == "ok"


def test_palette_alias_backwards_compat():
    # Old callers may still touch Color.PALETTE — keep it as an alias.
    assert Color.PALETTE is Color.DEFAULT_PALETTE
