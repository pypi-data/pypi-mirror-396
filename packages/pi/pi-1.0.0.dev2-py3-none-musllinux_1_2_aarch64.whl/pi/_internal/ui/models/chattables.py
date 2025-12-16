from typing import Protocol, Any, Literal

# UI models adhering to the Chattable protocol are used to render
# content into the Chat widget


class Chattable(Protocol):
    def get_chat_header(self) -> str | None: ...
    def get_chat_markdown_content(self) -> str: ...
    def get_chat_details(self) -> str | None: ...

    @property
    def css_class(self) -> str: ...

    @property
    def has_slimbox(self) -> bool: ...

    @property
    def can_focus(self) -> bool: ...


class UserMessage(Chattable):
    def __init__(self, content: str) -> None:
        self.content = content

    def get_chat_header(self) -> str | None:
        return None

    def get_chat_markdown_content(self) -> str:
        return self.content

    def get_chat_details(self) -> str | None:
        return None

    @property
    def css_class(self) -> str:
        return "user-message"

    @property
    def has_slimbox(self) -> bool:
        return True

    @property
    def can_focus(self) -> bool:
        return False


class ThinkingMessage(Chattable):
    def __init__(self, content: str) -> None:
        self.content = content

    def get_chat_header(self) -> str | None:
        return None

    def get_chat_markdown_content(self) -> str:
        return self.content

    def get_chat_details(self) -> str | None:
        return None

    @property
    def css_class(self) -> str:
        return "thinking-message"

    @property
    def has_slimbox(self) -> bool:
        return False

    @property
    def can_focus(self) -> bool:
        return False


class TextMessage(Chattable):
    def __init__(self, content: str) -> None:
        self.content = content

    def get_chat_header(self) -> str | None:
        return None

    def get_chat_markdown_content(self) -> str:
        return self.content

    def get_chat_details(self) -> str | None:
        return None

    @property
    def css_class(self) -> str:
        return "text-message"

    @property
    def has_slimbox(self) -> bool:
        return False

    @property
    def can_focus(self) -> bool:
        return False


class ToolMessage(Chattable):
    def __init__(
        self,
        tool_call_id: str,
        *,
        tool_name: str | None = None,
        tool_args: dict[str, Any] | None = None,
        result_status: Literal["success", "failure"] | None = None,
    ) -> None:
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.tool_call_id = tool_call_id
        self.result_status = result_status

    def get_chat_header(self) -> str | None:
        args = self.tool_args or {}

        match self.tool_name:
            case "exec":
                cmd = args.get("command")
                header = (
                    f"[bold $success]{self.tool_name}[/bold $success] "
                    f"[dim]({cmd})[/dim]"
                )
            case (
                "read_file"
                | "read_chunk"
                | "search_replace"
                | "rewrite"
                | "list_files"
            ):
                path = args.get("path")
                header = (
                    f"[bold $success]{self.tool_name}[/bold $success] "
                    f"[dim]({path})[/dim]"
                )
            case _:
                header = f"[bold $success]{self.tool_name}[/bold $success]"

        if self.result_status == "success":
            header += " [bold $success]✓[/bold $success]"
        elif self.result_status == "failure":
            header += " [bold $error]✗[/bold $error]"

        return header

    def get_chat_markdown_content(self) -> str:
        return ""

    def get_chat_details(self) -> str | None:
        return None

    @property
    def css_class(self) -> str:
        return "tool-message"

    @property
    def has_slimbox(self) -> bool:
        return False

    @property
    def can_focus(self) -> bool:
        # those tools don't have a panelable
        not_focusable = {
            "send_input",
            "kill",
            "wait",
            "current_screen",
            "eval_simple_python_expression",
        }
        return self.tool_name not in not_focusable


class ErrorMessage(Chattable):
    """Python exceptions that occur during agent execution"""

    error_name: str
    error_message: str

    def __init__(self, error: Exception, **kwargs: Any) -> None:
        self.error_name = type(error).__name__

        try:
            self.error_message = error.args[0]
        except KeyError:
            self.error_message = str(error)

        if self.error_message == self.error_name:
            self.error_message = ""

    def get_chat_header(self) -> str | None:
        return f"[bold $error]{self.error_name}[/bold $error]"

    def get_chat_markdown_content(self) -> str:
        content = ""

        if self.error_message:
            content += f"{self.error_message}"

        content += "\n\n**/error** to print full traceback"

        return content

    def get_chat_details(self) -> str | None:
        return None

    @property
    def css_class(self) -> str:
        return "error-message"

    @property
    def has_slimbox(self) -> bool:
        return False

    @property
    def can_focus(self) -> bool:
        return True
