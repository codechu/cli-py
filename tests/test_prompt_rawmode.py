"""Raw-mode select/multiselect tests with monkeypatched termios/tty.

These exercise the arrow-key paths without requiring a real pty —
we provide a fake stdin that reports `isatty() == True` and a usable
`fileno()`, and we stub `termios` / `tty` calls.
"""

from __future__ import annotations

import importlib
import io
import os

import pytest

from codechu_cli import multiselect, select

from conftest import TTYStringIO

prompt_mod = importlib.import_module("codechu_cli.prompt")


class FakeTTYIn(io.StringIO):
    """StringIO that pretends to be a TTY and exposes a real fileno()."""

    def __init__(self, data: str, fd: int = 0) -> None:
        super().__init__(data)
        self._fd = fd

    def isatty(self) -> bool:
        return True

    def fileno(self) -> int:
        return self._fd


@pytest.fixture
def stub_termios(monkeypatch):
    """Replace termios + tty with no-ops; flip _HAS_TERMIOS on."""
    calls: dict[str, list] = {"tcgetattr": [], "tcsetattr": [], "setcbreak": []}

    class FakeTermios:
        TCSADRAIN = 1

        @staticmethod
        def tcgetattr(fd):
            calls["tcgetattr"].append(fd)
            return ["original-state"]

        @staticmethod
        def tcsetattr(fd, when, attrs):
            calls["tcsetattr"].append((fd, when, attrs))

    class FakeTty:
        @staticmethod
        def setcbreak(fd):
            calls["setcbreak"].append(fd)

    monkeypatch.setattr(prompt_mod, "termios", FakeTermios)
    monkeypatch.setattr(prompt_mod, "tty", FakeTty)
    monkeypatch.setattr(prompt_mod, "_HAS_TERMIOS", True)
    return calls


def _devnull_fd():
    return os.open(os.devnull, os.O_RDONLY)


def test_select_rawmode_arrow_down_and_enter(stub_termios):
    fd = _devnull_fd()
    try:
        # down, down, enter
        keys = "\x1b[B" "\x1b[B" "\n"
        result = select(
            "Pick",
            ["a", "b", "c"],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn(keys, fd=fd),
        )
    finally:
        os.close(fd)
    assert result == "c"
    assert stub_termios["setcbreak"] == [fd]
    assert stub_termios["tcsetattr"], "termios must be restored on exit"


def test_select_rawmode_arrow_up_wraps(stub_termios):
    fd = _devnull_fd()
    try:
        # up from cursor=0 wraps to last, then enter
        keys = "\x1b[A" "\n"
        result = select(
            "Pick",
            [("A", 1), ("B", 2), ("C", 3)],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn(keys, fd=fd),
        )
    finally:
        os.close(fd)
    assert result == 3


def test_select_rawmode_quit_returns_cursor(stub_termios):
    fd = _devnull_fd()
    try:
        # 'q' exits with cursor still at default
        result = select(
            "Pick",
            ["a", "b"],
            default=1,
            stream=TTYStringIO(),
            in_stream=FakeTTYIn("q", fd=fd),
        )
    finally:
        os.close(fd)
    assert result == "b"


def test_select_rawmode_ignores_unknown_key(stub_termios):
    fd = _devnull_fd()
    try:
        # 'x' is ignored, then enter
        result = select(
            "Pick",
            ["a", "b"],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn("x\n", fd=fd),
        )
    finally:
        os.close(fd)
    assert result == "a"


def test_select_rawmode_vim_keys(stub_termios):
    fd = _devnull_fd()
    try:
        # j (down), j, k (up), enter → cursor 1
        result = select(
            "Pick",
            ["a", "b", "c"],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn("jjk\n", fd=fd),
        )
    finally:
        os.close(fd)
    assert result == "b"


def test_multiselect_rawmode_toggle_and_confirm(stub_termios):
    fd = _devnull_fd()
    try:
        # space (select 0), down, space (select 1), enter
        keys = " " "\x1b[B" " " "\n"
        result = multiselect(
            "Pick",
            ["a", "b", "c"],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn(keys, fd=fd),
        )
    finally:
        os.close(fd)
    assert result == ["a", "b"]


