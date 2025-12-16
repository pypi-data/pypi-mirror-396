from typing import Protocol
from dataclasses import dataclass

from pi._internal import rpc
from pi._internal import bus as _bus


@dataclass(frozen=True, kw_only=True)
class WellKnownProcess:
    client_id: str
    name: str
    description: str | None


@rpc.export
class Router(Protocol):
    async def list_well_known_processes(
        self,
    ) -> dict[str, WellKnownProcess]: ...


@rpc.export
class RouterClient(Protocol):
    async def well_known_peers_changed(
        self,
        *,
        peers: dict[str, WellKnownProcess],
    ) -> None: ...


def interface(bus: _bus.Bus) -> Router:
    return rpc.get_interface(Router, bus, "router")  # type: ignore [type-abstract]
