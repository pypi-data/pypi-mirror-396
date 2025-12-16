from http import HTTPStatus

import httpx
import pytest

from examples import echo, hello_world, hello_world_json


async def test_echo():
    transport = httpx.ASGITransport(app=echo.app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as client:
        response = await client.post("/", json={"foo": "bar"})
        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["body"] == {"foo": "bar"}

        response = await client.get("/")
        assert response.status_code == HTTPStatus.METHOD_NOT_ALLOWED


@pytest.mark.parametrize(
    "params,expected",
    [
        ({}, "World"),
        ({"name": "Python"}, "Python"),
    ],
    ids=["None", "Some"],
)
async def test_hello_world(params, expected):
    transport = httpx.ASGITransport(app=hello_world.app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as client:
        response = await client.get("/", params=params)
        result = response.text

        assert response.status_code == HTTPStatus.OK
        assert result == f"Hello, {expected}!"


@pytest.mark.parametrize(
    "params,expected",
    [
        ({}, "World"),
        ({"name": "Python"}, "Python"),
    ],
    ids=["None", "Some"],
)
async def test_hello_world_json(params, expected):
    transport = httpx.ASGITransport(app=hello_world_json.app)

    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as client:
        response = await client.get("/", params=params)
        result = response.json()

        assert response.status_code == HTTPStatus.OK
        assert result["name"] == expected
        assert result["result"] == f"Hello, {expected}!"
