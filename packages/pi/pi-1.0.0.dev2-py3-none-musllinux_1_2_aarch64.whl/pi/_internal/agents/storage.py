from dataclasses import dataclass, field
from datetime import datetime
import uuid
from pydantic_ai import PartEndEvent
from pydantic_ai.messages import (
    ModelMessage,
    ModelResponse,
    ModelRequest,
    PartStartEvent,
    PartDeltaEvent,
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    FinalResultEvent,
    AgentStreamEvent,
    ModelResponsePart,
    ThinkingPartDelta,
    TextPartDelta,
    ToolCallPartDelta,
    ThinkingPart,
    TextPart,
    ToolCallPart,
)

from pi._internal import protocols
from pydantic_ai.messages import ToolReturnPart, RetryPromptPart


def fix_stray_tool_calls(messages: list[ModelMessage]) -> list[ModelMessage]:
    # this is called twice because for whatever reason Pydantic AI
    # does history validation *before* calling history preprocesors,
    # so we have to repair history when we fetch it from storage.

    # at the same time fetch is only called once before the run, and
    # history can get corrupted in the middle of the run, so we have to
    # also call this in the preprocessor.

    assert isinstance(messages[-1], ModelRequest), (
        "Expected last message to be ModelRequest, "
        f"got {type(messages[-1]).__name__}"
    )

    # track tool calls that need returns
    # tool_call_id -> ToolCallPart

    stray_tool_calls: dict[str, ToolCallPart] = {}

    for message in messages:
        if isinstance(message, ModelResponse):
            # collect all tool calls from this response
            for response_part in message.parts:
                if isinstance(response_part, ToolCallPart):
                    stray_tool_calls[response_part.tool_call_id] = (
                        response_part
                    )

        elif isinstance(message, ModelRequest):
            # remove tool calls for which there's a return
            # ToolReturnPart for successful calls
            # RetryPromptPart for validation errors
            for request_part in message.parts:
                if isinstance(request_part, (ToolReturnPart, RetryPromptPart)):
                    stray_tool_calls.pop(request_part.tool_call_id, None)

    # handle stray tool calls
    if stray_tool_calls:
        missing_returns: list[ToolReturnPart] = []

        for tool_call_id, tool_call in stray_tool_calls.items():
            missing_returns.append(
                ToolReturnPart(
                    tool_name=tool_call.tool_name,
                    content=(
                        "Missing tool execution result "
                        "(likely due to interruption). "
                        "Please re-call the tool if necessary."
                    ),
                    metadata={"is_failure": True},  # flag for the ui adapter
                    tool_call_id=tool_call_id,
                )
            )

        messages[-1].parts = missing_returns + list(messages[-1].parts)

    return messages


