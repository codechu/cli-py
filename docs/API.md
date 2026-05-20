# API Reference — codechu-cli 0.2.0

Complete reference for every public symbol exported from `codechu_cli`.

Importable surface (from `codechu_cli/__init__.py`):

```python
from codechu_cli import (
    # color
    Color,
    # banner
    banner, ascii_banner, LOGOS,
    # format
    resolve_format, format_examples,
    # emoji
    e, capabilities, emoji,          # `emoji` is the submodule itself
    # prompt
    confirm, prompt, select, multiselect,
    # progress
    ProgressLine, ProgressBar, Spinner,
    BAR_STYLES, SPINNER_STYLES, SPINNER_FAMILIES,
    STYLE_TAGS, STYLE_COMPATIBILITY,
    register_bar_style, register_spinner_style,
    # meta
    __version__,
)
```

> **Discipline note.** Only `emoji.capabilities()` reads environment
> variables. Every other helper either auto-detects via
> `stream.isatty()` or takes the answer from its caller (`enabled=`,
> `caps=`). This makes apps deterministic and trivially testable.

---

## Module: `color`

### `class Color`

ANSI palette wrapper with fluent attribute access. Each palette key
becomes a method that wraps text in the matching escape sequence.

```python
Color(
    stream: IO[str],
    *,
    palette: dict[str, str] | None = None,
    enabled: bool | None = None,
)
```

| Param | Type | Default | Description |
|---|---|---|---|
| `stream` | `IO[str]` | — | Output stream. Used only for TTY detection — `Color` does not write to it. |
| `palette` | `dict[str, str] \| None` | `None` | Extra color codes merged onto `DEFAULT_PALETTE`. Later values override defaults. |
| `enabled` | `bool \| None` | `None` | Force colors on/off. `None` → auto-detect via `stream.isatty()`. **Does not read `NO_COLOR`** — the caller is responsible. |

**Class attribute** `Color.DEFAULT_PALETTE`:

| Key | ANSI | Meaning |
|---|---|---|
| `reset` | `\x1b[0m` | Reset all attributes |
| `dim` | `\x1b[2m` | Dim text |
| `bold` | `\x1b[1m` | Bold text |
| `low` | `\x1b[32m` | Green — success / low severity |
| `medium` | `\x1b[33m` | Yellow — warning |
| `high` | `\x1b[31m` | Red — error / high severity |
| `info` | `\x1b[36m` | Cyan — info |

**Instance attribute** `enabled` (read-only via property) — `True` if
colors will be emitted.

#### Fluent attribute access

Every key in the merged palette becomes a callable on the instance via
`__getattr__`:

```python
c = Color(sys.stderr)
c.low("ok")      # → "\x1b[32mok\x1b[0m" if enabled else "ok"
c.high("ERR")    # → "\x1b[31mERR\x1b[0m"
c.bold("title")  # → "\x1b[1mtitle\x1b[0m"
```

**Mechanics**:

