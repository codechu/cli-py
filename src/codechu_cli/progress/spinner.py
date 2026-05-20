"""Threaded spinner — context manager required."""

from __future__ import annotations

import sys
import threading
from typing import IO

from .._term import is_tty
from ..emoji import capabilities
from .line import ProgressLine
from .styles_spinner import SPINNER_STYLES

_BRAILLE_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼",
                   "⠴", "⠦", "⠧", "⠇", "⠏")
_ASCII_FRAMES = ("|", "/", "-", "\\")


class Spinner:
    """Threaded spinner with braille frames + ASCII fallback.

    Use as a context manager — this is the only supported entry/exit:

        with Spinner("Scanning…"):
            heavy_work()
    """

    def __init__(
        self,
        message: str = "",
        *,
        stream: IO[str] | None = None,
        style: str | None = None,
        frames: tuple[str, ...] | list[str] | None = None,
        interval: float = 0.08,
        enabled: bool | None = None,
    ) -> None:
        self._stream = stream if stream is not None else sys.stderr
        self.message = message
        self.interval = max(0.01, float(interval))
        if enabled is None:
            enabled = is_tty(self._stream)
        self.enabled = enabled
        if frames is None:
            if style is not None:
                if style not in SPINNER_STYLES:
                    raise KeyError(
                        f"unknown spinner style {style!r}. "
                        f"Available: {sorted(SPINNER_STYLES)}"
                    )
                frames = SPINNER_STYLES[style]
            else:
                caps = capabilities(self._stream)
                frames = _BRAILLE_FRAMES if "unicode" in caps else _ASCII_FRAMES
        self.frames = tuple(frames)
        self._line = ProgressLine(self._stream, enabled=self.enabled)
        self._stop_evt = threading.Event()
        self._thread: threading.Thread | None = None

    def _start(self) -> "Spinner":
        if not self.enabled or self._thread is not None:
            return self
        self._stop_evt.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def _run(self) -> None:
        i = 0
        while not self._stop_evt.is_set():
            frame = self.frames[i % len(self.frames)]
            text = f"{frame} {self.message}".rstrip()
            self._line.update(text)
            i += 1
            if self._stop_evt.wait(self.interval):
                break

    def _stop(self) -> None:
        self._stop_evt.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        self._line.clear()

    def __enter__(self) -> "Spinner":
        return self._start()

    def __exit__(self, exc_type, exc, tb) -> None:
        # Don't suppress exceptions.
        self._stop()


__all__ = ["Spinner"]
