"""Minimal Markdown → ANSI renderer.

Supports a small, well-defined subset:

* ``# H1`` and ``## H2`` headings
* ``**bold**`` and ``*italic*``
* Inline code with backticks: ```` `code` ````
* List items prefixed with ``-`` or ``*``
* Links ``[text](url)`` → ``text (url)``

This is intentionally not a full Markdown engine — the goal is to make
help text and short error messages readable in the terminal without
adding a dependency.

The renderer does **not** read environment variables. The caller picks
the color policy by passing either:

* ``color`` — a configured :class:`codechu_cli.Color` instance, or
* ``enabled`` — a ``bool`` (defaults to ``True`` when neither is given).

If both are ``None``/missing, ANSI is emitted unconditionally — let the
caller gate on TTY.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .color import Color


# Inline patterns (order matters: code first to protect literal `*` etc.)
_RE_CODE = re.compile(r"`([^`]+)`")
_RE_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_RE_ITALIC = re.compile(r"\*([^*\s][^*]*?)\*")
_RE_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _ansi(code: str, text: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{code}{text}\x1b[0m"


def _render_inline(text: str, enabled: bool, color: "Color | None") -> str:
    # Code first.
    def code_repl(m: re.Match[str]) -> str:
        body = m.group(1)
        if color is not None:
            return color.info(body) if enabled else body
        return _ansi("\x1b[36m", body, enabled)

    out = _RE_CODE.sub(code_repl, text)

    def bold_repl(m: re.Match[str]) -> str:
        body = m.group(1)
        if color is not None:
            return color.bold(body) if enabled else body
        return _ansi("\x1b[1m", body, enabled)

    out = _RE_BOLD.sub(bold_repl, out)

    def italic_repl(m: re.Match[str]) -> str:
        body = m.group(1)
        return _ansi("\x1b[3m", body, enabled)

    out = _RE_ITALIC.sub(italic_repl, out)

    def link_repl(m: re.Match[str]) -> str:
        label, url = m.group(1), m.group(2)
        if color is not None and enabled:
            return f"{color.bold(label)} ({color.dim(url)})"
        if enabled:
            return f"\x1b[1m{label}\x1b[0m (\x1b[2m{url}\x1b[0m)"
        return f"{label} ({url})"

    out = _RE_LINK.sub(link_repl, out)
    return out


def render_markdown(
    text: str,
    *,
    color: "Color | None" = None,
    enabled: bool | None = None,
) -> str:
    """Render a minimal Markdown subset to an ANSI-styled string.

    Parameters
    ----------
    text:
        Markdown source.
    color:
        Optional :class:`Color` instance to drive ANSI generation. When
        provided, its ``enabled`` flag wins unless ``enabled=`` is also
        passed explicitly.
    enabled:
        Force ANSI on/off. If ``None`` and no ``color`` is provided,
        ANSI is emitted (default: ``True``).
    """
    if enabled is None:
        enabled = color.enabled if color is not None else True

    lines = text.split("\n")
    out: list[str] = []
    for line in lines:
        stripped = line.lstrip()
        indent = line[: len(line) - len(stripped)]
        if stripped.startswith("## "):
            body = _render_inline(stripped[3:], enabled, color)
            if color is not None and enabled:
                out.append(indent + color.bold(body))
            else:
                out.append(indent + _ansi("\x1b[1m", body, enabled))
            continue
        if stripped.startswith("# "):
            body = _render_inline(stripped[2:], enabled, color)
            if color is not None and enabled:
                out.append(indent + color.bold(color.info(body)))
            else:
                out.append(indent + _ansi("\x1b[1;36m", body, enabled))
            continue
        if stripped.startswith(("- ", "* ")):
            body = _render_inline(stripped[2:], enabled, color)
            bullet = "•"
            if color is not None and enabled:
                bullet = color.dim(bullet)
            elif enabled:
                bullet = _ansi("\x1b[2m", bullet, enabled)
            out.append(f"{indent}  {bullet} {body}")
            continue
        out.append(indent + _render_inline(stripped, enabled, color))
    return "\n".join(out)


__all__ = ["render_markdown"]
