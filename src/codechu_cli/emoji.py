"""Emoji helpers with locale + terminal capability detection.

Conservative defaults ("temkinli"): if ``LANG=C`` / ``LANG=POSIX`` or
``TERM=dumb``, fall back to ASCII glyphs. Set ``CODECHU_CLI_EMOJI=always``
to force emoji on, ``never`` to force off.

Discipline note (explicit config): :func:`capabilities` is the *one*
helper in this module that reads environment variables, and it only
does so when the caller invokes it. :func:`e` does **not** call it
implicitly — pass the ``caps`` set explicitly, or accept the ASCII
fallback. This keeps emoji rendering a pure function of its inputs
and makes apps trivially debuggable.
"""

from __future__ import annotations

import os
import sys
from typing import IO, Iterable

from ._term import is_tty as _is_tty_helper

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


def capabilities(stream: IO[str] | None = None) -> set[str]:
    """Return capability tokens for the current terminal.

    Tokens: ``"unicode"``, ``"color"``, ``"emoji"``.

    - ``unicode`` if ``LANG`` mentions UTF-8 / utf8.
    - ``color`` if ``NO_COLOR`` absent + stream is a TTY + ``TERM`` != "dumb".
    - ``emoji`` if (unicode + interactive) or ``CODECHU_CLI_EMOJI=always``.
      ``CODECHU_CLI_EMOJI=never`` removes ``emoji`` unconditionally.

    This is the **only** function in the module that reads environment
    variables. Call it explicitly from your app's bootstrap and pass
    the result to :func:`e` (and other helpers that accept ``caps``).
    """
    if stream is None:
        stream = sys.stderr
    caps: set[str] = set()

    lang = os.environ.get("LANG", "")
    if "UTF-8" in lang or "utf8" in lang.lower():
        caps.add("unicode")

    term = os.environ.get("TERM", "")
    is_tty = _is_tty_helper(stream)
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


def e(
    name: str,
    caps: Iterable[str] | None = None,
    *,
    fallback: str | None = None,
) -> str:
    """Look up an emoji by ``name``.

    Returns the unicode glyph when ``"emoji"`` is in ``caps``, otherwise
    the ASCII fallback. Pass ``fallback=`` to override the registered
    ASCII form. Unknown names raise :class:`KeyError`.

    ``caps`` must be supplied explicitly by the caller (typically the
    result of :func:`capabilities`). If ``caps`` is ``None`` (the
    default), :func:`e` behaves as if no capabilities are present and
    returns the ASCII fallback — it does **not** read the environment
    or call :func:`capabilities` itself. This keeps the function pure
    and the dependency on terminal state explicit.
    """
    glyph, default_fallback = _GLYPHS[name]
    fb = fallback if fallback is not None else default_fallback
    if caps is None:
        return fb
    return glyph if "emoji" in caps else fb


def register(name: str, glyph: str, fallback: str) -> None:
    """Add or override a glyph in the registry.

    ``glyph`` is the unicode form, ``fallback`` is the ASCII form used
    when the terminal lacks emoji capability.
    """
    _GLYPHS[name] = (glyph, fallback)


def update(mapping: dict[str, tuple[str, str]]) -> None:
    """Bulk register glyphs. Each value is ``(unicode, fallback)``."""
    for name, pair in mapping.items():
        glyph, fallback = pair
        _GLYPHS[name] = (glyph, fallback)


def known() -> list[str]:
    """Return the list of registered glyph names."""
    return list(_GLYPHS.keys())


__all__ = ["capabilities", "e", "known", "register", "update"]
