"""codechu-cli — stdlib-only CLI primitives.

Public API re-exports. See module docstrings for details.
"""

from __future__ import annotations

from . import emoji
from .banner import LOGOS, ascii_banner, banner
from .color import Color
from .emoji import capabilities, e
from .format import format_examples, resolve_format
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

# Convenience re-exports so existing tests + casual users still find
# the helpers at codechu_cli. Authoritative home is the sibling libs.
from codechu_fmt import format_duration, format_rate, format_size
from codechu_meter import ETAEstimator, RateEstimator, Stopwatch
from codechu_spark import sparkline

__version__ = "0.1.0"

__all__ = [
    "BAR_STYLES",
    "Color",
    "ETAEstimator",
    "LOGOS",
    "ProgressBar",
    "ProgressLine",
    "RateEstimator",
    "SPINNER_FAMILIES",
    "SPINNER_STYLES",
    "STYLE_COMPATIBILITY",
    "STYLE_TAGS",
    "Spinner",
    "Stopwatch",
    "__version__",
    "ascii_banner",
    "banner",
    "capabilities",
    "confirm",
    "e",
    "emoji",
    "format_duration",
    "format_examples",
    "format_rate",
    "format_size",
    "multiselect",
    "prompt",
    "register_bar_style",
    "register_spinner_style",
    "resolve_format",
    "select",
    "sparkline",
]
