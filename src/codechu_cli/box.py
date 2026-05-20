"""Multi-line bordered text box.

Usage::

    from codechu_cli import box
    print(box("Hello\\nworld", style="rounded", title="greeting"))

Styles: ``single``, ``double``, ``rounded``. Caller prints the result.
"""

from __future__ import annotations

import re

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _visible_len(s: str) -> int:
    return len(_ANSI_RE.sub("", s))


_BOX_STYLES: dict[str, dict[str, str]] = {
    "single": {
        "tl": "┌", "tr": "┐", "bl": "└", "br": "┘",
        "h": "─", "v": "│",
    },
    "double": {
        "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝",
        "h": "═", "v": "║",
    },
    "rounded": {
        "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
        "h": "─", "v": "│",
    },
}


def box(
    text: str,
    *,
    style: str = "single",
    title: str | None = None,
    padding: int = 1,
) -> str:
    """Wrap ``text`` in a Unicode border box.

    Parameters
    ----------
    text:
        Multi-line input. ``\\n`` separates lines.
    style:
        One of ``"single"`` (default), ``"double"``, ``"rounded"``.
    title:
        Optional string inset into the top border.
    padding:
        Horizontal padding (spaces) inside the box on each side. Must
        be ``>= 0``. Vertical padding is not added — pad ``text``
        yourself if you want blank rows.
    """
    if style not in _BOX_STYLES:
        raise ValueError(f"unknown box style: {style!r}. Known: {sorted(_BOX_STYLES)}")
    if padding < 0:
        raise ValueError("padding must be >= 0")

    s = _BOX_STYLES[style]
    lines = text.split("\n") if text else [""]
    content_w = max((_visible_len(line) for line in lines), default=0)
    if title is not None:
        # Title needs space + 2 border corners; ensure inner width fits.
        content_w = max(content_w, _visible_len(title) + 2)

    inner_w = content_w + padding * 2

    # Top border (with optional title).
    if title:
        # ┌─ title ──────┐
        title_str = f" {title} "
        remaining = inner_w - _visible_len(title_str)
        # Place title after 1 leading horizontal char for readability.
        if remaining < 1:
            # Expand inner width to fit.
            inner_w = _visible_len(title_str) + 1
            remaining = 1
        top = s["tl"] + s["h"] + title_str + s["h"] * (remaining - 1) + s["tr"]
    else:
        top = s["tl"] + s["h"] * inner_w + s["tr"]

    bot = s["bl"] + s["h"] * inner_w + s["br"]

    pad = " " * padding
    body: list[str] = []
    for line in lines:
        gap = " " * (content_w - _visible_len(line))
        body.append(f"{s['v']}{pad}{line}{gap}{pad}{s['v']}")

    return "\n".join([top, *body, bot])


__all__ = ["box"]
