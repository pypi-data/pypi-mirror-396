from functools import wraps
from pathlib import Path
import traceback
from typing import Any, Callable, TypeVar, Awaitable, get_type_hints

from pydantic_ai import RunContext
from pydantic_ai.messages import ToolReturn

from pi._internal.agents.deps import PiDeps
from pi._internal import protocols
from pi._internal.bus import Bus


T = TypeVar("T", bound=ToolReturn)


def suppress_errors(
    func: Callable[..., Awaitable[T]],
) -> Callable[..., Awaitable[T]]:
    """Decorator to catch and gracefully handle errors in agent tools."""

    # Get the return type annotation from the function
    type_hints = get_type_hints(func)
    return_type: type[T] = type_hints.get("return", ToolReturn)

    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            result = await func(*args, **kwargs)
            return result
        except Exception as e:
            ctx: RunContext[PiDeps] = args[0]
            assert ctx.tool_call_id is not None, (
                "tool_call_id must not be None"
            )
            assert ctx.tool_name is not None, "tool_name must not be None"

            error_type = type(e).__name__
            error_message = str(e)
            error_traceback = traceback.format_exc()

            to_llm = f"Tool failed with {error_type}:\n{error_message}"

            metadata = {
                "is_failure": True,  # for the ui adapter to render failure
                "error_type": error_type,
                "error_message": error_message,
                "error_traceback": error_traceback,
            }
            return return_type(return_value=to_llm, metadata=metadata)

    return wrapper


async def get_cwd(bus: Bus) -> Path:
    shell = protocols.shell.interface(bus)
    process_info = await shell.process_info()
    cwd = Path(process_info.cwd) if process_info.cwd else Path.cwd()
    return cwd


def resolve_path(base_path: Path, path: str) -> Path:
    """Resolve a path relative to the base path."""
    p = Path(path)
    return p if p.is_absolute() else (base_path / p).resolve()
