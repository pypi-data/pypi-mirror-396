# Asgikit - ASGI Toolkit

Asgikit is a toolkit for building asgi applications and frameworks.

The [examples directory](./examples) contain usage examples of several use cases

## Features:

- Request
  - Headers
  - Cookies
  - Body (bytes, str, json, form, stream)
  - Form
- Response
  - Plain text
  - Json
  - Streaming
  - File
- Websockets

## Example request and response

```python
from asgikit import Request


async def main(scope, receive, send):
    assert scope["type"] == "http"

    request = Request(scope, receive, send)

    # request method
    method = request.method

    # request path
    path = request.path

    # request headers
    headers = request.headers

    # read body as json
    body = await request.body.read_json()

    data = {
        "lang": "Python",
        "async": True,
        "platform": "asgi",
        "method": method,
        "path": path,
        "headers": dict(headers.items()),
        "body": body,
    }

    # send json response
    await request.respond_json(data)
```

## Example websocket

```python
from asgikit import Request, WebSocketDisconnect


async def app(scope, receive, send):
    if scope["type"] != "websocket":
        return

    request = Request(scope, receive, send)
    ws = await request.upgrade()

    while True:
        try:
            message = await ws.read()
            await ws.write(message)
        except WebSocketDisconnect:
            print("Client disconnect")
            break
```
