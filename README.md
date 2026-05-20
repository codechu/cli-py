```text
   ┌─[ codechu-cli ]──────────────────────────────────┐
   │ $ deploy --prod                                  │
   │ ⠿ building ......... [██████████▌      ]  68%    │
   │ ? continue? [Y/n] ▏                              │
   └──────────────────────────────────────────────────┘
```

[![PyPI](https://img.shields.io/pypi/v/codechu-cli.svg)](https://pypi.org/project/codechu-cli/)
[![Python](https://img.shields.io/pypi/pyversions/codechu-cli.svg)](https://pypi.org/project/codechu-cli/)
[![CI](https://github.com/codechu/cli-py/actions/workflows/ci.yml/badge.svg)](https://github.com/codechu/cli-py/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> *Colors, progress bars, spinners, prompts — terminal UX in one import.*

# codechu-cli

Stdlib-only CLI primitives for Python — colors, progress bars, spinners,
prompts, emoji helpers — with consistent UX across Codechu tools.

```bash
pip install codechu-cli
```

## Documentation

- [`docs/API.md`](docs/API.md) — complete reference for every public
  symbol (Color, banner, format, emoji, prompt, progress).
- [`docs/MIGRATION.md`](docs/MIGRATION.md) — v0.1 → v0.2 breaking
  changes with before/after code.
- [`docs/RECIPES.md`](docs/RECIPES.md) — eight copy-paste patterns
  (colored messages, spinners, progress with ETA, confirms,
  single/multiselect, mixed flows, custom styles).

## What it gives you

- **`Color`** — ANSI palette with fluent methods (`c.low(...)`, `c.high(...)`)
  and TTY auto-detection (does not read `NO_COLOR`; caller decides)
- **`ProgressLine`** — single-line overwriting stderr progress
- **`ProgressBar`** — bracketed bar with percent + counts
- **`Spinner`** — threaded spinner (braille frames + ASCII fallback)
- **`confirm` / `prompt`** — yes-no + single-line input (with validator + password mode)
- **`select` / `multiselect`** — arrow-key pickers (numbered fallback off-TTY)
- **`banner`** — single-line header (TTY-only)
- **`resolve_format` / `format_examples`** — argparse output-format helpers
- **`emoji.capabilities` / `emoji.e`** — locale + terminal-aware glyph lookup

Pure stdlib. POSIX-first. Linux/macOS for raw-mode pickers; numbered
prompt fallback everywhere else (Windows, CI, pipes).

## Quick examples

### Color + banner

```python
import sys
from codechu_cli import Color, banner

banner("disk-cleaner", "1.2.0", mode="dry-run")

c = Color(sys.stderr)
print(c.low("ok") + " scan complete")
print(c.high("ERR") + " refusing destructive op")
```

### Progress bar

```python
from codechu_cli import ProgressBar

bar = ProgressBar(100).width(30).style("claude").with_eta()
for chunk in stream_chunks():
    process(chunk)
    bar.advance(1, label=chunk.name)
bar.finish()
```

### Spinner

```python
from codechu_cli import Spinner

with Spinner("Scanning…"):
    walk_filesystem()
```

### Styles (ProgressBar + Spinner)

Both `ProgressBar` and `Spinner` accept a named `style=` preset so you
don't have to remember glyphs. Explicit `fill`/`empty`/`frames` still
win — `style` just supplies defaults.

```python
from codechu_cli import ProgressBar, Spinner

# Industry-standard
ProgressBar(100).style("block")    # █░ — npm/cargo
ProgressBar(100).style("ascii")    # #- — GitHub Actions
ProgressBar(100).style("equals")   # =- — Docker

# Codechu signature
ProgressBar(100).style("codechu")  # ▰▱ — matches disk-cleaner UI

# Spinner styles — industry classics
Spinner("…", style="dots")          # ⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏  braille (default)
Spinner("…", style="dots2")         # ⣾⣽⣻⢿⡿⣟⣯⣷  bolder braille
Spinner("…", style="line")          # |/-\  ASCII safe
Spinner("…", style="arc")           # ◜◠◝◞◡◟
Spinner("…", style="pulse")         # • ◦   ◦

# Spinner styles — N-cell block patterns (Claude Code-style)
Spinner("…", style="blocks-bounce") # ▰▱▱▱▱ → ▱▰▱▱▱ → … 5-cell bouncing
Spinner("…", style="blocks-fill")   # ▱▱▱▱▱ → ▰▰▰▰▰  fill cycle
Spinner("…", style="blocks-snake")  # fill + drain (10 frames)
Spinner("…", style="blocks-pulse")  # ▱▱▱▱▱ ↔ ▰▰▰▰▰
Spinner("…", style="arrow3")        # ▸▹▹▹▹ → ▹▸▹▹▹ →  5-cell arrow scan

# Spinner styles — 3-cell variants (fit inline next to a label)
Spinner("…", style="dots3")         # .  → .. → ...
Spinner("…", style="wave3")         # ▁▂▃ vertical wave
Spinner("…", style="tri3")          # ◐◯◯ → ◯◐◯ → ◯◯◐

# Spinner styles — single-cell pulses
Spinner("…", style="grow-h")        # ▏▎▍▌▋▊▉█  horizontal grow (subpixel)
Spinner("…", style="grow-v")        # ▁▂▃▄▅▆▇█  vertical grow
Spinner("…", style="toggle")        # ■ ↔ □
Spinner("…", style="codechu")       # ◐◓◑◒  disk-quarters, Codechu signature
Spinner("…", style="codechu-fade")  # ▒▓█▓  solid pulse

# Pictographic (terminal must support emoji)
Spinner("…", style="earth")         # 🌍🌎🌏
Spinner("…", style="moon")          # 🌑🌒🌓🌔🌕🌖🌗🌘
Spinner("…", style="clock")         # 🕐🕑🕒…

# Fixed small-block (Claude Code-style polish — width baked in)
ProgressBar(100).style("blocks")        # ▰▰▰▱▱   width=5
ProgressBar(100).style("blocks-wide")   # 8 cells
ProgressBar(100).style("claude")        # █░ at width=10

# Subpixel-smooth — narrow bar that still shows fractional progress
ProgressBar(100).style("smooth")        # 10-cell, 80 distinct stops
ProgressBar(100).style("smooth-wide")   # 20-cell, 160 distinct stops

# Full override still works (style provides defaults; .fill()/.empty()/frames override)
ProgressBar(100).style("block").fill("*")
Spinner("…", style="dots", frames=["A", "B", "C"])
```

Fixed-block styles bake their width into the preset (Claude Code-style
polish: 5–10 cells); smooth styles use Unicode eighth-block partial
fills so a 10-cell bar still has 80 distinct steps.

When you don't know the total upfront, prefer `Spinner` over
`ProgressBar` — it signals "work in progress" without misleading
percentages. Reach for `ProgressBar` only when you can count items
honestly.

The full registries are exported as `SPINNER_STYLES` and `BAR_STYLES`
for introspection (e.g. for `--style` help text in a CLI).

### Timing helpers (sibling libraries)

The timing primitives live in three single-responsibility sibling
libraries. Starting with v0.2, `codechu-cli` no longer depends on
them — import directly from the package you need:

- [`codechu-fmt`](https://github.com/codechu/fmt-py) — human-readable
  formatters (`format_duration`, `format_rate`, `format_size`)
- [`codechu-meter`](https://github.com/codechu/meter-py) — measurement
  primitives (`Stopwatch`, `RateEstimator`, `ETAEstimator`)
- [`codechu-spark`](https://github.com/codechu/spark-py) — text
  visualizations (`sparkline`, `bar_chart`, `heatmap`)

```python
from codechu_fmt import format_duration
format_duration(90)                       # → '1m 30s'

from codechu_meter import Stopwatch
with Stopwatch() as sw:
    do_work()
print(sw)                                 # → '1m 30s'

from codechu_spark import sparkline
sparkline([1, 3, 7, 2, 5])                # → '▁▃█▂▅'
```

`ProgressBar`'s `{elapsed}`, `{eta}`, `{rate}`, `{remaining}` template
fields are computed by `ProgressBar` itself (no runtime dep on the
sibling libs).

Indeterminate mode — when you don't know the total upfront:

```python
bar = ProgressBar(None)  # animated sliding bar
for chunk in stream:
    bar.advance()
bar.set_total(known_total)     # switches to normal rendering
```

#### Complete catalog

Spinner families currently shipped:

- `classic` (7), `codechu` (2), `blocks` (5), `compact` (7), `grow` (2),
  `pictographic` (2), `modern` (9), `chaos` (7), `random-access` (6),
  `matrix` (4), `quadrant` (5), `conveyor` (4), `iconic` (5)
- **`loading`** (3) — `bar`, `buffering`, `signal`
- **`semantic`** (4) — `heartbeat`, `searching`, `atom`, `spiral`
- **`outro`** (3) — `success-flash`, `error-pulse`, `retry-slow`

Timing helpers live in sibling libs — see the "Timing helpers
(sibling libraries)" section above.

### Confirm + prompt

```python
from codechu_cli import confirm, prompt

if not confirm("Delete 12 GB of caches?", default=False):
    raise SystemExit(0)

name = prompt("Backup name", default="snapshot-1")

def positive(x: str) -> None:
    if not x.isdigit() or int(x) <= 0:
        raise ValueError("must be a positive integer")

retries = prompt("Retries", default="3", validate=positive)
secret = prompt("Token", password=True)
```

### Single + multi select

```python
from codechu_cli import select, multiselect

mode = select("Cleanup mode", [
    ("Conservative — caches only", "safe"),
    ("Aggressive — also logs",     "aggressive"),
    ("Custom",                     "custom"),
])

targets = multiselect("Pick targets", [
    "~/.cache/pip", "~/.cache/yarn", "~/.cargo/registry",
], defaults=(0, 1))
```

On non-TTY (CI, pipes) both fall back to a numbered-prompt UI — no
extra branching in caller code.

### Output format detection (argparse)

```python
import argparse, sys
from codechu_cli import format_examples, resolve_format

p = argparse.ArgumentParser(
    epilog=format_examples([
        ("disk-cleaner scan",        "scan default mounts"),
        ("disk-cleaner scan --json", "machine-readable output"),
    ]),
    formatter_class=argparse.RawDescriptionHelpFormatter,
)
p.add_argument("--format", default=resolve_format(sys.stdout))
```

### Emoji helpers (explicit-config pattern)

Capability detection is **explicit**. Call `capabilities()` once at
startup — it is the only function in the package that reads
environment variables — and pass the resulting set into every renderer
that needs it. `e()` does not consult the environment on its own.

```python
import sys
from codechu_cli import capabilities, e

caps = capabilities(sys.stderr)  # {"unicode", "color", "emoji"} or subset
print(f"{e('ok', caps)} done")          # "✓ done" or "+ done"
print(f"{e('arrow', caps)} next step")  # "→ next step" or "-> next step"

# Omitting caps is fine — it deterministically yields the ASCII form.
print(e("ok"))   # "+"

# Pipe caps into Spinner / select / multiselect so their glyphs match.
from codechu_cli import Spinner, select
with Spinner("Scanning…", caps=caps):
    pass
select("Pick", ["a", "b"], caps=caps)
```

`CODECHU_CLI_EMOJI=never` forces ASCII, `always` forces unicode — both
are read by `capabilities()`, not by the renderers.

## API reference

| Symbol | Purpose |
|---|---|
| `Color(stream, *, palette=None, enabled=None)` | ANSI palette with fluent methods (`c.low(...)`); TTY auto-detect |
| `banner(title, version, *, mode=None, stream=...)` | TTY-only header |
| `ProgressLine(stream=None, enabled=None)` | `.update()` / `.clear()` |
| `ProgressBar(total, *, enabled=None)` | fluent builder: `.stream() .width() .style() .with_eta() .with_rate() .prefix() .suffix()`, then `.advance() / .set_total() / .finish()` |
| `Spinner(message, *, frames=None, interval=0.08, caps=None)` | context-manager only: `with Spinner(...): ...` |
| `confirm(prompt, *, default, assume_yes, ...)` | yes/no |
| `prompt(message, *, default, validate, password, caps=None, ...)` | single-line input |
| `select(message, choices, *, default=0, caps=None, ...)` | single-choice picker |
| `multiselect(message, choices, *, defaults=(), caps=None, ...)` | multi-choice picker |
| `resolve_format(stream, *, tty_default, pipe_default)` | format chooser |
| `format_examples([(cmd, desc), ...])` | argparse epilog |
| `capabilities(stream=None)` | set of `{"unicode", "color", "emoji"}` (only env-reading helper) |
| `e(name, caps=None, *, fallback=None)` | glyph lookup with ASCII fallback; pass `caps` explicitly |

## Extension points

The library is opinionated about defaults but accepts customization at
every visible surface, so apps don't need to subclass to fit their
brand or locale.

```python
# Custom palette (merged onto defaults)
c = Color(sys.stdout, palette={
    "snapedge":   "\033[35m",
    "snapstable": "\033[36m",
})
print(c.snapedge("edge channel"))

# Force color on/off (override TTY detection)
c = Color(sys.stdout, enabled=True)

# Custom progress bar look
bar = (
    ProgressBar(100)
    .fill("█")
    .empty("░")
    .template("{bar} {pct}% · {elapsed} · ETA {eta}")
)
for _ in range(100):
    bar.advance(label="working…")
bar.finish()

# Turkish confirm
from gettext import gettext as _
confirm("Devam edilsin mi?",
        yes_chars=("e", "evet"),
        no_chars=("h", "hayır"),
        translate=_)

# Register custom emoji
from codechu_cli import emoji
emoji.register("snap", "📦", "snap")
print(emoji.e("snap"))    # 📦 or "snap" depending on capabilities

# vi-only keymap for select
select("Pick branch", branches,
       keymap={"up": ("k",), "down": ("j",)})
```

### Raw ASCII-art banners

`ascii_banner(art, ...)` prints a multi-line ASCII-art string with
optional color. Text-to-art generation (rendering a plain string like
`"DISK"` as multi-line glyph blocks via a font) is out of scope for
this library — that's a typography problem with its own quality
trade-offs. Future plugin libraries under the `codechu-glyph-*`
namespace will own that, depending on `codechu-cli` for the rendering
plumbing.

For now: bring your own art, or pick from the `LOGOS` registry:

```python
from codechu_cli import LOGOS, ascii_banner

ascii_banner(LOGOS["codechu"], color="info")
ascii_banner(my_own_art_string, color="dim")
```

## Internationalization

The library ships English defaults and does **not** bundle gettext / .po
files — that's an application concern. For the handful of strings it
emits autonomously (the select / multiselect hint line, the confirm
suffix, the prompt validator error, the numbered-fallback "Enter your
choice"), inject a translator callable:

```python
from gettext import gettext as _

confirm("Devam edilsin mi?", translate=_)
select("Bir seçin", choices, translate=_)
multiselect("Hedefler", targets, translate=_)
prompt("Yedek adı", validate=v, translate=_)
```

This follows the STANDARDS.md §11 library carve-out: libraries accept a
translator hook rather than shipping their own catalog.

## Discover

With 65 spinner styles, finding the right one is the hard part.

```bash
# Preview every style live
python -m codechu_cli demo

# Filter by family (13 families: classic, chaos, matrix, conveyor, …)
python -m codechu_cli demo --family chaos

# Filter by mood tag (calm, busy, chaotic, playful, minimal, narrow, wide)
python -m codechu_cli demo --tag calm

# Just list everything
python -m codechu_cli list
```

Or programmatically:

```python
from codechu_cli import SPINNER_FAMILIES, STYLE_TAGS, STYLE_COMPATIBILITY

print(SPINNER_FAMILIES["chaos"])
# ['static', 'storm', 'sparks', 'fireworks', 'electricity', 'maelstrom', 'build-up']

# Pick one safe for any terminal
import random
safe = STYLE_COMPATIBILITY["ascii-safe"]
spinner_style = random.choice(list(safe))
```

You can also register your own at runtime:

```python
from codechu_cli import register_spinner_style, register_bar_style

register_spinner_style(
    "my-spin", ["◐", "◓", "◑", "◒"],
    family="codechu", tags={"calm"},
)
register_bar_style("my-bar", fill="▰", empty="▱", width=10)
```

## Stability

Style names (the keys in `SPINNER_STYLES`, `BAR_STYLES`) are part of the
**public API**. Adding new names is non-breaking; removing or renaming
requires a deprecation cycle (warn for one minor version, then remove
on the next). Family names and tag names follow the same rule.

## Codechu family

Companion libraries from the Codechu Python ecosystem:

| Library | Purpose |
|---------|---------|
| [codechu-fmt](https://pypi.org/project/codechu-fmt/) | Human-readable formatting — sizes, durations, rates, percent |
| [codechu-meter](https://pypi.org/project/codechu-meter/) | Timing primitives — Stopwatch, ETA, percentile, histogram |
| [codechu-spark](https://pypi.org/project/codechu-spark/) | Unicode sparklines, mini bar charts, heatmaps |
| [codechu-events](https://pypi.org/project/codechu-events/) | Thread-safe multi-channel pub/sub bus with replay |
| [codechu-xdg](https://pypi.org/project/codechu-xdg/) | XDG Base Directory helpers, vendor-namespaced |
| [codechu-treeviz](https://pypi.org/project/codechu-treeviz/) | Tree visualization — treemap, sunburst, icicle, flame |
| [codechu-fs](https://pypi.org/project/codechu-fs/) | Filesystem primitives — atomic write, XDG trash, safe walk |
| [codechu-term](https://pypi.org/project/codechu-term/) | Terminal capability detection, alt buffer, raw mode |
| [codechu-color](https://pypi.org/project/codechu-color/) | Color palettes, WCAG contrast, color-blind variants |
| [codechu-treedata](https://pypi.org/project/codechu-treedata/) | N-ary tree data structures and algorithms |
| [codechu-log](https://pypi.org/project/codechu-log/) | Structured logging — context, JSON, rotation, redaction |
| [codechu-i18n](https://pypi.org/project/codechu-i18n/) | Internationalization — locale, plural rules, RTL |
| [codechu-ipc](https://pypi.org/project/codechu-ipc/) | Local IPC — Unix socket, FIFO, JSON-line protocol |
| [codechu-config](https://pypi.org/project/codechu-config/) | Schema-driven config — atomic save, migrations |

## Credits

- Spinner glyph styles adapted from [cli-spinners](https://github.com/sindresorhus/cli-spinners)
- ANSI escape conventions per ECMA-48
- Inspiration from [rich](https://github.com/Textualize/rich) and [questionary](https://github.com/tmbo/questionary); codechu-cli stays stdlib-only with line-oriented output

## License

MIT — see [LICENSE](LICENSE).

Part of [Codechu](https://github.com/codechu).
