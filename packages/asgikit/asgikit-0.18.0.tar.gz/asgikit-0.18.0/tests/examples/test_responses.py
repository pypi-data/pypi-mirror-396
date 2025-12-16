from http import HTTPStatus

import httpx
import pytest

from examples.responses import (
    response_file,
    response_streaming,
    response_streaming_json,
)


async def test_response_file():
    transport = httpx.ASGITransport(app=response_file.app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as client:
        response = await client.get("/")

        assert response.status_code == HTTPStatus.OK
        assert response.headers["content-type"] == "image/png"


@pytest.mark.parametrize(
    "limit,expected",
    [
        (2, "0\n1\n"),
        (10, "0\n1\n1\n2\n3\n5\n8\n13\n21\n34\n"),
    ],
    ids=[2, 10],
)
async def test_response_streaming(limit, expected):
    transport = httpx.ASGITransport(app=response_streaming.app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as client:
        response = await client.get("/", params={"limit": limit})
        result = response.text

        assert response.status_code == HTTPStatus.OK
        assert result == expected


@pytest.mark.parametrize(
    "limit,expected",
    [
        (2, {"fibonacci": [0, 1]}),
        (10, {"fibonacci": [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]}),
    ],
    ids=[2, 10],
)
async def test_response_streaming_json(limit, expected):
    transport = httpx.ASGITransport(app=response_streaming_json.app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as client:
        response = await client.get("/", params={"limit": limit})
        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result == expected
