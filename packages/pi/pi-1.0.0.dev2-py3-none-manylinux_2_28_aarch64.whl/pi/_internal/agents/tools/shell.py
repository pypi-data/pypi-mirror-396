from pydantic_ai import RunContext
from pydantic_ai.messages import ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from pi._internal.agents.deps import PiDeps
from pi._internal.agents.common import suppress_errors
from pi._internal import protocols

shell_toolset = FunctionToolset[PiDeps]()


@shell_toolset.tool
@suppress_errors
async def current_screen(ctx: RunContext[PiDeps]) -> ToolReturn:
    """Get the current terminal screen content (scraped text)."""
    shell = protocols.shell.interface(ctx.deps.bus)
    screen_content = await shell.scrape()

    return ToolReturn(
        return_value=screen_content,
        metadata={
            "screen_content": screen_content,
        },
    )


@shell_toolset.tool
@suppress_errors
async def process_info(ctx: RunContext[PiDeps]) -> ToolReturn:
    """Get information about the current shell process."""
    shell = protocols.shell.interface(ctx.deps.bus)
    pid = await shell.current_process_pid()
    info = await shell.process_info()

    # Format for LLM
    formatted = f"""Process Information:
PID: {pid}
Name: {info.name}
Kind: {info.kind}
Identification: {info.identification or "N/A"}
Executable: {info.exe or "N/A"}
CWD: {info.cwd or "N/A"}
UID/EUID: {info.uid}/{info.euid}
GID/EGID: {info.gid}/{info.egid}
Parent PID: {info.parent_pid or "N/A"}"""

    return ToolReturn(
        return_value=formatted,
        metadata={
            "pid": pid,
            "process_info": {
                "name": info.name,
                "kind": info.kind,
                "identification": info.identification,
                "parent_pid": info.parent_pid,
                "uid": info.uid,
                "euid": info.euid,
                "gid": info.gid,
                "egid": info.egid,
                "exe": info.exe,
                "cwd": info.cwd,
                "argv": info.argv,
                "env": info.env,
            },
        },
    )


@shell_toolset.tool
@suppress_errors
async def command_history(ctx: RunContext[PiDeps], n: int = 10) -> ToolReturn:
    """Get the last n commands from shell history with their execution info."""
    shell = protocols.shell.interface(ctx.deps.bus)
    history = await shell.command_history(n=n)

    # Format for LLM
    if not history:
        formatted = "No command history available."
    else:
        lines = ["Command History:"]
        for cmd in history:
            exit_status = (
                f"(exit: {cmd.exit_code})" if cmd.exit_code is not None else ""
            )
            lines.append(
                f"  [{cmd.command_number}] {cmd.command} {exit_status}"
            )
        formatted = "\n".join(lines)

    return ToolReturn(
        return_value=formatted,
        metadata={
            "n": n,
            "history": [
                {
                    "command_number": cmd.command_number,
                    "command": cmd.command,
                    "exit_code": cmd.exit_code,
                    "start_time": (
                        cmd.start_time.isoformat() if cmd.start_time else None
                    ),
                    "end_time": (
                        cmd.end_time.isoformat() if cmd.end_time else None
                    ),
                }
                for cmd in history
            ],
        },
    )


@shell_toolset.tool
@suppress_errors
async def command_output(
    ctx: RunContext[PiDeps], command_number: int
) -> ToolReturn:
    """Get the output of a specific command by its command number."""
    shell = protocols.shell.interface(ctx.deps.bus)
    output = await shell.command_output(command_number=command_number)

    # Format for LLM
    if output is None:
        formatted = f"No output available for command #{command_number}."
    else:
        formatted = f"Output of command #{command_number}:\n{output}"

    return ToolReturn(
        return_value=formatted,
        metadata={
            "command_number": command_number,
            "output": output,
        },
    )
