from pydantic_ai import RunContext
from pydantic_ai.messages import ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from pi._internal.agents.deps import PiDeps
from pi._internal.agents.common import suppress_errors, resolve_path, get_cwd


context_toolset = FunctionToolset[PiDeps]()


@context_toolset.tool
@suppress_errors
async def list_files(ctx: RunContext[PiDeps], path: str) -> ToolReturn:
    """
    List files and directories in the specified path.

    Args:
        path: Directory path to list (relative paths resolve to workspace)
    """
    assert ctx.tool_call_id is not None, "tool_call_id must not be None"
    assert ctx.tool_name is not None, "tool_name must not be None"

    cwd = await get_cwd(ctx.deps.bus)
    resolved_path = resolve_path(cwd, path)

    if not resolved_path.is_dir():
        raise ValueError(f"Path '{path}' is not a directory")

    result = []
    for item in sorted(resolved_path.iterdir()):
        file_type = "directory" if item.is_dir() else "file"
        try:
            size = item.stat().st_size if item.is_file() else 0
        except OSError:
            size = 0
        result.append(f"{item.name} ({file_type}, {size} bytes)")

    to_llm = "\n".join(result) if result else f"Directory '{path}' is empty."
    metadata = {
        "path": path,
    }

    return ToolReturn(
        return_value=to_llm,
        metadata=metadata,
    )


@context_toolset.tool
@suppress_errors
async def read_file(ctx: RunContext[PiDeps], path: str) -> ToolReturn:
    """
    Read and return the complete content of a file.

    Args:
        path: File path to read (relative paths resolve to workspace)
    """
    assert ctx.tool_call_id is not None, "tool_call_id must not be None"
    assert ctx.tool_name is not None, "tool_name must not be None"

    cwd = await get_cwd(ctx.deps.bus)
    resolved_path = resolve_path(cwd, path)

    to_llm = resolved_path.read_text(encoding="utf-8")
    metadata = {"path": path}

    return ToolReturn(
        return_value=to_llm,
        metadata=metadata,
    )


@context_toolset.tool
@suppress_errors
async def read_chunk(
    ctx: RunContext[PiDeps], path: str, from_line: int, to_line: int
) -> ToolReturn:
    """
    Read a chunk of a file.

    Args:
        path: File path to read (relative paths resolve to workspace)
        from_line: Starting line number (0-indexed)
        to_line: Ending line number (0-indexed)
    """
    assert ctx.tool_call_id is not None, "tool_call_id must not be None"
    assert ctx.tool_name is not None, "tool_name must not be None"

    cwd = await get_cwd(ctx.deps.bus)
    resolved_path = resolve_path(cwd, path)

    content = resolved_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # ensure chunk is within bounds.
    # the agent doesn't know the line count ahead of time
    # so we can't expect it to guess correctly
    bound_from_line = min(max(0, from_line), len(lines) - 1)
    bound_to_line = min(max(bound_from_line, to_line), len(lines) - 1)

    chunk = "\n".join(lines[bound_from_line : bound_to_line + 1])

    to_llm = f"Resolved lines: {bound_from_line} to {bound_to_line}\n\n{chunk}"
    metadata = {
        "path": path,
        "from_line": from_line,
        "to_line": to_line,
        "bound_from_line": bound_from_line,
        "bound_to_line": bound_to_line,
        "chunk": chunk,
    }

    return ToolReturn(return_value=to_llm, metadata=metadata)
