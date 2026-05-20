# Changelog

[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) + [SemVer](https://semver.org/).

## [Unreleased]

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
