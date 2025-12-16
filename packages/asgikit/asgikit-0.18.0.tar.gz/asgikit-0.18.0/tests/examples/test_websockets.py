from http import HTTPStatus

from httpx import AsyncClient
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from examples.websockets.echo_chat import app


async def test_websocket_chat():
    async with AsyncClient(
        transport=ASGIWebSocketTransport(app), base_url="http://localhost"
    ) as client:
        response = await client.get("/")
        assert response.status_code == HTTPStatus.OK
        assert "<title>WebSocket chat</title>" in response.text

        response = await client.get("/favicon.ico")
        assert response.status_code == HTTPStatus.NOT_FOUND

        async with aconnect_ws("/", client) as ws:
            await ws.send_text("Hello World!")
            message = await ws.receive_text()
            assert message == "Hello World!"
