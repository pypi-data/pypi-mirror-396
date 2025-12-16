from __future__ import annotations

import os
from pathlib import Path
import pydantic_ai

from pi._internal.agents.deps import PiDeps
from pi._internal.agents.history import save_new_messages, repair_tool_calls
from pi._internal.agents.tools import shell, context, edit


try:
    import logfire
    import logfire.exceptions
except ImportError:
    pass
else:
    try:
        logfire.configure(console=False)
        logfire.instrument_pydantic_ai()
    except logfire.exceptions.LogfireConfigError as ex:
        if "authenticate" not in str(ex):
            raise ex


_PI_DISABLE_CAPTIVE = os.environ.get("_PI_DISABLE_CAPTIVE") == "1"

if _PI_DISABLE_CAPTIVE:
    from pi._internal.agents.tools.exec_raw import exec_toolset
else:
    from pi._internal.agents.tools.exec_pi_captive import exec_toolset


PROMPTS_DIR = Path(__file__).parent / "prompts"


pi_agent = pydantic_ai.Agent[PiDeps, str](
    defer_model_check=True,
    deps_type=PiDeps,
    toolsets=[
        shell.shell_toolset,
        exec_toolset,
        context.context_toolset,
        edit.edit_toolset,
    ],
    history_processors=[repair_tool_calls, save_new_messages],
)


@pi_agent.system_prompt
async def pi_prompt(
    ctx: pydantic_ai.RunContext[PiDeps],
) -> str:
    return (PROMPTS_DIR / "PI_PROMPT.md").read_text()
