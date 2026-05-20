"""Confirmation, text, single-select, and multi-select prompts."""

from __future__ import annotations

import getpass
import sys
from typing import IO, Callable, Sequence

from ._term import is_tty as _is_tty_helper
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


# Default key bindings for select() / multiselect(). Each value is a
# tuple of raw key sequences that map to the named action. Override per
# call with ``keymap={...}``.
DEFAULT_KEYMAP: dict[str, tuple[str, ...]] = {
    "up": ("\x1b[A", "k"),         # arrow up + vi k
    "down": ("\x1b[B", "j"),       # arrow down + vi j
    "accept": ("\r", "\n"),        # Enter
    "toggle": (" ",),               # space — multiselect
    "select_all": ("a",),
    "cancel": ("\x1b", "q"),        # ESC or q
}


def _identity(s: str) -> str:
    return s


def _stream_is_tty(stream: IO[str]) -> bool:
    return _is_tty_helper(stream)


def confirm(
    prompt: str,
    *,
    default: bool = False,
    stream: IO[str] | None = None,
    in_stream: IO[str] | None = None,
    assume_yes: bool = False,
    yes_chars: tuple[str, ...] = ("y", "yes"),
    no_chars: tuple[str, ...] = ("n", "no"),
    suffix_format: str = "[{yes}/{no}]",
    translate: Callable[[str], str] | None = None,
) -> bool:
    """Yes/no prompt.

    - ``assume_yes`` short-circuits to ``True`` without prompting.
    - When ``stream`` is not a TTY, returns ``default`` without
      prompting.
    - ``yes_chars`` / ``no_chars`` define the accepted tokens (matched
      case-insensitively against the full token or its first letter).
      The suffix uppercases whichever set corresponds to ``default``.
    - ``suffix_format`` is a format string accepting ``{yes}`` /
      ``{no}``. Defaults to ``"[{yes}/{no}]"``.
    - ``translate`` (optional) wraps any library-emitted text (the
      suffix). The caller-supplied ``prompt`` is *not* translated — the
      caller already chose its language.
    """
    if assume_yes:
        return True
    if stream is None:
        stream = sys.stderr
    if in_stream is None:
        in_stream = sys.stdin
    t = translate if translate is not None else _identity
    if not _stream_is_tty(stream):
        return default
    y = yes_chars[0].upper() if default else yes_chars[0]
    n = no_chars[0] if default else no_chars[0].upper()
    suffix = " " + t(suffix_format.format(yes=y, no=n)) + " "
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
    # Match against either the full token or its first letter, lowered.
    yes_set = {c.lower() for c in yes_chars} | {c[0].lower() for c in yes_chars if c}
    no_set = {c.lower() for c in no_chars} | {c[0].lower() for c in no_chars if c}
    if ans in yes_set:
        return True
    if ans in no_set:
        return False
    return default


