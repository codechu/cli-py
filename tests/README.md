# Tests — codechu-cli

Run the suite from the repo root:

```bash
pytest -q
```

With coverage:

```bash
pytest --cov=codechu_cli --cov-report=term-missing
```

## Coverage gate

The coverage floor is **85 %**. PRs that drop below it are rejected;
add tests with your change.

## Conventions

- Use `io.StringIO` for stream injection — never touch real fds.
- For TTY behaviour, wrap a `StringIO` in a tiny shim that returns
  `True` from `isatty()`. There's a helper at the top of
  `test_color.py` that suites import.
- Don't `time.sleep()` — mock `time.sleep` and `time.monotonic` when
  testing `Spinner` / `ProgressBar` animation.
- Env-var-sensitive tests (`NO_COLOR`, `LANG`, `TERM`,
  `CODECHU_CLI_EMOJI`) use `monkeypatch.setenv` /
  `monkeypatch.delenv` — never mutate `os.environ` directly.
