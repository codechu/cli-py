"""Emoji helpers with locale + terminal capability detection.

Conservative defaults ("temkinli"): if ``LANG=C`` / ``LANG=POSIX`` or
``TERM=dumb``, fall back to ASCII glyphs. Set ``CODECHU_CLI_EMOJI=always``
to force emoji on, ``never`` to force off.
"""

from __future__ import annotations

import os
import sys
from typing import IO

# name -> (unicode glyph, ascii fallback)
_GLYPHS: dict[str, tuple[str, str]] = {
    "ok": ("✓", "+"),               # ✓
    "fail": ("✗", "x"),             # ✗
    "warn": ("⚠", "!"),             # ⚠
    "info": ("ℹ", "i"),             # ℹ
    "arrow": ("→", "->"),           # →
    "bullet": ("•", "*"),           # •
    "check_on": ("☑", "[x]"),       # ☑
    "check_off": ("☐", "[ ]"),      # ☐
    "scan": ("\U0001f50d", "search"),    # 🔍
    "trash": ("\U0001f5d1", "trash"),    # 🗑
    "broom": ("\U0001f9f9", "clean"),    # 🧹
    "disk": ("\U0001f4be", "disk"),      # 💾
    "watch": ("\U0001f441", "watch"),    # 👁
}


def _is_tty(stream: IO[str] | None) -> bool:
    if stream is None:
        return False
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except Exception:
        return False


def capabilities(stream: IO[str] | None = None) -> set[str]:
    """Return capability tokens for the current terminal.

    Tokens: ``"unicode"``, ``"color"``, ``"emoji"``.

    - ``unicode`` if ``LANG`` mentions UTF-8 / utf8.
    - ``color`` if ``NO_COLOR`` absent + stream is a TTY + ``TERM`` != "dumb".
    - ``emoji`` if (unicode + interactive) or ``CODECHU_CLI_EMOJI=always``.
      ``CODECHU_CLI_EMOJI=never`` removes ``emoji`` unconditionally.
    """
    if stream is None:
        stream = sys.stderr
    caps: set[str] = set()

    lang = os.environ.get("LANG", "")
    if "UTF-8" in lang or "utf8" in lang.lower():
        caps.add("unicode")

    term = os.environ.get("TERM", "")
    is_tty = _is_tty(stream)
    if "NO_COLOR" not in os.environ and is_tty and term != "dumb":
        caps.add("color")

    if "unicode" in caps and is_tty and term != "dumb":
        caps.add("emoji")

    force = os.environ.get("CODECHU_CLI_EMOJI", "").lower()
    if force == "always":
        caps.add("emoji")
    elif force == "never":
        caps.discard("emoji")

    return caps


def e(name: str, *, fallback: str | None = None, stream: IO[str] | None = None) -> str:
    """Look up an emoji by ``name``.

    Returns the unicode glyph when ``"emoji"`` is in :func:`capabilities`,
    otherwise the ASCII fallback. Pass ``fallback=`` to override.
    Unknown names raise :class:`KeyError`.
    """
    glyph, default_fallback = _GLYPHS[name]
    fb = fallback if fallback is not None else default_fallback
    return glyph if "emoji" in capabilities(stream) else fb


__all__ = ["capabilities", "e"]
