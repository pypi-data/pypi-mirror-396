from collections.abc import AsyncIterator
from typing import AsyncGenerator, Any

from pydantic_graph import GraphRunContext, End

from pydantic_ai import Agent
from pydantic_ai._agent_graph import (
    GraphAgentState,
    GraphAgentDeps,
    AgentNode,
)
from pydantic_ai.result import AgentStream, FinalResult
from pydantic_ai.messages import AgentStreamEvent, HandleResponseEvent

from pi._internal import agents


async def stream_node(
    agent: Agent[agents.deps.PiDeps, str],
    node: AgentNode[agents.deps.PiDeps, str] | End[FinalResult[str]],
    run_ctx: GraphRunContext[
        GraphAgentState, GraphAgentDeps[agents.deps.PiDeps, str]
    ],
) -> AsyncGenerator[AgentStreamEvent, None]:
    deps = run_ctx.deps.user_deps

    if agent.is_model_request_node(node) or agent.is_call_tools_node(node):
        stream: AgentStream[Any, Any] | AsyncIterator[HandleResponseEvent]
        async with node.stream(run_ctx) as stream:
            async for model_event in stream:
                deps.session.record_event(model_event)
                yield model_event


async def run_agent(
    agent: Agent[agents.deps.PiDeps, str],
    *,
    user_prompt: str,
    deps: agents.deps.PiDeps,
) -> AsyncGenerator[AgentStreamEvent, None]:
    message_history = deps.session.get_pydantic_ai_history()

    async with agent.iter(
        user_prompt, deps=deps, message_history=message_history
    ) as run:
        async for node in run:
            async for event in stream_node(agent, node, run.ctx):
                yield event
