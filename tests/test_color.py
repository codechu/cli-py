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
