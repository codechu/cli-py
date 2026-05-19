"""Banner tests."""

from __future__ import annotations

import io

from codechu_cli import LOGOS, ascii_banner, banner

from conftest import TTYStringIO


def test_banner_silent_on_non_tty():
    s = io.StringIO()
    banner("Tool", "1.0.0", stream=s)
    assert s.getvalue() == ""


def test_banner_emits_on_tty(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    s = TTYStringIO()
    banner("Tool", "1.0.0", mode="dry-run", stream=s)
    out = s.getvalue()
    assert "Tool 1.0.0" in out
    assert "dry-run" in out


def test_banner_without_mode():
    s = TTYStringIO()
    banner("Tool", "1.0.0", stream=s)
    assert "Tool 1.0.0" in s.getvalue()


# --- ascii_banner -----------------------------------------------------


def test_ascii_banner_silent_on_non_tty():
    s = io.StringIO()
    ascii_banner("HELLO", stream=s)
    assert s.getvalue() == ""


def test_ascii_banner_emits_on_tty():
    s = TTYStringIO()
    ascii_banner("LINE-A\nLINE-B\n", stream=s)
    out = s.getvalue()
    assert "LINE-A" in out
    assert "LINE-B" in out


def test_ascii_banner_force_enabled_on_non_tty():
    s = io.StringIO()
    ascii_banner("FORCED", stream=s, enabled=True)
    assert "FORCED" in s.getvalue()


def test_ascii_banner_silent_when_explicitly_disabled():
    s = TTYStringIO()
    ascii_banner("MUTED", stream=s, enabled=False)
    assert s.getvalue() == ""


def test_ascii_banner_color_wraps_lines(monkeypatch):
    monkeypatch.delenv("NO_COLOR", raising=False)
    s = TTYStringIO()
    ascii_banner("XYZ", color="low", stream=s)
    out = s.getvalue()
    assert "\x1b[32m" in out  # green ANSI
    assert "XYZ" in out


def test_ascii_banner_empty_input_is_noop():
    s = TTYStringIO()
    ascii_banner("", stream=s)
    assert s.getvalue() == ""


def test_logos_registry_has_known_keys():
    assert "codechu" in LOGOS
    assert isinstance(LOGOS["codechu"], str)
    assert LOGOS["codechu"].count("\n") >= 4  # multi-line
