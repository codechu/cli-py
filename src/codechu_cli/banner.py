"""Banner headers — single-line + raw multi-line ASCII art."""

from __future__ import annotations

import sys
from typing import IO

from ._term import is_tty
from .color import Color


def banner(
    title: str,
    version: str,
    *,
    mode: str | None = None,
    stream: IO[str] | None = None,
) -> None:
    """Emit a single-line banner to ``stream`` when it's a TTY."""
    if stream is None:
        stream = sys.stderr
    if not is_tty(stream):
        return
    c = Color(stream)
    parts = [c.bold(f"{title} {version}")]
    if mode:
        parts.append(c.dim(f"[{mode}]"))
    try:
        stream.write("  ".join(parts) + "\n")
        stream.flush()
    except Exception:
        pass


# Pre-built logos.
LOGOS: dict[str, str] = {
    "codechu": r"""
   ___          _           _
  / __\___   __| | ___  ___| |__  _   _
 / /  / _ \ / _` |/ _ \/ __| '_ \| | | |
/ /__| (_) | (_| |  __/ (__| | | | |_| |
\____/\___/ \__,_|\___|\___|_| |_|\__,_|
""",
    "disk": r"""
  ╭─────────╮
 ╱  ◌  ◌  ◌  ╲
│   D I S K   │
 ╲  ◌  ◌  ◌  ╱
  ╰─────────╯
""",
}


def ascii_banner(
    art: str,
    *,
    color: str | None = None,
    stream: IO[str] | None = None,
    enabled: bool | None = None,
) -> None:
    """Print a multi-line ASCII-art banner to ``stream``.

    By default only renders when ``stream`` is a TTY. Pass ``enabled=True``
    to force, ``enabled=False`` to suppress.
    """
    if stream is None:
        stream = sys.stderr
    if enabled is False:
        return
    if enabled is None and not is_tty(stream):
        return
    if not art:
        return

    c = Color(stream)
    try:
        for line in art.splitlines():
            if line and color:
                wrap = getattr(c, color, None)
                stream.write((wrap(line) if callable(wrap) else line) + "\n")
            else:
                stream.write(line + "\n")
        stream.flush()
    except Exception:
        pass


__all__ = ["banner", "ascii_banner", "LOGOS"]
