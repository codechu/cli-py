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
