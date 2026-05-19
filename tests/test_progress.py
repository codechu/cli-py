"""Progress + spinner tests."""

from __future__ import annotations

import io
import threading
import time

from codechu_cli import ProgressBar, ProgressLine, Spinner

from conftest import TTYStringIO


def test_progressline_noop_on_non_tty():
    s = io.StringIO()
    pl = ProgressLine(s)
    assert pl.enabled is False
    pl.update("hello")
    pl.clear()
    assert s.getvalue() == ""


def test_progressline_writes_with_carriage_return():
    s = TTYStringIO()
    pl = ProgressLine(s)
    pl.update("foo")
    pl.update("bar")
    out = s.getvalue()
    assert "\rfoo" in out
    assert "\rbar" in out


def test_progressline_clear_emits_blanks():
    s = TTYStringIO()
    pl = ProgressLine(s)
    pl.update("hello")
    pl.clear()
    # Second \r followed by spaces and trailing \r
    assert s.getvalue().endswith("\r")


def test_progressbar_advance_and_finish():
    s = TTYStringIO()
    bar = ProgressBar(10, stream=s, width=10)
    bar.advance(3, label="step")
    bar.advance(7)
    bar.finish()
    text = s.getvalue()
    assert "30%" in text
    assert "100%" in text
    assert "3/10" in text
    assert "10/10" in text
    assert "step" in text


def test_progressbar_set_total():
    s = TTYStringIO()
    bar = ProgressBar(5, stream=s, width=10)
    bar.advance(1)
    bar.set_total(20)
    bar.advance(0)
    assert "1/20" in s.getvalue()


def test_progressbar_disabled_on_non_tty():
    s = io.StringIO()
    bar = ProgressBar(10, stream=s)
    bar.advance(5)
    bar.finish()
    assert s.getvalue() == ""


def test_spinner_start_stop_without_sleep(monkeypatch):
    """Spinner background thread paints at least one frame, then stops cleanly."""
    s = TTYStringIO()
    painted = threading.Event()

    real_update = ProgressLine.update

    def watching_update(self, msg):
        real_update(self, msg)
        painted.set()

    monkeypatch.setattr(ProgressLine, "update", watching_update)

    sp = Spinner("working", stream=s, interval=0.01)
    sp.start()
    try:
        # Wait for at least one paint, but with a tight deadline.
        assert painted.wait(2.0), "spinner thread never painted a frame"
    finally:
        sp.stop()

    assert sp._thread is None
    assert "working" in s.getvalue()


def test_spinner_noop_on_non_tty():
    s = io.StringIO()
    sp = Spinner("hi", stream=s)
    sp.start()
    sp.stop()
    assert s.getvalue() == ""


def test_spinner_context_manager(monkeypatch):
    s = TTYStringIO()
    with Spinner("ctx", stream=s, interval=0.01) as sp:
        assert sp._thread is not None
    assert sp._thread is None


def test_spinner_ascii_fallback_when_no_unicode(monkeypatch):
    monkeypatch.setenv("LANG", "C")
    monkeypatch.setenv("TERM", "dumb")
    s = TTYStringIO()
    sp = Spinner("x", stream=s)
    assert sp.frames == ("|", "/", "-", "\\")


# Touch `time` so ruff doesn't strip the import (we leave it available
# for callers who want to monkeypatch).
_ = time
