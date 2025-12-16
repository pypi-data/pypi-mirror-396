import json
from collections.abc import AsyncIterator
from enum import Enum
from typing import Any

from asgikit._constants import SCOPE_ASGIKIT, STATE, WEBSOCKET
from asgikit.exceptions import (
    AsgiException,
    WebSocketStateError,
    WebSocketClosedError,
    WebSocketDisconnect,
)
from asgikit.headers import encode_headers

__all__ = ("WebSocket", "WebSocketState")


class WebSocketState(Enum):
    """State of the WebSocket connection"""

    NEW = 1
    """Created, not yet accepted"""

    CONNECTED = 2
    """Received the connect event"""

    ACCEPTED = 3
    """Websocket accepted"""

    CLOSED = 4
    """Websocket closed"""


class WebSocket:
    """Represents a WebSocket connection"""

    __slots__ = ("_scope", "_receive", "_send")

    def __init__(self, scope, receive, send):
        self._scope = scope
        self._receive = receive
        self._send = send

        self._scope.setdefault(SCOPE_ASGIKIT, {})
        self._scope[SCOPE_ASGIKIT].setdefault(WEBSOCKET, {})
        self._scope[SCOPE_ASGIKIT][WEBSOCKET].setdefault(STATE, WebSocketState.NEW)

    @property
    def state(self) -> WebSocketState:
        """State of the websocket connection"""
        return self._scope[SCOPE_ASGIKIT][WEBSOCKET][STATE]

    def __set_state(self, state: WebSocketState):
        self._scope[SCOPE_ASGIKIT][WEBSOCKET][STATE] = state

    @property
    def subprotocols(self) -> list[str]:
        """Return a list of subprotocols of this WebSocket connection"""
        return self._scope["subprotocols"]

    async def __connect(self):
        message = await self._receive()
        if message["type"] != "websocket.connect":
            raise AsgiException(f"Unexpected asgi message: {message['type']}")

        self.__set_state(WebSocketState.CONNECTED)

    async def accept(
        self,
        subprotocol: str = None,
        headers: dict[str, str] = None,
    ):
        """Accepts the WebSocket connection

        :raise WebSocketStateError: If the WebSocket has already been accepted
        """

        assert self._scope["type"] == "websocket"

        if self.state != WebSocketState.NEW:
            raise WebSocketStateError()

        await self.__connect()

        encoded_headers = encode_headers(headers or {})

        await self._send(
            {
                "type": "websocket.accept",
                "subprotocol": subprotocol,
                "headers": encoded_headers,
            }
        )

        self.__set_state(WebSocketState.ACCEPTED)

    async def _read(self) -> dict[str, Any]:
        """Receive data from the WebSocket connection

        :raise WebSocketStateError: If the WebSocket is not yet accepted
        :raise WebSocketClosedError: If the WebSocket is closed
        :raise WebSocketDisconnect: if the client disconnect
        """

        if self.state == WebSocketState.CLOSED:
            raise WebSocketClosedError()

        if self.state != WebSocketState.ACCEPTED:
            raise WebSocketStateError()

        message = await self._receive()
        if message["type"] == "websocket.disconnect":
            self.__set_state(WebSocketState.CLOSED)
            raise WebSocketDisconnect(message["code"], message.get("reason"))

        if message["type"] != "websocket.receive":
            raise AsgiException(f"Invalid message: {message['type']}")

        return message

    async def read(self) -> str | bytes:
        """Read data from the WebSocket connection

        Data can be either str or bytes
        """

        message = await self._read()
        return message.get("text") or message.get("bytes")

    async def iter(self) -> AsyncIterator[str | bytes]:
        """Iterate over data from the WebSocket connection

        Data can be either str or bytes
        """
        try:
            while True:
                yield await self.read()
        except WebSocketDisconnect:
            pass

    async def read_json(self) -> Any:
        """Read data as json from the WebSocket connection"""

        data = await self.read()
        return json.loads(data)

    async def iter_json(self) -> AsyncIterator[Any]:
        """Iterate over data as json from the WebSocket connection"""

        async for data in self.iter():
            yield json.loads(data)

    async def _write(self, message: dict[str, Any]):
        if self.state == WebSocketState.CLOSED:
            raise WebSocketClosedError()

        if self.state != WebSocketState.ACCEPTED:
            raise WebSocketStateError()

        await self._send(message)

    async def write(self, data: str | bytes):
        """Send data to the WebSocket connection

        :raise WebSocketStateError: If the WebSocket is not yet accepted
        :raise WebSocketClosedError: If the WebSocket is closed
        """

        key = "text" if isinstance(data, str) else "bytes"
        await self._write(
            {
                "type": "websocket.send",
                key: data,
            }
        )

    async def write_json(self, data: Any):
        """Send data as json to the WebSocket connection

        :raise WebSocketClosedError: If the WebSocket is closed
        """

        json_data = json.dumps(data)
        await self.write(json_data)

    async def close(self, code: int = 1000, reason: str = None):
        """Close the WebSocket connection

        Does nothing if the websocket is already closed
        """

        if self.state == WebSocketState.CLOSED:
            return

        await self._send(
            {
                "type": "websocket.close",
                "code": code,
                "reason": reason,
            }
        )

        self.__set_state(WebSocketState.CLOSED)
