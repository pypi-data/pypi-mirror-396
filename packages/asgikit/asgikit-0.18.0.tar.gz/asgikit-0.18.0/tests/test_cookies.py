import sys

import pytest

from asgikit.cookies import Cookies
from asgikit.requests import Request, parse_cookie


def test_parse_cookie():
    data = "key1=value1; key2=value2"
    result = parse_cookie([data])
    assert result == {"key1": ["value1"], "key2": ["value2"]}


def test_request_get_cookie():
    scope = {
        "type": "http",
        "headers": [
            (b"cookie", b"key1=value1; key2=value2"),
        ],
    }

    request = Request(scope, None, None)
    result = request.cookies
    assert result == {"key1": ["value1"], "key2": ["value2"]}


def test_cookies():
    cookies = Cookies()
    cookies.set("name", "value")
    result = next(cookies.encode())
    assert result == (b"Set-Cookie", b"name=value; HttpOnly; SameSite=lax")


@pytest.mark.parametrize(
    "samesite,expected",
    [
        ("strict", (b"Set-Cookie", b"name=value; HttpOnly; SameSite=strict")),
        ("none", (b"Set-Cookie", b"name=value; HttpOnly; SameSite=none")),
    ],
    ids=("strict", "none"),
)
def test_cookies_same_site(samesite, expected):
    cookies = Cookies()
    cookies.set("name", "value", samesite=samesite)
    result = next(cookies.encode())
    assert result == expected


def test_cookies_httponly():
    cookies = Cookies()
    cookies.set("name", "value", httponly=False)
    result = next(cookies.encode())
    assert result == (b"Set-Cookie", b"name=value; SameSite=lax")


def test_cookies_max_age():
    cookies = Cookies()
    cookies.set("name", "value", max_age=1)
    result = next(cookies.encode())
    assert result == (b"Set-Cookie", b"name=value; HttpOnly; Max-Age=1; SameSite=lax")


def test_cookies_secure():
    cookies = Cookies()
    cookies.set("name", "value", secure=True)
    result = next(cookies.encode())
    assert result == (b"Set-Cookie", b"name=value; HttpOnly; SameSite=lax; Secure")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="requires Python >= 3.14")
def test_cookies_partitioned():
    cookies = Cookies()
    cookies.set("name", "value", partitioned=True)
    result = next(cookies.encode())
    assert result == (b"Set-Cookie", b"name=value; HttpOnly; Partitioned; SameSite=lax")


def test_cookies_multiple():
    cookies = Cookies()
    cookies.set("name1", "value1", httponly=False)
    cookies.set("name2", "value2", httponly=False)
    result = list(cookies.encode())
    assert result == [
        (b"Set-Cookie", b"name1=value1; SameSite=lax"),
        (b"Set-Cookie", b"name2=value2; SameSite=lax"),
    ]


def test_cookies_delete():
    cookies = Cookies()
    cookies.delete("name")
    result = next(cookies.encode())
    assert b"Max-Age=0" in result[1]
