# Migration Guide — v0.1 → v0.2

`codechu-cli` 0.2 is a focused rewrite of the surface. The library now
does one thing — terminal UX primitives — and explicitly delegates
timing, formatting, and sparklines to sibling packages.

This guide documents every breaking change with before/after code.

## Summary

| Area | v0.1 | v0.2 |
|---|---|---|
| `Color` palette access | `c("level", "text")` (single callable) | `c.level("text")` (fluent attribute) |
| `Color` env reading | Read `NO_COLOR` automatically | Caller passes `enabled=` (or auto-detects via TTY) |
| `ProgressBar` construction | Long kwarg constructor | `ProgressBar(total)` + builder methods |
| `Spinner` lifecycle | Manual `.start()` / `.stop()` | Context manager only (`with Spinner(...):`) |
| Timing / formatting re-exports | Available from `codechu_cli` | Removed — import from `codechu_fmt` / `codechu_meter` / `codechu_spark` |
| `emoji.e()` capability source | Implicit env read | Caller passes `caps` explicitly |
| Internal TTY helpers | Duplicated per module | New private `_term.py` |
| `progress.py` shape | Single file | `progress/` package (line + bar + spinner + style registries) |

---

## 1. `Color` — fluent attribute access

### Before (v0.1)

```python
from codechu_cli import Color
c = Color(sys.stdout)
c("low", "ok")         # callable with two positional args
c("high", "bad")
```

### After (v0.2)

```python
from codechu_cli import Color
c = Color(sys.stdout)
c.low("ok")            # method per palette key
c.high("bad")
```

Each key in `Color.DEFAULT_PALETTE` (and anything you merge via
`palette=`) becomes a method on the instance. The lookup goes through
`__getattr__`, so unknown keys raise `AttributeError` with the known
set in the message:

```
AttributeError: 'Color' has no color 'glow'. Known: ['bold', 'dim', 'high', 'info', 'low', 'medium', 'reset']
```

### Why

The single-callable form forced callers to spell the palette key as a
string at every site, which broke autocomplete and silently no-op'd on
typos. The method form lets IDEs surface the available keys and lets
linters flag misspellings.

---

## 2. `Color` no longer reads `NO_COLOR`

### Before (v0.1)

```python
# v0.1 silently consulted NO_COLOR=1 and disabled color.
c = Color(sys.stdout)
```

### After (v0.2)

```python
# Caller decides.
c = Color(sys.stdout)                       # auto-detect via isatty()
c = Color(sys.stdout, enabled=False)        # force off (e.g. NO_COLOR set)
c = Color(sys.stdout, enabled=True)         # force on
```

If you want the v0.1 behavior, do it in your bootstrap:

```python
import os, sys
from codechu_cli import Color

no_color = "NO_COLOR" in os.environ
c = Color(sys.stdout, enabled=None if not no_color else False)
```

### Why

Only one helper in the package now reads the environment
(`emoji.capabilities()`). Every other primitive takes the answer from
its caller. This makes apps deterministic and testable without mocking
`os.environ`.

---

## 3. `ProgressBar` — kwarg constructor → builder

### Before (v0.1)

```python
from codechu_cli import ProgressBar

bar = ProgressBar(
    total=100,
    width=30,
    fill="█",
    empty="░",
    template="[{bar}] {pct}% {label}",
    show_eta=True,
    show_rate=True,
    stream=sys.stderr,
)
```

### After (v0.2)

```python
from codechu_cli import ProgressBar

bar = (
    ProgressBar(100)
    .width(30)
    .style("claude")          # bakes fill / empty / width
    .template("[{bar}] {pct}% {label}")
    .with_eta()
    .with_rate()
)
```

Every visual knob is now a builder method (see `docs/API.md` for the
full list). All builder methods return `self`, so chaining works in
any order; you can also split the chain across statements:

```python
bar = ProgressBar(100)
bar.style("codechu").width(20)
if verbose:
    bar.with_eta().with_rate()
```

### Why

The kwarg constructor grew to ~12 parameters and most were independent
toggles. The builder reads better, supports conditional configuration,
and gives each knob a docstring.

---

## 4. `Spinner` — context manager required

### Before (v0.1)

```python
from codechu_cli import Spinner

sp = Spinner("Scanning…")
sp.start()
try:
    walk_filesystem()
finally:
    sp.stop()
```

### After (v0.2)

```python
from codechu_cli import Spinner

with Spinner("Scanning…"):
    walk_filesystem()
```

The thread starts on `__enter__` and stops + clears on `__exit__`.
`__exit__` does **not** suppress exceptions raised inside the block.

