"""Progress lines, bars, and spinners."""

from __future__ import annotations

import sys
import threading
import time
from typing import IO

from .emoji import capabilities

_BRAILLE_FRAMES = ("⠋", "⠙", "⠹", "⠸", "⠼",
                   "⠴", "⠦", "⠧", "⠇", "⠏")
_ASCII_FRAMES = ("|", "/", "-", "\\")


SPINNER_STYLES: dict[str, list[str]] = {
    # Industry classics (names match cli-spinners' canon where applicable):
    "dots":     ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    "dots2":    ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
    "line":     ["|", "/", "-", "\\"],          # ASCII safe
    "arc":      ["◜", "◠", "◝", "◞", "◡", "◟"],
    "bouncing": ["⠁", "⠂", "⠄", "⠂"],            # subtle dot bounce
    "pulse":    ["•", "◦", " ", "◦"],
    "clock":    ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕",
                 "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"],

    # Codechu signature: clockwise disk quarters — echoes the disk-cleaner
    # mark / Codechu publisher visual (radial gradient disk).
    "codechu":      ["◐", "◓", "◑", "◒"],
    "codechu-fade": ["▒", "▓", "█", "▓"],   # solid pulse, for "deep work"

    # 5-cell block patterns — Claude Code-style indeterminate progress
    # bars that double as spinners (work without a known total).
    "blocks-bounce": [
        "▰▱▱▱▱", "▱▰▱▱▱", "▱▱▰▱▱", "▱▱▱▰▱", "▱▱▱▱▰",
        "▱▱▱▰▱", "▱▱▰▱▱", "▱▰▱▱▱",
    ],
    "blocks-fill": [
        "▱▱▱▱▱", "▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰",
    ],
    "blocks-snake": [
        "▰▱▱▱▱", "▰▰▱▱▱", "▰▰▰▱▱", "▰▰▰▰▱", "▰▰▰▰▰",
        "▱▰▰▰▰", "▱▱▰▰▰", "▱▱▱▰▰", "▱▱▱▱▰", "▱▱▱▱▱",
    ],
    "blocks-pulse": ["▱▱▱▱▱", "▰▰▰▰▰"],
    "blocks-fill-solid": [
        "     ", "█    ", "██   ", "███  ", "████ ", "█████",
    ],

    # 3-cell patterns — even narrower; fit inline next to a label
    "dots3":   [".  ", ".. ", "...", " ..", "  .", "   "],
    "wave3":   ["▁  ", "▂▁ ", "▃▂▁", "▄▃▂", "▃▄▃", "▂▃▄", "▁▂▃", " ▁▂", "  ▁"],
    "tri3":    ["◐◯◯", "◯◐◯", "◯◯◐", "◯◐◯"],

    # Single-cell grow/shrink — subpixel pulse using eighths
    "grow-h":  ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█",
                "▉", "▊", "▋", "▌", "▍", "▎"],
    "grow-v":  ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█",
                "▇", "▆", "▅", "▄", "▃", "▂"],

    # Arrows + toggles
    "arrow3":     ["▸▹▹▹▹", "▹▸▹▹▹", "▹▹▸▹▹", "▹▹▹▸▹", "▹▹▹▹▸"],
    "toggle":     ["■", "□"],
    "toggle-sq":  ["▪", "▫"],
    "toggle-rd":  ["⊙", "⊚"],

    # Pictographic — for fun / dev-mode banners; emoji-only terminals
    "earth":   ["🌍", "🌎", "🌏"],
    "moon":    ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],
    "weather": ["☀ ", "☀☁", "☁☁", "☁🌧", "🌧🌧", "🌧☁", "☁☀", " ☀"],

    # --- Striking / modern ---------------------------------------------
    # comet: solid head with fading tail, wraps around 8 cells
    "comet": [
        "█▓▒░    ", " █▓▒░   ", "  █▓▒░  ", "   █▓▒░ ",
        "    █▓▒░", "░    █▓▒", "▒░    █▓", "▓▒░    █",
    ],
    # wave: 8-column sine wave shifting left, audio-visualizer feel
    "wave": [
        "▂▃▅▆▇█▇▆", "▃▅▆▇█▇▆▅", "▅▆▇█▇▆▅▃", "▆▇█▇▆▅▃▂",
        "▇█▇▆▅▃▂▁", "█▇▆▅▃▂▁▂", "▇▆▅▃▂▁▂▃", "▆▅▃▂▁▂▃▅",
    ],
    # pulse-radial: radial expand+contract from center, 7 wide
    "pulse-radial": [
        "   █   ", "  ▓█▓  ", " ▒▓█▓▒ ", "░▒▓█▓▒░",
        " ▒▓█▓▒ ", "  ▓█▓  ",
    ],
    # equalizer: 4-column vertical bars, oscillate independently
    "equalizer": [
        "▁▃▅▇", "▃▅▇█", "▅▇█▇", "▇█▇▅",
        "█▇▅▃", "▇▅▃▁", "▅▃▁▃", "▃▁▃▅",
    ],
    # ripple: solid head leaving fading ring trail, restart per cycle
    "ripple": [
        "█       ", "▓█      ", "▒▓█     ", "░▒▓█    ",
        " ░▒▓█   ", "  ░▒▓█  ", "   ░▒▓█ ", "    ░▒▓█",
    ],
    # orbit-quad: 2-cell corner pair rotating clockwise — minimalist
    "orbit-quad": ["◜◝", "◝◞", "◞◟", "◟◜"],
    # shimmer: sparkles + dots at varying positions, feels alive
    "shimmer": [
        "·  ✦   ", " ✦   · ", "  · ✦  ", "✦   ·  ",
        "  ✦   ·", "· ✦    ",
    ],
    # glitch: brief disturbed-text moments — deliberate jank
    "glitch": [
        "▒▓█▓▒", "▓█▒░█", "▒▓░█▒", "█▒▓░▓",
        "▓▒█▓░", "░▓▒█▓",
    ],
    # double-bounce: two dots in opposite phase — disco rhythm
    "double-bounce": [
        "●○○○○○○○", "○●○○○○○●", "○○●○○○●○", "○○○●○●○○",
        "○○○○●○○○", "○○○●○●○○", "○○●○○○●○", "○●○○○○○●",
    ],

    # --- Chaos / heavy-load / stress patterns --------------------------
    # static: TV-static gradient noise. Suggests "many things happening,
    # not periodic" — good for heavy parallel work.
    "static": [
        "░▒▓▒░▓▒░", "▓░▒▓░▒░▓", "▒▓░▒▓░▓▒",
        "░▓▒░▓▒▓░", "▓▒░▒▓░▒▓", "▒░▓▒░▓▒░",
    ],
    # storm: scattered raindrops + dashes, irregular spacing. Asymmetric
    # by design — eye reads it as unpredictable.
    "storm": [
        "╱  ·  ╲ ", " ·╱  ╲  ", "╲  ·╱  ·", "·  ╲ ·  ",
        " ╱·  ╲ ·", "╲ · ╱   ", "  ╱ ·  ╲", "· ╲  ╱· ",
    ],
    # sparks: explosive sparkle bursts at random positions. Each frame
    # has a different cluster — no two consecutive look alike.
    "sparks": [
        "· ✦   ·  ", "✦  · ✦  ·", "  ✦·   ✦ ", "· ✦  ✦  ·",
        "✦   · ✦  ", " ✦ ·   ✦·", "·  ✦ ·  ✦", " ·✦  ·✦  ",
    ],
    # fireworks: single burst that grows + fades, then a beat of calm.
    # The pause is intentional — gives rhythm to the chaos.
    "fireworks": [
        "         ", "    ·    ", "   ·✦·   ", "  ✶✦✶    ",
        " ·✶✦✶·   ", "  ·✦·    ", "         ", "  ·      ",
    ],
    # electricity: lightning bolts striking at random positions.
    # Discontinuous frames — feels like discrete strikes, not flow.
    "electricity": [
        "⚡       ", "   ⚡    ", "        ", "⚡  ⚡   ",
        "      ⚡ ", "        ", " ⚡   ⚡ ", "    ⚡   ",
    ],
    # maelstrom: swirling diagonals — angry slashes intersecting.
    # Suggests "system under turbulence" without specifying error state.
    "maelstrom": [
        "╲╱╲╱╲╱", "╱╲╱╲╱╲", "╲╱╲╲╱╱", "╱╱╲╲╱╲",
        "╲╲╱╱╲╱", "╱╲╲╱╲╱", "╲╱╱╲╲╱", "╱╲╱╲╲╱",
    ],
    # build-up: calm → busy → eruption → calm. One full intensity arc
    # per cycle; suggests "load is increasing under pressure".
    "build-up": [
        "·       ", "··      ", "···     ", "·· ·    ",
        "·· ··   ", "·✦ ·· · ", "·✦·✦·✦·✦", "·  ✦  · ",
        "        ", "   ·    ",
    ],

    # --- Random-access patterns ----------------------------------------
    # Single entity teleporting between positions — no spatial coherence.
    # This is the *seek* fingerprint: each frame's position is unrelated
    # to the last. Distinct from chaos (dense+unpredictable); random
    # access is sparse+unpredictable in position.

    # scatter: single dot teleports to random positions in an 8-cell row
    "scatter": [
        "●       ", "      ●  ", "  ●      ", "        ●",
        "   ●     ", " ●       ", "       ● ", "    ●    ",
    ],
    # multi-seek: 2-3 simultaneous reads at uncorrelated positions
    "multi-seek": [
        "●  ●     ", "     ● ● ", "  ●   ●  ", "●     ●  ",
        " ● ● ●   ", "   ●  ● ●", "● ●    ● ", " ●  ●  ● ",
    ],
    # disk-thrash: wider hashes at random spots — HDD head movement feel
    "disk-thrash": [
        "━━       ", "     ━━━ ", " ━━      ", "      ━━━",
        "━     ━━ ", "   ━━━  ━", "━━     ━━", " ━━━ ━   ",
    ],
    # hash-spray: sparse decorrelated dots — hash output / cache misses
    "hash-spray": [
        "·  ·  · ", "    ·   ", "  ·    ·", "·       ",
        "   ·  · ", "·    ·  ", " ·    · ", "  ·  ·  ",
    ],
    # rand-walk: single point doing brownian-ish motion (no teleport,
    # small unpredictable steps) — distinct from scatter's hard jumps
    "rand-walk": [
        "  ●   ", "   ●  ", "  ●   ", " ●    ",
        "  ●   ", "   ●  ", "    ● ", "   ●  ",
        "  ●   ", " ●    ",
    ],
    # gather: scattered dots converge to center, scatter again — like
    # random reads consolidating, then dispersing
    "gather": [
        "●     ●●", " ●   ●● ", "  ● ●●  ", "  ●●●   ",
        "   ●●   ", "  ● ●   ", " ●   ●  ", "●     ●●",
    ],

    # --- Matrix / digital-rain --------------------------------------
    # True multi-column rain needs multi-line UI (v0.2 Live coordinator).
    # Single-line variants that evoke the aesthetic:

    # matrix: single cell flickering through katakana/symbols — a
    # character "morphing" in place, classic Matrix close-up feel
    "matrix": [
        "ﾊ", "ﾐ", "ﾑ", "ﾒ", "ﾓ", "ｦ", "ｱ", "ｲ", "ｳ", "ｴ",
        "ｵ", "ﾅ", "ﾆ", "ﾇ", "ﾈ", "ﾉ", "0", "1", "Z", "ﾄ",
    ],
    # matrix-rain: 4 columns each cycling random chars at offset phases
    # — looks like a horizontal slice through rain
    "matrix-rain": [
        "ﾊ ｱ 1 ﾐ", "ﾐ ﾊ 0 ｴ", "ｱ ﾐ 1 ﾄ", "ｴ ﾊ 0 ﾅ",
        "ﾆ ｱ 1 ﾐ", "ﾅ ﾐ 0 ﾊ", "ﾄ ﾆ 1 ｴ", "ｦ ﾅ 0 ｱ",
        "ｲ ﾄ 1 ﾆ", "ﾐ ｦ 0 ﾅ",
    ],
    # matrix-drop: single cell vertical-fall illusion via half-blocks
    # — top edge → upper half → full → lower half → bottom → gone
    "matrix-drop": [
        "▔", "▀", "█", "▄", "▁", " ",
    ],
    # matrix-trail: head + fading body — vertical drop with afterglow
    # (each frame is the head's position, but the body persists as
    # different fill levels — uses subpixel chars for smoothness)
    "matrix-trail": [
        "▔", "▀", "█", "▆", "▄", "▂", "▁", " ",
    ],

    # --- Quadrant-block grids ------------------------------------------
    # Single CLI row, but each cell renders as a 2x2 sub-grid via
    # Unicode quadrant block characters (▘▝▖▗▀▄▌▐▙▚▛▜▟▞█ + space).
    # Result: 4 sub-cells per visual cell, each can be lit/dark
    # independently — gives a 2-row "grid of mini squares" illusion.

    # quad-random: 4 cells, each picks a different random pattern per
    # frame. Visually busy — "many cells flashing on/off independently"
    "quad-random": [
        "▘▗▖▝", "▟▙▛▜", "▖▘▗▝", "▞▀▄▚",
        "▝▖▘▗", "▛▜▟▙", "▖▝▘▗", "▚▞▀▄",
        "▌▐▝▘", "▟▖▞▛", "▀▙▚▗", "▐▌▜▝",
    ],

    # quad-twinkle: sparse single-corner lights in a 6-cell row.
    # Slower, calmer — feels like stars twinkling on/off, not chaos
    "quad-twinkle": [
        "▘     ", "  ▝   ", "    ▗ ", " ▖    ",
        "   ▖  ", "▝   ▗ ", "  ▘ ▗ ", "▖   ▝ ",
        "   ▘  ", "▗  ▖  ",
    ],

    # quad-pulse: all 4 cells light together then fade through corners
    # back to empty. Slow heartbeat through quadrant fill levels
    "quad-pulse": [
        "    ", "▘▝▖▗", "▙▚▞▟", "████",
        "▙▚▞▟", "▘▝▖▗", "    ", "    ",
    ],

    # quad-rain: half-blocks falling in random columns — 2-row vertical
    # drop illusion (▀ = head, █ = mid-fall, ▄ = bottom, space = clear)
    "quad-rain": [
        "▀  ▀ ", "█  █▀", "▄  █ ", " ▀ ▄ ",
        "▀█   ", "▄█ ▀ ", " ▄ █ ", "  ▄▄ ",
        "▀ ▀  ", "█▀█  ",
    ],

    # quad-cross: alternating diagonal blocks — ▚/▞ checkerboard shift.
    # Hypnotic, mathematical; less "random" more "geometric flicker"
    "quad-cross": [
        "▚▞▚▞", "▞▚▞▚", "▚▚▞▞", "▞▞▚▚",
        "█▚▞ ", " ▞▚█", "▚█ ▞", "▞ █▚",
    ],

    # --- Conveyor / pipeline ------------------------------------------
    # Multiple discrete items continuously shifting right — "batches
    # being processed through a pipeline". Distinct from comet (single
    # head + fade trail): conveyor has multiple items, no fade.

    # conveyor: paired blocks ▓░ marching right, 4-cell phase repeat
    "conveyor": [
        "▓░  ▓░  ", " ▓░  ▓░ ", "  ▓░  ▓░", "░  ▓░  ▓",
    ],
    # conveyor-fast: same shape, 2-cell stride (twice as quick visually)
    "conveyor-fast": [
        "▓░▓░▓░▓░", "░▓░▓░▓░▓",
    ],
    # conveyor-mixed: varied item sizes — irregular cargo on the belt
    "conveyor-mixed": [
        "━ ━━  ━ ", " ━ ━━  ━", "━ ━ ━━  ", " ━ ━ ━━ ",
        "  ━ ━ ━━", "━  ━ ━ ━", "━━  ━ ━ ", " ━━  ━ ━",
    ],
    # pipeline: bracketed packages — emphasis on "discrete unit" feel,
    # 4 items spaced apart, each shifts one cell per frame
    "pipeline": [
        "[ ]  [ ] ", " [ ]  [ ]", "[]  [ ]  ", " []  [ ] ",
        "  []  [ ]", "   []  []", " ]  []  [", "  ]  []  ",
    ],

    # --- Pacman / Game of Life ----------------------------------------
    # Iconic aesthetics, not literal simulations — true cellular
    # automata or arcade games need multi-line UI (v0.2 Live).

    # pacman: classic mouth-chomping moving right, eating pellets
    "pacman": [
        "C • • • •", "O • • • •", " c• • • •", " C • • • •",
        "  o• • •",  "  C • • •", "   c• •",   "   C • •",
        "    o•",    "    C •",   "     c",    "     C",
    ],
    # pacman-reverse: pacman moving left (mirror), pellets behind
    "pacman-reverse": [
        "• • • • C", "• • • • O", "• • • •c ", "• • • •C ",
        "• • • o  ", "• • • C  ", "• • o    ", "• • C    ",
        "• o      ", "• C      ", "o        ", "C        ",
    ],
    # pacman-ghost: pacman fleeing while ghost chases — adversarial
    "pacman-ghost": [
        "C  ᗣ    ", " C  ᗣ   ", "  C  ᗣ  ", "   C  ᗣ ",
        "    C  ᗣ", "ᗣ    C  ", " ᗣ    C ", "  ᗣ    C",
    ],

    # game-of-life: sparse cells evolving — not real CA, but the
    # emergent visual feel of Conway's Game of Life
    "game-of-life": [
        "▘   ▝   ", " ▘▖    ▗", "  ▝▘    ", "▝ ▗  ▘ ▝",
        "  ▖▝▘▗  ", " ▘▝▖▘   ", "▝ ▘▘ ▝▖ ", "▖   ▘ ▝▘",
        "  ▖  ▝▗ ", "▘▝▖ ▘   ",
    ],
    # life-glider: single sub-pixel "glider" moving diagonally — the
    # most famous GoL pattern, distilled to its essence
    "life-glider": [
        "▘     ", " ▖    ", "  ▝   ", "   ▖  ", "    ▝ ",
        "     ▖", "▝     ", " ▖    ",
    ],
    # life-blinker: 3-cell oscillator alternating horizontal/vertical
    # (the simplest GoL oscillator); rendered with half-blocks
    "life-blinker": [
        "▄▄▄ ", "    ", " ▌  ", "    ", "▄▄▄ ", "    ",
    ],
}

