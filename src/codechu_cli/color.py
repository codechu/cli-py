"""ANSI color helper with NO_COLOR + TTY detection."""

from __future__ import annotations

import os
from typing import IO


class Color:
    """ANSI color helper with ``NO_COLOR`` and TTY detection.

    Usage::

        c = Color(sys.stdout)
        c("low", "ok")   # → "\\x1b[32mok\\x1b[0m" if color enabled, else "ok"
    """

    PALETTE: dict[str, str] = {
        "reset": "\033[0m",
        "dim": "\033[2m",
        "bold": "\033[1m",
        "low": "\033[32m",      # green
        "medium": "\033[33m",   # yellow
        "high": "\033[31m",     # red
        "info": "\033[36m",     # cyan
    }

    def __init__(self, stream: IO[str]) -> None:
        self._stream = stream

    @property
    def enabled(self) -> bool:
        if os.environ.get("NO_COLOR"):
            return False
        isatty = getattr(self._stream, "isatty", None)
        try:
            return bool(isatty and isatty())
        except Exception:
            return False

    def __call__(self, code: str, text: str) -> str:
        if not self.enabled:
            return text
        seq = self.PALETTE.get(code)
        if seq is None:
            return text
        return f"{seq}{text}{self.PALETTE['reset']}"


__all__ = ["Color"]
