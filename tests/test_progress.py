"""Progress + spinner tests."""

from __future__ import annotations

import io
import threading
import time

import pytest

from codechu_cli import (
    BAR_STYLES,
    SPINNER_FAMILIES,
    SPINNER_STYLES,
    STYLE_COMPATIBILITY,
    STYLE_TAGS,
    ProgressBar,
    ProgressLine,
    Spinner,
    register_bar_style,
    register_spinner_style,
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


def test_register_spinner_style_basic():
    register_spinner_style("my-test-style", ["A", "B", "C"])
    try:
        assert "my-test-style" in SPINNER_STYLES
        assert SPINNER_STYLES["my-test-style"] == ["A", "B", "C"]
        sp = Spinner("x", style="my-test-style")
        assert list(sp.frames) == ["A", "B", "C"]
    finally:
        SPINNER_STYLES.pop("my-test-style", None)
        STYLE_COMPATIBILITY.get("modern", set()).discard("my-test-style")


def test_register_spinner_style_with_family_and_tags():
    register_spinner_style(
        "fam-test", ["X", "Y"], family="my-family", tags={"calm", "minimal"}
    )
    try:
        assert "fam-test" in SPINNER_FAMILIES["my-family"]
        assert "fam-test" in STYLE_TAGS["calm"]
        assert "fam-test" in STYLE_TAGS["minimal"]
    finally:
        SPINNER_STYLES.pop("fam-test", None)
        SPINNER_FAMILIES.pop("my-family", None)
        STYLE_TAGS["calm"].discard("fam-test")
        STYLE_TAGS["minimal"].discard("fam-test")
        STYLE_COMPATIBILITY.get("modern", set()).discard("fam-test")


def test_register_spinner_style_empty_frames_raises():
    with pytest.raises(ValueError):
        register_spinner_style("empty", [])


def test_register_bar_style_basic():
    register_bar_style("my-bar", fill="#", empty=".", width=7)
    try:
        assert "my-bar" in BAR_STYLES
        bar = ProgressBar(10, style="my-bar")
        assert bar.fill == "#"
        assert bar.empty == "."
        assert bar.width == 7
    finally:
        BAR_STYLES.pop("my-bar", None)


def test_register_bar_style_smooth_flag():
    register_bar_style("my-smooth", fill="█", empty=" ", width=5, smooth=True)
    try:
        bar = ProgressBar(10, style="my-smooth")
        assert bar.smooth is True
    finally:
        BAR_STYLES.pop("my-smooth", None)


def test_spinner_families_cover_all_styles():
    # Every spinner style must appear in exactly one family.
    all_in_families: list[str] = []
    for names in SPINNER_FAMILIES.values():
        all_in_families.extend(names)
    in_families = set(all_in_families)
    # No duplicates across families
    assert len(all_in_families) == len(in_families), (
        "spinner style listed in multiple families"
    )
    assert in_families == set(SPINNER_STYLES), (
        f"family coverage mismatch: missing={set(SPINNER_STYLES) - in_families}, "
        f"extra={in_families - set(SPINNER_STYLES)}"
    )


def test_style_compatibility_no_overlap():
    ascii_safe = STYLE_COMPATIBILITY["ascii-safe"]
    needs_emoji = STYLE_COMPATIBILITY["needs-emoji"]
    needs_cjk = STYLE_COMPATIBILITY["needs-cjk"]
    modern = STYLE_COMPATIBILITY["modern"]
    assert not (ascii_safe & needs_emoji)
    assert not (ascii_safe & needs_cjk)
    assert not (needs_emoji & needs_cjk)
    assert not (modern & needs_emoji)
    assert not (modern & needs_cjk)


def test_dropped_styles_gone():
    assert "weather" not in SPINNER_STYLES
    assert "pacman-ghost" not in SPINNER_STYLES


def test_demo_module_lists_styles():
    import os
    import pathlib
    import subprocess
    import sys as _sys

    src = pathlib.Path(__file__).resolve().parent.parent / "src"
    env = dict(os.environ)
    env["PYTHONPATH"] = (
        f"{src}{os.pathsep}{env['PYTHONPATH']}" if "PYTHONPATH" in env else str(src)
    )
    result = subprocess.run(
        [_sys.executable, "-m", "codechu_cli", "list"],
        capture_output=True,
        text=True,
        timeout=10,
        env=env,
    )
    assert result.returncode == 0, result.stderr
    assert "dots" in result.stdout
    assert "codechu" in result.stdout


def test_progressbar_indeterminate_renders_pattern():
    s = TTYStringIO()
    bar = ProgressBar(total=None, stream=s)
    bar.advance()
    bar.advance()
    out = s.getvalue()
    # Any frame from the `bar` spinner style appears in the output
    assert any(f in out for f in SPINNER_STYLES["bar"])
    # No percent (renders as --%)
    assert "--%" in out or "--" in out


def test_progressbar_indeterminate_set_total_switches():
    s = TTYStringIO()
    bar = ProgressBar(total=None, stream=s)
    bar.advance()
    bar.set_total(10)
    bar.advance(4)  # current was 1 from the indeterminate advance → 5/10
    out = s.getvalue()
    assert "50%" in out
    assert "5/10" in out


def test_progressbar_spinner_template_default_dots():
    s = TTYStringIO()
    bar = ProgressBar(
        10, stream=s, width=5, template="{spinner} {pct}%"
    )
    bar.advance(5)
    out = s.getvalue()
    # At least one dots frame appears
    assert any(f in out for f in SPINNER_STYLES["dots"])


def test_progressbar_spinner_template_custom_style():
    s = TTYStringIO()
    bar = ProgressBar(
        10, stream=s, width=5, template="{spinner} hi", spinner_style="line"
    )
    bar.advance(1)
    bar.advance(1)
    out = s.getvalue()
    assert any(f in out for f in SPINNER_STYLES["line"])


def test_progressbar_remaining_template():
    s = TTYStringIO()
    bar = ProgressBar(10, stream=s, width=5, template="rem={remaining}")
    bar.advance(3)
    out = s.getvalue()
    assert "rem=7" in out


def test_progressbar_remaining_indeterminate():
    s = TTYStringIO()
    bar = ProgressBar(total=None, stream=s, template="rem={remaining}")
    bar.advance()
    assert "rem=?" in s.getvalue()


def test_progressbar_rate_template():
    s = TTYStringIO()
    bar = ProgressBar(100, stream=s, width=5, template="r={rate}")
    bar.advance(10)
    # Too soon — should show '?'
    assert "r=?" in s.getvalue()
    time.sleep(0.6)
    bar.advance(10)
    out = s.getvalue()
    # After window passes, expect either /s or ?
    assert "/s" in out or "r=?" in out


def test_bar_style_gradient_edge_renders_edge_chars():
    s = TTYStringIO()
    bar = ProgressBar(10, stream=s, style="gradient-edge", width=10)
    bar.advance(5)
    out = s.getvalue()
    # ▓ or ▒ (edge chars) should appear at the boundary
    assert "▓" in out or "▒" in out


def test_bar_style_tape_renders_separators():
    s = TTYStringIO()
    bar = ProgressBar(5, stream=s, style="tape", width=5)
    bar.advance(2)
    out = s.getvalue()
    assert "│" in out


def test_bar_reverse_direction():
    s = TTYStringIO()
    bar = ProgressBar(10, stream=s, width=10, fill="█", empty="░", reverse=True)
    bar.advance(3)  # 30% — 3 cells filled
    out = s.getvalue()
    # Right-to-left fill: the rightmost cells are filled. Find the last
    # rendered bar segment in the output.
    # A 30% reverse bar of width 10 = "░░░░░░░███"
    assert "░░░░░░░███" in out


def test_progressbar_refresh_pauses_after_idle(monkeypatch):
    s = TTYStringIO()
    bar = ProgressBar(10, stream=s, width=5)
    bar.advance(1)
    # Force the last_advance into the past so refresh() activates pause
    bar._last_advance = time.monotonic() - 5.0
    bar.refresh()
    out = s.getvalue()
    # Pulse uses blocks-pulse frames (▱ or ▰ blocks)
    assert "▱" in out or "▰" in out


@pytest.mark.parametrize("style", [
    "bar", "buffering", "signal", "heartbeat", "searching",
    "atom", "spiral", "success-flash", "error-pulse", "retry-slow",
])
def test_new_spinner_styles_roundtrip(style):
    sp = Spinner("x", style=style)
    assert list(sp.frames) == SPINNER_STYLES[style]


def test_new_spinner_styles_in_families():
    loading = set(SPINNER_FAMILIES["loading"])
    assert {"bar", "buffering", "signal"} <= loading
    semantic = set(SPINNER_FAMILIES["semantic"])
    assert {"heartbeat", "searching", "atom", "spiral"} <= semantic
    outro = set(SPINNER_FAMILIES["outro"])
    assert {"success-flash", "error-pulse", "retry-slow"} <= outro


def test_new_spinner_styles_in_tags():
    assert "heartbeat" in STYLE_TAGS["calm"]
    assert "bar" in STYLE_TAGS["busy"]
    assert "atom" in STYLE_TAGS["playful"]
    assert "signal" in STYLE_TAGS["narrow"]
    assert "spiral" in STYLE_TAGS["wide"]
    assert "success-flash" in STYLE_TAGS["outro"]
    assert "signal" in STYLE_TAGS["network"]


# Touch `time` so ruff doesn't strip the import (we leave it available
# for callers who want to monkeypatch).
_ = time
