"""Confirmation, text, single-select, and multi-select prompts."""

from __future__ import annotations

import getpass
import sys
from typing import IO, Callable, Sequence

from .emoji import e

# Optional POSIX raw-mode imports — guarded so the module imports on Windows.
try:
    import termios
    import tty
    _HAS_TERMIOS = True
except ImportError:  # pragma: no cover - Windows
    termios = None  # type: ignore[assignment]
    tty = None      # type: ignore[assignment]
    _HAS_TERMIOS = False


Choice = str | tuple[str, object]


def _stream_is_tty(stream: IO[str]) -> bool:
    isatty = getattr(stream, "isatty", None)
    try:
        return bool(isatty and isatty())
    except Exception:
        return False


def confirm(
    prompt: str,
    *,
    default: bool = False,
    stream: IO[str] | None = None,
    in_stream: IO[str] | None = None,
    assume_yes: bool = False,
) -> bool:
    """Yes/no prompt.

    - ``assume_yes`` short-circuits to ``True`` without prompting.
    - When ``stream`` is not a TTY, returns ``default`` without
      prompting.
    """
    if assume_yes:
        return True
    if stream is None:
        stream = sys.stderr
    if in_stream is None:
        in_stream = sys.stdin
    if not _stream_is_tty(stream):
        return default
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        stream.write(prompt + suffix)
        stream.flush()
        line = in_stream.readline()
    except Exception:
        return default
    if not line:
        return default
    ans = line.strip().lower()
    if not ans:
        return default
    return ans in ("y", "yes")


def prompt(
    message: str,
    *,
    default: str | None = None,
    validate: Callable[[str], None] | None = None,
    password: bool = False,
    stream: IO[str] | None = None,
    in_stream: IO[str] | None = None,
) -> str:
    """Ask for a single line of input.

    - ``validate`` is a callable that raises :class:`ValueError` on bad
      input; the prompt loops until a valid value is given.
    - ``password=True`` disables echo via :func:`getpass.getpass`.
    - When ``stream`` is not a TTY and a ``default`` is set, returns
      the default; otherwise reads one line from ``in_stream`` and
      returns it (no looping in non-TTY mode — validators still run
      and raise).
    """
    if stream is None:
        stream = sys.stderr
    if in_stream is None:
        in_stream = sys.stdin
    suffix = f" [{default}] " if default is not None else " "
    full = f"{message}{suffix}"

    is_tty = _stream_is_tty(stream)

    while True:
        if password:
            try:
                ans = getpass.getpass(full, stream=stream)
            except Exception:
                ans = ""
        else:
            try:
                stream.write(full)
                stream.flush()
                line = in_stream.readline()
            except Exception:
                line = ""
            if not line and default is not None:
                return default
            ans = line.rstrip("\r\n") if line else ""

        if not ans and default is not None:
            ans = default

        if validate is not None:
            try:
                validate(ans)
            except ValueError as err:
                try:
                    stream.write(f"  {e('fail', stream=stream)} {err}\n")
                    stream.flush()
                except Exception:
                    pass
                if not is_tty:
                    raise
                continue
        return ans


def _normalize_choices(choices: Sequence[Choice]) -> list[tuple[str, object]]:
    out: list[tuple[str, object]] = []
    for c in choices:
        if isinstance(c, tuple):
            label, value = c
            out.append((str(label), value))
        else:
            out.append((str(c), c))
    return out


def _numbered_select_fallback(
    message: str,
    pairs: list[tuple[str, object]],
    default_idx: int,
    stream: IO[str],
    in_stream: IO[str],
) -> object:
    stream.write(message + "\n")
    for i, (label, _) in enumerate(pairs, 1):
        marker = "*" if (i - 1) == default_idx else " "
        stream.write(f"  {marker} {i}) {label}\n")
    stream.flush()
    while True:
        raw = prompt(
            "Select",
            default=str(default_idx + 1),
            stream=stream,
            in_stream=in_stream,
        )
        try:
            idx = int(raw) - 1
        except ValueError:
            stream.write(f"  {e('fail', stream=stream)} not a number\n")
            stream.flush()
            if not _stream_is_tty(stream):
                # Non-TTY won't get better input, bail.
                idx = default_idx
                break
            continue
        if 0 <= idx < len(pairs):
            break
        stream.write(f"  {e('fail', stream=stream)} out of range\n")
        stream.flush()
        if not _stream_is_tty(stream):
            idx = default_idx
            break
    return pairs[idx][1]


def _numbered_multiselect_fallback(
    message: str,
    pairs: list[tuple[str, object]],
    default_set: set[int],
    stream: IO[str],
    in_stream: IO[str],
) -> list[object]:
    stream.write(message + " (comma-separated indices, blank = defaults)\n")
    for i, (label, _) in enumerate(pairs, 1):
        marker = "x" if (i - 1) in default_set else " "
        stream.write(f"  [{marker}] {i}) {label}\n")
    stream.flush()
    raw = prompt(
        "Select",
        default=",".join(str(i + 1) for i in sorted(default_set)),
        stream=stream,
        in_stream=in_stream,
    )
    if not raw.strip():
        return [pairs[i][1] for i in sorted(default_set)]
    out: list[object] = []
    seen: set[int] = set()
    for tok in raw.split(","):
        tok = tok.strip()
        if not tok:
            continue
        try:
            idx = int(tok) - 1
        except ValueError:
            continue
        if 0 <= idx < len(pairs) and idx not in seen:
            seen.add(idx)
            out.append(pairs[idx][1])
    return out


