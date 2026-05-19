"""Output format detection + argparse epilog helper."""

from __future__ import annotations

from typing import IO


def resolve_format(
    stream: IO[str],
    *,
    tty_default: str = "table",
    pipe_default: str = "json",
) -> str:
    """Pick a default output format based on whether ``stream`` is a TTY."""
    isatty = getattr(stream, "isatty", None)
    try:
        return tty_default if isatty and isatty() else pipe_default
    except Exception:
        return pipe_default


def format_examples(examples: list[tuple[str, str]]) -> str:
    """Format a list of ``(command, description)`` for argparse ``epilog``.

    Renders an aligned ``Examples:`` block. Width of the command column
    is the longest command + 2 spaces, capped at 60 to keep wrapping
    sane on narrow terminals.
    """
    if not examples:
        return ""
    longest = min(60, max(len(cmd) for cmd, _ in examples))
    lines = ["Examples:"]
    for cmd, desc in examples:
        if len(cmd) <= longest:
            lines.append(f"  {cmd.ljust(longest)}  {desc}")
        else:
            lines.append(f"  {cmd}")
            lines.append(f"  {' ' * longest}  {desc}")
    return "\n".join(lines)


__all__ = ["format_examples", "resolve_format"]
