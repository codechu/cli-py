# Contributing to codechu-cli

Thanks for thinking about contributing. `codechu-cli` is a small,
focused CLI primitives library — pure stdlib, POSIX-first. Patches
that keep that invariant intact are warmly received.

This library was originally extracted from [Disk Cleaner](https://github.com/codechu/disk-cleaner),
but is maintained independently with its own release cadence.

## Development setup

```bash
git clone https://github.com/codechu/cli-py.git
cd cli-py
pip install -e ".[dev]"
pytest -q
ruff check src tests
```

## Workflow

- Branch names: `feature/<short>`, `fix/<short>`, `refactor/<short>`,
  `docs/<short>`, `test/<short>`.
- Commit messages: [Conventional Commits](https://www.conventionalcommits.org/)
  (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:`).
- Open a PR using the template; describe the *why* in the body.
- One change per PR — keep diffs reviewable.

## Bug reports

A useful bug report includes:

- Python version + OS + terminal emulator (`$TERM`, `$LANG`).
- A minimal reproducer (≤30 lines, stdlib-only if possible).
- Expected vs observed behaviour. For TTY/non-TTY differences,
  mention whether you ran under a pty, a CI runner, or a real shell.

## Tests

- `pytest -q` must pass; coverage stays at **≥85 %**.
- New feature → new test. Interactive components (`select`,
  `multiselect`, `Spinner`) need tests that bypass the raw-mode
  path — use non-TTY streams + monkeypatched `time.sleep`.
- Don't introduce real sleeps for synchronization — mock `time`.
- Prefer `io.StringIO` for stream injection over touching real fds.

## Public API discipline

The public surface is what `codechu_cli.__all__` exports. Everything
else is internal — please don't extend it without a discussion first.

## Style

- `ruff check` + `ruff format` clean.
- Type hints on public APIs (`from __future__ import annotations`).
- Use `logging.getLogger(__name__)`; avoid `print`.
- Pure stdlib — no new third-party runtime dependencies.

## Security

If you find a security issue, see [SECURITY.md](SECURITY.md) — do not
open a public issue for it.
