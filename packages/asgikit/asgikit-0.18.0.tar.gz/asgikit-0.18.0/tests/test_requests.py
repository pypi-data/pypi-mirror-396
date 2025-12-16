import asyncio
from http import HTTPMethod, HTTPStatus

import pytest
from asgiref.typing import HTTPScope
from pylint.pyreverse import inspector

from asgikit.cookies import Cookies
from asgikit.requests import Request

from tests.utils.asgi import HttpSendInspector


async def test_request_properties():
    scope: HTTPScope = {
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
        "headers": [
            (b"accept", b"application/json"),
            (b"content-type", b"application/xml"),
            (b"content-length", b"1024"),
        ],
        "client": ("127.0.0.1", 12435),
        "server": ("127.0.0.1", 80),
        "extensions": {},
    }

    request = Request(scope, None, None)

    assert request.http_version == "1.1"
    assert request.method == HTTPMethod.GET
    assert request.path == "/"
    assert request.cookies == {}
    assert request.client == ("127.0.0.1", 12435)
    assert request.server == ("127.0.0.1", 80)
    assert request.body.content_type == "application/xml"
    assert request.body.content_length == 1024


async def test_upgrade_http_request_should_fail():
    scope = {
        "type": "http",
        "headers": [],
    }
    request = Request(scope, None, None)
    with pytest.raises(AssertionError, match="request is not websocket"):
        await request.upgrade()


async def test_respond_bytes():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)

    await request.respond_bytes(b"Hello, World!")

    assert inspector.body == b"Hello, World!"


async def test_respond_plain_text():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)

    await request.respond_text("Hello, World!")

    assert inspector.body_str == "Hello, World!"


async def test_respond_stream():
    async def stream_data():
        yield b"Hello, "
        yield b"World!"

    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_stream(stream_data())

    assert inspector.body_str == "Hello, World!"


async def test_respond_stream_context_manager():
    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}
    request = Request(scope, None, inspector)

    async with request.response_writer() as write:
        await write(b"Hello, ")
        await write(b"World!")

    assert inspector.body_str == "Hello, World!"


async def test_respond_file(tmp_path):
    tmp_file = tmp_path / "tmp_file.txt"
    tmp_file.write_text("Hello, World!")

    inspector = HttpSendInspector()
    scope = {"type": "http", "http_version": "1.1", "headers": []}

    async def sleep_receive():
        while True:
            await asyncio.sleep(1000)

    request = Request(scope, sleep_receive, inspector)
    await request.respond_file(tmp_file)

    assert inspector.body_str == "Hello, World!"


async def test_respond_file_pathsend(tmp_path):
    tmp_file = tmp_path / "tmp_file.txt"
    tmp_file.write_text("Hello, World!")

    scope = {
        "type": "http",
        "http_version": "1.1",
        "headers": [],
        "extensions": {"http.response.pathsend": {}},
    }

    async def sleep_receive():
        while True:
            await asyncio.sleep(1000)

    result = None

    async def send(event):
        nonlocal result
        result = event

    request = Request(scope, sleep_receive, send)
    await request.respond_file(tmp_file)

    assert result == {
        "type": "http.response.pathsend",
        "path": str(tmp_file),
    }


async def test_respond_status():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_empty(HTTPStatus.IM_A_TEAPOT)

    assert inspector.status == HTTPStatus.IM_A_TEAPOT
    assert inspector.body_str == ""


async def test_respond_empty():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)

    await request.respond_empty(HTTPStatus.OK)
    assert inspector.status == HTTPStatus.OK
    assert inspector.body_str == ""


async def test_respond_plain_text_with_encoding():
    inspector = HttpSendInspector(encoding="iso-8859-6")
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_text("زيت", encoding="iso-8859-6")
    assert inspector.body_str == "زيت"


async def test_respond_temporary_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.redirect("/redirect")

    assert inspector.status == HTTPStatus.TEMPORARY_REDIRECT
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_permanent_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.redirect("/redirect", permanent=True)

    assert inspector.status == HTTPStatus.PERMANENT_REDIRECT
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_post_get_redirect():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.redirect_post_get("/redirect")

    assert inspector.status == HTTPStatus.SEE_OTHER
    assert (b"location", b"/redirect") in inspector.headers


async def test_respond_header():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    await request.respond_empty(HTTPStatus.OK, headers={"name": "value"})

    assert inspector.status == HTTPStatus.OK
    assert (b"name", b"value") in inspector.headers


async def test_respond_cookie():
    inspector = HttpSendInspector()
    scope = {"type": "http", "headers": []}
    request = Request(scope, None, inspector)
    cookies = Cookies()
    cookies.set("name", "value")
    await request.respond_empty(HTTPStatus.OK, cookies=cookies)

    assert inspector.status == HTTPStatus.OK
    assert (b"Set-Cookie", b"name=value; HttpOnly; SameSite=lax") in inspector.headers


async def test_get_body_on_websocket_request_should_fail():
    scope = {"type": "websocket", "headers": []}
    request = Request(scope, None, None)

    with pytest.raises(AssertionError, match="request is not http"):
        request.body