def prompt(
    message: str,
    *,
    default: str | None = None,
    validate: Callable[[str], None] | None = None,
    password: bool = False,
    stream: IO[str] | None = None,
    in_stream: IO[str] | None = None,
    translate: Callable[[str], str] | None = None,
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
    t = translate if translate is not None else _identity
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
                    msg = t("Invalid input: {err}").format(err=err)
                    stream.write(f"  {e('fail', stream=stream)} {msg}\n")
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
    t: Callable[[str], str] = _identity,
) -> object:
    stream.write(message + "\n")
    for i, (label, _) in enumerate(pairs, 1):
        marker = "*" if (i - 1) == default_idx else " "
        stream.write(f"  {marker} {i}) {label}\n")
    stream.flush()
    choice_label = t("Enter your choice (1-{n})").format(n=len(pairs))
    while True:
        raw = prompt(
            choice_label,
            default=str(default_idx + 1),
            stream=stream,
            in_stream=in_stream,
            translate=t,
        )
        try:
            idx = int(raw) - 1
        except ValueError:
            stream.write(f"  {e('fail', stream=stream)} {t('not a number')}\n")
            stream.flush()
            if not _stream_is_tty(stream):
                # Non-TTY won't get better input, bail.
                idx = default_idx
                break
            continue
        if 0 <= idx < len(pairs):
            break
        stream.write(f"  {e('fail', stream=stream)} {t('out of range')}\n")
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
    t: Callable[[str], str] = _identity,
) -> list[object]:
    stream.write(message + " " + t("(comma-separated indices, blank = defaults)") + "\n")
    for i, (label, _) in enumerate(pairs, 1):
        marker = "x" if (i - 1) in default_set else " "
        stream.write(f"  [{marker}] {i}) {label}\n")
    stream.flush()
    choice_label = t("Enter your choice (1-{n})").format(n=len(pairs))
    raw = prompt(
        choice_label,
        default=",".join(str(i + 1) for i in sorted(default_set)),
        stream=stream,
        in_stream=in_stream,
        translate=t,
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
    or the literal character. This is the legacy name-mapping reader,
    kept for back-compat with tests that exercise it directly.
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


def _read_raw_key(in_stream: IO[str]) -> str:
    """Read one key event as its raw byte sequence (e.g. ``"\\x1b[A"``).

    Used for keymap matching. Escape-prefixed reads peek at the next
    char and pull the third (``A`` / ``B`` / ``C`` / ``D``) when an
    ANSI CSI is in play; a bare ESC is returned verbatim.
    """
    ch = in_stream.read(1)
    if ch == "\x1b":
        nxt = in_stream.read(1)
        if nxt == "[":
            arrow = in_stream.read(1)
            return "\x1b[" + arrow
        if nxt == "":
            return "\x1b"
        # Unknown ESC-prefixed sequence — return ESC, swallow next.
        return "\x1b"
    return ch


def _match_action(key: str, keymap: dict[str, tuple[str, ...]]) -> str | None:
    """Return the keymap action name whose tuple contains ``key``."""
    for action, keys in keymap.items():
        if key in keys:
            return action
    return None


def _render_select(
    stream: IO[str],
    message: str,
    pairs: list[tuple[str, object]],
    cursor: int,
    *,
    first: bool,
    hint: str = "",
) -> None:
    if not first:
        # Move cursor up to the message line and clear lines below.
        stream.write(f"\x1b[{len(pairs) + 1}A")
    stream.write("\r\x1b[2K" + message + "\n")
    for i, (label, _) in enumerate(pairs):
        marker = e("arrow", stream=stream) if i == cursor else " "
        stream.write(f"\r\x1b[2K  {marker} {label}\n")
    if first and hint:
        # Print the hint once below the list, then move back above it
        # so subsequent redraws can overwrite the list cleanly.
        stream.write(f"\r\x1b[2K{hint}\n")
        stream.write("\x1b[1A")
    stream.flush()


def _render_multiselect(
    stream: IO[str],
    message: str,
    pairs: list[tuple[str, object]],
    cursor: int,
    selected: set[int],
    *,
    first: bool,
    hint: str = "",
) -> None:
    if not first:
        stream.write(f"\x1b[{len(pairs) + 1}A")
    stream.write("\r\x1b[2K" + message + "\n")
    for i, (label, _) in enumerate(pairs):
        box = e("check_on", stream=stream) if i in selected else e("check_off", stream=stream)
        pointer = e("arrow", stream=stream) if i == cursor else " "
        stream.write(f"\r\x1b[2K  {pointer} {box} {label}\n")
    if first and hint:
        stream.write(f"\r\x1b[2K{hint}\n")
        stream.write("\x1b[1A")
    stream.flush()


def select(
    message: str,
    choices: Sequence[Choice],
    *,
    default: int = 0,
    stream: IO[str] | None = None,
    in_stream: IO[str] | None = None,
    keymap: dict[str, tuple[str, ...]] | None = None,
    translate: Callable[[str], str] | None = None,
) -> object:
    """Single-choice picker. Arrow keys on TTY, numbered fallback elsewhere.

    Returns the selected value (the second item of a ``(label, value)``
    tuple, or the label itself if a plain string was given).

    Pass ``keymap=`` to override individual actions (see
    :data:`DEFAULT_KEYMAP`). Pass ``translate=`` to localize the hint
    line and the numbered-fallback messages.
    """
    if stream is None:
        stream = sys.stderr
    if in_stream is None:
        in_stream = sys.stdin
    if not choices:
        raise ValueError("select() requires at least one choice")
    pairs = _normalize_choices(choices)
    default_idx = max(0, min(default, len(pairs) - 1))
    km = {**DEFAULT_KEYMAP, **(keymap or {})}
    t = translate if translate is not None else _identity

    if not _raw_mode_available(stream, in_stream):
        return _numbered_select_fallback(message, pairs, default_idx, stream, in_stream, t)

    fd = in_stream.fileno()
    old = termios.tcgetattr(fd)
    cursor = default_idx
    hint = t("Use ↑↓ (or j/k) to move, Enter to select, q to cancel")
    try:
        tty.setcbreak(fd)
        _render_select(stream, message, pairs, cursor, first=True, hint=hint)
        while True:
            key = _read_raw_key(in_stream)
            action = _match_action(key, km)
            if action == "up":
                cursor = (cursor - 1) % len(pairs)
            elif action == "down":
                cursor = (cursor + 1) % len(pairs)
            elif action == "accept":
                break
            elif action == "cancel":
                break
            else:
                continue
            _render_select(stream, message, pairs, cursor, first=False, hint=hint)
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
    keymap: dict[str, tuple[str, ...]] | None = None,
    translate: Callable[[str], str] | None = None,
) -> list[object]:
    """Multi-choice picker. Space toggles, ``a`` select-all, enter confirms.

    Returns a list of selected values in choice order. ``keymap=`` and
    ``translate=`` work the same way as :func:`select`.
    """
    if stream is None:
        stream = sys.stderr
    if in_stream is None:
        in_stream = sys.stdin
    if not choices:
        return []
    pairs = _normalize_choices(choices)
    default_set = {i for i in defaults if 0 <= i < len(pairs)}
    km = {**DEFAULT_KEYMAP, **(keymap or {})}
    t = translate if translate is not None else _identity

    if not _raw_mode_available(stream, in_stream):
        return _numbered_multiselect_fallback(message, pairs, default_set, stream, in_stream, t)

    fd = in_stream.fileno()
    old = termios.tcgetattr(fd)
    cursor = 0
    selected = set(default_set)
    hint = t("Use space to toggle, a to select all, Enter to confirm, q to cancel")
    try:
        tty.setcbreak(fd)
        _render_multiselect(stream, message, pairs, cursor, selected, first=True, hint=hint)
        while True:
            key = _read_raw_key(in_stream)
            action = _match_action(key, km)
            if action == "up":
                cursor = (cursor - 1) % len(pairs)
            elif action == "down":
                cursor = (cursor + 1) % len(pairs)
            elif action == "toggle":
                if cursor in selected:
                    selected.discard(cursor)
                else:
                    selected.add(cursor)
            elif action == "select_all":
                if len(selected) == len(pairs):
                    selected.clear()
                else:
                    selected = set(range(len(pairs)))
            elif action == "accept":
                break
            elif action == "cancel":
                break
            else:
                continue
            _render_multiselect(stream, message, pairs, cursor, selected, first=False, hint=hint)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return [pairs[i][1] for i in sorted(selected)]


__all__ = ["confirm", "multiselect", "prompt", "select"]
