from http import HTTPStatus
import logging

import pytest

from asgikit import WebSocketResponseNotSupportedError
from asgikit.exceptions import (
    ResponseAlreadyStartedError,
    ResponseAlreadyEndedError,
    ResponseNotStartedError,
)
from asgikit.responses import Response


async def test_call_start_twice_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http"}, None, send)
    await response.start(HTTPStatus.OK)

    with pytest.raises(ResponseAlreadyStartedError):
        await response.start(HTTPStatus.OK)


async def test_call_start_on_finished_response_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http"}, None, send)
    await response.start(HTTPStatus.OK)
    await response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await response.start(HTTPStatus.OK)


async def test_call_write_on_without_start_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http"}, None, send)

    with pytest.raises(ResponseNotStartedError):
        await response.write(b"")


async def test_call_write_on_finished_response_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http"}, None, send)
    await response.start(HTTPStatus.OK)
    await response.end()

    with pytest.raises(ResponseAlreadyEndedError):
        await response.write(b"")


async def test_call_end_without_start_should_fail():
    async def send(_event):
        pass

    response = Response({"type": "http"}, None, send)

    with pytest.raises(ResponseNotStartedError):
        await response.end()


async def test_call_end_on_finished_response(caplog):
    async def send(_event):
        pass

    response = Response({"type": "http"}, None, send)
    await response.start(HTTPStatus.OK)
    await response.end()
    assert response.is_finished

    with caplog.at_level(logging.WARNING):
        await response.end()

    assert caplog.records[0].message == "Response already ended"


async def test_start_websocket_http_response_on_unsupported_server_should_fail():
    response = Response({"type": "websocket"}, None, None)
    with pytest.raises(WebSocketResponseNotSupportedError):
        await response.start(HTTPStatus.OK)
