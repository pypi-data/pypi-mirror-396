from __future__ import annotations

import asyncio
import dataclasses

from pi._internal import bus
from pi._internal.agents.storage import Session


@dataclasses.dataclass(kw_only=True)
class PiDeps:
    bus: bus.Bus
    session: Session
    edit_lock: asyncio.Lock = dataclasses.field(default_factory=asyncio.Lock)
