import pytest
from asgiref.typing import HTTPDisconnectEvent, HTTPRequestEvent

from asgikit.exceptions import ClientDisconnectError, RequestAlreadyConsumedError
from asgikit.requests_body import Body


async def test_request_stream():
    num = 1

    async def receive() -> HTTPRequestEvent:
        nonlocal num
        event = {
            "type": "http.request",
            "body": f"{num}".encode(),
            "more_body": (num < 5),
        }
        num += 1
        return event

    scope = {
        "headers": [
            (b"content-type", b"octet-stream"),
            (b"content-length", b"5"),
        ]
    }
    body = Body(scope, receive)

    result = []
    async for data in body:
        result.append(data)

    assert result == [b"1", b"2", b"3", b"4", b"5"]


async def test_request_stream_client_disconnect():
    sent = False

    async def receive() -> HTTPRequestEvent | HTTPDisconnectEvent:
        nonlocal sent
        if not sent:
            sent = True
            event: HTTPRequestEvent = {
                "type": "http.request",
                "body": b"12345",
                "more_body": True,
            }
        else:
            event: HTTPDisconnectEvent = {"type": "http.disconnect"}
        return event

    scope = {
        "headers": [
            (b"content-type", b"octet-stream"),
            (b"content-length", b"5"),
        ]
    }
    body = Body(scope, receive)

    with pytest.raises(ClientDisconnectError):
        async for _ in body:
            pass


async def test_request_body_single_chunk():
    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": b"12345",
            "more_body": False,
        }

    scope = {
        "headers": [
            (b"content-type", b"octet-stream"),
            (b"content-length", b"5"),
        ]
    }
    body = Body(scope, receive)

    result = await body.read_bytes()
    assert result == b"12345"


async def test_request_body_multiple_chunk():
    num = 1

    async def receive() -> HTTPRequestEvent:
        nonlocal num
        event = {
            "type": "http.request",
            "body": f"{num}".encode(),
            "more_body": (num < 5),
        }
        num += 1
        return event

    scope = {
        "headers": [
            (b"content-type", b"octet-stream"),
            (b"content-length", b"5"),
        ]
    }
    body = Body(scope, receive)

    result = await body.read_bytes()
    assert result == b"12345"


async def test_request_body_charset():
    scope = {
        "headers": [
            (b"content-type", b"text/plain; charset=latin-1"),
            (b"content-length", b"1"),
        ]
    }
    body = Body(scope, None)

    assert body.charset == "latin-1"


async def test_request_body_charset_no_content_type():
    scope = {"headers": []}
    body = Body(scope, None)

    assert body.charset == "utf-8"


@pytest.mark.parametrize(
    "content_type",
    [
        b'text/plain; charset="iso-8859-1"',
        b"text/plain; charset=iso-8859-1",
    ],
    ids=[
        "with quotes",
        "without quotes",
    ],
)
async def test_charset(content_type):
    scope = {
        "headers": [(b"content-type", content_type)],
    }

    body = Body(scope, None)
    assert body.charset == "iso-8859-1"


async def test_read_text():
    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": b"12345",
            "more_body": False,
        }

    scope = {
        "headers": [
            (b"content-type", b"text/plain"),
            (b"content-length", b"5"),
        ]
    }
    body = Body(scope, receive)

    result = await body.read_text()
    assert result == "12345"


async def test_read_text_with_charset():
    plain = "زيت"
    encoded = plain.encode("iso-8859-6")

    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": encoded,
            "more_body": False,
        }

    scope = {
        "headers": [
            (b"content-type", b"text/plain; charset=iso-8859-6"),
            (b"content-length", str(len(encoded)).encode("latin-1")),
        ]
    }
    body = Body(scope, receive)

    result = await body.read_text()
    assert result == plain


@pytest.mark.parametrize(
    "data,expected",
    [
        (b'{"name": "a", "value": 1}', {"name": "a", "value": 1}),
        (b"[1, 2, 3]", [1, 2, 3]),
        (
            b'[{"name": "a", "value": 1}, {"name": "b", "value": 2}]',
            [{"name": "a", "value": 1}, {"name": "b", "value": 2}],
        ),
        (b"", None),
    ],
    ids=[
        "object",
        "list[integer]",
        "list[object]",
        "empty",
    ],
)
async def test_read_json(data: bytes, expected: list | dict):
    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": data,
            "more_body": False,
        }

    scope = {
        "headers": [
            (b"content-type", b"application/json"),
            (b"content-length", str(len(data)).encode("latin-1")),
        ]
    }
    body = Body(scope, receive)

    result = await body.read_json()
    assert result == expected


@pytest.mark.parametrize(
    "data,expected",
    [
        (b"name=a&value=1", {"name": ["a"], "value": ["1"]}),
        (b"name=a&name=b&value=1&value=2", {"name": ["a", "b"], "value": ["1", "2"]}),
        (b"name=a&value=1&value=2", {"name": ["a"], "value": ["1", "2"]}),
        (b"", {}),
    ],
    ids=[
        "single values",
        "multiple values",
        "mixed",
        "empty",
    ],
)
async def test_read_form(data: bytes, expected: dict):
    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": data,
            "more_body": False,
        }

    scope = {
        "headers": [
            (b"content-type", b"application/x-www-urlencoded"),
            (b"content-length", str(len(data)).encode("latin-1")),
        ]
    }
    body = Body(scope, receive)

    result = await body.read_form()
    assert result == expected


async def test_read_text_with_invalid_utf_8_data_should_fail():
    plain = "¶"
    encoded = plain.encode("latin-1")

    scope = {
        "headers": [
            (b"content-type", b"text/plain; charset=utf-8"),
            (b"content-length", str(len(encoded)).encode("latin-1")),
        ],
    }

    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": encoded,
            "more_body": False,
        }

    body = Body(scope, receive)
    with pytest.raises(UnicodeDecodeError):
        await body.read_text()


async def test_read_text_with_invalid_charset_should_give_wring_result():
    plain = "¶"
    encoded = plain.encode("utf-8")

    scope = {
        "headers": [
            (b"content-type", b"text/plain"),
            (b"content-length", str(len(encoded)).encode("latin-1")),
        ],
    }

    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": encoded,
            "more_body": False,
        }

    body = Body(scope, receive)
    result = await body.read_text(encoding="latin-1")
    assert result != plain


async def test_read_already_consumed_body_should_fail():
    plain = "Hello, World!"
    encoded = plain.encode()

    scope = {
        "headers": [
            (b"content-type", b"text/plain"),
            (b"content-length", str(len(encoded)).encode("latin-1")),
        ],
    }

    async def receive() -> HTTPRequestEvent:
        return {
            "type": "http.request",
            "body": encoded,
            "more_body": False,
        }

    body = Body(scope, receive)
    await body.read_text()
    with pytest.raises(RequestAlreadyConsumedError):
        await body.read_text()
