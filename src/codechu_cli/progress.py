"""Progress lines, bars, and spinners."""

from __future__ import annotations

import sys
import threading
import time
from typing import IO

from codechu_fmt import format_duration, format_rate
from codechu_meter import RateEstimator

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

    # --- Loading / connection (universal expectations) ---------------
    # bar: sliding indeterminate bar inside brackets — the npm/yarn/cargo
    # "loading" archetype every user expects
    "bar": [
        "[▓▓▓░░░░░]", "[░▓▓▓░░░░]", "[░░▓▓▓░░░]", "[░░░▓▓▓░░]",
        "[░░░░▓▓▓░]", "[░░░░░▓▓▓]", "[░░░░▓▓▓░]", "[░░░▓▓▓░░]",
        "[░░▓▓▓░░░]", "[░▓▓▓░░░░]",
    ],
    # buffering: dot grows in the middle, then shrinks
    "buffering": [
        "[░░▓░░]", "[░▓▓▓░]", "[▓▓▓▓▓]", "[▓▓▓▓▓]",
        "[░▓▓▓░]", "[░░▓░░]", "[░░░░░]",
    ],
    # signal: 4 vertical bars filling up — cell tower / wifi
    "signal": [
        "▁   ", "▁▂  ", "▁▂▃ ", "▁▂▃▄",
        "▁▂▃ ", "▁▂  ", "▁   ", "    ",
    ],

    # --- Semantic / situational ----------------------------------------
    # heartbeat: ECG blip on a flat line — health-check, keepalive
    "heartbeat": [
        "─────────", "──── ────", "───▁ ────", "──▁▃ ────",
        "─▁▃█▃▁───", "──▁▃ ────", "───▁ ────", "─────────",
        "─────────", "─────────",
    ],
    # searching: magnifier sweeping right then resetting
    "searching": [
        "🔍       ", " 🔍      ", "  🔍     ", "   🔍    ",
        "    🔍   ", "     🔍  ", "      🔍 ", "       🔍",
    ],
    # atom: 3 electrons orbiting a nucleus (visual: which one is "lit")
    "atom": [
        "●○○○", "○●○○", "○○●○", "○○○●",
        "○○●○", "○●○○",
    ],
    # spiral: arm of a galaxy building up, then collapsing
    "spiral": [
        "╲    ", "╲╲   ", "╲╲╲  ", "╲╲╲╲ ", "╲╲╲╲╲",
        " ╲╲╲╲", "  ╲╲╲", "   ╲╲", "    ╲", "     ",
    ],

    # --- One-shot outro frames (intended for animate-once contexts) ---
    # success-flash: ✓ flash that fades to clean
    "success-flash": [
        "  ✓  ", " ✓✓✓ ", "✓✓✓✓✓", " ✓✓✓ ", "  ✓  ", "     ",
    ],
    # error-pulse: ✗ pulsing — failure rhythm (distinct from spinner)
    "error-pulse": [
        "  ✗  ", " ✗✗✗ ", "✗✗✗✗✗", " ✗✗✗ ", "  ✗  ", "  ·  ",
    ],
    # retry-slow: long quiet braille pulse — "I'm trying again, patience"
    "retry-slow": [
        "⠁  ", " ⠂ ", "  ⠄", "  ⠠", " ⠐ ", "⠈  ",
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

    # Gradient boundary — soft transition from fill to empty instead of a
    # hard cut. ``edge`` chars render at the boundary cell, in order.
    "gradient-edge": {"fill": "█", "empty": "░", "edge": "▓▒"},
    # Discrete cells with separators between every cell.
    "tape":          {"fill": "▰", "empty": "░", "separator": "│"},
}

DEFAULT_BAR_STYLE = "ascii"


