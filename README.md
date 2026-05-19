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

## License

MIT — see [LICENSE](LICENSE).

Part of [Codechu](https://github.com/codechu).
