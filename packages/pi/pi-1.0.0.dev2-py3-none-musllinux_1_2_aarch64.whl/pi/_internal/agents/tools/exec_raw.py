import asyncio
import asyncio.subprocess
import codecs
import os

from pydantic_ai import RunContext
from pydantic_ai.messages import ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from pi._internal.agents.deps import PiDeps
from pi._internal.agents.common import suppress_errors
from pi._internal import protocols


exec_toolset = FunctionToolset[PiDeps]()


@exec_toolset.tool
@suppress_errors
async def exec(
    ctx: RunContext[PiDeps],
    command: str,
    timeout: int = 60,
) -> ToolReturn:
    """
    Execute a shell command.

    Args:
        command: Shell command to execute
        timeout: Command timeout in seconds
    """
    assert ctx.tool_call_id is not None, "tool_call_id must not be None"
    assert ctx.tool_name is not None, "tool_name must not be None"

    try:
        unescaped_command = codecs.decode(command, "unicode_escape")
    except (UnicodeDecodeError, ValueError):
        unescaped_command = command

    shell = protocols.shell.interface(ctx.deps.bus)
    process_info = await shell.process_info()
    cwd = process_info.cwd or os.getcwd()

    process: asyncio.subprocess.Process | None = None

    wrapped_command = ["sh", "-c", f"cd {cwd} && {unescaped_command}"]

    process = await asyncio.create_subprocess_exec(
        *wrapped_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=timeout,
    )

    output = stdout.decode("utf-8", errors="replace")
    if stderr:
        error_output = stderr.decode("utf-8", errors="replace")
        if error_output.strip():
            output += f"\nSTDERR:\n{error_output}"

    to_llm = output
    metadata = {
        "command": command,
        "wrapped_command": wrapped_command,
        "cwd": cwd,
        "timeout": timeout,
    }

    return ToolReturn(
        return_value=to_llm,
        metadata=metadata,
    )
