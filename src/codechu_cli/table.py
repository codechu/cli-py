"""ASCII table widget with pluggable styles, alignment, and color callbacks.

Usage::

    t = Table(["File", "Size", "Risk"])
    t.add_row(["foo.log", "1.2 GB", "high"])
    t.align(1, "right")
    print(t.style("box"))

The table does **not** read environment variables. Color callbacks
must be supplied by the caller — e.g. ``t.color_col(2, c.high)``.
"""

from __future__ import annotations

import re
from typing import Callable, Literal

AlignMode = Literal["left", "right", "center"]

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _visible_len(s: str) -> int:
    """Length excluding ANSI escape sequences."""
    return len(_ANSI_RE.sub("", s))


def _pad(text: str, width: int, mode: AlignMode) -> str:
    pad = width - _visible_len(text)
    if pad <= 0:
        return text
    if mode == "right":
        return " " * pad + text
    if mode == "center":
        left = pad // 2
        right = pad - left
        return " " * left + text + " " * right
    return text + " " * pad


# Style registry: each style is a dict describing border glyphs.
# Keys: top_l, top_m, top_r, top_h, mid_l, mid_m, mid_r, mid_h,
#       bot_l, bot_m, bot_r, bot_h, v (vertical), sep (header separator)
# An empty/None value means "no border on that side".
_STYLES: dict[str, dict[str, str]] = {
    "plain": {
        "v": "",
        "h": "",
        "pad": " ",
        "col_sep": "  ",
        "header_sep": "",
    },
    "box": {
        "top_l": "┌",
        "top_m": "┬",
        "top_r": "┐",
        "top_h": "─",
        "mid_l": "├",
        "mid_m": "┼",
        "mid_r": "┤",
        "mid_h": "─",
        "bot_l": "└",
        "bot_m": "┴",
        "bot_r": "┘",
        "bot_h": "─",
        "v": "│",
        "pad": " ",
    },
    "github": {
        "v": "|",
        "pad": " ",
        "header_sep_l": "|",
        "header_sep_m": "|",
        "header_sep_r": "|",
        "header_sep_h": "-",
    },
}


class Table:
    """ASCII table with pluggable styles."""

    def __init__(self, headers: list[str], *, width: int | None = None) -> None:
        self._headers: list[str] = list(headers)
        self._rows: list[list[str]] = []
        self._aligns: list[AlignMode] = ["left"] * len(headers)
        self._colors: dict[int, Callable[[str], str]] = {}
        self._style: str = "plain"
        self._width_cap: int | None = width

    # ----- builders -------------------------------------------------

    def add_row(self, values: list[str]) -> "Table":
        """Append a row. ``values`` are pre-formatted strings."""
        row = [str(v) for v in values]
        # Normalize length to header count.
        if len(row) < len(self._headers):
            row = row + [""] * (len(self._headers) - len(row))
        elif len(row) > len(self._headers):
            row = row[: len(self._headers)]
        self._rows.append(row)
        return self

    def align(self, col: int, mode: AlignMode) -> "Table":
        """Set per-column alignment (``left``, ``right``, ``center``)."""
        if mode not in ("left", "right", "center"):
            raise ValueError(f"unknown align mode: {mode!r}")
        if not 0 <= col < len(self._headers):
            raise IndexError(f"col {col} out of range (0..{len(self._headers) - 1})")
        self._aligns[col] = mode
        return self

    def style(self, name: str) -> "Table":
        """Set the rendering style: ``plain``, ``box``, or ``github``."""
        if name not in _STYLES:
            raise ValueError(f"unknown style: {name!r}. Known: {sorted(_STYLES)}")
        self._style = name
        return self

    def color_col(self, col: int, fn: Callable[[str], str]) -> "Table":
        """Apply ``fn`` to every cell value in column ``col`` when rendering."""
        if not 0 <= col < len(self._headers):
            raise IndexError(f"col {col} out of range (0..{len(self._headers) - 1})")
        self._colors[col] = fn
        return self

    # ----- rendering ------------------------------------------------

    def _widths(self) -> list[int]:
        widths = [_visible_len(h) for h in self._headers]
        for row in self._rows:
            for i, cell in enumerate(row):
                # Width is computed on the *colored* cell so that
                # ANSI escapes don't inflate padding.
                colored = self._colors[i](cell) if i in self._colors else cell
                w = _visible_len(colored)
                if w > widths[i]:
                    widths[i] = w
        if self._width_cap is not None:
            # Best-effort: cap each column proportionally to fit.
            total = sum(widths) + 2 * (len(widths) - 1)
            if total > self._width_cap and widths:
                shrink = total - self._width_cap
                # Shrink widest first.
                while shrink > 0 and max(widths) > 1:
                    idx = widths.index(max(widths))
                    widths[idx] -= 1
                    shrink -= 1
        return widths

    def _render_cells(self, row: list[str], widths: list[int]) -> list[str]:
        out: list[str] = []
        for i, cell in enumerate(row):
            colored = self._colors[i](cell) if i in self._colors else cell
            out.append(_pad(colored, widths[i], self._aligns[i]))
        return out

    def _render_plain(self, widths: list[int]) -> str:
        lines: list[str] = []
        lines.append("  ".join(_pad(h, widths[i], self._aligns[i]) for i, h in enumerate(self._headers)))
        for row in self._rows:
            lines.append("  ".join(self._render_cells(row, widths)))
        return "\n".join(lines)

    def _render_box(self, widths: list[int]) -> str:
        s = _STYLES["box"]
        h = s["top_h"]

        def border(left: str, mid: str, right: str, fill: str) -> str:
            segs = [fill * (w + 2) for w in widths]
            return left + mid.join(segs) + right

        def row_line(cells: list[str]) -> str:
            inner = " " + " │ ".join(cells) + " "
            return "│" + inner + "│"

        lines: list[str] = []
        lines.append(border(s["top_l"], s["top_m"], s["top_r"], h))
        lines.append(row_line(
            [_pad(h_, widths[i], self._aligns[i]) for i, h_ in enumerate(self._headers)]
        ))
        lines.append(border(s["mid_l"], s["mid_m"], s["mid_r"], h))
        for row in self._rows:
            lines.append(row_line(self._render_cells(row, widths)))
        lines.append(border(s["bot_l"], s["bot_m"], s["bot_r"], h))
        return "\n".join(lines)

    def _render_github(self, widths: list[int]) -> str:
        def row_line(cells: list[str]) -> str:
            return "| " + " | ".join(cells) + " |"

        lines: list[str] = []
        lines.append(row_line(
            [_pad(h_, widths[i], self._aligns[i]) for i, h_ in enumerate(self._headers)]
        ))
        # Separator with alignment hints.
        seps: list[str] = []
        for i, w in enumerate(widths):
            dashes = "-" * max(3, w)
            mode = self._aligns[i]
            if mode == "right":
                seps.append(dashes[:-1] + ":")
            elif mode == "center":
                seps.append(":" + dashes[1:-1] + ":")
            else:
                seps.append(dashes)
        lines.append("| " + " | ".join(seps) + " |")
        for row in self._rows:
            lines.append(row_line(self._render_cells(row, widths)))
        return "\n".join(lines)

    def __str__(self) -> str:
        widths = self._widths()
        if self._style == "box":
            return self._render_box(widths)
        if self._style == "github":
            return self._render_github(widths)
        return self._render_plain(widths)


__all__ = ["Table"]
