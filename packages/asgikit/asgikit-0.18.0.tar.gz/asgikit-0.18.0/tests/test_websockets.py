import pytest

from asgiref.typing import HTTPScope

from asgikit.exceptions import WebSocketStateError, WebSocketClosedError
from asgikit.websockets import WebSocket, WebSocketState
from tests.utils.asgi import AsgiReceiveInspector, WebSocketSendInspector


async def test_websocket():
    scope = {
        "type": "websocket",
        "subprotocols": ["stomp"],
        "headers": [],
    }

    receive = AsgiReceiveInspector()
    send = WebSocketSendInspector()

    websocket = WebSocket(scope, receive, send)

    receive.send({"type": "websocket.connect"})

    await websocket.accept(subprotocol="stomp")
    assert send.subprotocol == "stomp"


SCOPE: HTTPScope = {
    "asgi": {
        "version": "3.0",
        "spec_version": "2.3",
    },
    "type": "http",
    "http_version": "1.1",
    "method": "GET",
    "scheme": "http",
    "path": "/",
    "raw_path": b"/",
    "query_string": b"",
    "root_path": "",
    "headers": [(b"custom-header", b"value")],
    "client": None,
    "server": None,
    "extensions": None,
}


async def test_call_accept_twice_should_fail():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    with pytest.raises(WebSocketStateError):
        await websocket.accept()


async def test_call_read_on_state_new_should_fail():
    scope = {"type": "websocket", "headers": []}

    websocket = WebSocket(scope, None, None)

    with pytest.raises(WebSocketStateError):
        await websocket.read()


async def test_call_read_on_websocket_closed_should_fail():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)

    await websocket.accept()
    await websocket.close()

    with pytest.raises(WebSocketClosedError):
        await websocket.read()


async def test_call_write_on_state_new_should_fail():
    scope = {"type": "websocket", "headers": []}

    websocket = WebSocket(scope, None, None)

    with pytest.raises(WebSocketStateError):
        await websocket.write("data")


async def test_call_write_on_websocket_closed_should_fail():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)

    await websocket.accept()
    await websocket.close()

    with pytest.raises(WebSocketClosedError):
        await websocket.write("data")


async def test_iter():
    scope = {"type": "websocket", "headers": []}

    _events = iter(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": "1"},
            {"type": "websocket.receive", "bytes": b"2"},
            {"type": "websocket.receive", "text": "3"},
            {
                "type": "websocket.disconnect",
                "code": "1000",
                "reason": "client disconnect",
            },
        ]
    )

    async def receive():
        nonlocal _events
        return next(_events)

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    result = []
    async for item in websocket.iter():
        result.append(item)

    assert result == ["1", b"2", "3"]


async def test_read_text():
    scope = {"type": "websocket", "headers": []}

    _events = iter(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": "text"},
        ]
    )

    async def receive():
        nonlocal _events
        return next(_events)

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    result = await websocket.read()
    assert result == "text"


async def test_read_bytes():
    scope = {"type": "websocket", "headers": []}

    _events = iter(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "bytes": b"bytes"},
        ]
    )

    async def receive():
        nonlocal _events
        return next(_events)

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    result = await websocket.read()
    assert result == b"bytes"


async def test_read_json_text():
    scope = {"type": "websocket", "headers": []}

    _events = iter(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": """{"str": "value", "int": 1}"""},
        ]
    )

    async def receive():
        nonlocal _events
        return next(_events)

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    result = await websocket.read_json()
    assert result == {"str": "value", "int": 1}


async def test_read_json_bytes():
    scope = {"type": "websocket", "headers": []}

    _events = iter(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "bytes": b"""{"str": "value", "int": 1}"""},
        ]
    )

    async def receive():
        nonlocal _events
        return next(_events)

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    result = await websocket.read_json()
    assert result == {"str": "value", "int": 1}


async def test_iter_json():
    scope = {"type": "websocket", "headers": []}

    _events = iter(
        [
            {"type": "websocket.connect"},
            {"type": "websocket.receive", "text": """{"i": 1}"""},
            {"type": "websocket.receive", "bytes": b"""{"i": 2}"""},
            {"type": "websocket.receive", "text": """{"i": 3}"""},
            {
                "type": "websocket.disconnect",
                "code": "1000",
                "reason": "client disconnect",
            },
        ]
    )

    async def receive():
        nonlocal _events
        return next(_events)

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)
    await websocket.accept()

    result = []
    async for item in websocket.iter_json():
        result.append(item)

    assert result == [{"i": 1}, {"i": 2}, {"i": 3}]


async def test_write_text():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    result = None

    async def send(event):
        nonlocal result
        if event["type"] == "websocket.send":
            result = event["text"]

    websocket = WebSocket(scope, receive, send)

    await websocket.accept()
    await websocket.write("data")

    assert result == "data"


async def test_write_bytes():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    result = None

    async def send(event):
        nonlocal result
        if event["type"] == "websocket.send":
            result = event["bytes"]

    websocket = WebSocket(scope, receive, send)

    await websocket.accept()
    await websocket.write(b"data")

    assert result == b"data"


async def test_write_json_text():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    result = None

    async def send(event):
        nonlocal result
        if event["type"] == "websocket.send":
            result = event["text"]

    websocket = WebSocket(scope, receive, send)

    await websocket.accept()
    await websocket.write_json({"key": "value"})

    assert result == """{"key": "value"}"""


async def test_close_already_closed():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)

    await websocket.accept()
    await websocket.close()
    assert websocket.state == WebSocketState.CLOSED

    await websocket.close()
    assert websocket.state == WebSocketState.CLOSED


async def test_close_not_yet_accepted():
    scope = {"type": "websocket", "headers": []}

    async def receive():
        return {"type": "websocket.connect"}

    async def send(_event):
        pass

    websocket = WebSocket(scope, receive, send)

    assert websocket.state == WebSocketState.NEW

    await websocket.close()

    assert websocket.state == WebSocketState.CLOSED
