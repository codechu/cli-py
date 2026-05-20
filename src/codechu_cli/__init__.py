"""codechu-cli — stdlib-only CLI primitives.

Public API. See module docstrings for details. Formatting / metering /
sparkline helpers used to be re-exported here; they now live in their
own packages — import directly from ``codechu_fmt``, ``codechu_meter``,
and ``codechu_spark``.
"""

from __future__ import annotations

from . import emoji
from .banner import LOGOS, ascii_banner, banner
from .box import box
from .color import Color
from .emoji import capabilities, e
from .format import format_examples, resolve_format
from .markdown import render_markdown
from .progress import (
    BAR_STYLES,
    SPINNER_FAMILIES,
    SPINNER_STYLES,
    STYLE_COMPATIBILITY,
    STYLE_TAGS,
    ProgressBar,
    ProgressLine,
    Spinner,
    register_bar_style,
    register_spinner_style,
)
from .prompt import confirm, multiselect, prompt, select
from .table import Table

__version__ = "0.4.0"

__all__ = [
    "BAR_STYLES",
    "Color",
    "LOGOS",
    "ProgressBar",
    "ProgressLine",
    "SPINNER_FAMILIES",
    "SPINNER_STYLES",
    "STYLE_COMPATIBILITY",
    "STYLE_TAGS",
    "Spinner",
    "Table",
    "__version__",
    "ascii_banner",
    "banner",
    "box",
    "capabilities",
    "confirm",
    "e",
    "emoji",
    "format_examples",
    "multiselect",
    "prompt",
    "register_bar_style",
    "register_spinner_style",
    "render_markdown",
    "resolve_format",
    "select",
]
