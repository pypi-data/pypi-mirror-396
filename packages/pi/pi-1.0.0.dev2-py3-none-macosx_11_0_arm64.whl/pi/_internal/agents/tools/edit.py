import difflib
from rapidfuzz import fuzz
from pydantic_ai import RunContext
from pydantic_ai.messages import ToolReturn
from pydantic_ai.toolsets import FunctionToolset

from pi._internal.agents.deps import PiDeps
from pi._internal.agents.common import suppress_errors
from pi._internal.agents.common import resolve_path, get_cwd

edit_toolset = FunctionToolset[PiDeps]()


@edit_toolset.tool
@suppress_errors
async def search_replace(
    ctx: RunContext[PiDeps],
    path: str,
    search: str,
    replace: str,
) -> ToolReturn:
    """
    Search and replace a single occurrence with exact and fuzzy matching.

    Args:
        path: The path to the file to search and replace in
        search: The text to search for
        replace: The replacement text
    """
    assert ctx.tool_call_id is not None, "tool_call_id must not be None"
    assert ctx.tool_name is not None, "tool_name must not be None"

    FUZZY_THRESHOLD = 80.0  # used when exact match fails

    cwd = await get_cwd(ctx.deps.bus)
    resolved_path = resolve_path(cwd, path)

    async with ctx.deps.edit_lock:
        # Read file
        old_content = resolved_path.read_text(encoding="utf-8")

        # -----------------
        # Apply replacement
        # -----------------
        if search in old_content:
            # strategy 1: exact match
            new_content = old_content.replace(search, replace, 1)
        else:
            # strategy 2: fuzzy match
            lines = old_content.splitlines(keepends=True)
            search_lines = search.splitlines()

            assert search_lines, "Search text can't be empty"

            # find best matching window
            best_score = 0.0
            best_start_line = -1

            for i in range(len(lines) - len(search_lines) + 1):
                window = lines[i : i + len(search_lines)]
                window_text = "".join(window)

                score = fuzz.ratio(search, window_text)

                if score > best_score:
                    best_score = score
                    best_start_line = i

            if best_score < FUZZY_THRESHOLD:
                raise ValueError(
                    "Search text did not match any part of the file, "
                    "please double check."
                )

            # apply replacement
            new_lines = lines[:best_start_line]
            new_lines.extend(replace.splitlines(keepends=True))
            new_lines.extend(lines[best_start_line + len(search_lines) :])
            new_content = "".join(new_lines)

    # ------------------------------------------
    # Write result and create diff for metadata
    # ------------------------------------------
    diff_lines = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile=f"{path} (before)",
        tofile=f"{path} (after)",
        lineterm="",
    )
    diff = "\n".join(diff_lines)

    resolved_path.write_text(new_content, encoding="utf-8")

    # format output for the llm
    to_llm = f"Updated file: {path}"

    metadata = {
        "path": path,
        "action": "search_replace",
        "diff": diff,
    }

    return ToolReturn(
        return_value=to_llm,
        metadata=metadata,
    )


@edit_toolset.tool
@suppress_errors
async def rewrite(
    ctx: RunContext[PiDeps], path: str, content: str
) -> ToolReturn:
    """
    Write content to a file, creating directories and file if needed.

    Args:
        path: File path to write (relative paths resolve to workspace)
        content: Content to write to the file (overwrites existing content)
    """
    assert ctx.tool_call_id is not None, "tool_call_id must not be None"
    assert ctx.tool_name is not None, "tool_name must not be None"

    cwd = await get_cwd(ctx.deps.bus)
    resolved_path = resolve_path(cwd, path)

    async with ctx.deps.edit_lock:
        try:
            old_content = resolved_path.read_text(encoding="utf-8")
            file_existed = True
        except FileNotFoundError:
            # file doesn't exist
            old_content = ""
            file_existed = False

        diff_lines = difflib.unified_diff(
            old_content.splitlines(),
            content.splitlines(),
            fromfile=f"{path} (before)",
            tofile=f"{path} (after)",
            lineterm="",
        )
        diff = "\n".join(diff_lines)

        # Create parent directories if needed
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
        resolved_path.write_text(content, encoding="utf-8")

    # format output for the llm
    if file_existed:
        to_llm = f"Updated file: {path}"
    else:
        to_llm = f"Created file: {path}"

    metadata = {
        "path": path,
        "action": "update" if file_existed else "create",
        "diff": diff,
        "new_lines": len(content.splitlines()),
    }

    return ToolReturn(
        return_value=to_llm,
        metadata=metadata,
    )