There is no public `.start()` / `.stop()` on `Spinner` anymore — the
implementations are still there as `_start` / `_stop` for the context
manager's own use, but they are not part of the API.

### Why

Manual lifecycle was a leak waiting to happen — the spinner thread
would survive an unhandled exception and continue overwriting stderr
during a traceback. The context manager makes that impossible.

---

## 5. Dropped umbrella re-exports

v0.1 re-exported timing / formatting / sparkline helpers from
`codechu_cli` for convenience. v0.2 removes them — those helpers live
in their own packages now.

### Before (v0.1)

```python
from codechu_cli import (
    format_size, format_duration, format_rate,
    Stopwatch, RateEstimator, ETAEstimator,
    sparkline,
)
```

### After (v0.2)

```python
from codechu_fmt import format_size, format_duration, format_rate
from codechu_meter import Stopwatch, RateEstimator, ETAEstimator
from codechu_spark import sparkline
```

`ProgressBar`'s `{elapsed}` / `{eta}` / `{rate}` / `{remaining}` are
still computed internally — `codechu-cli` has no runtime dependency on
the sibling libs.

### Why

Three things in one package made `codechu-cli` impossible to evolve
without forcing churn on unrelated callers. The split mirrors the
Codechu org rule: **one package, one responsibility.**

---

## 6. `emoji.e()` — capabilities are explicit

### Before (v0.1)

```python
from codechu_cli import e
e("ok")   # internally called capabilities() — read LANG, TERM, NO_COLOR, …
```

### After (v0.2)

```python
import sys
from codechu_cli import capabilities, e

caps = capabilities(sys.stderr)   # call ONCE in your bootstrap
e("ok", caps)                     # pass caps explicitly
e("ok")                           # OK — deterministic: yields the ASCII fallback
```

`e()` no longer reads the environment. `capabilities()` is the only
function in the package that does, and it only runs when you call it.

The same is true for `Spinner`, `select`, `multiselect`, and
`prompt` — pass `caps=` if you want unicode glyphs, otherwise they
fall back to ASCII.

### Why

Implicit env reads made the library hard to test and hard to reason
about in environments with overlapping configuration (containers,
SSH-forwarded TTYs, snap sandboxes). Threading `caps` through every
renderer keeps the dependency on terminal state visible at the call
site.

---

## 7. `_term.py` — new private TTY helpers

v0.2 introduces a private module `codechu_cli._term` with `is_tty` and
a local `capabilities` helper. It deduplicates the TTY-detection logic
that used to live inline in every module.

It is **internal** (underscore prefix, not in `__all__`, not in
`__init__.py` re-exports). Callers should use the public surface:

- For "is this a TTY?" — most public helpers handle it for you via
  `enabled=None`.
- For the emoji-flavored capability set — use
  `codechu_cli.emoji.capabilities()`.

If you really need the bare TTY check, prefer
`stream.isatty()` directly over reaching into `_term`.

---

## 8. `progress.py` → `progress/` package

v0.1 had a single `progress.py` containing the line, bar, spinner, and
style registries.

v0.2 splits it into a package:

```
src/codechu_cli/progress/
    __init__.py        # re-exports the public surface
    line.py            # ProgressLine
    bar.py             # ProgressBar
    spinner.py         # Spinner
    styles_bar.py      # BAR_STYLES, SUBPIXEL, register_bar_style
    styles_spinner.py  # SPINNER_STYLES, SPINNER_FAMILIES, STYLE_TAGS, …
```

The public re-exports from `codechu_cli` are unchanged — you can still
write `from codechu_cli import ProgressBar`. But if you were importing
internals (e.g. `from codechu_cli.progress import _Bar`), update to
the new module paths.

---

## Migration checklist

- [ ] Replace `c("level", "text")` with `c.level("text")` everywhere.
- [ ] Add explicit `enabled=` to `Color()` if you relied on `NO_COLOR`
      auto-detection (or live with TTY-only detection).
- [ ] Replace `ProgressBar(total, width=…, fill=…, …)` with the
      builder chain `ProgressBar(total).width(…).fill(…)…`.
- [ ] Wrap `Spinner` use sites in `with` blocks; remove `.start()` /
      `.stop()` calls.
- [ ] Move imports of `format_*`, `Stopwatch`, `RateEstimator`,
      `ETAEstimator`, `sparkline` to the sibling packages.
- [ ] Compute `caps = capabilities(stream)` in bootstrap; thread it
      into `e()`, `Spinner`, `select`, `multiselect`, `prompt`.
- [ ] Drop any imports against `codechu_cli._term` (it's private).
- [ ] Drop any imports against the old single `codechu_cli.progress`
      submodule layout.
