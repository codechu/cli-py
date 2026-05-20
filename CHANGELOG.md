# Changelog

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) + [SemVer](https://semver.org/).

## [Unreleased]

## [0.4.0] - 2026-05-20

### Changed
- **Defork**: `ProgressBar` now uses `codechu_meter.RateEstimator` and
  `codechu_fmt.format_duration` / `format_rate` directly. The inline
  `_RateEstimator` / `_fmt_duration` / `_fmt_rate` helpers in
  `progress/bar.py` are removed.
- **Visible output for very long ETAs**: duration formatting now
  promotes ≥3600 s to ``"1h Xm"`` (was ``"61m 40s"``). This is the
  documented improvement of the consolidation; matches the rest of
  the Codechu fmt family.

### Dependencies
- New required dependencies: ``codechu-fmt>=0.4,<0.5`` and
  ``codechu-meter>=0.3,<0.4``. Both are pure-stdlib, no transitive
  deps.

## [0.3.0] - 2026-05-20

### Added
- `Table` — ASCII table widget with `plain` / `box` / `github` styles,
  per-column alignment, caller-supplied color callbacks, and auto
  widths that ignore ANSI escapes.
- `box(text, *, style, title, padding)` — Unicode-bordered text box
  (`single` / `double` / `rounded`) with optional inset title.
- `render_markdown(text, *, color, enabled)` — minimal Markdown → ANSI
  for help text and short docs (`# H1`, `## H2`, `**bold**`,
  `*italic*`, `` `code` ``, `-` / `*` lists, `[text](url)`).

## [0.2.0]

### Changed (breaking)
- Explicit-config refactor: library code no longer reads environment
  variables implicitly. `capabilities()` (in both `emoji` and the
  private `_term`) is the only env-reading helper, and callers must
  invoke it themselves.
- `e(name, caps=None, *, fallback=None)` — `caps` is now a positional
  parameter that the caller must supply (the previous `stream=` kwarg
  is gone). Omitting `caps` yields the ASCII fallback; pass
  `capabilities(...)` to get unicode glyphs.
- `Spinner(..., caps=None)` — frame selection no longer calls
  `capabilities()` internally. Pass `caps={"unicode", ...}` to opt
  into braille frames; default is ASCII.
- `prompt() / select() / multiselect()` accept a new `caps=` kwarg
  that is threaded through to `e()` for the glyphs they render.

## [0.1.0] - 2026-05-20

### Added
- Initial extraction from [codechu/disk-cleaner](https://github.com/codechu/disk-cleaner)
- `Color` — ANSI palette with `NO_COLOR` + TTY detection
- `ProgressLine` — single-line overwriting stderr progress
- `ProgressBar(total, ...)` — bracketed progress bar with percent + counts
- `Spinner(message, ...)` — threaded spinner, braille frames with ASCII fallback
- `confirm()` — yes/no prompt with TTY / `assume_yes` short-circuit
- `prompt()` — single-line input with optional validator + password mode
- `select()` — single-choice picker (arrow keys on TTY, numbered fallback)
- `multiselect()` — multi-choice picker (space toggle, `a` select-all)
- `banner()` — single-line interactive header
- `resolve_format()` — TTY vs pipe default format chooser
- `format_examples()` — argparse epilog formatter
- `emoji.capabilities()` + `emoji.e()` — locale + terminal-aware glyph lookup
- `Color`: `palette=` merge + `force=` override
- `ProgressBar`: `fill`, `empty`, `template`, `{elapsed}`, `{eta}` template fields
- `confirm()`: `yes_chars`, `no_chars`, `suffix_format`, `translate`
- `prompt()`: `translate`
- `select()` / `multiselect()`: `keymap=`, `translate=`
- `emoji.register()`, `emoji.update()`, `emoji.known()` — runtime glyph extension
- Spinner/ProgressBar named style presets (industry-standard + Codechu signature)
- Fixed-block (`blocks`, `claude`) + subpixel (`smooth`) ProgressBar styles
- `SPINNER_FAMILIES`, `STYLE_TAGS`, `STYLE_COMPATIBILITY` metadata registries
- `register_spinner_style()` / `register_bar_style()` runtime extension
- `python -m codechu_cli demo|list` preview CLI (filter by `--family`/`--tag`)
- 10 spinner styles in 3 new families (loading, semantic, outro):
  `bar`, `buffering`, `signal`, `heartbeat`, `searching`, `atom`,
  `spiral`, `success-flash`, `error-pulse`, `retry-slow`
- `ProgressBar` indeterminate mode — pass `total=None` for an animated
  sliding bar; `set_total(n)` switches to normal rendering
- `ProgressBar` template fields `{spinner}`, `{remaining}`, `{rate}`
- `ProgressBar` `gradient-edge` and `tape` bar styles
- `ProgressBar` `reverse=True` — fills right-to-left
- `ProgressBar.refresh()` — re-render current state; activates an
  auto-paused pulse after 2 s of idle
- Refactor: timing helpers split into sibling libraries —
  `codechu-fmt` (formatters), `codechu-meter` (measurement),
  `codechu-spark` (visualization). Convenience re-exports retained
  in `codechu_cli` for casual usage.

### Stability

- Style, family, and tag names are part of the public API. Removal or
  rename requires a one-minor-version deprecation cycle.
