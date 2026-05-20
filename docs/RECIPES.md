# Recipes — codechu-cli

Copy-paste patterns for common CLI tasks. Every snippet is runnable
against the published `codechu-cli` 0.2.x.

## 1. Print colored error / warning / info

```python
import sys
from codechu_cli import Color, capabilities, e

caps = capabilities(sys.stderr)
c = Color(sys.stderr)

print(f"{e('ok',   caps)} {c.low('scan complete')}")
print(f"{e('warn', caps)} {c.medium('disk above 90 %')}")
print(f"{e('fail', caps)} {c.high('refusing destructive op')}")
print(f"{e('info', caps)} {c.info('dry-run mode — no changes written')}")
```

`Color` auto-detects via `stream.isatty()`. To force colors (e.g. for
`--color=always`) pass `enabled=True`:

```python
c = Color(sys.stderr, enabled=True)
```

---

## 2. Run a long task with a Spinner

```python
import sys
from codechu_cli import Spinner, capabilities

caps = capabilities(sys.stderr)

with Spinner("Scanning home directory…", caps=caps):
    walk_filesystem()
```

For a specific look:

```python
with Spinner("Indexing…", style="codechu", caps=caps):
    build_index()
```

`Spinner` is **only** usable as a context manager — there is no public
`.start()` / `.stop()`. If the task raises, the spinner is cleared
cleanly and the exception propagates.

---

## 3. Show progress with ETA for a known total

```python
from codechu_cli import ProgressBar

paths = list(walk())
bar = (
    ProgressBar(len(paths))
    .style("claude")     # █░ at width 10
    .with_eta()
    .with_rate()
    .units("files")
)
for p in paths:
    process(p)
    bar.advance(1, label=p.name)
bar.finish()
```

If you don't know the total upfront, start in indeterminate mode and
switch later:

```python
bar = ProgressBar(None)            # animated sliding bar
for chunk in stream():
    bar.advance()
    if chunk.is_last:
        bar.set_total(chunk.total) # transitions to normal rendering
bar.finish()
```

---

## 4. Confirm a destructive action

```python
from codechu_cli import confirm

if not confirm("Delete 12 GB of caches?", default=False):
    raise SystemExit(0)
```

For non-English UX, override the tokens:

```python
from gettext import gettext as _

go = confirm(
    "Devam edilsin mi?",
    yes_chars=("e", "evet"),
    no_chars=("h", "hayır"),
    translate=_,
)
```

For CI, short-circuit:

```python
go = confirm("…", assume_yes=args.yes)   # returns True without prompting
```

---

## 5. Interactive single-select menu

```python
from codechu_cli import select, capabilities
import sys

caps = capabilities(sys.stderr)

mode = select(
    "Cleanup mode",
    [
        ("Conservative — caches only", "safe"),
        ("Aggressive — also logs",     "aggressive"),
        ("Custom",                     "custom"),
    ],
    default=0,
    caps=caps,
)
print(f"Chose: {mode}")
```

- TTY: arrow keys (or `j`/`k`), Enter to accept, `q`/ESC to cancel.
- Non-TTY: numbered prompt — no caller-side branching required.

Custom keymap (vi-only):

```python
select("Branch", branches, keymap={"up": ("k",), "down": ("j",)})
```

---

## 6. Multiselect with keyboard navigation

```python
from codechu_cli import multiselect, capabilities
import sys

caps = capabilities(sys.stderr)

targets = multiselect(
    "Pick targets to clean",
    [
        ("~/.cache/pip",          "pip"),
        ("~/.cache/yarn",         "yarn"),
        ("~/.cargo/registry",     "cargo"),
        ("/var/log/journal/*",    "journal"),
    ],
    defaults=(0, 1),
    caps=caps,
)
print(f"Cleaning: {targets}")
```

Keymap:

| Key | Action |
|---|---|
| `↑` / `k` | Move cursor up |
| `↓` / `j` | Move cursor down |
| `Space` | Toggle current item |
| `a` | Select all (or clear all when full) |
| `Enter` | Confirm |
| `q` / `ESC` | Cancel — returns current selection |

---

## 7. Mix Spinner + ProgressBar in one flow

When work has a discovery phase (unknown size) followed by a
processing phase (known size), start with a `Spinner` and hand off to
a `ProgressBar`:

```python
import sys
from codechu_cli import Spinner, ProgressBar, capabilities

caps = capabilities(sys.stderr)

with Spinner("Discovering files…", caps=caps):
    paths = list(walk())

bar = ProgressBar(len(paths)).style("codechu").with_eta()
for p in paths:
    process(p)
    bar.advance(1, label=p.name)
bar.finish()

print(f"Processed {len(paths)} files.")
```

The spinner clears its line on exit, so the bar starts on a fresh
line.

---

## 8. Register a custom progress bar style

```python
from codechu_cli import (
    ProgressBar,
    register_bar_style,
    register_spinner_style,
)

# Custom bar with project-specific glyphs
register_bar_style(
    "snapedge",
    fill="▰",
    empty="▱",
    width=12,
)

# Custom spinner, tagged so `--tag calm` will surface it
register_spinner_style(
    "snapwave",
    ["~", "≈", "∼", "≋"],
    family="codechu",
    tags={"calm", "narrow"},
)

bar = ProgressBar(100).style("snapedge").spinner_style("snapwave")
for _ in range(100):
    bar.advance(label="syncing…")
bar.finish()
```

`register_bar_style` takes `fill`, `empty`, `width`, and `smooth`.
`register_spinner_style` requires `frames` (non-empty) and optionally
`family`, `tags`, and `compatibility` (bucket in `STYLE_COMPATIBILITY`,
default `"modern"`).

Both registries are part of the public API — your registered names
are usable everywhere built-in names are (`ProgressBar.style()`,
`Spinner(style=…)`, `--style` CLI flags, etc.).
