"""Shared test helpers."""

from __future__ import annotations

import io


class TTYStringIO(io.StringIO):
    """A StringIO that reports as a TTY (for testing TTY-only branches)."""

    def isatty(self) -> bool:  # noqa: D401 - simple override
        return True
