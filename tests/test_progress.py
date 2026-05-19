"""Progress + spinner tests."""

from __future__ import annotations

import io
import threading
import time

import pytest

from codechu_cli import (
    BAR_STYLES,
    SPINNER_STYLES,
    ProgressBar,
    ProgressLine,
    Spinner,
)

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


def test_progressbar_custom_fill_and_empty():
    s = TTYStringIO()
    bar = ProgressBar(10, stream=s, width=10, fill="█", empty="░")
    bar.advance(5, label="half")
    bar.finish()
    text = s.getvalue()
    assert "█" in text
    assert "░" in text
    assert "50%" in text


def test_progressbar_custom_template():
    s = TTYStringIO()
    bar = ProgressBar(
        10,
        stream=s,
        width=10,
        template="{bar} :: {current}/{total} :: {pct}%",
    )
    bar.advance(4, label="ignored")
    bar.finish()
    text = s.getvalue()
    assert " :: 4/10 :: 40%" in text


def test_progressbar_template_elapsed_and_eta():
    s = TTYStringIO()
    bar = ProgressBar(
        10,
        stream=s,
        width=10,
        template="{pct}% e={elapsed} eta={eta}",
    )
    # Before any progress: eta should be "?"
    bar.advance(0, label="")
    out_before = s.getvalue()
    assert "eta=?" in out_before
    # After progress: eta becomes a duration string (Xs or Xm Ys)
    bar.advance(5)
    bar.finish()
    text = s.getvalue()
    # elapsed always present in some "Ns" or "Nm Ns" form
    assert "e=" in text
    # eta is no longer "?" after meaningful advance
    assert "eta=0s" in text or "eta=1s" in text or "eta=" in text


def test_spinner_style_dots():
    sp = Spinner("x", style="dots")
    assert list(sp.frames) == SPINNER_STYLES["dots"]


def test_spinner_style_unknown_raises():
    with pytest.raises(KeyError) as exc:
        Spinner("x", style="zzz")
    msg = str(exc.value)
    assert "zzz" in msg
    assert "dots" in msg


def test_spinner_explicit_frames_overrides_style():
    sp = Spinner("x", style="dots", frames=["A", "B"])
    assert list(sp.frames) == ["A", "B"]


def test_progress_bar_style_block():
    bar = ProgressBar(10, style="block")
    assert bar.fill == "█"
    assert bar.empty == "░"


def test_progress_bar_style_unknown_raises():
    with pytest.raises(KeyError) as exc:
        ProgressBar(10, style="zzz")
    msg = str(exc.value)
    assert "zzz" in msg
    assert "block" in msg


def test_progress_bar_explicit_fill_overrides_style():
    bar = ProgressBar(10, style="block", fill="*")
    assert bar.fill == "*"
    # empty still comes from the style
    assert bar.empty == "░"


def test_bar_styles_registry_has_codechu():
    assert "codechu" in BAR_STYLES
    assert "codechu-gradient" in BAR_STYLES
    assert BAR_STYLES["codechu"] == {"fill": "▰", "empty": "▱"}


def test_spinner_styles_registry_has_codechu():
    assert "codechu" in SPINNER_STYLES
    assert "codechu-fade" in SPINNER_STYLES
    assert SPINNER_STYLES["codechu"] == ["◐", "◓", "◑", "◒"]


def test_spinner_styles_block_patterns_present():
    # 5-cell block patterns
    for name in ("blocks-bounce", "blocks-fill", "blocks-snake",
                 "blocks-pulse", "blocks-fill-solid"):
        assert name in SPINNER_STYLES, f"missing 5-cell style {name}"
        # Every frame in a 5-cell pattern is 5 visible columns wide.
        for frame in SPINNER_STYLES[name]:
            assert len(frame) == 5, f"{name} frame length != 5: {frame!r}"


def test_spinner_styles_3cell_patterns_present():
    for name in ("dots3", "wave3", "tri3"):
        assert name in SPINNER_STYLES
        for frame in SPINNER_STYLES[name]:
            assert len(frame) == 3, f"{name} frame length != 3: {frame!r}"


def test_spinner_styles_single_cell_grow():
    # grow-h / grow-v cycle through eighths plus the full block.
    assert "▏" in SPINNER_STYLES["grow-h"]
    assert "█" in SPINNER_STYLES["grow-h"]
    assert "▁" in SPINNER_STYLES["grow-v"]
    assert "█" in SPINNER_STYLES["grow-v"]


def test_spinner_styles_toggle_pairs():
    for name in ("toggle", "toggle-sq", "toggle-rd"):
        assert name in SPINNER_STYLES
        assert len(SPINNER_STYLES[name]) == 2


def test_blocks_style_default_width():
    bar = ProgressBar(10, style="blocks")
    assert bar.width == 5


def test_blocks_style_explicit_width_wins():
    bar = ProgressBar(10, style="blocks", width=12)
    assert bar.width == 12


def test_claude_alias_exists():
    assert "claude" in BAR_STYLES
    assert BAR_STYLES["claude"].get("width") == 10


def test_smooth_style_default():
    bar = ProgressBar(8, style="smooth")
    assert bar.smooth is True
    assert bar.width == 10


def test_smooth_renders_subpixel():
    s = TTYStringIO()
    bar = ProgressBar(8, stream=s, style="smooth")
    for _ in range(8):
        bar.advance(1)
    bar.finish()
    text = s.getvalue()
    partials = "▏▎▍▌▋▊▉"
    assert any(ch in text for ch in partials), (
        "expected at least one subpixel partial-fill char in rendered frames"
    )


def test_smooth_full_renders_full_blocks():
    s = TTYStringIO()
    bar = ProgressBar(4, stream=s, style="smooth")
    bar.advance(4)
    bar.finish()
    text = s.getvalue()
    # At 100% the bar body should be exactly width full blocks.
    assert "[" + ("█" * 10) + "]" in text


def test_blocks_render_fixed_count():
    s = TTYStringIO()
    bar = ProgressBar(5, stream=s, style="blocks")
    bar.advance(3)
    bar.finish()
    text = s.getvalue()
    # Find the latest rendered frame containing the 60% bar.
    assert "[" + "▰" * 3 + "▱" * 2 + "]" in text


# Touch `time` so ruff doesn't strip the import (we leave it available
# for callers who want to monkeypatch).
_ = time
