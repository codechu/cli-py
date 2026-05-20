"""Bar style registry."""

from __future__ import annotations

BAR_STYLES: dict[str, dict] = {
    # Industry classics
    "ascii":  {"fill": "#",  "empty": "-"},
    "equals": {"fill": "=",  "empty": "-"},
    "block":  {"fill": "█",  "empty": "░"},
    "slim":   {"fill": "━",  "empty": "─"},
    "dots":   {"fill": "●",  "empty": "○"},
    "arrow":  {"fill": "▶",  "empty": " "},
    "pipe":   {"fill": "|",  "empty": " "},

    # Codechu signature
    "codechu":          {"fill": "▰", "empty": "▱"},
    "codechu-gradient": {"fill": "▓", "empty": "░"},

    # Fixed-block
    "blocks":      {"fill": "▰", "empty": "▱", "width": 5},
    "blocks-wide": {"fill": "▰", "empty": "▱", "width": 8},
    "blocks-fat":  {"fill": "█", "empty": "░", "width": 5},
    "claude":      {"fill": "█", "empty": "░", "width": 10},

    # Subpixel-smooth
    "smooth":      {"fill": "█", "empty": " ", "width": 10, "smooth": True},
    "smooth-wide": {"fill": "█", "empty": " ", "width": 20, "smooth": True},

    # Gradient / tape
    "gradient-edge": {"fill": "█", "empty": "░", "edge": "▓▒"},
    "tape":          {"fill": "▰", "empty": "░", "separator": "│"},
}

DEFAULT_BAR_STYLE = "ascii"

# Re-exported here so the bar renderer can import from one place.
from .styles_spinner import (  # noqa: E402,F401
    SPINNER_STYLES,
    STYLE_COMPATIBILITY,
    STYLE_TAGS,
)

# Eighths ramp used by smooth rendering (9 stops: 0/8 .. 8/8).
SUBPIXEL = " ▏▎▍▌▋▊▉█"


def register_bar_style(
    name: str,
    *,
    fill: str | None = None,
    empty: str | None = None,
    width: int | None = None,
    smooth: bool = False,
) -> None:
    """Register a custom progress bar style at runtime."""
    spec: dict[str, object] = {}
    if fill is not None:
        spec["fill"] = fill
    if empty is not None:
        spec["empty"] = empty
    if width is not None:
        spec["width"] = width
    if smooth:
        spec["smooth"] = True
    BAR_STYLES[name] = spec


__all__ = [
    "BAR_STYLES",
    "DEFAULT_BAR_STYLE",
    "SUBPIXEL",
    "register_bar_style",
]
