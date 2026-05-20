"""Single-line overwriting progress output."""

from __future__ import annotations

import sys
from typing import IO

from .._term import is_tty


class ProgressLine:
    """Single-line overwriting stderr progress.

    ``enabled`` defaults to ``stream.isatty()``. When disabled, all
    methods are no-ops so callers don't need to branch.
    """

    def __init__(
        self,
        stream: IO[str] | None = None,
        enabled: bool | None = None,
    ) -> None:
        self._stream = stream if stream is not None else sys.stderr
        if enabled is None:
            enabled = is_tty(self._stream)
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


__all__ = ["ProgressLine"]
