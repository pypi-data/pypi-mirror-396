from httpx import ASGITransport, AsyncClient
from httpx_ws import aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from asgikit.requests import Request


async def test_request_response():
    async def app(scope, receive, send):
        if scope["type"] != "http":
            return

        request = Request(scope, receive, send)
        await request.respond_text("Ok")

    async with AsyncClient(transport=ASGITransport(app)) as client:
        client_response = await client.get("http://localhost:8000/")
        assert client_response.text == "Ok"


async def test_websocket_chat():
    async def app(scope, receive, send):
        if scope["type"] != "websocket":
            return

        request = Request(scope, receive, send)
        websocket = await request.upgrade()

        while True:
            data = await websocket.read()
            await websocket.write(data)

    async with AsyncClient(transport=ASGIWebSocketTransport(app)) as client:
        async with aconnect_ws("http://localhost", client) as ws:
            await ws.send_text("Hello World!")
            message = await ws.receive_text()
            assert message == "Hello World!"
