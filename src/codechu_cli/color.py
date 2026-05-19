"""ANSI color helper with NO_COLOR + TTY detection."""

from __future__ import annotations

import os
from typing import IO


class Color:
    """ANSI color helper with ``NO_COLOR`` and TTY detection.

    Usage::

        c = Color(sys.stdout)
        c("low", "ok")   # → "\\x1b[32mok\\x1b[0m" if color enabled, else "ok"

    Pass ``palette={...}`` to merge custom codes onto :attr:`DEFAULT_PALETTE`.
    Pass ``force=True`` / ``force=False`` to override TTY / NO_COLOR auto-detection.
    Unknown codes pass the text through unchanged.
    """

    DEFAULT_PALETTE: dict[str, str] = {
        "reset": "\033[0m",
        "dim": "\033[2m",
        "bold": "\033[1m",
        "low": "\033[32m",      # green
        "medium": "\033[33m",   # yellow
        "high": "\033[31m",     # red
        "info": "\033[36m",     # cyan
    }

    # Backwards-compat alias — old callers used Color.PALETTE.
    PALETTE = DEFAULT_PALETTE

    def __init__(
        self,
        stream: IO[str],
        *,
        palette: dict[str, str] | None = None,
        force: bool | None = None,
    ) -> None:
        # Merge: custom palette overrides + extends defaults.
        self._palette = {**self.DEFAULT_PALETTE, **(palette or {})}
        self._stream = stream
        self._force = force  # None = auto-detect

    @property
    def enabled(self) -> bool:
        if self._force is not None:
            return self._force
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
        seq = self._palette.get(code)
        if seq is None:
            return text
        reset = self._palette.get("reset", self.DEFAULT_PALETTE["reset"])
        return f"{seq}{text}{reset}"


__all__ = ["Color"]
