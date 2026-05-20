"""Progress bar with a fluent builder API."""

from __future__ import annotations

import sys
import time
from collections import deque
from typing import IO

from .._term import is_tty
from .line import ProgressLine
from .styles_bar import BAR_STYLES, DEFAULT_BAR_STYLE, SUBPIXEL
from .styles_spinner import SPINNER_STYLES


def _fmt_duration(secs: float) -> str:
    """Compact duration: ``Xs`` under 60 s, ``Xm Ys`` otherwise."""
    if secs < 0:
        secs = 0.0
    s = int(round(secs))
    if s < 60:
        return f"{s}s"
    return f"{s // 60}m {s % 60}s"


def _fmt_rate(rate: float, unit: str) -> str:
    """Compact rate string like ``42 items/s``."""
    if rate >= 100:
        return f"{int(round(rate))} {unit}/s"
    if rate >= 10:
        return f"{rate:.1f} {unit}/s"
    return f"{rate:.2f} {unit}/s"


class _RateEstimator:
    """Tiny windowed rate estimator (events per second)."""

    def __init__(self, window_seconds: float = 1.0) -> None:
        self._window = window_seconds
        self._events: deque[tuple[float, float]] = deque()  # (ts, n)

    def observe(self, n: float = 1) -> None:
        now = time.monotonic()
        self._events.append((now, float(n)))
        cutoff = now - self._window
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()

    def rate(self) -> float:
        if not self._events:
            return 0.0
        now = time.monotonic()
        cutoff = now - self._window
        while self._events and self._events[0][0] < cutoff:
            self._events.popleft()
        if not self._events:
            return 0.0
        total = sum(n for _, n in self._events)
        return total / self._window


