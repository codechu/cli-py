"""ANSI color helper with a fluent palette API.

Usage::

    c = Color(sys.stdout)
    c.low("ok")     # → "\\x1b[32mok\\x1b[0m" if color enabled, else "ok"
    c.high("bad")

Each palette key becomes a method on the instance via ``__getattr__``.
Unknown keys raise :class:`AttributeError`.

Color does **not** read environment variables (no ``NO_COLOR``
auto-detection). The caller decides — pass ``enabled=False`` (or
``True``) explicitly, or rely on ``stream.isatty()`` auto-detection
(``enabled=None``, the default).
"""

from __future__ import annotations

from typing import IO, Callable

from ._term import is_tty


class Color:
    DEFAULT_PALETTE: dict[str, str] = {
        "reset": "\033[0m",
        "dim": "\033[2m",
        "bold": "\033[1m",
        "low": "\033[32m",      # green
        "medium": "\033[33m",   # yellow
        "high": "\033[31m",     # red
        "info": "\033[36m",     # cyan
    }

    def __init__(
        self,
        stream: IO[str],
        *,
        palette: dict[str, str] | None = None,
        enabled: bool | None = None,
    ) -> None:
        self._palette = {**self.DEFAULT_PALETTE, **(palette or {})}
        self._stream = stream
        if enabled is None:
            enabled = is_tty(stream)
        self._enabled = bool(enabled)

    @property
    def enabled(self) -> bool:
        return self._enabled

    def _wrap(self, code: str, text: str) -> str:
        if not self._enabled:
            return text
        seq = self._palette.get(code)
        if seq is None:
            return text
        reset = self._palette.get("reset", self.DEFAULT_PALETTE["reset"])
        return f"{seq}{text}{reset}"

    def __getattr__(self, name: str) -> Callable[[str], str]:
        # Only invoked for missing attributes. Private attrs (starting
        # with "_") should not be intercepted — raise normally.
        if name.startswith("_"):
            raise AttributeError(name)
        # Use object.__getattribute__ to avoid recursion through __getattr__.
        palette = object.__getattribute__(self, "_palette")
        if name not in palette:
            raise AttributeError(
                f"{type(self).__name__!r} has no color {name!r}. "
                f"Known: {sorted(palette)}"
            )

        def _apply(text: str, _code: str = name) -> str:
            return self._wrap(_code, text)

        _apply.__name__ = name
        _apply.__qualname__ = f"Color.{name}"
        return _apply


__all__ = ["Color"]
