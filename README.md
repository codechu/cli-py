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

Line-oriented CLI primitives for Python: colors, progress bars,
spinners, prompts, tables, boxes. Consistent UX across every Codechu
tool, with graceful fallbacks for pipes, Windows, and CI.

```text
deploy
[12 of 24 · 50% · 1m 32s · 156 items/s]  ████████████░░░░░░░░░░░░  ⠼
  ↳ migrating database…                                            ✓
  ↳ rolling out workers                                            ⠿
```

## Install

```bash
pip install codechu-cli
```

Requires Python 3.10+. Depends on
[`codechu-fmt`](https://pypi.org/project/codechu-fmt/) and
[`codechu-meter`](https://pypi.org/project/codechu-meter/) (both
stdlib-only — no transitive deps).

## Quick example

```python
from codechu_cli import ProgressBar, Spinner, confirm

if not confirm("Deploy to production?"):
    raise SystemExit(0)

bar = ProgressBar(len(files)).style("claude").with_eta().with_rate()
for f in files:
    process(f)
    bar.advance(1, label=f.name)
bar.finish()

with Spinner("publishing artifacts…"):
    publish()
```

POSIX-first. Raw-mode pickers on Linux/macOS, numbered-prompt
fallback everywhere else (Windows, CI, pipes).

## What you get

- **`ProgressBar`** — bracketed bar with percent, count, ETA, rate.
  Multiple style presets; subpixel-smooth narrow bars.
- **`Spinner`** — threaded spinner with Braille frames + ASCII
  fallback, dozens of style presets organised by family and mood.
- **`confirm` / `prompt`** — yes-no + single-line input with
  validator + password mode.
- **`select` / `multiselect`** — arrow-key pickers, numbered
  fallback off-TTY.
- **`Color`** — fluent ANSI palette (`c.low(...)`, `c.high(...)`)
  with caller-controlled enable/disable (no `NO_COLOR` reading).
- **`Table` / `box` / `render_markdown`** — formatted widgets that
  respect Unicode widths and ANSI escape codes.

## Read more

- [API reference](docs/API.md) — every public symbol with signatures.
- [Recipes](docs/RECIPES.md) — 11 idiomatic patterns end to end.
- [Customize](docs/CUSTOMIZE.md) — palettes, templates, custom
  keymaps, i18n, ASCII-art banners, style discovery.
- [Migration guide](docs/MIGRATION.md) — v0.1 → v0.2 → v0.3 breaking
  changes with before/after code.
- [Changelog](CHANGELOG.md)

## Family

| Library | Purpose |
|---------|---------|
| [codechu-fmt](https://pypi.org/project/codechu-fmt/) | Human-readable sizes, durations, rates |
| [codechu-meter](https://pypi.org/project/codechu-meter/) | Timing primitives — stopwatch, ETA, rate |
| [codechu-spark](https://pypi.org/project/codechu-spark/) | Unicode sparklines, mini bar charts, heatmaps |
| [codechu-term](https://pypi.org/project/codechu-term/) | Terminal capabilities, alt buffer, raw mode |
| [codechu-color](https://pypi.org/project/codechu-color/) | Color palettes, WCAG contrast, color-blind variants |

Full ecosystem: [github.com/codechu](https://github.com/codechu).

## Credits

- Spinner glyph styles adapted from
  [cli-spinners](https://github.com/sindresorhus/cli-spinners).
- ANSI escape conventions per ECMA-48.
- Inspiration from [rich](https://github.com/Textualize/rich) and
  [questionary](https://github.com/tmbo/questionary); codechu-cli
  stays minimal and line-oriented.

## License

MIT — see [LICENSE](LICENSE).

Part of [Codechu](https://github.com/codechu).
