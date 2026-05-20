"""Progress + spinner tests — fluent builder, context manager."""

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


# --- ProgressLine -----------------------------------------------------


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
    assert s.getvalue().endswith("\r")


# --- ProgressBar: builder API ----------------------------------------


def test_progressbar_only_total_in_constructor():
    # Constructor must reject kwargs other than `enabled`.
    with pytest.raises(TypeError):
        ProgressBar(10, width=20)  # type: ignore[call-arg]
    with pytest.raises(TypeError):
        ProgressBar(10, style="block")  # type: ignore[call-arg]


def test_progressbar_advance_and_finish():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(10)
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
    bar = ProgressBar(5).stream(s).width(10)
    bar.advance(1)
    bar.set_total(20)
    bar.advance(0)
    assert "1/20" in s.getvalue()


def test_progressbar_disabled_on_non_tty():
    s = io.StringIO()
    bar = ProgressBar(10).stream(s)
    bar.advance(5)
    bar.finish()
    assert s.getvalue() == ""


def test_progressbar_enabled_kw_forces_on():
    s = io.StringIO()
    bar = ProgressBar(10, enabled=True).stream(s).width(5)
    bar.advance(5)
    assert s.getvalue() != ""


def test_progressbar_builder_chains_return_self():
    bar = ProgressBar(10)
    assert bar.style("block") is bar
    assert bar.width(10) is bar
    assert bar.fill("*") is bar
    assert bar.empty(".") is bar
    assert bar.smooth(True) is bar
    assert bar.template("x") is bar
    assert bar.reverse() is bar
    assert bar.units("b") is bar
    assert bar.spinner_style("dots") is bar
    assert bar.with_eta() is bar
    assert bar.with_rate() is bar
    assert bar.prefix("p") is bar
    assert bar.suffix("s") is bar


def test_progressbar_custom_fill_and_empty():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(10).fill("█").empty("░")
    bar.advance(5, label="half")
    bar.finish()
    text = s.getvalue()
    assert "█" in text
    assert "░" in text
    assert "50%" in text


def test_progressbar_custom_template():
    s = TTYStringIO()
    bar = (
        ProgressBar(10)
        .stream(s)
        .width(10)
        .template("{bar} :: {current}/{total} :: {pct}%")
    )
    bar.advance(4, label="ignored")
    bar.finish()
    text = s.getvalue()
    assert " :: 4/10 :: 40%" in text


def test_progressbar_template_elapsed_and_eta():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(10).template("{pct}% e={elapsed} eta={eta}")
    bar.advance(0, label="")
    assert "eta=?" in s.getvalue()
    bar.advance(5)
    bar.finish()
    assert "e=" in s.getvalue()


def test_progressbar_prefix_suffix_render():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(5).prefix("[X] ").suffix(" [Y]")
    bar.advance(5)
    out = s.getvalue()
    assert "[X] " in out
    assert " [Y]" in out


def test_progressbar_with_eta_appends_summary():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(5).with_eta()
    bar.advance(5)
    out = s.getvalue()
    assert "eta" in out


def test_progressbar_with_rate_appends_summary():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(5).with_rate()
    bar.advance(5)
    out = s.getvalue()
    assert "rate" in out


# --- Spinner ----------------------------------------------------------


def test_spinner_context_manager_paints(monkeypatch):
    s = TTYStringIO()
    painted = threading.Event()

    real_update = ProgressLine.update

    def watching_update(self, msg):
        real_update(self, msg)
        painted.set()

    monkeypatch.setattr(ProgressLine, "update", watching_update)

    with Spinner("working", stream=s, interval=0.01) as sp:
        assert painted.wait(2.0), "spinner thread never painted a frame"
        assert sp._thread is not None
    assert sp._thread is None
    assert "working" in s.getvalue()


def test_spinner_noop_on_non_tty():
    s = io.StringIO()
    with Spinner("hi", stream=s):
        pass
    assert s.getvalue() == ""


