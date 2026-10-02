"""Console helpers that give the quality gate clear, structured terminal output."""

from __future__ import annotations

import contextlib
import datetime as dt
import shutil
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Generator, Sequence


_COLORED = sys.stdout.isatty()
_RESET = "\x1b[0m"
_BOLD = "\x1b[1m"
_GREEN = "\x1b[32m"
_RED = "\x1b[31m"
_CYAN = "\x1b[36m"
_MINUTE_SECONDS = 60
_HOUR_SECONDS = 3600


@contextlib.contextmanager
def section(title: str, command: Sequence[str]) -> Generator[None]:
    """Print a structured section header and a timed passed/failed footer."""
    started_at = dt.datetime.now(tz=dt.UTC)
    _rule(title, _BOLD)
    _line(_style("$ " + " ".join(command), _CYAN))
    _blank()
    try:
        yield
    except BaseException:
        elapsed = _elapsed(dt.datetime.now(tz=dt.UTC) - started_at)
        _rule(f"failed in {elapsed}", _RED)
        _blank()
        raise
    else:
        elapsed = _elapsed(dt.datetime.now(tz=dt.UTC) - started_at)
        _rule(f"passed in {elapsed}", _GREEN)
        _blank()


def message(text: str) -> None:
    """Print a plain quality-gate message."""
    _line(text)


def _rule(title: str, style: str) -> None:
    width = shutil.get_terminal_size((100, 20)).columns
    available = max(width - len(title) - 2, 2)
    left = available // 2
    right = available - left
    _line(_style(("=" * left) + f" {title} " + ("=" * right), style))


def _elapsed(delta: dt.timedelta) -> str:
    seconds = delta.total_seconds()
    if seconds >= _HOUR_SECONDS:
        return f"{int(seconds // _HOUR_SECONDS)}h"
    if seconds >= _MINUTE_SECONDS:
        return f"{int(seconds // _MINUTE_SECONDS)}m"
    if seconds >= 1:
        return f"{int(seconds)}s"
    return f"{seconds:.2f}s"


def _style(text: str, style: str) -> str:
    if not _COLORED:
        return text
    return f"{style}{text}{_RESET}"


def _blank() -> None:
    _line("")


def _line(text: str) -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()