DEFAULT_SPINNER_STYLE = "dots"


BAR_STYLES: dict[str, dict] = {
    # Industry classics
    "ascii":  {"fill": "#",  "empty": "-"},   # cargo, GitHub Actions
    "equals": {"fill": "=",  "empty": "-"},   # Docker, classic make
    "block":  {"fill": "█",  "empty": "░"},   # modern npm/cargo
    "slim":   {"fill": "━",  "empty": "─"},
    "dots":   {"fill": "●",  "empty": "○"},
    "arrow":  {"fill": "▶",  "empty": " "},
    "pipe":   {"fill": "|",  "empty": " "},   # very minimal

    # Codechu signature: gradient blocks (matches disk-cleaner UI fill)
    "codechu":          {"fill": "▰", "empty": "▱"},
    "codechu-gradient": {"fill": "▓", "empty": "░"},

    # Fixed-block (Claude Code-style polish — width baked into the preset)
    "blocks":      {"fill": "▰", "empty": "▱", "width": 5},
    "blocks-wide": {"fill": "▰", "empty": "▱", "width": 8},
    "blocks-fat":  {"fill": "█", "empty": "░", "width": 5},
    "claude":      {"fill": "█", "empty": "░", "width": 10},   # alias / homage

    # Subpixel-smooth: narrow bars that render fractional progress via eighths
    "smooth":      {"fill": "█", "empty": " ", "width": 10, "smooth": True},
    "smooth-wide": {"fill": "█", "empty": " ", "width": 20, "smooth": True},
}

