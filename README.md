# codechu-cli

Stdlib-only CLI primitives for Python — colors, progress bars, spinners,
prompts, emoji helpers — with consistent UX across Codechu tools.

```bash
pip install codechu-cli
```

## What it gives you

- **`Color`** — ANSI palette with `NO_COLOR` + TTY detection
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
print(c("low", "ok") + " scan complete")
print(c("high", "ERR") + " refusing destructive op")
```

### Progress bar

```python
from codechu_cli import ProgressBar

bar = ProgressBar(total=100, width=30)
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
ProgressBar(100, style="block")    # █░ — npm/cargo
ProgressBar(100, style="ascii")    # #- — GitHub Actions
ProgressBar(100, style="equals")   # =- — Docker

# Codechu signature
ProgressBar(100, style="codechu")  # ▰▱ — matches disk-cleaner UI

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
ProgressBar(100, style="blocks")        # ▰▰▰▱▱   width=5
ProgressBar(100, style="blocks-wide")   # 8 cells
ProgressBar(100, style="claude")        # █░ at width=10

# Subpixel-smooth — narrow bar that still shows fractional progress
ProgressBar(100, style="smooth")        # 10-cell, 80 distinct stops
ProgressBar(100, style="smooth-wide")   # 20-cell, 160 distinct stops

# Full override still works (style provides defaults; fill/empty/frames override)
ProgressBar(100, style="block", fill="*")
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

### Emoji helpers

```python
from codechu_cli import capabilities, e

caps = capabilities()  # {"unicode", "color", "emoji"} or subset
print(f"{e('ok')} done")            # "✓ done" or "+ done"
print(f"{e('arrow')} next step")    # "→ next step" or "-> next step"
```

`CODECHU_CLI_EMOJI=never` forces ASCII, `always` forces unicode.

## API reference

| Symbol | Purpose |
|---|---|
| `Color(stream)` | ANSI palette; respects `NO_COLOR` + `isatty()` |
| `banner(title, version, *, mode=None, stream=...)` | TTY-only header |
| `ProgressLine(stream=None, enabled=None)` | `.update()` / `.clear()` |
| `ProgressBar(total, *, width=40, ...)` | `.advance(n, label)` / `.set_total(n)` / `.finish()` |
| `Spinner(message, *, frames=None, interval=0.08)` | context manager + `.start()/.stop()` |
| `confirm(prompt, *, default, assume_yes, ...)` | yes/no |
| `prompt(message, *, default, validate, password, ...)` | single-line input |
| `select(message, choices, *, default=0, ...)` | single-choice picker |
| `multiselect(message, choices, *, defaults=(), ...)` | multi-choice picker |
| `resolve_format(stream, *, tty_default, pipe_default)` | format chooser |
| `format_examples([(cmd, desc), ...])` | argparse epilog |
| `capabilities(stream=None)` | set of `{"unicode", "color", "emoji"}` |
| `e(name, *, fallback=None)` | glyph lookup with ASCII fallback |

## Extension points

The library is opinionated about defaults but accepts customization at
every visible surface, so apps don't need to subclass to fit their
brand or locale.

```python
# Custom palette (merged onto defaults)
c = Color(sys.stdout, palette={
    "snap-edge":   "\033[35m",
    "snap-stable": "\033[36m",
})
print(c("snap-edge", "edge channel"))

# Force color on/off (override NO_COLOR + TTY detection)
c = Color(sys.stdout, force=True)

# Custom progress bar look
bar = ProgressBar(100, fill="█", empty="░",
                  template="{bar} {pct}% · {elapsed} · ETA {eta}")
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

## License

MIT — see [LICENSE](LICENSE).

Part of [Codechu](https://github.com/codechu).