- `Color.__getattr__(name)` is only called for missing attributes
  (Python's standard rule).
- Names starting with `_` raise `AttributeError` unconditionally, so
  internal lookups don't get hijacked.
- Names not in the palette raise `AttributeError` with the known keys
  in the message.
- The returned callable has `__name__` / `__qualname__` set to the
  color key, so it shows up sensibly in tracebacks.

#### Extending the palette

```python
c = Color(sys.stderr, palette={
    "snapedge":   "\033[35m",
    "snapstable": "\033[36m",
})
c.snapedge("edge channel")
```

| Returns | Type |
|---|---|
| `Color.<name>(text)` | `str` — text wrapped in the ANSI sequence (or unchanged if `enabled=False` or `name` missing). |

**Raises**: `AttributeError` for unknown palette keys.

---

## Module: `banner`

### `banner(title, version, *, mode=None, stream=None) -> None`

Emit a single-line header to `stream` when (and only when) it is a TTY.

| Param | Type | Default | Description |
|---|---|---|---|
| `title` | `str` | — | App name. |
| `version` | `str` | — | Semver string. |
| `mode` | `str \| None` | `None` | Optional sub-label (e.g. `"dry-run"`). Rendered in dim. |
| `stream` | `IO[str] \| None` | `sys.stderr` | Output stream. Silently no-ops if not a TTY. |

**Returns**: `None`. Exceptions during write are swallowed.

**Example**:

```python
from codechu_cli import banner
banner("disk-cleaner", "1.2.0", mode="dry-run")
# → bold "disk-cleaner 1.2.0"  dim "[dry-run]"
```

### `LOGOS: dict[str, str]`

Registry of pre-built ASCII-art logos.

| Key | Description |
|---|---|
| `codechu` | The Codechu wordmark in fig-style ASCII. |
| `disk` | A small box logo used by `disk-cleaner`. |

### `ascii_banner(art, *, color=None, stream=None, enabled=None) -> None`

Print a multi-line ASCII-art block to `stream`.

| Param | Type | Default | Description |
|---|---|---|---|
| `art` | `str` | — | Multi-line string. Empty → no-op. |
| `color` | `str \| None` | `None` | A color name on `Color`'s palette (e.g. `"info"`). |
| `stream` | `IO[str] \| None` | `sys.stderr` | Output stream. |
| `enabled` | `bool \| None` | `None` | `None` → only when stream is a TTY. `True` forces, `False` suppresses. |

**Example**:

```python
from codechu_cli import LOGOS, ascii_banner
ascii_banner(LOGOS["codechu"], color="info")
```

---

## Module: `format`

### `resolve_format(stream, *, tty_default="table", pipe_default="json") -> str`

Pick a default `--format` value based on whether `stream` is a TTY.

| Param | Type | Default | Description |
|---|---|---|---|
| `stream` | `IO[str]` | — | Usually `sys.stdout`. |
| `tty_default` | `str` | `"table"` | Returned when stream is a TTY. |
| `pipe_default` | `str` | `"json"` | Returned otherwise. |

**Returns**: `str` — one of the two defaults.

**Example**:

```python
import sys
from codechu_cli import resolve_format

parser.add_argument("--format", default=resolve_format(sys.stdout))
```

### `format_examples(examples) -> str`

Format `(command, description)` pairs as an argparse `epilog` block,
aligned on the command column (capped at 60 chars).

| Param | Type | Description |
|---|---|---|
| `examples` | `list[tuple[str, str]]` | `(command, description)` pairs. |

**Returns**: `str` — formatted block beginning with `Examples:` (empty
string if `examples` is empty).

**Example**:

```python
epilog = format_examples([
    ("disk-cleaner scan",        "scan default mounts"),
    ("disk-cleaner scan --json", "machine-readable output"),
])
```

---

## Module: `emoji`

### `capabilities(stream=None) -> set[str]`

Detect terminal capabilities. **This is the only function in the
package that reads environment variables.**

| Param | Type | Default | Description |
|---|---|---|---|
| `stream` | `IO[str] \| None` | `sys.stderr` | Stream to TTY-check. |

**Returns**: `set[str]` containing zero or more of:

| Token | When present |
|---|---|
| `"unicode"` | `LANG` mentions `UTF-8` / `utf8`. |
| `"color"` | `NO_COLOR` absent + stream is a TTY + `TERM` != `"dumb"`. |
| `"emoji"` | `unicode` + TTY + `TERM` != `"dumb"`. `CODECHU_CLI_EMOJI=always` forces on, `never` forces off. |

### `e(name, caps=None, *, fallback=None) -> str`

Look up a glyph by name.

| Param | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Registered glyph key. |
| `caps` | `Iterable[str] \| None` | `None` | Capability tokens (typically the result of `capabilities()`). `None` → ASCII fallback unconditionally. |
| `fallback` | `str \| None` | `None` | Override the registered ASCII form. |

**Returns**: `str` — unicode glyph if `"emoji"` is in `caps`, else the
fallback.

**Raises**: `KeyError` if `name` is not registered.

**Pre-registered glyphs**:

| Name | Unicode | ASCII |
|---|---|---|
| `ok` | `✓` | `+` |
| `fail` | `✗` | `x` |
| `warn` | `⚠` | `!` |
| `info` | `ℹ` | `i` |
| `arrow` | `→` | `->` |
| `bullet` | `•` | `*` |
| `check_on` | `☑` | `[x]` |
| `check_off` | `☐` | `[ ]` |
| `scan` | `🔍` | `search` |
| `trash` | `🗑` | `trash` |
| `broom` | `🧹` | `clean` |
| `disk` | `💾` | `disk` |
| `watch` | `👁` | `watch` |

### `register(name, glyph, fallback) -> None`

Add or override a glyph in the registry.

### `update(mapping) -> None`

Bulk register. `mapping: dict[str, tuple[str, str]]` where each value
is `(unicode, fallback)`.

### `known() -> list[str]`

Return all registered glyph names.

---

## Module: `prompt`

All prompts accept a `caps` parameter that is forwarded to `emoji.e()`
so glyphs match the rest of the app. None of the prompts read
environment variables.

### `confirm(prompt, *, default=False, ...) -> bool`

Yes/no prompt.

| Param | Type | Default | Description |
|---|---|---|---|
| `prompt` | `str` | — | Question text (already in the caller's language). |
| `default` | `bool` | `False` | Returned on empty input, non-TTY, or read failure. |
| `stream` | `IO[str] \| None` | `sys.stderr` | Output stream. |
| `in_stream` | `IO[str] \| None` | `sys.stdin` | Input stream. |
| `assume_yes` | `bool` | `False` | Short-circuit to `True` without prompting. |
| `yes_chars` | `tuple[str, ...]` | `("y", "yes")` | Accepted positive tokens. |
| `no_chars` | `tuple[str, ...]` | `("n", "no")` | Accepted negative tokens. |
| `suffix_format` | `str` | `"[{yes}/{no}]"` | Format for the suffix; uppercases whichever side matches `default`. |
| `translate` | `Callable[[str], str] \| None` | `None` | Wraps library-emitted text (only the suffix). |

**Returns**: `bool`.

### `prompt(message, *, default=None, ...) -> str`

Single-line input.

| Param | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | — | Question. |
| `default` | `str \| None` | `None` | Returned on empty input. Shown as `[default]`. |
| `validate` | `Callable[[str], None] \| None` | `None` | Raises `ValueError` on bad input → re-prompt on TTY, re-raise off-TTY. |
| `password` | `bool` | `False` | Use `getpass.getpass` (no echo). |
| `stream` | `IO[str] \| None` | `sys.stderr` | Output stream. |
| `in_stream` | `IO[str] \| None` | `sys.stdin` | Input stream. |
| `translate` | `Callable[[str], str] \| None` | `None` | Wraps library error text. |
| `caps` | `Iterable[str] \| None` | `None` | Capability set for glyph choice. |

**Returns**: `str`.

### `select(message, choices, *, default=0, ...) -> object`

Arrow-key single-choice picker; numbered-prompt fallback off-TTY.

| Param | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | — | Header line. |
| `choices` | `Sequence[Choice]` | — | Items: plain `str` *or* `(label, value)`. |
| `default` | `int` | `0` | Initial cursor index. Clamped to `[0, len-1]`. |
| `stream` | `IO[str] \| None` | `sys.stderr` | Output stream. |
| `in_stream` | `IO[str] \| None` | `sys.stdin` | Input stream. |
| `keymap` | `dict[str, tuple[str, ...]] \| None` | `None` | Override the default keymap. |
| `translate` | `Callable[[str], str] \| None` | `None` | Translator for hint + fallback labels. |
| `caps` | `Iterable[str] \| None` | `None` | Capability set for glyph choice. |

**Returns**: the second element of the chosen `(label, value)` (or the
label itself for plain strings).

**Raises**: `ValueError` if `choices` is empty.

### `multiselect(message, choices, *, defaults=(), ...) -> list[object]`

Multi-choice picker.

| Param | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | — | Header line. |
| `choices` | `Sequence[Choice]` | — | Items: plain `str` *or* `(label, value)`. |
| `defaults` | `Sequence[int]` | `()` | Pre-selected indices. Out-of-range entries silently dropped. |
| Same `stream`/`in_stream`/`keymap`/`translate`/`caps` as `select`. | | | |

**Returns**: `list` of selected values (in choice order). Empty list if
`choices` is empty.

### `DEFAULT_KEYMAP` (module attribute)

| Action | Default keys |
|---|---|
| `up` | `\x1b[A` (Arrow Up), `k` (vi) |
| `down` | `\x1b[B` (Arrow Down), `j` (vi) |
| `accept` | `\r`, `\n` (Enter) |
| `toggle` | `␣` (Space) — multiselect only |
| `select_all` | `a` — multiselect only |
| `cancel` | `\x1b` (ESC), `q` |

Override per call: `select(..., keymap={"up": ("k",), "down": ("j",)})`.

### `Choice` (type alias)

`Choice = str | tuple[str, object]`

---

## Module: `progress`

### `class ProgressLine`

Bare single-line overwriting output. `ProgressBar` and `Spinner` use it
internally; you only need it directly if you're rendering custom
status text.

```python
ProgressLine(stream: IO[str] | None = None, enabled: bool | None = None)
```

| Param | Type | Default | Description |
|---|---|---|---|
| `stream` | `IO[str] \| None` | `sys.stderr` | Output stream. |
| `enabled` | `bool \| None` | `None` → auto-detect via `stream.isatty()`. | Force on/off. |

**Methods**:

| Method | Behavior |
|---|---|
| `update(msg: str) -> None` | Write `\r{msg}` plus padding to clear any leftover characters from the previous line. No-op when disabled. |
| `clear() -> None` | Erase the current line; reset the recorded width. |

### `class ProgressBar`

Bracketed progress bar with builder API.

```python
ProgressBar(total: int | None = None, *, enabled: bool | None = None)
```

| Param | Type | Default | Description |
|---|---|---|---|
| `total` | `int \| None` | `None` | Total count. `None` or `<= 0` → indeterminate mode (animated sliding bar). |
| `enabled` | `bool \| None` | `None` → auto-detect via stream's TTY. | Force on/off. |

**Class attribute** `ProgressBar.DEFAULT_TEMPLATE`:

```
"[{bar}] {pct}% · {current}/{total} · {label}"
```

#### Builder methods (chainable; each returns `self`)

| Method | Effect |
|---|---|
| `.stream(stream)` | Set output stream (re-creates the internal `ProgressLine` on next render). |
| `.width(n)` | Override bar width (cells). Min 1. |
| `.style(name)` | Apply a preset from `BAR_STYLES`. Raises `KeyError` on unknown name. |
| `.fill(ch)` | Override the fill glyph. |
| `.empty(ch)` | Override the empty glyph. |
| `.smooth(on=True)` | Force subpixel-smooth rendering using `SUBPIXEL` (eighth-blocks). |
| `.template(tmpl)` | Override the format string. Placeholders below. |
| `.reverse(on=True)` | Render right-to-left. |
| `.units(unit)` | Unit label used by `{rate}` (e.g. `"bytes"`). |
| `.spinner_style(name)` | Select the spinner frames used for `{spinner}`. Raises `KeyError` on unknown name. |
| `.with_eta(on=True)` | Append `eta {…}` to default-template output. |
| `.with_rate(on=True)` | Append `rate {…}` to default-template output. |
| `.prefix(text)` | Prepend literal text to every render. |
| `.suffix(text)` | Append literal text to every render. |

#### Template placeholders

| Field | Value |
|---|---|
| `{bar}` | The rendered bar cells. |
| `{pct}` | Integer percent, or `"--"` in indeterminate mode. |
| `{current}` | Current count. |
| `{total}` | Total count. |
| `{label}` | Label passed to `.advance(label=…)`. |
| `{elapsed}` | Compact duration since start (`Xs` or `Xm Ys`). |
| `{eta}` | Estimated remaining time, or `"?"`. |
| `{remaining}` | `total - current` or `"?"`. |
| `{rate}` | Windowed rate (1 s window), or `"?"`. |
| `{spinner}` | Current spinner frame (from `.spinner_style`). |

When using `DEFAULT_TEMPLATE` with no label, the trailing ` · `
separator is stripped automatically.

#### Action methods

| Method | Behavior |
|---|---|
| `set_total(n: int) -> None` | Update total. `<= 0` switches to indeterminate. Triggers a render. |
| `advance(n: int = 1, label: str = "") -> None` | Increment current and re-render. Records a tick for the rate estimator. |
| `refresh(label: str = "") -> None` | Re-render without advancing. Useful when only the label changed. |
| `finish() -> None` | Clear the line. Call after the work is done. |

#### Properties

| Property | Type | Meaning |
|---|---|---|
| `enabled` | `bool` | Resolved on first access; cached. |
| `total` | `int` | Total count (`0` in indeterminate mode). |
| `current` | `int` | Current count. |
| `fill_ch` | `str` | Effective fill (override > style preset). |
| `empty_ch` | `str` | Effective empty. |
| `width_n` | `int` | Effective width. |
| `is_smooth` | `bool` | Effective smooth flag. |

### `class Spinner`

Threaded spinner. **Context manager only** — `__enter__` starts the
thread, `__exit__` stops it and clears the line.

```python
Spinner(
    message: str = "",
    *,
    stream: IO[str] | None = None,
    style: str | None = None,
    frames: tuple[str, ...] | list[str] | None = None,
    interval: float = 0.08,
    enabled: bool | None = None,
    caps: Iterable[str] | None = None,
)
```

| Param | Type | Default | Description |
|---|---|---|---|
| `message` | `str` | `""` | Label rendered next to the frame. |
| `stream` | `IO[str] \| None` | `sys.stderr` | Output stream. |
| `style` | `str \| None` | `None` | Name in `SPINNER_STYLES`. Raises `KeyError` if unknown. |
| `frames` | `tuple[str, ...] \| list[str] \| None` | `None` | Explicit frames. Wins over `style`. |
| `interval` | `float` | `0.08` | Seconds between frames. Floored to `0.01`. |
| `enabled` | `bool \| None` | `None` → auto-detect via TTY. | Force on/off. When disabled, the context manager is a no-op. |
| `caps` | `Iterable[str] \| None` | `None` | Used only when neither `style` nor `frames` is set: chooses braille vs ASCII fallback frames. |

**Frame defaults** (when both `style` and `frames` are omitted):
- `"unicode"` in `caps` → braille frames (`⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏`).
- otherwise → ASCII (`|/-\\`).

**Context manager protocol**:

| Phase | Action |
|---|---|
| `__enter__` | Spawn a daemon thread that overwrites the line with the current frame every `interval` seconds. Returns `self`. |
| `__exit__` | Signal stop, join (≤ 1 s), clear the line. **Does not** suppress exceptions raised inside the `with` block. |

**Example**:

```python
from codechu_cli import Spinner
with Spinner("Scanning…", style="dots"):
    walk_filesystem()
```

### Style registries (module attributes)

#### `BAR_STYLES`

| Style | Family / mood | Glyphs |
|---|---|---|
| `ascii` | classic, ascii-safe | `#-` |
| `equals` | classic, ascii-safe | `=-` |
| `block` | classic | `█░` |
| `slim` | classic | `━─` |
| `dots` | classic | `●○` |
| `arrow` | classic | `▶ ` |
| `pipe` | classic, ascii-safe | `\| ` |
| `codechu` | signature | `▰▱` |
| `codechu-gradient` | signature | `▓░` |
| `blocks` | fixed-block (width=5) | `▰▱` |
| `blocks-wide` | fixed-block (width=8) | `▰▱` |
| `blocks-fat` | fixed-block (width=5) | `█░` |
| `claude` | Claude-style polish (width=10) | `█░` |
| `smooth` | subpixel (width=10) | `█ ` + eighths |
| `smooth-wide` | subpixel (width=20) | `█ ` + eighths |
| `gradient-edge` | gradient (edge=`▓▒`) | `█░` |
| `tape` | separator (`\|`) | `▰░` |

Each preset is a dict with these recognized keys: `fill`, `empty`,
`edge`, `separator`, `width` (default 40), `smooth` (default `False`).

#### `SUBPIXEL`

The eighth-block ramp string used by smooth rendering:
`" ▏▎▍▌▋▊▉█"` (9 stops, indices 0–8).

#### `SPINNER_STYLES` (65 entries)

Names grouped by `SPINNER_FAMILIES`:

| Family | Members |
|---|---|
| `classic` | `dots`, `dots2`, `line`, `arc`, `pulse`, `bouncing`, `clock` |
| `codechu` | `codechu`, `codechu-fade` |
| `blocks` | `blocks-bounce`, `blocks-fill`, `blocks-snake`, `blocks-pulse`, `blocks-fill-solid` |
| `compact` | `dots3`, `wave3`, `tri3`, `arrow3`, `toggle`, `toggle-sq`, `toggle-rd` |
| `grow` | `grow-h`, `grow-v` |
| `pictographic` | `earth`, `moon` |
| `modern` | `comet`, `wave`, `pulse-radial`, `equalizer`, `ripple`, `orbit-quad`, `shimmer`, `glitch`, `double-bounce` |
| `chaos` | `static`, `storm`, `sparks`, `fireworks`, `electricity`, `maelstrom`, `build-up` |
| `random-access` | `scatter`, `multi-seek`, `disk-thrash`, `hash-spray`, `rand-walk`, `gather` |
| `matrix` | `matrix`, `matrix-rain`, `matrix-drop`, `matrix-trail` |
| `quadrant` | `quad-random`, `quad-twinkle`, `quad-pulse`, `quad-rain`, `quad-cross` |
| `conveyor` | `conveyor`, `conveyor-fast`, `conveyor-mixed`, `pipeline` |
| `iconic` | `pacman`, `pacman-reverse`, `game-of-life`, `life-glider`, `life-blinker` |
| `loading` | `bar`, `buffering`, `signal` |
| `semantic` | `heartbeat`, `searching`, `atom`, `spiral` |
| `outro` | `success-flash`, `error-pulse`, `retry-slow` |

Selected styles with sample frames:

| Style | Family | Mood tags | Sample glyphs |
|---|---|---|---|
| `dots` | classic | narrow | `⠋ ⠙ ⠹ ⠸ ⠼ ⠴ ⠦ ⠧ ⠇ ⠏` |
| `dots2` | classic | narrow | `⣾ ⣽ ⣻ ⢿ ⡿ ⣟ ⣯ ⣷` |
| `line` | classic | narrow, ascii-safe | `\| / - \\` |
| `arc` | classic | calm, narrow | `◜ ◠ ◝ ◞ ◡ ◟` |
| `pulse` | classic | narrow | `• ◦ ' ' ◦` |
| `clock` | classic | playful, narrow, needs-emoji | `🕐 🕑 …` |
| `codechu` | codechu | (signature) | `◐ ◓ ◑ ◒` |
| `codechu-fade` | codechu | calm | `▒ ▓ █ ▓` |
| `blocks-fill` | blocks | busy | `▱▱▱▱▱ → ▰▰▰▰▰` |
| `blocks-snake` | blocks | busy | fill + drain, 10 frames |
| `blocks-pulse` | blocks | — | `▱▱▱▱▱ ↔ ▰▰▰▰▰` |
| `dots3` | compact | calm, minimal, narrow | `.   ..  ...` |
| `toggle` | compact | minimal, narrow | `■ □` |
| `grow-h` | grow | calm, narrow | `▏▎▍▌▋▊▉█` |
| `earth` | pictographic | playful, narrow, needs-emoji | `🌍 🌎 🌏` |
| `moon` | pictographic | calm, playful, narrow, needs-emoji | `🌑 🌒 …` |
| `comet` | modern | busy | trailing `█▓▒░` block |
| `wave` | modern | busy | `▂▃▅▆▇█▇▆` |
| `equalizer` | modern | busy | `▁▃▅▇` rotation |
| `static` | chaos | chaotic | `░▒▓` shuffles |
| `electricity` | chaos | chaotic, needs-emoji | `⚡` shuffles |
| `matrix-rain` | matrix | needs-cjk, wide | Katakana columns |
| `pacman` | iconic | playful | `C • • • •` chomp |
| `heartbeat` | semantic | calm, wide | `─▁▃█▃▁─` |
| `searching` | semantic | busy, wide, needs-emoji | `🔍` sweep |
| `success-flash` | outro | outro, narrow | `✓✓✓✓✓` flash |
| `error-pulse` | outro | outro, narrow | `✗✗✗✗✗` pulse |

`DEFAULT_SPINNER_STYLE = "dots"`. `DEFAULT_BAR_STYLE = "ascii"`.

#### `STYLE_TAGS`

Mood-/shape-based tags. Each tag maps to a `set[str]` of style names.

| Tag | Intended use |
|---|---|
| `calm` | Slow, soft pulses. Long-running ambient tasks. |
| `busy` | High motion. Active work. |
| `chaotic` | Glitch / noise aesthetics. Stress / fail states. |
| `playful` | Iconic, fun glyphs (pacman, earth, moon). |
| `minimal` | Two-state toggles / tiny dot patterns. |
| `narrow` | 1–3 cells wide; safe inline next to a label. |
| `wide` | 6+ cells; needs its own line. |
| `outro` | Closing-state animations. |
| `network` | Connection / signal motifs. |

#### `STYLE_COMPATIBILITY`

| Key | Meaning |
|---|---|
| `ascii-safe` | Renders correctly without unicode. |
| `modern` | Default unicode-capable set. Auto-populated from `SPINNER_STYLES` minus the special-needs sets. |
| `needs-emoji` | Requires emoji-capable terminals (clock, earth, moon, sparks, fireworks, electricity). |
| `needs-cjk` | Requires CJK glyph coverage (`matrix`, `matrix-rain`). |
| `ascii-safe-bar` | ASCII-safe bar styles. |

### `register_spinner_style(name, frames, *, family=None, tags=None, compatibility="modern") -> None`

Add a custom spinner at runtime.

| Param | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Registry key. Overwrites if present. |
| `frames` | `list[str]` | — | Non-empty list. Raises `ValueError` if empty. |
| `family` | `str \| None` | `None` | If set, appended to `SPINNER_FAMILIES[family]`. |
| `tags` | `set[str] \| None` | `None` | Added to each given `STYLE_TAGS` bucket. |
| `compatibility` | `str` | `"modern"` | Bucket in `STYLE_COMPATIBILITY`. |

### `register_bar_style(name, *, fill=None, empty=None, width=None, smooth=False) -> None`

Add a custom bar style at runtime.

| Param | Type | Default | Description |
|---|---|---|---|
| `name` | `str` | — | Registry key. |
| `fill` | `str \| None` | `None` | Fill glyph. |
| `empty` | `str \| None` | `None` | Empty glyph. |
| `width` | `int \| None` | `None` | Baked-in width (else 40). |
| `smooth` | `bool` | `False` | Use subpixel rendering. |

---

## Module: `_term` (internal)

The underscore prefix marks `_term` as **private**: it is not in the
package's public re-exports and may change without a deprecation cycle.
It is documented here only because callers occasionally need the same
TTY-detection logic in their own code, and reaching for `_term.is_tty`
is cheaper than re-implementing it.

### `is_tty(stream) -> bool`

Return whether `stream` is a TTY. `None` → `False`; any exception from
`stream.isatty()` is swallowed and returns `False`.

### `capabilities(stream=None) -> dict[str, bool]`

Separate from `emoji.capabilities()`. Returns a dict:

| Key | Meaning |
|---|---|
| `tty` | `is_tty(stream)` |
| `unicode` | `"UTF-8"` / `"utf8"` in `LANG`. |
| `dumb_term` | `TERM == "dumb"`. |

If you need the public capability set (color, emoji), use
`codechu_cli.emoji.capabilities` instead — that's the supported API.

---

## Module attribute: `__version__`

`str` — the package's semver (`"0.2.0"` at time of writing).