DEFAULT_BAR_STYLE = "ascii"

# Eighths ramp used by smooth rendering (9 stops: 0/8 .. 8/8).
SUBPIXEL = " ▏▎▍▌▋▊▉█"


def _stream_is_tty(stream: IO[str]) -> bool:
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except Exception:
        return False


class ProgressLine:
    """Single-line overwriting stderr progress with optional state.

    ``enabled`` defaults to ``stream.isatty()``. When disabled, all
    methods are no-ops so callers don't need to branch.
    """

    def __init__(self, stream: IO[str] | None = None, enabled: bool | None = None) -> None:
        self._stream = stream if stream is not None else sys.stderr
        if enabled is None:
            enabled = _stream_is_tty(self._stream)
        self.enabled = enabled
        self._last_width = 0

    def update(self, msg: str) -> None:
        if not self.enabled:
            return
        pad = " " * max(0, self._last_width - len(msg))
        try:
            self._stream.write(f"\r{msg}{pad}")
            self._stream.flush()
        except Exception:
            return
        self._last_width = len(msg)

    def clear(self) -> None:
        if not self.enabled or self._last_width == 0:
            return
        try:
            self._stream.write("\r" + " " * self._last_width + "\r")
            self._stream.flush()
        except Exception:
            pass
        self._last_width = 0


