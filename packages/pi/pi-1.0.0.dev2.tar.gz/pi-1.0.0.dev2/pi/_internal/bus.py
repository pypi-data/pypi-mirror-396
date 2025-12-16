from __future__ import annotations
from typing import TYPE_CHECKING, Any, Protocol, TypedDict, cast

import asyncio
import collections
import dataclasses
import json
import os
import uuid
import pathlib


if TYPE_CHECKING:
    from collections.abc import Mapping

    type Payload = Mapping[str, Any]

    class AsyncCallback(Protocol):
        async def __call__(self, **kwargs: Any) -> Any:
            pass


class Message(TypedDict):
    id: str
    message_name: str
    response_to: str | None
    payload: Payload
    receiver: str
    sender: str


class RegisterMessage(TypedDict):
    well_known_name: str | None
    description: str | None


class ErrorMessage(TypedDict):
    id: str | None
    error: str


def new_message(
    message_name: str,
    payload: Payload,
    receiver: str,
    sender: str,
    response_to: str | None = None,
) -> Message:
    return Message(
        id=str(uuid.uuid4()),
        message_name=message_name,
        response_to=response_to,
        payload=payload,
        receiver=receiver,
        sender=sender,
    )


class Bus:
    client_name: str | None
    client_id: str

    _listener_task: asyncio.Task[None] | None
    _waiters: dict[str, asyncio.Future[Any]]
    _subscribers: dict[
        str,
        list[AsyncCallback],
    ]
    _implementations: dict[str, AsyncCallback]

    def __init__(self) -> None:
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None
        self.name = None
        self._connected = False
        self._lock = asyncio.Lock()
        self._listener_task = None
        self._waiters = {}
        self._subscribers = collections.defaultdict(list)
        self._implementations = {}

    async def _listener(self) -> None:
        while True:
            message = await self._receive_message()
            await self._handle_message(message)

    async def _respond(self, message: Message) -> None:
        if message["message_name"] not in self._implementations:
            response = new_message(
                receiver=message["sender"],
                sender=self.client_id,
                payload=ErrorMessage(
                    id=message["id"],
                    error=f"Unknown RPC method {message['message_name']}",
                ),
                message_name="ErrorMessage",
                response_to=message["id"],
            )
            await self._send_message(response)
            return

        meth = self._implementations[message["message_name"]]
        result = await meth(**message["payload"])

        if dataclasses.is_dataclass(result):
            assert not isinstance(result, type)
            ser_result = dataclasses.asdict(result)
        else:
            ser_result = result

        response = new_message(
            receiver=message["sender"],
            sender=self.client_id,
            payload={"result": ser_result},
            message_name=message["message_name"],
            response_to=message["id"],
        )

        await self._send_message(response)

    def subscribe(
        self,
        message_name: str,
        subscriber: AsyncCallback,
    ) -> None:
        """Subscribe to a given broadcast message."""
        self._subscribers[message_name].append(subscriber)

    def implement(
        self,
        message_name: str,
        callback: AsyncCallback,
    ) -> None:
        if message_name in self._implementations:
            raise RuntimeError(
                f"Message {message_name!r} is already implemented"
            )

        self._implementations[message_name] = callback

    async def _dispatch_broadcast(
        self,
        message_name: str,
        payload: Payload,
    ) -> None:
        subscribers = self._subscribers.get(message_name)
        if subscribers:
            for sub in subscribers:
                asyncio.create_task(sub(**payload))

    async def _send_message(self, message: Message) -> None:
        """Send a null-terminated JSON message."""
        if not self.writer:
            raise RuntimeError("Not connected")

        message_bytes = json.dumps(message).encode("utf-8") + b"\0"
        self.writer.write(message_bytes)
        await self.writer.drain()

    async def _receive_message(self) -> Message:
        """Receive a null-terminated JSON message."""
        if not self.reader:
            raise RuntimeError("Not connected")

        data = b""
        while True:
            chunk = await self.reader.read(1)
            if not chunk:
                raise ConnectionError("Socket closed")
            if chunk == b"\0":
                break
            data += chunk

        msg = json.loads(data.decode("utf-8"))

        assert isinstance(msg, dict)
        assert "id" in msg
        return cast("Message", msg)

    async def _connect(
        self,
        *,
        name: str | None = None,
        socket_path: str | pathlib.Path | None = None,
    ) -> None:
        if self._connected:
            return

        async with self._lock:
            if self._connected:
                return

            # Get socket path from environment if not passed explicitly
            if not socket_path:
                socket_path = os.environ.get("PI_SOCKET")

            if not socket_path:
                raise RuntimeError("PI_SOCKET environment variable not set")

            # Connect to Unix socket
            self.reader, self.writer = await asyncio.open_unix_connection(
                socket_path
            )

            register_message = new_message(
                receiver="router",
                sender="00000000-0000-0000-0000-000000000000",
                payload=RegisterMessage(
                    well_known_name=name,
                    description=f"Python async client: {name}"
                    if name
                    else None,
                ),
                message_name="RegisterMessage",
                response_to=None,
            )

            message_id = register_message["id"]
            await self._send_message(register_message)

            message_box: list[Message] = []

            # depending on other concurrent events,
            # the first received message may be not a registration response,
            # but some broadcasted message. we still want to process them,
            # but only after we properly initialize the bus
            while True:
                message = await self._receive_message()
                if message["response_to"] == message_id:
                    break

                message_box.append(message)

            # Check if registration was successful
            if message.get("message_name") == "ErrorMessage":
                error_msg = message["payload"].get(
                    "error", "Unknown registration error"
                )
                raise RuntimeError(f"Registration failed: {error_msg}")

            # Extract client ID
            self.client_id = message["payload"]["client_id"]
            self.client_name = name

            # handle any pending messages, before
            # we start listening for anything new
            for message in message_box:
                await self._handle_message(message)

            self._listener_task = asyncio.create_task(self._listener())
            self._connected = True

    async def call(
        self,
        *,
        receiver: str,
        message_name: str,
        payload: dict[str, Any],
        timeout: float,
        wait_for_response: bool = True,
    ) -> dict[str, Any] | None:
        """
        Send a message and optionally wait for response.

        Args:
            receiver: Target receiver (well-known name or UUID)
            message_name: Type of message (e.g., "TerminalInfoRequest")
            payload: Message payload as dict
            timeout: Timeout in seconds when waiting for response

        Returns:
            Response message dict
        """
        if not self._connected:
            raise RuntimeError("Not connected. Call connect() first.")

        message = new_message(
            receiver=receiver,
            sender=self.client_id,
            payload=payload,
            message_name=message_name,
        )

        message_id = message["id"]

        await self._send_message(message)

        if not wait_for_response:
            return None

        waiter: asyncio.Future[dict[str, Any]] = asyncio.Future()
        self._waiters[message_id] = waiter

        try:
            async with asyncio.timeout(timeout):
                return await waiter
        except TimeoutError:
            raise TimeoutError(
                f"No response received within {timeout} seconds"
            ) from None

    async def close(self) -> None:
        """Close the connection."""

        if self._listener_task:
            self._listener_task.cancel()
            self._listener_task = None
        for waiter in self._waiters.values():
            waiter.cancel()
        self._waiters.clear()

        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()

        self._connected = False
        del self.client_id
        self.reader = None
        self.writer = None

    async def _handle_message(self, message: Message) -> None:
        receiver = message["receiver"]

        if receiver == "broadcast":
            await self._dispatch_broadcast(
                message["message_name"],
                message["payload"],
            )
            return

        assert receiver == self.client_id or (
            self.client_name is not None and receiver == self.client_name
        )

        req_id = message["response_to"]
        if req_id is None:
            # a call to us
            asyncio.create_task(self._respond(message))

        else:
            # result of our call

            waiter = self._waiters.pop(req_id)
            if waiter.cancelled():
                return

            if message.get("message_name") == "ErrorMessage":
                error_msg = message["payload"].get(
                    "error", "Unknown registration error"
                )
                error = RuntimeError(f"RPC call failed: {error_msg}")
                waiter.set_exception(error)
            else:
                waiter.set_result(message)


async def connect(
    *,
    name: str | None = None,
    socket_path: str | pathlib.Path | None = None,
) -> Bus:
    bus = Bus()
    await bus._connect(name=name, socket_path=socket_path)
    return bus