SPINNER_FAMILIES: dict[str, list[str]] = {
    "classic":      ["dots", "dots2", "line", "arc", "pulse", "bouncing", "clock"],
    "codechu":      ["codechu", "codechu-fade"],
    "blocks":       ["blocks-bounce", "blocks-fill", "blocks-snake",
                     "blocks-pulse", "blocks-fill-solid"],
    "compact":      ["dots3", "wave3", "tri3", "arrow3",
                     "toggle", "toggle-sq", "toggle-rd"],
    "grow":         ["grow-h", "grow-v"],
    "pictographic": ["earth", "moon"],
    "modern":       ["comet", "wave", "pulse-radial", "equalizer", "ripple",
                     "orbit-quad", "shimmer", "glitch", "double-bounce"],
    "chaos":        ["static", "storm", "sparks", "fireworks",
                     "electricity", "maelstrom", "build-up"],
    "random-access": ["scatter", "multi-seek", "disk-thrash", "hash-spray",
                      "rand-walk", "gather"],
    "matrix":       ["matrix", "matrix-rain", "matrix-drop", "matrix-trail"],
    "quadrant":     ["quad-random", "quad-twinkle", "quad-pulse",
                     "quad-rain", "quad-cross"],
    "conveyor":     ["conveyor", "conveyor-fast", "conveyor-mixed", "pipeline"],
    "iconic":       ["pacman", "pacman-reverse",
                     "game-of-life", "life-glider", "life-blinker"],
    "loading":      ["bar", "buffering", "signal"],
    "semantic":     ["heartbeat", "searching", "atom", "spiral"],
    "outro":        ["success-flash", "error-pulse", "retry-slow"],
}

STYLE_TAGS: dict[str, set[str]] = {
    # mood tags — pick semantic intent
    "calm":    {"dots3", "moon", "codechu-fade", "pulse-radial",
                "life-glider", "life-blinker", "grow-h", "grow-v", "arc",
                "heartbeat", "retry-slow", "signal"},
    "busy":    {"wave", "equalizer", "blocks-snake", "blocks-fill",
                "conveyor", "conveyor-fast", "comet", "ripple",
                "bar", "buffering", "searching"},
    "chaotic": {"static", "storm", "sparks", "fireworks",
                "electricity", "maelstrom", "glitch", "quad-random"},
    "playful": {"pacman", "pacman-reverse", "earth", "moon", "clock",
                "atom", "spiral"},
    "minimal": {"toggle", "toggle-sq", "toggle-rd", "dots3",
                "tri3", "orbit-quad", "life-glider"},
    "narrow":  {"toggle", "toggle-sq", "toggle-rd", "dots", "dots2",
                "line", "arc", "pulse", "grow-h", "grow-v",
                "matrix", "matrix-drop", "matrix-trail",
                "earth", "moon", "clock",
                "signal", "atom", "success-flash", "error-pulse",
                "retry-slow"},  # 1-cell wide
    "wide":    {"matrix-rain", "conveyor-mixed", "pipeline",
                "blocks-fill-solid", "multi-seek", "disk-thrash",
                "bar", "buffering", "heartbeat", "searching",
                "spiral"},  # 6+ cells
    "outro":   {"success-flash", "error-pulse"},
    "network": {"signal", "bar", "retry-slow"},
}

STYLE_COMPATIBILITY: dict[str, set[str]] = {
    # Guaranteed to render anywhere — ASCII-only or universal blocks
    "ascii-safe": {"line", "dots3", "ascii", "equals", "pipe"},

    # Modern terminal with monospace Unicode font (JetBrains, Cascadia,
    # DejaVu, Fira). Default tier — most styles fall here. Filled below.
    "modern": set(),

    # Needs emoji-presentation support; degrades to tofu/misalign on
    # legacy terminals
    "needs-emoji": {"clock", "earth", "moon", "electricity",
                    "sparks", "fireworks"},

    # Needs CJK font fallback for half-width katakana
    "needs-cjk": {"matrix", "matrix-rain"},

    # Bar styles
    "ascii-safe-bar": {"ascii", "equals", "pipe"},
}

# Populate the "modern" tier — every spinner not already covered by
# ascii-safe / needs-emoji / needs-cjk.
STYLE_COMPATIBILITY["modern"] = (
    set(SPINNER_STYLES)
    - STYLE_COMPATIBILITY["needs-emoji"]
    - STYLE_COMPATIBILITY["needs-cjk"]
    - STYLE_COMPATIBILITY["ascii-safe"]
)


