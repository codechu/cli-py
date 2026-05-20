"""Color tests — fluent API, TTY detection, explicit enabled flag."""

from __future__ import annotations

import io

import pytest

from codechu_cli import Color

from conftest import TTYStringIO


def test_disabled_on_non_tty():
    s = io.StringIO()
    c = Color(s)
    assert c.enabled is False
    assert c.low("ok") == "ok"


def test_enabled_on_tty():
    s = TTYStringIO()
    c = Color(s)
    assert c.enabled is True
    out = c.low("ok")
    assert out.startswith("\033[32m")
    assert out.endswith("\033[0m")


def test_color_ignores_no_color_env(monkeypatch):
    # New rule: Color must NOT read environment variables. NO_COLOR set
    # in the env does not turn color off on a TTY stream.
    monkeypatch.setenv("NO_COLOR", "1")
    c = Color(TTYStringIO())
    assert c.enabled is True
    assert c.high("bad").startswith("\033[31m")


def test_unknown_code_raises_attribute_error():
    c = Color(TTYStringIO())
    with pytest.raises(AttributeError):
        c.notacode  # noqa: B018 — exercising __getattr__


def test_isatty_raises_is_treated_as_non_tty():
    class Broken:
        def isatty(self):
            raise RuntimeError("nope")

    c = Color(Broken())
    assert c.enabled is False


def test_custom_palette_extends_defaults():
    c = Color(TTYStringIO(), palette={"snap-edge": "\033[35m"})
    out = c.__getattr__("snap-edge")("edge") if False else None  # noqa
    # palette keys with hyphens go via __getattr__ — but Python attr
    # access doesn't allow hyphens, so callers using non-identifier
    # keys must wrap them. Verify via a clean identifier key instead.
    c2 = Color(TTYStringIO(), palette={"snapedge": "\033[35m"})
    out = c2.snapedge("edge")
    assert out.startswith("\033[35m")
    assert out.endswith("\033[0m")
    # Defaults still present
    assert c.low("ok").startswith("\033[32m")
    assert out  # silence linter


def test_custom_palette_overrides_default():
    c = Color(TTYStringIO(), palette={"low": "\033[95m"})
    assert c.low("x").startswith("\033[95m")


def test_enabled_true_overrides_non_tty():
    c = Color(io.StringIO(), enabled=True)
    assert c.enabled is True
    assert c.low("ok").startswith("\033[32m")


def test_enabled_false_disables_on_tty():
    c = Color(TTYStringIO(), enabled=False)
    assert c.enabled is False
    assert c.low("ok") == "ok"


def test_methods_are_callable_per_palette_key():
    c = Color(TTYStringIO())
    for key in ("low", "medium", "high", "info", "bold", "dim"):
        method = getattr(c, key)
        assert callable(method)
        assert method("x").endswith("\033[0m")
