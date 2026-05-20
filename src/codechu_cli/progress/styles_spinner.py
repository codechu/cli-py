"""Spinner style registry — frames, families, tags, compatibility."""

from __future__ import annotations

SPINNER_STYLES: dict[str, list[str]] = {
    # Industry classics (names match cli-spinners' canon where applicable):
    "dots":     ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    "dots2":    ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"],
    "line":     ["|", "/", "-", "\\"],
    "arc":      ["◜", "◠", "◝", "◞", "◡", "◟"],
    "bouncing": ["⠁", "⠂", "⠄", "⠂"],
    "pulse":    ["•", "◦", " ", "◦"],
    "clock":    ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕",
                 "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"],

    # Codechu signature
    "codechu":      ["◐", "◓", "◑", "◒"],
    "codechu-fade": ["▒", "▓", "█", "▓"],

    # 5-cell block patterns
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

    # 3-cell patterns
    "dots3":   [".  ", ".. ", "...", " ..", "  .", "   "],
    "wave3":   ["▁  ", "▂▁ ", "▃▂▁", "▄▃▂", "▃▄▃", "▂▃▄", "▁▂▃", " ▁▂", "  ▁"],
    "tri3":    ["◐◯◯", "◯◐◯", "◯◯◐", "◯◐◯"],

    # Single-cell grow/shrink
    "grow-h":  ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█",
                "▉", "▊", "▋", "▌", "▍", "▎"],
    "grow-v":  ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█",
                "▇", "▆", "▅", "▄", "▃", "▂"],

    # Arrows + toggles
    "arrow3":     ["▸▹▹▹▹", "▹▸▹▹▹", "▹▹▸▹▹", "▹▹▹▸▹", "▹▹▹▹▸"],
    "toggle":     ["■", "□"],
    "toggle-sq":  ["▪", "▫"],
    "toggle-rd":  ["⊙", "⊚"],

    # Pictographic
    "earth":   ["🌍", "🌎", "🌏"],
    "moon":    ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"],

    # Modern
    "comet": [
        "█▓▒░    ", " █▓▒░   ", "  █▓▒░  ", "   █▓▒░ ",
        "    █▓▒░", "░    █▓▒", "▒░    █▓", "▓▒░    █",
    ],
    "wave": [
        "▂▃▅▆▇█▇▆", "▃▅▆▇█▇▆▅", "▅▆▇█▇▆▅▃", "▆▇█▇▆▅▃▂",
        "▇█▇▆▅▃▂▁", "█▇▆▅▃▂▁▂", "▇▆▅▃▂▁▂▃", "▆▅▃▂▁▂▃▅",
    ],
    "pulse-radial": [
        "   █   ", "  ▓█▓  ", " ▒▓█▓▒ ", "░▒▓█▓▒░",
        " ▒▓█▓▒ ", "  ▓█▓  ",
    ],
    "equalizer": [
        "▁▃▅▇", "▃▅▇█", "▅▇█▇", "▇█▇▅",
        "█▇▅▃", "▇▅▃▁", "▅▃▁▃", "▃▁▃▅",
    ],
    "ripple": [
        "█       ", "▓█      ", "▒▓█     ", "░▒▓█    ",
        " ░▒▓█   ", "  ░▒▓█  ", "   ░▒▓█ ", "    ░▒▓█",
    ],
    "orbit-quad": ["◜◝", "◝◞", "◞◟", "◟◜"],
    "shimmer": [
        "·  ✦   ", " ✦   · ", "  · ✦  ", "✦   ·  ",
        "  ✦   ·", "· ✦    ",
    ],
    "glitch": [
        "▒▓█▓▒", "▓█▒░█", "▒▓░█▒", "█▒▓░▓",
        "▓▒█▓░", "░▓▒█▓",
    ],
    "double-bounce": [
        "●○○○○○○○", "○●○○○○○●", "○○●○○○●○", "○○○●○●○○",
        "○○○○●○○○", "○○○●○●○○", "○○●○○○●○", "○●○○○○○●",
    ],

    # Chaos
    "static": [
        "░▒▓▒░▓▒░", "▓░▒▓░▒░▓", "▒▓░▒▓░▓▒",
        "░▓▒░▓▒▓░", "▓▒░▒▓░▒▓", "▒░▓▒░▓▒░",
    ],
    "storm": [
        "╱  ·  ╲ ", " ·╱  ╲  ", "╲  ·╱  ·", "·  ╲ ·  ",
        " ╱·  ╲ ·", "╲ · ╱   ", "  ╱ ·  ╲", "· ╲  ╱· ",
    ],
    "sparks": [
        "· ✦   ·  ", "✦  · ✦  ·", "  ✦·   ✦ ", "· ✦  ✦  ·",
        "✦   · ✦  ", " ✦ ·   ✦·", "·  ✦ ·  ✦", " ·✦  ·✦  ",
    ],
    "fireworks": [
        "         ", "    ·    ", "   ·✦·   ", "  ✶✦✶    ",
        " ·✶✦✶·   ", "  ·✦·    ", "         ", "  ·      ",
    ],
    "electricity": [
        "⚡       ", "   ⚡    ", "        ", "⚡  ⚡   ",
        "      ⚡ ", "        ", " ⚡   ⚡ ", "    ⚡   ",
    ],
    "maelstrom": [
        "╲╱╲╱╲╱", "╱╲╱╲╱╲", "╲╱╲╲╱╱", "╱╱╲╲╱╲",
        "╲╲╱╱╲╱", "╱╲╲╱╲╱", "╲╱╱╲╲╱", "╱╲╱╲╲╱",
    ],
    "build-up": [
        "·       ", "··      ", "···     ", "·· ·    ",
        "·· ··   ", "·✦ ·· · ", "·✦·✦·✦·✦", "·  ✦  · ",
        "        ", "   ·    ",
    ],

    # Random-access
    "scatter": [
        "●       ", "      ●  ", "  ●      ", "        ●",
        "   ●     ", " ●       ", "       ● ", "    ●    ",
    ],
    "multi-seek": [
        "●  ●     ", "     ● ● ", "  ●   ●  ", "●     ●  ",
        " ● ● ●   ", "   ●  ● ●", "● ●    ● ", " ●  ●  ● ",
    ],
    "disk-thrash": [
        "━━       ", "     ━━━ ", " ━━      ", "      ━━━",
        "━     ━━ ", "   ━━━  ━", "━━     ━━", " ━━━ ━   ",
    ],
    "hash-spray": [
        "·  ·  · ", "    ·   ", "  ·    ·", "·       ",
        "   ·  · ", "·    ·  ", " ·    · ", "  ·  ·  ",
    ],
    "rand-walk": [
        "  ●   ", "   ●  ", "  ●   ", " ●    ",
        "  ●   ", "   ●  ", "    ● ", "   ●  ",
        "  ●   ", " ●    ",
    ],
    "gather": [
        "●     ●●", " ●   ●● ", "  ● ●●  ", "  ●●●   ",
        "   ●●   ", "  ● ●   ", " ●   ●  ", "●     ●●",
    ],

    # Matrix
    "matrix": [
        "ﾊ", "ﾐ", "ﾑ", "ﾒ", "ﾓ", "ｦ", "ｱ", "ｲ", "ｳ", "ｴ",
        "ｵ", "ﾅ", "ﾆ", "ﾇ", "ﾈ", "ﾉ", "0", "1", "Z", "ﾄ",
    ],
    "matrix-rain": [
        "ﾊ ｱ 1 ﾐ", "ﾐ ﾊ 0 ｴ", "ｱ ﾐ 1 ﾄ", "ｴ ﾊ 0 ﾅ",
        "ﾆ ｱ 1 ﾐ", "ﾅ ﾐ 0 ﾊ", "ﾄ ﾆ 1 ｴ", "ｦ ﾅ 0 ｱ",
        "ｲ ﾄ 1 ﾆ", "ﾐ ｦ 0 ﾅ",
    ],
    "matrix-drop": [
        "▔", "▀", "█", "▄", "▁", " ",
    ],
    "matrix-trail": [
        "▔", "▀", "█", "▆", "▄", "▂", "▁", " ",
    ],

    # Quadrant
    "quad-random": [
        "▘▗▖▝", "▟▙▛▜", "▖▘▗▝", "▞▀▄▚",
        "▝▖▘▗", "▛▜▟▙", "▖▝▘▗", "▚▞▀▄",
        "▌▐▝▘", "▟▖▞▛", "▀▙▚▗", "▐▌▜▝",
    ],
    "quad-twinkle": [
        "▘     ", "  ▝   ", "    ▗ ", " ▖    ",
        "   ▖  ", "▝   ▗ ", "  ▘ ▗ ", "▖   ▝ ",
        "   ▘  ", "▗  ▖  ",
    ],
    "quad-pulse": [
        "    ", "▘▝▖▗", "▙▚▞▟", "████",
        "▙▚▞▟", "▘▝▖▗", "    ", "    ",
    ],
    "quad-rain": [
        "▀  ▀ ", "█  █▀", "▄  █ ", " ▀ ▄ ",
        "▀█   ", "▄█ ▀ ", " ▄ █ ", "  ▄▄ ",
        "▀ ▀  ", "█▀█  ",
    ],
    "quad-cross": [
        "▚▞▚▞", "▞▚▞▚", "▚▚▞▞", "▞▞▚▚",
        "█▚▞ ", " ▞▚█", "▚█ ▞", "▞ █▚",
    ],

    # Conveyor
    "conveyor": [
        "▓░  ▓░  ", " ▓░  ▓░ ", "  ▓░  ▓░", "░  ▓░  ▓",
    ],
    "conveyor-fast": [
        "▓░▓░▓░▓░", "░▓░▓░▓░▓",
    ],
    "conveyor-mixed": [
        "━ ━━  ━ ", " ━ ━━  ━", "━ ━ ━━  ", " ━ ━ ━━ ",
        "  ━ ━ ━━", "━  ━ ━ ━", "━━  ━ ━ ", " ━━  ━ ━",
    ],
    "pipeline": [
        "[ ]  [ ] ", " [ ]  [ ]", "[]  [ ]  ", " []  [ ] ",
        "  []  [ ]", "   []  []", " ]  []  [", "  ]  []  ",
    ],

    # Pacman / Game of Life
    "pacman": [
        "C • • • •", "O • • • •", " c• • • •", " C • • • •",
        "  o• • •",  "  C • • •", "   c• •",   "   C • •",
        "    o•",    "    C •",   "     c",    "     C",
    ],
    "pacman-reverse": [
        "• • • • C", "• • • • O", "• • • •c ", "• • • •C ",
        "• • • o  ", "• • • C  ", "• • o    ", "• • C    ",
        "• o      ", "• C      ", "o        ", "C        ",
    ],
    "game-of-life": [
        "▘   ▝   ", " ▘▖    ▗", "  ▝▘    ", "▝ ▗  ▘ ▝",
        "  ▖▝▘▗  ", " ▘▝▖▘   ", "▝ ▘▘ ▝▖ ", "▖   ▘ ▝▘",
        "  ▖  ▝▗ ", "▘▝▖ ▘   ",
    ],
    "life-glider": [
        "▘     ", " ▖    ", "  ▝   ", "   ▖  ", "    ▝ ",
        "     ▖", "▝     ", " ▖    ",
    ],
    "life-blinker": [
        "▄▄▄ ", "    ", " ▌  ", "    ", "▄▄▄ ", "    ",
    ],

    # Loading
    "bar": [
        "[▓▓▓░░░░░]", "[░▓▓▓░░░░]", "[░░▓▓▓░░░]", "[░░░▓▓▓░░]",
        "[░░░░▓▓▓░]", "[░░░░░▓▓▓]", "[░░░░▓▓▓░]", "[░░░▓▓▓░░]",
        "[░░▓▓▓░░░]", "[░▓▓▓░░░░]",
    ],
    "buffering": [
        "[░░▓░░]", "[░▓▓▓░]", "[▓▓▓▓▓]", "[▓▓▓▓▓]",
        "[░▓▓▓░]", "[░░▓░░]", "[░░░░░]",
    ],
    "signal": [
        "▁   ", "▁▂  ", "▁▂▃ ", "▁▂▃▄",
        "▁▂▃ ", "▁▂  ", "▁   ", "    ",
    ],

    # Semantic
    "heartbeat": [
        "─────────", "──── ────", "───▁ ────", "──▁▃ ────",
        "─▁▃█▃▁───", "──▁▃ ────", "───▁ ────", "─────────",
        "─────────", "─────────",
    ],
    "searching": [
        "🔍       ", " 🔍      ", "  🔍     ", "   🔍    ",
        "    🔍   ", "     🔍  ", "      🔍 ", "       🔍",
    ],
    "atom": [
        "●○○○", "○●○○", "○○●○", "○○○●",
        "○○●○", "○●○○",
    ],
    "spiral": [
        "╲    ", "╲╲   ", "╲╲╲  ", "╲╲╲╲ ", "╲╲╲╲╲",
        " ╲╲╲╲", "  ╲╲╲", "   ╲╲", "    ╲", "     ",
    ],

    # Outro
    "success-flash": [
        "  ✓  ", " ✓✓✓ ", "✓✓✓✓✓", " ✓✓✓ ", "  ✓  ", "     ",
    ],
    "error-pulse": [
        "  ✗  ", " ✗✗✗ ", "✗✗✗✗✗", " ✗✗✗ ", "  ✗  ", "  ·  ",
    ],
    "retry-slow": [
        "⠁  ", " ⠂ ", "  ⠄", "  ⠠", " ⠐ ", "⠈  ",
    ],
}

