# CLAUDE.md — codechu-cli

Bootstrap per `codechu-org/ai/AGENTS.md` §0 before any work. Prefer
the local clone at `$org_home/codechu-org/ai/AGENTS.md` (if
`~/.config/codechu/config.toml` has `org_home` set); otherwise
WebFetch the public raw URL
<https://raw.githubusercontent.com/codechu/codechu-org/main/ai/AGENTS.md>.
This file lists only product-local overrides.

## Product-local notes

- Pure-Python, stdlib-only. No GTK, no curses, no third-party
  runtime dependencies. Tests in `tests/` must keep that invariant.
- POSIX-first. Raw-mode features (`select`, `multiselect`) detect
  non-TTY / Windows up front and fall back to numbered prompts —
  do not add a hard `termios` import at module top.
- Public API surface: see `codechu_cli.__all__`. Anything else
  (private helpers, frame constants) is internal.
- Coverage target: ≥85 %.
- Emoji defaults are conservative ("temkinli") — when `LANG=C` or
  `TERM=dumb`, fall back to ASCII glyphs. `CODECHU_CLI_EMOJI=always`
  forces on, `never` forces off.

## Discipline reminders (org rules apply)

- Conventional Commits, no AI signature.
- No `--no-verify`, no force push, no unapproved publish.
- See `codechu-org/ai/AGENTS.md` for the full list.
