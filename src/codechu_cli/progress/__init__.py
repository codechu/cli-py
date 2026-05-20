"""Progress lines, bars, and spinners.

Public API re-exports. The implementation is split across:

- :mod:`codechu_cli.progress.line` — :class:`ProgressLine`
- :mod:`codechu_cli.progress.bar` — :class:`ProgressBar` with builder
- :mod:`codechu_cli.progress.spinner` — :class:`Spinner` (context manager)
- :mod:`codechu_cli.progress.styles_spinner` — spinner registry
- :mod:`codechu_cli.progress.styles_bar` — bar registry
"""

from __future__ import annotations

from .bar import ProgressBar
from .line import ProgressLine
from .spinner import Spinner
from .styles_bar import (
    BAR_STYLES,
    DEFAULT_BAR_STYLE,
    SUBPIXEL,
    register_bar_style,
)
from .styles_spinner import (
    DEFAULT_SPINNER_STYLE,
    SPINNER_FAMILIES,
    SPINNER_STYLES,
    STYLE_COMPATIBILITY,
    STYLE_TAGS,
    register_spinner_style,
)

__all__ = [
    "BAR_STYLES",
    "DEFAULT_BAR_STYLE",
    "DEFAULT_SPINNER_STYLE",
    "ProgressBar",
    "ProgressLine",
    "SPINNER_FAMILIES",
    "SPINNER_STYLES",
    "STYLE_COMPATIBILITY",
    "STYLE_TAGS",
    "SUBPIXEL",
    "Spinner",
    "register_bar_style",
    "register_spinner_style",
]
