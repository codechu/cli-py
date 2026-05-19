"""Progress lines, bars, and spinners."""

from __future__ import annotations

import sys
import threading
import time
from typing import IO

from .emoji import capabilities

_BRAILLE_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼",
                   "⠴", "⠦", "⠧", "⠇", "⠏")
_ASCII_FRAMES = ("|", "/", "-", "\\")


def _stream_is_tty(stream: IO[str]) -> bool:
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except Exception:
        return False


class ProgressLine:
    """Single-line overwriting stderr progress with optional state.

    ``enabled`` defaults to ``stream.isatty()``. When disabled, all
    methods are no-ops so callers don't need to branch.
    """

    def __init__(self, stream: IO[str] | None = None, enabled: bool | None = None) -> None:
        self._stream = stream if stream is not None else sys.stderr
        if enabled is None:
            enabled = _stream_is_tty(self._stream)
        self.enabled = enabled
        self._last_width = 0

    def update(self, msg: str) -> None:
        if not self.enabled:
            return
        pad = " " * max(0, self._last_width - len(msg))
        try:
            self._stream.write(f"\r{msg}{pad}")
            self._stream.flush()
        except Exception:
            return
        self._last_width = len(msg)

    def clear(self) -> None:
        if not self.enabled or self._last_width == 0:
            return
        try:
            self._stream.write("\r" + " " * self._last_width + "\r")
            self._stream.flush()
        except Exception:
            pass
        self._last_width = 0


def _fmt_duration(seconds: float) -> str:
    """Render a duration as ``Xs`` or ``Xm Ys`` (rounded to whole seconds)."""
    if seconds < 0 or seconds != seconds:  # NaN guard
        return "?"
    s = int(round(seconds))
    if s < 60:
        return f"{s}s"
    m, rem = divmod(s, 60)
    return f"{m}m {rem}s"


class ProgressBar:
    """Bracketed progress bar with percent + count.

    Renders ``[###----] 30% · 3/10 · label`` to ``stream`` (default
    ``sys.stderr``). All methods are no-ops when ``enabled`` is False.

    Customize the look with ``fill``, ``empty``, and ``template``. The
    template gets these fields: ``{bar} {pct} {current} {total} {label}
    {elapsed} {eta}``. ``{elapsed}`` and ``{eta}`` are formatted via
    :func:`_fmt_duration` (``Xs`` or ``Xm Ys``). ``{eta}`` shows ``?``
    until at least one :meth:`advance` lands with a positive total and
    nonzero current.
    """

    DEFAULT_TEMPLATE = "[{bar}] {pct}% · {current}/{total} · {label}"

    def __init__(
        self,
        total: int,
        *,
        stream: IO[str] | None = None,
        width: int = 40,
        fill: str = "#",
        empty: str = "-",
        template: str | None = None,
        enabled: bool | None = None,
    ) -> None:
        self._stream = stream if stream is not None else sys.stderr
        self.width = max(4, width)
        self.total = max(0, int(total))
        self.current = 0
        self.fill = fill
        self.empty = empty
        self.template = template if template is not None else self.DEFAULT_TEMPLATE
        if enabled is None:
            enabled = _stream_is_tty(self._stream)
        self.enabled = enabled
        self._line = ProgressLine(self._stream, enabled=self.enabled)
        self._t_start = time.monotonic()

    def set_total(self, n: int) -> None:
        self.total = max(0, int(n))
        self._render(label="")

    def advance(self, n: int = 1, label: str = "") -> None:
        self.current = min(self.total, self.current + n) if self.total else self.current + n
        self._render(label=label)

    def _render(self, *, label: str) -> None:
        if not self.enabled:
            return
        total = self.total or 1
        ratio = min(1.0, self.current / total) if total else 0.0
        filled = int(round(ratio * self.width))
        # Repeat fill/empty strings; clamp if a multi-char glyph would
        # overflow due to int rounding edges.
        bar_str = (self.fill * filled) + (self.empty * (self.width - filled))
        pct = int(round(ratio * 100))
        elapsed = time.monotonic() - self._t_start
        if self.total > 0 and self.current > 0:
            eta_s = elapsed * (self.total - self.current) / self.current
            eta_str = _fmt_duration(max(0.0, eta_s))
        else:
            eta_str = "?"
        msg = self.template.format(
            bar=bar_str,
            pct=pct,
            current=self.current,
            total=self.total,
            label=label,
            elapsed=_fmt_duration(elapsed),
            eta=eta_str,
        )
        # Trim trailing " · " when the default template ran with an
        # empty label, matching prior behavior.
        if self.template is self.DEFAULT_TEMPLATE or self.template == self.DEFAULT_TEMPLATE:
            if not label and msg.endswith(" · "):
                msg = msg[:-3]
        self._line.update(msg)

    def finish(self) -> None:
        self._line.clear()


class Spinner:
    """Threaded spinner with braille frames + ASCII fallback.

    Usage::

        with Spinner("Scanning…"):
            heavy_work()

    Or manually::

        sp = Spinner("Scanning…").start()
        try:
            heavy_work()
        finally:
            sp.stop()
    """

    def __init__(
        self,
        message: str = "",
        *,
        stream: IO[str] | None = None,
        frames: tuple[str, ...] | list[str] | None = None,
        interval: float = 0.08,
        enabled: bool | None = None,
    ) -> None:
        self._stream = stream if stream is not None else sys.stderr
        self.message = message
        self.interval = max(0.01, float(interval))
        if enabled is None:
            enabled = _stream_is_tty(self._stream)
        self.enabled = enabled
        if frames is None:
            caps = capabilities(self._stream)
            frames = _BRAILLE_FRAMES if "unicode" in caps else _ASCII_FRAMES
        self.frames = tuple(frames)
        self._line = ProgressLine(self._stream, enabled=self.enabled)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> "Spinner":
        if not self.enabled or self._thread is not None:
            return self
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def _run(self) -> None:
        i = 0
        while not self._stop.is_set():
            frame = self.frames[i % len(self.frames)]
            text = f"{frame} {self.message}".rstrip()
            self._line.update(text)
            i += 1
            if self._stop.wait(self.interval):
                break

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        self._line.clear()

    def __enter__(self) -> "Spinner":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        # Don't suppress exceptions.
        self.stop()


# Re-export for tests that want to monkeypatch.
__all__ = ["ProgressBar", "ProgressLine", "Spinner"]


# Keep ``time`` referenced so tests can ``monkeypatch.setattr(progress, 'time', fake)``.
_ = time
