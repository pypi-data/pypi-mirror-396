import copy

from asgiref.typing import HTTPScope

from asgikit.requests import Request


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
    "headers": [
        (b"accept", b"application/json"),
        (b"content-type", b"application/xml"),
        (b"content-length", b"1024"),
    ],
    "client": None,
    "server": None,
    "extensions": None,
}


async def test_http_context_properties():
    scope = copy.deepcopy(SCOPE)
    scope["headers"] += []
    request = Request(scope, None, None)

    assert request.http_version == "1.1"
    assert request.path == "/"
    assert request.cookies == {}
    assert request.headers == {
        "accept": ["application/json"],
        "content-type": ["application/xml"],
        "content-length": ["1024"],
    }
