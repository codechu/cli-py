"""Private terminal capability helpers shared across modules.

This module is intentionally private (underscore prefix). It is not
re-exported from :mod:`codechu_cli` and is not part of the public API.
"""

from __future__ import annotations

import os
import sys
from typing import IO


def is_tty(stream: IO[str] | None) -> bool:
    """Return whether ``stream`` is a TTY. Swallows errors → ``False``."""
    if stream is None:
        return False
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except Exception:
        return False


def capabilities(stream: IO[str] | None = None) -> dict[str, bool]:
    """Return a dict of capability flags for ``stream`` / the environment.

    Keys: ``"tty"``, ``"unicode"``, ``"dumb_term"``.
    """
    if stream is None:
        stream = sys.stderr
    lang = os.environ.get("LANG", "")
    term = os.environ.get("TERM", "")
    return {
        "tty": is_tty(stream),
        "unicode": ("UTF-8" in lang) or ("utf8" in lang.lower()),
        "dumb_term": term == "dumb",
    }


__all__ = ["capabilities", "is_tty"]
