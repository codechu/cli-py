"""Banner headers — single-line and ASCII-art variants."""

from __future__ import annotations

import sys
from typing import IO

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
    if not _is_tty(stream):
        return
    c = Color(stream)
    parts = [c("bold", f"{title} {version}")]
    if mode:
        parts.append(c("dim", f"[{mode}]"))
    try:
        stream.write("  ".join(parts) + "\n")
        stream.flush()
    except Exception:
        pass


# --- ASCII-art banner -------------------------------------------------


# Pre-built logos. Each is a triple-quoted multi-line block. The leading
# blank line is intentional so f-string-style insertion stays readable
# at the call site.
LOGOS: dict[str, str] = {
    "codechu": r"""
   ___          _           _
  / __\___   __| | ___  ___| |__  _   _
 / /  / _ \ / _` |/ _ \/ __| '_ \| | | |
/ /__| (_) | (_| |  __/ (__| | | | |_| |
\____/\___/ \__,_|\___|\___|_| |_|\__,_|
""",
    # A compact disk-shaped block — for tools that show a single product
    # banner (disk-cleaner uses this). Kept under 5 lines for terminals
    # with limited vertical room.
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

    By default the banner only renders when ``stream`` is a TTY — pipes
    and redirected output get no visual noise. Pass ``enabled=True`` to
    force the output (useful in CI logs that capture stderr).

    ``art`` may be a raw multi-line string (your own art) or a value
    looked up via :data:`LOGOS` — pass the dict value directly, e.g.
    ``ascii_banner(LOGOS["codechu"], color="info")``.

    ``color`` is a key from the :class:`Color` palette
    (``"info"``, ``"low"``, ``"dim"``, …). When color support is off
    or no color is given, the art renders plainly.

    The function is silent on errors so it can never break a CLI.
    """
    if stream is None:
        stream = sys.stderr
    if enabled is False:
        return
    if enabled is None and not _is_tty(stream):
        return
    if not art:
        return

    c = Color(stream)
    try:
        for line in art.splitlines():
            # Keep blank lines as-is (preserves vertical breathing room).
            if line and color:
                stream.write(c(color, line) + "\n")
            else:
                stream.write(line + "\n")
        stream.flush()
    except Exception:
        pass


def _is_tty(stream: IO[str]) -> bool:
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except Exception:
        return False


__all__ = ["banner", "ascii_banner", "LOGOS"]