class ProgressBar:
    """Bracketed progress bar with percent + count.

    Construct with the total only, then chain builder methods:

        ProgressBar(100).width(40).style("claude").with_eta().with_rate()

    All builder methods return ``self`` so they can be chained. Pass
    ``total=None`` (or omit any value) for indeterminate mode.
    """

    DEFAULT_TEMPLATE = "[{bar}] {pct}% · {current}/{total} · {label}"

    def __init__(
        self,
        total: int | None = None,
        *,
        enabled: bool | None = None,
    ) -> None:
        # total=None (or non-positive) → indeterminate mode
        if total is None or int(total) <= 0:
            self.total = 0
            self._indeterminate = True
        else:
            self.total = int(total)
            self._indeterminate = False
        self.current = 0

        # Defaults (mutated by builder methods).
        self._stream: IO[str] = sys.stderr
        self._style_name: str = DEFAULT_BAR_STYLE
        self._apply_style(self._style_name)
        self._template: str = self.DEFAULT_TEMPLATE
        self._reverse: bool = False
        self._units: str | None = None
        self._spinner_style: str = "dots"
        self._show_eta: bool = False
        self._show_rate: bool = False
        self._prefix: str = ""
        self._suffix: str = ""

        # Per-call overrides for fill/empty/width/smooth: None = use style preset
        self._fill_override: str | None = None
        self._empty_override: str | None = None
        self._width_override: int | None = None
        self._smooth_override: bool | None = None

        self._enabled_arg = enabled
        self._resolved_enabled: bool | None = None

        # Counters / timing
        self._spinner_idx = 0
        self._indeterm_idx = 0
        self._t_start = time.monotonic()
        self._last_advance = time.monotonic()
        self._rate = _RateEstimator(window_seconds=1.0)

        # Lazy: line is constructed on first render so stream/enabled
        # changes via the builder are respected.
        self._line: ProgressLine | None = None

    # ------------------------------------------------------------------
    # Builder methods (each returns self)
    # ------------------------------------------------------------------

    def stream(self, stream: IO[str]) -> "ProgressBar":
        self._stream = stream
        self._line = None  # rebuild on next render
        return self

    def width(self, n: int) -> "ProgressBar":
        self._width_override = max(1, int(n))
        return self

    def style(self, name: str) -> "ProgressBar":
        if name not in BAR_STYLES:
            raise KeyError(
                f"unknown bar style {name!r}. Available: {sorted(BAR_STYLES)}"
            )
        self._style_name = name
        self._apply_style(name)
        return self

    def fill(self, ch: str) -> "ProgressBar":
        self._fill_override = ch
        return self

    def empty(self, ch: str) -> "ProgressBar":
        self._empty_override = ch
        return self

    def smooth(self, on: bool = True) -> "ProgressBar":
        self._smooth_override = bool(on)
        return self

    def template(self, tmpl: str) -> "ProgressBar":
        self._template = tmpl
        return self

    def reverse(self, on: bool = True) -> "ProgressBar":
        self._reverse = bool(on)
        return self

    def units(self, unit: str) -> "ProgressBar":
        self._units = unit
        return self

    def spinner_style(self, name: str) -> "ProgressBar":
        if name not in SPINNER_STYLES:
            raise KeyError(
                f"unknown spinner style {name!r}. "
                f"Available: {sorted(SPINNER_STYLES)}"
            )
        self._spinner_style = name
        return self

    def with_eta(self, on: bool = True) -> "ProgressBar":
        self._show_eta = bool(on)
        return self

    def with_rate(self, on: bool = True) -> "ProgressBar":
        self._show_rate = bool(on)
        return self

    def prefix(self, text: str) -> "ProgressBar":
        self._prefix = text
        return self

    def suffix(self, text: str) -> "ProgressBar":
        self._suffix = text
        return self

    # ------------------------------------------------------------------
    # Style helpers
    # ------------------------------------------------------------------

    def _apply_style(self, name: str) -> None:
        preset = BAR_STYLES[name]
        self._style_fill = preset.get("fill", "#")
        self._style_empty = preset.get("empty", "-")
        self._style_edge = preset.get("edge")
        self._style_separator = preset.get("separator")
        self._style_width = preset.get("width", 40)
        self._style_smooth = bool(preset.get("smooth", False))

    @property
    def fill_ch(self) -> str:
        return self._fill_override if self._fill_override is not None else self._style_fill

    @property
    def empty_ch(self) -> str:
        return self._empty_override if self._empty_override is not None else self._style_empty

    @property
    def width_n(self) -> int:
        if self._width_override is not None:
            return self._width_override
        return max(1, int(self._style_width))

    @property
    def is_smooth(self) -> bool:
        if self._smooth_override is not None:
            return self._smooth_override
        return self._style_smooth

    @property
    def enabled(self) -> bool:
        if self._resolved_enabled is None:
            if self._enabled_arg is None:
                self._resolved_enabled = is_tty(self._stream)
            else:
                self._resolved_enabled = bool(self._enabled_arg)
        return self._resolved_enabled

    def _ensure_line(self) -> ProgressLine:
        if self._line is None:
            self._line = ProgressLine(self._stream, enabled=self.enabled)
        return self._line

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_total(self, n: int) -> None:
        self.total = max(0, int(n))
        self._indeterminate = self.total <= 0
        self._render(label="")

    def advance(self, n: int = 1, label: str = "") -> None:
        if self._indeterminate:
            self.current += n
            self._indeterm_idx += 1
        else:
            self.current = (
                min(self.total, self.current + n) if self.total else self.current + n
            )
        if n:
            self._rate.observe(n)
        self._last_advance = time.monotonic()
        self._render(label=label)

    def refresh(self, label: str = "") -> None:
        """Re-render the current state without advancing."""
        self._render(label=label)

    def finish(self) -> None:
        self._ensure_line().clear()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_smooth(self, frac: float) -> str:
        w = self.width_n
        if w <= 0:
            return ""
        frac = max(0.0, min(1.0, frac))
        total_eighths = int(round(frac * w * 8))
        full_cells = total_eighths // 8
        remainder = total_eighths % 8
        out = "█" * full_cells
        if full_cells < w:
            out += SUBPIXEL[remainder]
            out += " " * (w - full_cells - 1)
        return out

    def _render_cells(self, ratio: float) -> str:
        w = self.width_n
        filled = int(round(ratio * w))
        filled = max(0, min(w, filled))
        if self.is_smooth:
            return self._render_smooth(ratio)
        cells: list[str] = [self.fill_ch] * filled + [self.empty_ch] * (w - filled)
        if self._style_edge and 0 < filled < w:
            for i, ch in enumerate(self._style_edge):
                pos = filled + i
                if pos >= w:
                    break
                cells[pos] = ch
        if self._reverse:
            cells = list(reversed(cells))
        if self._style_separator:
            return self._style_separator.join(cells)
        return "".join(cells)

    def _indeterminate_body(self) -> str:
        frames = SPINNER_STYLES["bar"]
        return frames[self._indeterm_idx % len(frames)]

    def _paused_body(self) -> str:
        frames = SPINNER_STYLES["blocks-pulse"]
        f = frames[self._indeterm_idx % len(frames)]
        w = self.width_n
        if len(f) >= w:
            return f[:w]
        return (f * ((w // len(f)) + 1))[:w]

    def _render(self, *, label: str) -> None:
        if not self.enabled:
            return
        now = time.monotonic()
        elapsed = now - self._t_start
        idle = now - self._last_advance

        if self._indeterminate:
            bar_str = self._indeterminate_body()
            pct_str = "--"
            eta_str = "?"
            remaining_str = "?"
        elif idle > 2.0:
            self._indeterm_idx += 1
            bar_str = self._paused_body()
            total = self.total or 1
            ratio = min(1.0, self.current / total) if total else 0.0
            pct_str = str(int(round(ratio * 100)))
            if self.total > 0 and self.current > 0:
                eta_s = elapsed * (self.total - self.current) / self.current
                eta_str = _fmt_duration(max(0.0, eta_s))
            else:
                eta_str = "?"
            remaining_str = str(max(0, self.total - self.current))
        else:
            total = self.total or 1
            ratio = min(1.0, self.current / total) if total else 0.0
            bar_str = self._render_cells(ratio)
            pct_str = str(int(round(ratio * 100)))
            if self.total > 0 and self.current > 0:
                eta_s = elapsed * (self.total - self.current) / self.current
                eta_str = _fmt_duration(max(0.0, eta_s))
            else:
                eta_str = "?"
            remaining_str = str(max(0, self.total - self.current))

        spin_frames = SPINNER_STYLES[self._spinner_style]
        spinner_str = spin_frames[self._spinner_idx % len(spin_frames)]
        self._spinner_idx += 1

        if self._indeterminate or elapsed < 0.5 or self._rate.rate() <= 0:
            rate_str = "?"
        else:
            rate_str = _fmt_rate(self._rate.rate(), self._units or "items")

        msg = self._template.format(
            bar=bar_str,
            pct=pct_str,
            current=self.current,
            total=self.total,
            label=label,
            elapsed=_fmt_duration(elapsed),
            eta=eta_str,
            spinner=spinner_str,
            remaining=remaining_str,
            rate=rate_str,
        )

        if self._template == self.DEFAULT_TEMPLATE and not label and msg.endswith(" · "):
            msg = msg[:-3]

        # Prefix/suffix decoration (only when set)
        if self._prefix:
            msg = self._prefix + msg
        if self._suffix:
            msg = msg + self._suffix
        # `_show_eta` / `_show_rate` are advisory hints; users that opt in
        # but use the default template get an appended summary so the
        # builder calls do something visible.
        if self._template == self.DEFAULT_TEMPLATE and (self._show_eta or self._show_rate):
            extras: list[str] = []
            if self._show_eta:
                extras.append(f"eta {eta_str}")
            if self._show_rate:
                extras.append(f"rate {rate_str}")
            msg = msg + " · " + " · ".join(extras)

        self._ensure_line().update(msg)


__all__ = ["ProgressBar"]