def register_spinner_style(
    name: str,
    frames: list[str],
    *,
    family: str | None = None,
    tags: set[str] | None = None,
    compatibility: str = "modern",
) -> None:
    """Register a custom spinner style at runtime.

    ``family`` adds the name to ``SPINNER_FAMILIES[family]`` (creating
    the family if missing). ``tags`` adds the name to each
    ``STYLE_TAGS[tag]`` set. ``compatibility`` adds to
    ``STYLE_COMPATIBILITY[compatibility]``.
    """
    if not frames:
        raise ValueError("frames cannot be empty")
    SPINNER_STYLES[name] = list(frames)
    if family:
        SPINNER_FAMILIES.setdefault(family, []).append(name)
    if tags:
        for tag in tags:
            STYLE_TAGS.setdefault(tag, set()).add(name)
    STYLE_COMPATIBILITY.setdefault(compatibility, set()).add(name)


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


# Back-compat alias: prior to 0.1.0 the inline ``_fmt_duration`` helper
# was used directly; route through :func:`timing.format_duration`.
_fmt_duration = format_duration


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
        total: int | None = None,
        *,
        stream: IO[str] | None = None,
        width: int | None = None,
        style: str | None = None,
        fill: str | None = None,
        empty: str | None = None,
        smooth: bool | None = None,
        template: str | None = None,
        enabled: bool | None = None,
        spinner_style: str | None = None,
        units: str | None = None,
        reverse: bool = False,
    ) -> None:
        self._stream = stream if stream is not None else sys.stderr
        # total=None (or non-positive) → indeterminate mode
        if total is None or int(total) <= 0:
            self.total = 0
            self._indeterminate = True
        else:
            self.total = int(total)
            self._indeterminate = False
        self.current = 0
        if style is not None and style not in BAR_STYLES:
            raise KeyError(
                f"unknown bar style {style!r}. "
                f"Available: {sorted(BAR_STYLES)}"
            )
        preset = BAR_STYLES[style if style is not None else DEFAULT_BAR_STYLE]
        self.fill = fill if fill is not None else preset.get("fill", "#")
        self.empty = empty if empty is not None else preset.get("empty", "-")
        self.edge = preset.get("edge")
        self.separator = preset.get("separator")
        resolved_width = width if width is not None else preset.get("width", 40)
        # Allow narrow fixed-block presets (5–8 cells); only floor if the
        # caller passed something nonsensical with the default ascii preset.
        self.width = max(1, int(resolved_width))
        self.smooth = bool(smooth if smooth is not None else preset.get("smooth", False))
        self.template = template if template is not None else self.DEFAULT_TEMPLATE
        self.reverse = bool(reverse)
        self.units = units
        if spinner_style is not None and spinner_style not in SPINNER_STYLES:
            raise KeyError(
                f"unknown spinner style {spinner_style!r}. "
                f"Available: {sorted(SPINNER_STYLES)}"
            )
        # Default to "dots" for {spinner} field when no explicit style.
        self._spinner_style = spinner_style if spinner_style is not None else "dots"
        self._spinner_idx = 0
        self._indeterm_idx = 0
        if enabled is None:
            enabled = _stream_is_tty(self._stream)
        self.enabled = enabled
        self._line = ProgressLine(self._stream, enabled=self.enabled)
        self._t_start = time.monotonic()
        self._last_advance = time.monotonic()
        self._rate = RateEstimator(window_seconds=1.0)

    def set_total(self, n: int) -> None:
        self.total = max(0, int(n))
        self._indeterminate = self.total <= 0
        self._render(label="")

    def advance(self, n: int = 1, label: str = "") -> None:
        if self._indeterminate:
            # Animation tick only — still update current for accounting.
            self.current += n
            self._indeterm_idx += 1
        else:
            self.current = (
                min(self.total, self.current + n) if self.total else self.current + n
            )
        if n:
            self._rate.observe(n)
        self._last_advance = time.monotonic()
        self._render(label=label)

    def refresh(self, label: str = "") -> None:
        """Re-render the current state without advancing.

        For long-idle bars, call this periodically so the auto-paused
        pulse animation activates (after 2 s of inactivity).
        """
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

    def _render_cells(self, ratio: float) -> str:
        """Determinate-mode bar body: fill/empty cells with optional
        gradient ``edge`` and ``separator``."""
        filled = int(round(ratio * self.width))
        filled = max(0, min(self.width, filled))
        if self.smooth:
            return self._render_smooth(ratio)
        cells: list[str] = [self.fill] * filled + [self.empty] * (self.width - filled)
        # Apply edge gradient: replace cells just past the fill boundary
        # with progressively-fainter ``edge`` chars.
        if self.edge and 0 < filled < self.width:
            for i, ch in enumerate(self.edge):
                pos = filled + i
                if pos >= self.width:
                    break
                cells[pos] = ch
        if self.reverse:
            cells = list(reversed(cells))
        if self.separator:
            return self.separator.join(cells)
        return "".join(cells)

    def _indeterminate_body(self) -> str:
        """Sliding pattern from the ``bar`` spinner style."""
        frames = SPINNER_STYLES["bar"]
        return frames[self._indeterm_idx % len(frames)]

    def _paused_body(self) -> str:
        """Pulse animation for long-idle bars."""
        frames = SPINNER_STYLES["blocks-pulse"]
        # Fit width by repeating/truncating
        f = frames[self._indeterm_idx % len(frames)]
        if len(f) >= self.width:
            return f[: self.width]
        return (f * ((self.width // len(f)) + 1))[: self.width]

    def _render(self, *, label: str) -> None:
        if not self.enabled:
            return
        now = time.monotonic()
        elapsed = now - self._t_start
        idle = now - self._last_advance
        # Indeterminate body
        if self._indeterminate:
            bar_str = self._indeterminate_body()
            pct_str = "--"
            eta_str = "?"
            remaining_str = "?"
            ratio = 0.0
        elif idle > 2.0:
            # Auto-paused: replace bar with pulse, keep counters.
            self._indeterm_idx += 1
            bar_str = self._paused_body()
            total = self.total or 1
            ratio = min(1.0, self.current / total) if total else 0.0
            pct_str = str(int(round(ratio * 100)))
            if self.total > 0 and self.current > 0:
                eta_s = elapsed * (self.total - self.current) / self.current
                eta_str = format_duration(max(0.0, eta_s))
            else:
                eta_str = "?"
            remaining_str = str(max(0, self.total - self.current))
        else:
            total = self.total or 1
            ratio = min(1.0, self.current / total) if total else 0.0
            bar_str = self._render_cells(ratio)
            pct_str = str(int(round(ratio * 100)))
            if self.total > 0 and self.current > 0:
                eta_s = elapsed * (self.total - self.current) / self.current
                eta_str = format_duration(max(0.0, eta_s))
            else:
                eta_str = "?"
            remaining_str = str(max(0, self.total - self.current))

        # {spinner} frame
        spin_frames = SPINNER_STYLES[self._spinner_style]
        spinner_str = spin_frames[self._spinner_idx % len(spin_frames)]
        self._spinner_idx += 1

        # {rate}
        if self._indeterminate or elapsed < 0.5 or self._rate.rate() <= 0:
            rate_str = "?"
        else:
            rate_str = format_rate(
                self._rate.rate(), unit=self.units if self.units else "items"
            )

        msg = self.template.format(
            bar=bar_str,
            pct=pct_str,
            current=self.current,
            total=self.total,
            label=label,
            elapsed=format_duration(elapsed),
            eta=eta_str,
            spinner=spinner_str,
            remaining=remaining_str,
            rate=rate_str,
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
    "SPINNER_FAMILIES",
    "SPINNER_STYLES",
    "STYLE_COMPATIBILITY",
    "STYLE_TAGS",
    "Spinner",
    "register_bar_style",
    "register_spinner_style",
]


# Keep ``time`` referenced so tests can ``monkeypatch.setattr(progress, 'time', fake)``.
_ = time