DEFAULT_SPINNER_STYLE = "dots"


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
                "retry-slow"},
    "wide":    {"matrix-rain", "conveyor-mixed", "pipeline",
                "blocks-fill-solid", "multi-seek", "disk-thrash",
                "bar", "buffering", "heartbeat", "searching",
                "spiral"},
    "outro":   {"success-flash", "error-pulse"},
    "network": {"signal", "bar", "retry-slow"},
}

STYLE_COMPATIBILITY: dict[str, set[str]] = {
    "ascii-safe": {"line", "dots3", "ascii", "equals", "pipe"},
    "modern": set(),
    "needs-emoji": {"clock", "earth", "moon", "electricity",
                    "sparks", "fireworks"},
    "needs-cjk": {"matrix", "matrix-rain"},
    "ascii-safe-bar": {"ascii", "equals", "pipe"},
}

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
    """Register a custom spinner style at runtime."""
    if not frames:
        raise ValueError("frames cannot be empty")
    SPINNER_STYLES[name] = list(frames)
    if family:
        SPINNER_FAMILIES.setdefault(family, []).append(name)
    if tags:
        for tag in tags:
            STYLE_TAGS.setdefault(tag, set()).add(name)
    STYLE_COMPATIBILITY.setdefault(compatibility, set()).add(name)


__all__ = [
    "DEFAULT_SPINNER_STYLE",
    "SPINNER_FAMILIES",
    "SPINNER_STYLES",
    "STYLE_COMPATIBILITY",
    "STYLE_TAGS",
    "register_spinner_style",
]