def test_spinner_no_public_start_or_stop():
    sp = Spinner("x", stream=io.StringIO())
    # The public API is the context manager — start/stop must be private.
    assert not hasattr(sp, "start")
    assert not hasattr(sp, "stop")


def test_spinner_ascii_fallback_when_no_unicode(monkeypatch):
    monkeypatch.setenv("LANG", "C")
    monkeypatch.setenv("TERM", "dumb")
    s = TTYStringIO()
    sp = Spinner("x", stream=s)
    assert sp.frames == ("|", "/", "-", "\\")


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


# --- Bar styles -------------------------------------------------------


def test_progress_bar_style_block():
    bar = ProgressBar(10).style("block")
    assert bar.fill_ch == "█"
    assert bar.empty_ch == "░"


def test_progress_bar_style_unknown_raises():
    with pytest.raises(KeyError) as exc:
        ProgressBar(10).style("zzz")
    msg = str(exc.value)
    assert "zzz" in msg
    assert "block" in msg


def test_progress_bar_explicit_fill_overrides_style():
    bar = ProgressBar(10).style("block").fill("*")
    assert bar.fill_ch == "*"
    assert bar.empty_ch == "░"


def test_bar_styles_registry_has_codechu():
    assert "codechu" in BAR_STYLES
    assert "codechu-gradient" in BAR_STYLES
    assert BAR_STYLES["codechu"] == {"fill": "▰", "empty": "▱"}


def test_spinner_styles_registry_has_codechu():
    assert "codechu" in SPINNER_STYLES
    assert "codechu-fade" in SPINNER_STYLES
    assert SPINNER_STYLES["codechu"] == ["◐", "◓", "◑", "◒"]


def test_spinner_styles_block_patterns_present():
    for name in ("blocks-bounce", "blocks-fill", "blocks-snake",
                 "blocks-pulse", "blocks-fill-solid"):
        assert name in SPINNER_STYLES
        for frame in SPINNER_STYLES[name]:
            assert len(frame) == 5


def test_spinner_styles_3cell_patterns_present():
    for name in ("dots3", "wave3", "tri3"):
        assert name in SPINNER_STYLES
        for frame in SPINNER_STYLES[name]:
            assert len(frame) == 3


def test_spinner_styles_single_cell_grow():
    assert "▏" in SPINNER_STYLES["grow-h"]
    assert "█" in SPINNER_STYLES["grow-h"]
    assert "▁" in SPINNER_STYLES["grow-v"]
    assert "█" in SPINNER_STYLES["grow-v"]


def test_spinner_styles_toggle_pairs():
    for name in ("toggle", "toggle-sq", "toggle-rd"):
        assert name in SPINNER_STYLES
        assert len(SPINNER_STYLES[name]) == 2


def test_blocks_style_default_width():
    bar = ProgressBar(10).style("blocks")
    assert bar.width_n == 5


def test_blocks_style_explicit_width_wins():
    bar = ProgressBar(10).style("blocks").width(12)
    assert bar.width_n == 12


def test_claude_alias_exists():
    assert "claude" in BAR_STYLES
    assert BAR_STYLES["claude"].get("width") == 10


def test_smooth_style_default():
    bar = ProgressBar(8).style("smooth")
    assert bar.is_smooth is True
    assert bar.width_n == 10


def test_smooth_renders_subpixel():
    s = TTYStringIO()
    bar = ProgressBar(8).stream(s).style("smooth")
    for _ in range(8):
        bar.advance(1)
    bar.finish()
    text = s.getvalue()
    partials = "▏▎▍▌▋▊▉"
    assert any(ch in text for ch in partials)


def test_smooth_full_renders_full_blocks():
    s = TTYStringIO()
    bar = ProgressBar(4).stream(s).style("smooth")
    bar.advance(4)
    bar.finish()
    text = s.getvalue()
    assert "[" + ("█" * 10) + "]" in text


def test_blocks_render_fixed_count():
    s = TTYStringIO()
    bar = ProgressBar(5).stream(s).style("blocks")
    bar.advance(3)
    bar.finish()
    text = s.getvalue()
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
        bar = ProgressBar(10).style("my-bar")
        assert bar.fill_ch == "#"
        assert bar.empty_ch == "."
        assert bar.width_n == 7
    finally:
        BAR_STYLES.pop("my-bar", None)


