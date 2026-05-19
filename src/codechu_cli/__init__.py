"""codechu-cli — stdlib-only CLI primitives.

Public API re-exports. See module docstrings for details.
"""

from __future__ import annotations

from .banner import LOGOS, ascii_banner, banner
from .color import Color
from .emoji import capabilities, e
from .format import format_examples, resolve_format
from .progress import ProgressBar, ProgressLine, Spinner
from .prompt import confirm, multiselect, prompt, select

__version__ = "0.1.0"

__all__ = [
    "Color",
    "LOGOS",
    "ProgressBar",
    "ProgressLine",
    "Spinner",
    "__version__",
    "ascii_banner",
    "banner",
    "capabilities",
    "confirm",
    "e",
    "format_examples",
    "multiselect",
    "prompt",
    "resolve_format",
    "select",
]