@dataclass
class Session:
    id_: uuid.UUID
    display_name: str = field(default="New robot")

    messages: list[ModelMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    process_info: protocols.shell.ProcessInfo | None = None

    @property
    def process_name(self) -> str:
        return (
            self.process_info.name if self.process_info else "unknown process"
        )

    def record_event(self, event: AgentStreamEvent) -> None:
        # This method will record all the messages that happen *during* the run
        # This includes thinking, text, tool calls, and tool results.
        # Not user or system message though, because there is no convenient way
        # to intercerpt them before all other messages.

        match event:
            case PartStartEvent(part=part):
                # append this new part to history as part of a ModelResponse
                # then we're going to use it to apply all the deltas to it

                if self.messages and isinstance(
                    self.messages[-1], ModelResponse
                ):
                    response = self.messages[-1]
                else:
                    response = ModelResponse(parts=[])
                    self.messages.append(response)

                # because .parts is now a Sequence, but we still have to
                # modify it to assemble correct inputs for the next run,
                # we're gonna be doing this conversion to list
                response.parts = list(response.parts)
                response.parts.append(part)

            case PartDeltaEvent(delta=delta):
                assert self.messages, "History shouldn't be empty by now"
                assert isinstance(self.messages[-1], ModelResponse), (
                    "Last message should be a ModelResponse, "
                    "missing start event?"
                )

                # see the comment above
                self.messages[-1].parts = list(self.messages[-1].parts)

                response = self.messages[-1]
                last_part = response.parts[-1]

                # sometimes there's a type mismatch between the delta
                # and the last part that causes a runtime error.
                # right now it's not clear how to prevent this mismatch,
                # so here's an ugly hack
                match delta:
                    case ThinkingPartDelta():
                        if not isinstance(last_part, ThinkingPart):
                            self.messages[-1].parts.append(
                                ThinkingPart(content="")
                            )
                    case TextPartDelta():
                        if not isinstance(last_part, TextPart):
                            self.messages[-1].parts.append(
                                TextPart(content="")
                            )
                    case ToolCallPartDelta():
                        if not isinstance(last_part, ToolCallPart):
                            self.messages[-1].parts.append(
                                ToolCallPart(tool_name="", args={})
                            )
                    case _:
                        # in case there's all of a sudden a new kind of delta
                        # that we need to handle after some version bump
                        raise ValueError(f"Unknown delta type: {type(delta)}")

                # replace with new part that's longer by one delta
                self.messages[-1].parts[-1] = delta.apply(
                    self.messages[-1].parts[-1]
                )

            case FunctionToolCallEvent(part=_part):
                # this is also part of a ModelResponse
                # because it's generated by the model

                # we're calling it _part because otherwise mypy things
                # that it's shadowed in the function below

                if self.messages and isinstance(
                    self.messages[-1], ModelResponse
                ):
                    response = self.messages[-1]
                else:
                    response = ModelResponse(parts=[])
                    self.messages.append(response)

                def is_duplicate(recorded_part: ModelResponsePart) -> bool:
                    return (
                        isinstance(recorded_part, ToolCallPart)
                        and recorded_part.tool_call_id == _part.tool_call_id
                    )

                if any(
                    is_duplicate(recorded_part)
                    for recorded_part in response.parts
                ):
                    pass
                    # the event gets emitted twice for some reason,
                    # so we'll ignore the second one
                else:
                    # see the comment above
                    response.parts = list(response.parts)
                    response.parts.append(_part)

            case FunctionToolResultEvent(result=result):
                # this is part of a ModelRequest because it's generated
                # by the framework from the app side
                if self.messages and isinstance(
                    self.messages[-1], ModelRequest
                ):
                    request = self.messages[-1]
                else:
                    request = ModelRequest(parts=[])
                    self.messages.append(request)

                # see the comment above
                request.parts = list(request.parts)
                request.parts.append(result)

            case PartEndEvent(part=part):
                # this is a newly introduced event that provides a complete
                # part after it's done streaming. our current setup works
                # without it, but in the future we should consider refactoring.
                pass
            case FinalResultEvent():
                pass  # ignore final result,
                # normally it's a duplicate of the last message
            case _:
                raise ValueError(f"Unknown event type: {event.event_kind}")

    def add_message(self, message: ModelMessage) -> None:
        # This method is used to record user and system messages
        # from the history processor. That way they can be put before
        # all the other messages.
        self.messages.append(message)

    def get_pydantic_ai_history(self) -> list[ModelMessage]:
        if not self.messages:
            return []

        # verify the last message is a ModelRequest, which it has to be
        # by design of the history processors mechanism
        last_message = self.messages[-1]
        if not isinstance(last_message, ModelRequest):
            self.messages.append(ModelRequest(parts=[]))
            last_message = self.messages[-1]

        self.messages = fix_stray_tool_calls(self.messages)
        return self.messages

    def get_tool_result(self, tool_call_id: str) -> ToolReturnPart | None:
        for message in self.messages:
            if isinstance(message, ModelRequest):
                for part in message.parts:
                    if (
                        isinstance(part, ToolReturnPart)
                        and part.tool_call_id == tool_call_id
                    ):
                        return part
        return None


@dataclass
class HistoryStorage:
    sessions: dict[uuid.UUID, Session] = field(default_factory=dict)

    def create_session(
        self, process_info: protocols.shell.ProcessInfo | None = None
    ) -> Session:
        session = Session(id_=uuid.uuid4(), process_info=process_info)
        self.sessions[session.id_] = session
        return session

    def get_session(self, session_id: uuid.UUID) -> Session | None:
        return self.sessions.get(session_id, None)