def _fmt_duration(seconds: float) -> str:
    """Render a duration as ``Xs`` or ``Xm Ys`` (rounded to whole seconds)."""
    if seconds < 0 or seconds != seconds:  # NaN guard
        return "?"
    s = int(round(seconds))
    if s < 60:
        return f"{s}s"
    m, rem = divmod(s, 60)
    return f"{m}m {rem}s"


class ProgressBar:
    """Bracketed progress bar with percent + count.

    Renders ``[###----] 30% · 3/10 · label`` to ``stream`` (default
    ``sys.stderr``). All methods are no-ops when ``enabled`` is False.

    Customize the look with ``fill``, ``empty``, and ``template``. The
    template gets these fields: ``{bar} {pct} {current} {total} {label}
    {elapsed} {eta}``. ``{elapsed}`` and ``{eta}`` are formatted via
    :func:`_fmt_duration` (``Xs`` or ``Xm Ys``). ``{eta}`` shows ``?``
    until at least one :meth:`advance` lands with a positive total and
    nonzero current.
    """

    DEFAULT_TEMPLATE = "[{bar}] {pct}% · {current}/{total} · {label}"

    def __init__(
        self,
        total: int,
        *,
        stream: IO[str] | None = None,
        width: int | None = None,
        style: str | None = None,
        fill: str | None = None,
        empty: str | None = None,
        smooth: bool | None = None,
        template: str | None = None,
        enabled: bool | None = None,
    ) -> None:
        self._stream = stream if stream is not None else sys.stderr
        self.total = max(0, int(total))
        self.current = 0
        if style is not None and style not in BAR_STYLES:
            raise KeyError(
                f"unknown bar style {style!r}. "
                f"Available: {sorted(BAR_STYLES)}"
            )
        preset = BAR_STYLES[style if style is not None else DEFAULT_BAR_STYLE]
        self.fill = fill if fill is not None else preset.get("fill", "#")
        self.empty = empty if empty is not None else preset.get("empty", "-")
        resolved_width = width if width is not None else preset.get("width", 40)
        # Allow narrow fixed-block presets (5–8 cells); only floor if the
        # caller passed something nonsensical with the default ascii preset.
        self.width = max(1, int(resolved_width))
        self.smooth = bool(smooth if smooth is not None else preset.get("smooth", False))
        self.template = template if template is not None else self.DEFAULT_TEMPLATE
        if enabled is None:
            enabled = _stream_is_tty(self._stream)
        self.enabled = enabled
        self._line = ProgressLine(self._stream, enabled=self.enabled)
        self._t_start = time.monotonic()

    def set_total(self, n: int) -> None:
        self.total = max(0, int(n))
        self._render(label="")

    def advance(self, n: int = 1, label: str = "") -> None:
        self.current = min(self.total, self.current + n) if self.total else self.current + n
        self._render(label=label)

    def _render_smooth(self, frac: float) -> str:
        """Render ``self.width`` cells using eighths-based partial fills."""
        if self.width <= 0:
            return ""
        frac = max(0.0, min(1.0, frac))
        total_eighths = int(round(frac * self.width * 8))
        full_cells = total_eighths // 8
        remainder = total_eighths % 8
        out = "█" * full_cells
        if full_cells < self.width:
            out += SUBPIXEL[remainder]
            out += " " * (self.width - full_cells - 1)
        return out

    def _render(self, *, label: str) -> None:
        if not self.enabled:
            return
        total = self.total or 1
        ratio = min(1.0, self.current / total) if total else 0.0
        if self.smooth:
            bar_str = self._render_smooth(ratio)
        else:
            filled = int(round(ratio * self.width))
            # Repeat fill/empty strings; clamp if a multi-char glyph would
            # overflow due to int rounding edges.
            bar_str = (self.fill * filled) + (self.empty * (self.width - filled))
        pct = int(round(ratio * 100))
        elapsed = time.monotonic() - self._t_start
        if self.total > 0 and self.current > 0:
            eta_s = elapsed * (self.total - self.current) / self.current
            eta_str = _fmt_duration(max(0.0, eta_s))
        else:
            eta_str = "?"
        msg = self.template.format(
            bar=bar_str,
            pct=pct,
            current=self.current,
            total=self.total,
            label=label,
            elapsed=_fmt_duration(elapsed),
            eta=eta_str,
        )
        # Trim trailing " · " when the default template ran with an
        # empty label, matching prior behavior.
        if self.template is self.DEFAULT_TEMPLATE or self.template == self.DEFAULT_TEMPLATE:
            if not label and msg.endswith(" · "):
                msg = msg[:-3]
        self._line.update(msg)

    def finish(self) -> None:
        self._line.clear()