def test_multiselect_rawmode_select_all_and_clear(stub_termios):
    fd = _devnull_fd()
    try:
        # a (select all), a (clear all), space (select 0), enter
        result = multiselect(
            "Pick",
            ["a", "b", "c"],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn("aa \n", fd=fd),
        )
    finally:
        os.close(fd)
    assert result == ["a"]


def test_multiselect_rawmode_quit_returns_current(stub_termios):
    fd = _devnull_fd()
    try:
        # space, q
        result = multiselect(
            "Pick",
            ["a", "b"],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn(" q", fd=fd),
        )
    finally:
        os.close(fd)
    assert result == ["a"]


def test_multiselect_rawmode_starts_with_defaults(stub_termios):
    fd = _devnull_fd()
    try:
        # Just hit enter — should return the defaults
        result = multiselect(
            "Pick",
            ["a", "b", "c"],
            defaults=(0, 2),
            stream=TTYStringIO(),
            in_stream=FakeTTYIn("\n", fd=fd),
        )
    finally:
        os.close(fd)
    assert result == ["a", "c"]


def test_read_key_escape_alone():
    """A bare ESC (no following [) yields 'esc'."""
    assert prompt_mod._read_key(io.StringIO("\x1bx")) == "esc"


def test_read_key_unknown_arrow():
    """ESC [ Z (e.g. shift-tab) maps to 'esc'."""
    assert prompt_mod._read_key(io.StringIO("\x1b[Z")) == "esc"


def test_raw_mode_available_false_when_no_termios(monkeypatch):
    monkeypatch.setattr(prompt_mod, "_HAS_TERMIOS", False)
    assert prompt_mod._raw_mode_available(TTYStringIO(), FakeTTYIn("")) is False


def test_select_rawmode_translated_hint(stub_termios):
    fd = _devnull_fd()
    out = TTYStringIO()
    try:
        select(
            "Pick",
            ["a", "b"],
            stream=out,
            in_stream=FakeTTYIn("\n", fd=fd),
            translate=lambda s: "TR:" + s,
        )
    finally:
        os.close(fd)
    assert "TR:Use" in out.getvalue()


def test_multiselect_rawmode_translated_hint(stub_termios):
    fd = _devnull_fd()
    out = TTYStringIO()
    try:
        multiselect(
            "Pick",
            ["a", "b"],
            stream=out,
            in_stream=FakeTTYIn("\n", fd=fd),
            translate=lambda s: "TR:" + s,
        )
    finally:
        os.close(fd)
    assert "TR:Use space" in out.getvalue()


def test_select_rawmode_custom_keymap(stub_termios):
    """Custom keymap: use 'n'/'p' instead of j/k for next/prev."""
    fd = _devnull_fd()
    try:
        # 'n' = down, 'n' = down, enter → cursor 2
        result = select(
            "Pick",
            ["a", "b", "c"],
            stream=TTYStringIO(),
            in_stream=FakeTTYIn("nn\n", fd=fd),
            keymap={"down": ("n",), "up": ("p",)},
        )
    finally:
        os.close(fd)
    assert result == "c"


def test_select_fallback_translated_choice_label():
    """Non-TTY in_stream forces the numbered fallback; translator wraps
    the 'Enter your choice (1-N)' message it prints."""
    s = TTYStringIO()
    seen: list[str] = []

    def t(msg: str) -> str:
        seen.append(msg)
        return "[X] " + msg

    result = prompt_mod.select(
        "Pick",
        ["a", "b", "c"],
        stream=s,
        in_stream=io.StringIO("2\n"),
        translate=t,
    )
    assert result == "b"
    # The "Enter your choice (1-3)" template was passed through translate.
    assert any("Enter your choice" in m for m in seen)
    assert "[X] Enter your choice (1-3)" in s.getvalue()