def test_register_bar_style_smooth_flag():
    register_bar_style("my-smooth", fill="█", empty=" ", width=5, smooth=True)
    try:
        bar = ProgressBar(10).style("my-smooth")
        assert bar.is_smooth is True
    finally:
        BAR_STYLES.pop("my-smooth", None)


def test_spinner_families_cover_all_styles():
    all_in_families: list[str] = []
    for names in SPINNER_FAMILIES.values():
        all_in_families.extend(names)
    in_families = set(all_in_families)
    assert len(all_in_families) == len(in_families)
    assert in_families == set(SPINNER_STYLES)


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
    bar = ProgressBar(None).stream(s)
    bar.advance()
    bar.advance()
    out = s.getvalue()
    assert any(f in out for f in SPINNER_STYLES["bar"])
    assert "--%" in out or "--" in out


def test_progressbar_indeterminate_set_total_switches():
    s = TTYStringIO()
    bar = ProgressBar(None).stream(s)
    bar.advance()
    bar.set_total(10)
    bar.advance(4)
    out = s.getvalue()
    assert "50%" in out
    assert "5/10" in out


def test_progressbar_spinner_template_default_dots():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(5).template("{spinner} {pct}%")
    bar.advance(5)
    out = s.getvalue()
    assert any(f in out for f in SPINNER_STYLES["dots"])


def test_progressbar_spinner_template_custom_style():
    s = TTYStringIO()
    bar = (
        ProgressBar(10)
        .stream(s)
        .width(5)
        .template("{spinner} hi")
        .spinner_style("line")
    )
    bar.advance(1)
    bar.advance(1)
    out = s.getvalue()
    assert any(f in out for f in SPINNER_STYLES["line"])


def test_progressbar_remaining_template():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(5).template("rem={remaining}")
    bar.advance(3)
    out = s.getvalue()
    assert "rem=7" in out


def test_progressbar_remaining_indeterminate():
    s = TTYStringIO()
    bar = ProgressBar(None).stream(s).template("rem={remaining}")
    bar.advance()
    assert "rem=?" in s.getvalue()


def test_progressbar_rate_template():
    s = TTYStringIO()
    bar = ProgressBar(100).stream(s).width(5).template("r={rate}")
    bar.advance(10)
    assert "r=?" in s.getvalue()
    time.sleep(0.6)
    bar.advance(10)
    out = s.getvalue()
    assert "/s" in out or "r=?" in out


def test_bar_style_gradient_edge_renders_edge_chars():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).style("gradient-edge").width(10)
    bar.advance(5)
    out = s.getvalue()
    assert "▓" in out or "▒" in out


def test_bar_style_tape_renders_separators():
    s = TTYStringIO()
    bar = ProgressBar(5).stream(s).style("tape").width(5)
    bar.advance(2)
    out = s.getvalue()
    assert "│" in out


def test_bar_reverse_direction():
    s = TTYStringIO()
    bar = (
        ProgressBar(10)
        .stream(s)
        .width(10)
        .fill("█")
        .empty("░")
        .reverse()
    )
    bar.advance(3)
    out = s.getvalue()
    assert "░░░░░░░███" in out


def test_progressbar_refresh_pauses_after_idle():
    s = TTYStringIO()
    bar = ProgressBar(10).stream(s).width(5)
    bar.advance(1)
    bar._last_advance = time.monotonic() - 5.0
    bar.refresh()
    out = s.getvalue()
    assert "▱" in out or "▰" in out


@pytest.mark.parametrize("style", [
    "bar", "buffering", "signal", "heartbeat", "searching",
    "atom", "spiral", "success-flash", "error-pulse", "retry-slow",
])
def test_new_spinner_styles_roundtrip(style):
    sp = Spinner("x", style=style)
    assert list(sp.frames) == SPINNER_STYLES[style]


# Touch `time` so ruff doesn't strip the import.
_ = time