def _raw_mode_available(stream: IO[str], in_stream: IO[str]) -> bool:
    if not _HAS_TERMIOS:
        return False
    if not _stream_is_tty(stream):
        return False
    if not _stream_is_tty(in_stream):
        return False
    if not hasattr(in_stream, "fileno"):
        return False
    try:
        in_stream.fileno()
    except Exception:
        return False
    return True


def _read_key(in_stream: IO[str]) -> str:
    """Read a single key (or escape sequence) from a raw-mode stream.

    Returns one of: "up", "down", "enter", "space", "a", "q", "esc",
    or the literal character.
    """
    ch = in_stream.read(1)
    if ch == "\x1b":
        nxt = in_stream.read(1)
        if nxt == "[":
            arrow = in_stream.read(1)
            return {"A": "up", "B": "down", "C": "right", "D": "left"}.get(arrow, "esc")
        return "esc"
    if ch in ("\r", "\n"):
        return "enter"
    if ch == " ":
        return "space"
    return ch


def _render_select(
    stream: IO[str],
    message: str,
    pairs: list[tuple[str, object]],
    cursor: int,
    *,
    first: bool,
) -> None:
    if not first:
        # Move cursor up to the message line and clear lines below.
        stream.write(f"\x1b[{len(pairs) + 1}A")
    stream.write("\r\x1b[2K" + message + "\n")
    for i, (label, _) in enumerate(pairs):
        marker = e("arrow", stream=stream) if i == cursor else " "
        stream.write(f"\r\x1b[2K  {marker} {label}\n")
    stream.flush()


def _render_multiselect(
    stream: IO[str],
    message: str,
    pairs: list[tuple[str, object]],
    cursor: int,
    selected: set[int],
    *,
    first: bool,
) -> None:
    if not first:
        stream.write(f"\x1b[{len(pairs) + 1}A")
    stream.write("\r\x1b[2K" + message + "\n")
    for i, (label, _) in enumerate(pairs):
        box = e("check_on", stream=stream) if i in selected else e("check_off", stream=stream)
        pointer = e("arrow", stream=stream) if i == cursor else " "
        stream.write(f"\r\x1b[2K  {pointer} {box} {label}\n")
    stream.flush()


def select(
    message: str,
    choices: Sequence[Choice],
    *,
    default: int = 0,
    stream: IO[str] | None = None,
    in_stream: IO[str] | None = None,
) -> object:
    """Single-choice picker. Arrow keys on TTY, numbered fallback elsewhere.

    Returns the selected value (the second item of a ``(label, value)``
    tuple, or the label itself if a plain string was given).
    """
    if stream is None:
        stream = sys.stderr
    if in_stream is None:
        in_stream = sys.stdin
    if not choices:
        raise ValueError("select() requires at least one choice")
    pairs = _normalize_choices(choices)
    default_idx = max(0, min(default, len(pairs) - 1))

    if not _raw_mode_available(stream, in_stream):
        return _numbered_select_fallback(message, pairs, default_idx, stream, in_stream)

    fd = in_stream.fileno()
    old = termios.tcgetattr(fd)
    cursor = default_idx
    try:
        tty.setcbreak(fd)
        _render_select(stream, message, pairs, cursor, first=True)
        while True:
            key = _read_key(in_stream)
            if key in ("up", "k"):
                cursor = (cursor - 1) % len(pairs)
            elif key in ("down", "j"):
                cursor = (cursor + 1) % len(pairs)
            elif key == "enter":
                break
            elif key in ("q", "esc"):
                break
            else:
                continue
            _render_select(stream, message, pairs, cursor, first=False)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return pairs[cursor][1]


def multiselect(
    message: str,
    choices: Sequence[Choice],
    *,
    defaults: Sequence[int] = (),
    stream: IO[str] | None = None,
    in_stream: IO[str] | None = None,
) -> list[object]:
    """Multi-choice picker. Space toggles, ``a`` select-all, enter confirms.

    Returns a list of selected values in choice order.
    """
    if stream is None:
        stream = sys.stderr
    if in_stream is None:
        in_stream = sys.stdin
    if not choices:
        return []
    pairs = _normalize_choices(choices)
    default_set = {i for i in defaults if 0 <= i < len(pairs)}

    if not _raw_mode_available(stream, in_stream):
        return _numbered_multiselect_fallback(message, pairs, default_set, stream, in_stream)

    fd = in_stream.fileno()
    old = termios.tcgetattr(fd)
    cursor = 0
    selected = set(default_set)
    try:
        tty.setcbreak(fd)
        _render_multiselect(stream, message, pairs, cursor, selected, first=True)
        while True:
            key = _read_key(in_stream)
            if key in ("up", "k"):
                cursor = (cursor - 1) % len(pairs)
            elif key in ("down", "j"):
                cursor = (cursor + 1) % len(pairs)
            elif key == "space":
                if cursor in selected:
                    selected.discard(cursor)
                else:
                    selected.add(cursor)
            elif key == "a":
                if len(selected) == len(pairs):
                    selected.clear()
                else:
                    selected = set(range(len(pairs)))
            elif key == "enter":
                break
            elif key in ("q", "esc"):
                break
            else:
                continue
            _render_multiselect(stream, message, pairs, cursor, selected, first=False)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return [pairs[i][1] for i in sorted(selected)]


__all__ = ["confirm", "multiselect", "prompt", "select"]
