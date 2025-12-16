from __future__ import annotations

from typing import Protocol
from dataclasses import dataclass
import datetime

import enum

from pi._internal import rpc
from pi._internal import bus as _bus


@dataclass(frozen=True, kw_only=True)
class CommandHistory:
    command_number: int
    """Sequential command number (starts from 1)"""

    command: str
    """The command text (between prompt end and command start)"""

    exit_code: int | None
    """Exit code if available"""

    start_time: datetime.datetime | None
    """Timestamp when command input started (OSC 133;B)"""

    end_time: datetime.datetime | None
    """Timestamp when command execution ended (OSC 133;D)"""


@dataclass(frozen=True, kw_only=True)
class TerminalInfo:
    foreground_color: str | None
    background_color: str | None
    cursor_blinking: bool | None


class ProcessKind(enum.StrEnum):
    Unknown = "unknown"
    Shell = "shell"


@dataclass(frozen=True, kw_only=True)
class ProcessInfo:
    pid: int
    """Process ID"""

    name: str
    """Process name (usually argv[0])"""

    kind: ProcessKind
    """Known process kind, e.g shell"""

    identification: str | None
    """Process identification if known (e.g. shell type)"""

    parent_pid: int | None
    """Parent process PID if one could be found"""

    uid: int | None
    """User ID of process if known"""

    euid: int | None
    """Effective UID of process if known"""

    gid: int | None
    """Group ID of process if known"""

    egid: int | None
    """Effective GID of process if known"""

    exe: str | None
    """Full path to process executable if known"""

    cwd: str | None
    """Process current working directiry if known"""

    argv: list[str]
    """Process argument vector"""

    env: dict[str, str]
    """Process environment variables"""


@dataclass(frozen=True, kw_only=True)
class PiInfo:
    path: str


@rpc.export
class Shell(Protocol):
    async def current_process_pid(self) -> int: ...
    async def scrape(self) -> str: ...
    async def terminal_info(self) -> TerminalInfo: ...
    async def process_info(self) -> ProcessInfo: ...
    async def command_history(self, *, n: int) -> list[CommandHistory]: ...
    async def command_output(self, *, command_number: int) -> str | None: ...
    async def close_sidebar(self) -> None: ...
    async def pi_info(self) -> PiInfo: ...


class TerminalEventKind(enum.StrEnum):
    SidebarDeactivated = "sidebar_deactivated"
    SidebarActivated = "sidebar_activated"
    Idle = "idle"
    Active = "active"


@dataclass(frozen=True, kw_only=True)
class TerminalEvent:
    kind: TerminalEventKind
    active_pid: int


@rpc.export
class ShellEvents(Protocol):
    async def terminal_event(self, *, event: TerminalEvent) -> None: ...


def interface(bus: _bus.Bus) -> Shell:
    return rpc.get_interface(Shell, bus, "shell")  # type: ignore [type-abstract]
