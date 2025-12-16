import sys
from collections.abc import Iterable
import http.cookies
from http.cookies import SimpleCookie
import itertools
from typing import Literal, TypeAlias

from asgikit._constants import HEADER_ENCODING
from asgikit.multidict import MultiDict

__all__ = ("Cookies", "SameSitePolicy", "parse_cookie")

SameSitePolicy: TypeAlias = Literal["strict", "lax", "none"]


def _parse_cookie(cookie: str):
    for chunk in cookie.split(";"):
        if "=" in chunk:
            key, val = chunk.split("=", 1)
        else:
            # Assume an empty name per
            # https://bugzilla.mozilla.org/show_bug.cgi?id=169091
            key, val = "", chunk
        key, val = key.strip(), val.strip()
        if key or val:
            # unquote using Python's algorithm.
            # pylint: disable=protected-access
            yield key, http.cookies._unquote(val)


def parse_cookie(cookies: list[str]) -> MultiDict[str]:
    values = itertools.chain.from_iterable(_parse_cookie(cookie) for cookie in cookies)
    return MultiDict(values)


class Cookies:
    """Cookies to be sent in the response"""

    __slots__ = ("_cookie",)

    def __init__(self):
        self._cookie = SimpleCookie()

    # pylint: disable=too-many-arguments
    def set(
        self,
        name: str,
        value: str,
        *,
        expires: int = None,
        domain: str = None,
        path: str = None,
        max_age: int = None,
        secure: bool = False,
        httponly: bool = True,
        samesite: SameSitePolicy = "lax",
        partitioned: bool = False,
    ):
        """Add a cookie"""

        self._cookie[name] = value
        if expires is not None:
            self._cookie[name]["expires"] = expires
        if domain is not None:
            self._cookie[name]["domain"] = domain
        if path is not None:
            self._cookie[name]["path"] = path
        if max_age is not None:
            self._cookie[name]["max-age"] = max_age

        self._cookie[name]["secure"] = secure
        self._cookie[name]["httponly"] = httponly
        self._cookie[name]["samesite"] = samesite

        if partitioned:
            if sys.version_info < (3, 14):
                raise NotImplementedError(
                    "Partitioned cookies are only supported in Python >= 3.14."
                )
            self._cookie[name]["partitioned"] = True

    def delete(
        self,
        name: str,
        *,
        domain: str = None,
        path: str = None,
        secure: bool = False,
        httponly: bool = True,
        samesite: SameSitePolicy = "lax",
    ):
        """Remove a cookie"""

        self.set(
            name,
            "",
            expires=0,
            max_age=0,
            domain=domain,
            path=path,
            secure=secure,
            httponly=httponly,
            samesite=samesite,
        )

    def encode(self) -> Iterable[tuple[bytes, bytes]]:
        for c in self._cookie.values():
            yield b"Set-Cookie", c.output(header="").strip().encode(HEADER_ENCODING)

    def __eq__(self, other):
        return isinstance(other, Cookies) and self._cookie == other._cookie

    def __hash__(self):
        return hash(self._cookie)

    def __getitem__(self, item):
        return self._cookie[item]

    def __bool__(self):
        return bool(self._cookie)