class Spinner:
    """Threaded spinner with braille frames + ASCII fallback.

    Usage::

        with Spinner("Scanning…"):
            heavy_work()

    Or manually::

        sp = Spinner("Scanning…").start()
        try:
            heavy_work()
        finally:
            sp.stop()
    """

    def __init__(
        self,
        message: str = "",
        *,
        stream: IO[str] | None = None,
        style: str | None = None,
        frames: tuple[str, ...] | list[str] | None = None,
        interval: float = 0.08,
        enabled: bool | None = None,
    ) -> None:
        self._stream = stream if stream is not None else sys.stderr
        self.message = message
        self.interval = max(0.01, float(interval))
        if enabled is None:
            enabled = _stream_is_tty(self._stream)
        self.enabled = enabled
        if frames is None:
            if style is not None:
                if style not in SPINNER_STYLES:
                    raise KeyError(
                        f"unknown spinner style {style!r}. "
                        f"Available: {sorted(SPINNER_STYLES)}"
                    )
                frames = SPINNER_STYLES[style]
            else:
                caps = capabilities(self._stream)
                frames = _BRAILLE_FRAMES if "unicode" in caps else _ASCII_FRAMES
        self.frames = tuple(frames)
        self._line = ProgressLine(self._stream, enabled=self.enabled)
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> "Spinner":
        if not self.enabled or self._thread is not None:
            return self
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        return self

    def _run(self) -> None:
        i = 0
        while not self._stop.is_set():
            frame = self.frames[i % len(self.frames)]
            text = f"{frame} {self.message}".rstrip()
            self._line.update(text)
            i += 1
            if self._stop.wait(self.interval):
                break

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
            self._thread = None
        self._line.clear()

    def __enter__(self) -> "Spinner":
        return self.start()

    def __exit__(self, exc_type, exc, tb) -> None:
        # Don't suppress exceptions.
        self.stop()


# Re-export for tests that want to monkeypatch.
__all__ = [
    "BAR_STYLES",
    "DEFAULT_BAR_STYLE",
    "DEFAULT_SPINNER_STYLE",
    "ProgressBar",
    "ProgressLine",
    "SPINNER_STYLES",
    "Spinner",
]


# Keep ``time`` referenced so tests can ``monkeypatch.setattr(progress, 'time', fake)``.
_ = time
