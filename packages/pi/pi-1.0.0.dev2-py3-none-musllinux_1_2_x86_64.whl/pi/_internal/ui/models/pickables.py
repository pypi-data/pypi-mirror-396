import dataclasses
from datetime import datetime
from typing import Any, Protocol, Self

from pi._internal.agents.storage import Session


# UI models adhering to the Pickable protocol are used to render
# content into the SidebarInput's Picker widget


class Pickable(Protocol):
    def get_picker_label(self) -> str: ...
    def get_picker_sort_key(self) -> Any: ...


@dataclasses.dataclass
class Command(Pickable):
    """A command that can be executed from the command palette"""

    id: str
    label: str
    description: str
    score: float = 0.0  # Fuzzy match score for sorting

    def get_picker_label(self) -> str:
        """Return label for Pickable protocol with formatting"""
        # Show command with "/" prefix and dim description
        return f"[bold]{self.id}[/bold] [dim]{self.description}[/dim]"

    def get_picker_sort_key(self) -> Any:
        """Return sort key for Pickable protocol"""
        # Higher score = better match
        return self.score


class PickableNewSession(Pickable):
    """Represents the 'New Session' option in the session list"""

    def get_picker_label(self) -> str:
        return "[bold]+ New Session[/bold]"

    def get_picker_sort_key(self) -> Any:
        # Always sort to the top by returning a future datetime
        return datetime.max


class PickableSession(Pickable):
    """Wrapper around Session that makes it listable in the session list"""

    def __init__(self, session: Session):
        self.session = session

    @classmethod
    def from_session(cls, session: Session) -> Self:
        """Create a wrapper around the given session"""
        return cls(session)

    def get_picker_label(self) -> str:
        """Return formatted label for UI display"""
        date_str = self.session.created_at.strftime("%Y-%m-%d %H:%M")
        name = self.session.display_name
        return f"[bold]{name}[/bold]\n[dim]{date_str}[/dim]"

    def get_picker_sort_key(self) -> Any:
        """Return sort key for ordering (Pickable protocol)"""
        return self.session.updated_at
