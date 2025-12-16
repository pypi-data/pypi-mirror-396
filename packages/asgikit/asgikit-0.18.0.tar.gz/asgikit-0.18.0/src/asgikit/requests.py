from collections.abc import AsyncGenerator, AsyncIterable, Awaitable, Callable
from contextlib import asynccontextmanager
from email.utils import formatdate
from functools import partial
import hashlib
from http import HTTPMethod, HTTPStatus
import json
import logging
import mimetypes
import os
from typing import Any
from urllib.parse import parse_qsl, unquote_plus

import anyio

from asgikit._constants import (
    COOKIES,
    DEFAULT_ENCODING,
    HEADERS,
    QUERY,
    REQUEST,
    SCOPE_ASGIKIT,
)
from asgikit.requests_body import Body
from asgikit.sync import run_sync
from asgikit.cookies import Cookies, parse_cookie
from asgikit.exceptions import (
    ClientDisconnectError,
)
from asgikit.files import async_file_stream
from asgikit.headers import Headers
from asgikit.multidict import MultiDict
from asgikit.responses import Response
from asgikit.websockets import WebSocket

__all__ = ("Request",)

logger = logging.getLogger(__name__)


# pylint: disable=too-many-public-methods
class Request:
    """Represents an incoming request

    It encapsulates a :py:class:`~asgikit.responses.Response` object that is used
    to respond to the request.
    """

    __slots__ = (
        "_scope",
        "_receive",
        "_send",
        "__body",
        "__response",
    )

    def __init__(self, scope, receive, send):
        assert scope["type"] in ("http", "websocket")

        self._scope = scope
        self._receive = receive
        self._send = send

        self._scope.setdefault(SCOPE_ASGIKIT, {})
        self._scope[SCOPE_ASGIKIT].setdefault(REQUEST, {})

        self.__body = None
        self.__response = None

    @property
    def is_http(self) -> bool:
        return self._scope["type"] == "http"

    @property
    def is_websocket(self) -> bool:
        return self._scope["type"] == "websocket"

    @property
    def body(self) -> Body:
        """Request body

        :return: The request :py:class:`~asgikit.Body` object,
            or :py:type:`None` if request is websocket
        """

        assert self._scope["type"] == "http", "request is not http"

        if not self.__body:
            self.__body = Body(self._scope, self._receive)
        return self.__body

    @property
    def response(self) -> Response:
        """The underlying response object"""

        if not self.__response:
            self.__response = Response(self._scope, self._receive, self._send)
        return self.__response

    @property
    def state(self) -> dict | None:
        """State managed by the ASGI server"""
        return self._scope.get("state")

    @property
    def http_version(self) -> str:
        """HTTP version"""
        return self._scope["http_version"]

    @property
    def server(self) -> tuple[str, int | None]:
        """Server information"""
        return self._scope["server"]

    @property
    def client(self) -> tuple[str, int] | None:
        """Client information"""
        return self._scope["client"]

    @property
    def scheme(self) -> str:
        """URL scheme"""
        return self._scope["scheme"]

    @property
    def method(self) -> HTTPMethod | None:
        """HTTP method of the request"""

        if self._scope["type"] == "http":
            # pylint: disable=no-value-for-parameter
            return HTTPMethod(self._scope["method"])

        return None

    @property
    def root_path(self) -> str:
        """Root path"""
        return self._scope["root_path"]

    @property
    def path(self) -> str:
        """Request path"""
        return self._scope["path"]

    @property
    def raw_path(self) -> str | None:
        """Raw request path"""
        return self._scope["raw_path"]

    @property
    def headers(self) -> Headers:
        """Request headers"""

        if HEADERS not in self._scope[SCOPE_ASGIKIT][REQUEST]:
            self._scope[SCOPE_ASGIKIT][REQUEST][HEADERS] = Headers(
                self._scope["headers"]
            )
        return self._scope[SCOPE_ASGIKIT][REQUEST][HEADERS]

    @property
    def raw_query(self) -> str:
        """Raw query string"""
        return unquote_plus(self._scope["query_string"].decode("ascii"))

    @property
    def query(self) -> MultiDict[str]:
        """Parsed query string"""

        if QUERY not in self._scope[SCOPE_ASGIKIT][REQUEST]:
            query_string = self.raw_query
            parsed_query = MultiDict(parse_qsl(query_string, keep_blank_values=True))
            self._scope[SCOPE_ASGIKIT][REQUEST][QUERY] = parsed_query
        return self._scope[SCOPE_ASGIKIT][REQUEST][QUERY]

    @property
    def cookies(self) -> MultiDict[str]:
        """Request cookies"""

        if COOKIES not in self._scope[SCOPE_ASGIKIT][REQUEST]:
            if cookies := self.headers.get("cookie"):
                cookie_value = parse_cookie(cookies)
            else:
                cookie_value = {}
            self._scope[SCOPE_ASGIKIT][REQUEST][COOKIES] = cookie_value
        return self._scope[SCOPE_ASGIKIT][REQUEST][COOKIES]

    # Compatibility with asgikit middleware
    @property
    def session(self) -> Any:
        """Get the `session` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self._scope.get("session")

    @property
    def auth(self) -> Any:
        """Get the `auth` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self._scope.get("auth")

    @property
    def user(self) -> Any:
        """Get the `user` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self._scope.get("user")

    @property
    def path_params(self) -> dict[str, Any]:
        """Get the `path_params` attribute from the asgi scope

        For compatibility with starlette middleware
        """
        return self._scope.get("path_params")

    # ...

    async def upgrade(
        self,
        subprotocol: str = None,
        headers: dict[str, str] = None,
    ):
        assert self._scope["type"] == "websocket", "request is not websocket"

        ws = WebSocket(self._scope, self._receive, self._send)
        await ws.accept(subprotocol, headers)
        return ws

    async def respond(self, response: Response):
        await response(self._scope, self._receive, self._send)

    # pylint: disable=too-many-arguments
    async def respond_bytes(
        self,
        content: bytes,
        *,
        status=HTTPStatus.OK,
        media_type: str = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond with the given content and finish the response"""

        content_length = len(content)

        await self.response.start(
            status,
            media_type=media_type,
            content_length=content_length,
            headers=headers,
            cookies=cookies,
        )
        await self.response.write(content, more_body=False)

    # pylint: disable=too-many-arguments
    async def respond_text(
        self,
        content: str,
        *,
        status=HTTPStatus.OK,
        media_type: str = "text/plain",
        headers: dict[str, str] = None,
        cookies: Cookies = None,
        encoding: str = DEFAULT_ENCODING,
    ):
        """Respond with the given content and finish the response"""

        data = content.encode(encoding)
        await self.respond_bytes(
            data, status=status, media_type=media_type, headers=headers, cookies=cookies
        )

    # pylint: disable=too-many-arguments
    async def respond_json(
        self,
        content: Any,
        *,
        status=HTTPStatus.OK,
        media_type: str = "application/json",
        headers: dict[str, str] = None,
        cookies: Cookies = None,
        encoding: str = DEFAULT_ENCODING,
    ):
        """Respond with the given content serialized as JSON"""

        data = json.dumps(
            content,
            allow_nan=False,
            indent=None,
            ensure_ascii=False,
            separators=(",", ":"),
        )

        await self.respond_text(
            data,
            status=status,
            media_type=media_type,
            encoding=encoding,
            headers=headers,
            cookies=cookies,
        )

    async def respond_empty(
        self,
        status: HTTPStatus = HTTPStatus.NO_CONTENT,
        *,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Send an empty response with the given status"""

        await self.response.start(status, headers=headers, cookies=cookies)
        await self.response.end()

    async def redirect(
        self,
        location: str,
        *,
        permanent: bool = False,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Respond with a redirect

        :param location: Location to redirect to
        :param permanent: If true, send permanent redirect (HTTP 308),
            otherwise send a temporary redirect (HTTP 307).
        """

        headers = headers or {}

        status = (
            HTTPStatus.TEMPORARY_REDIRECT
            if not permanent
            else HTTPStatus.PERMANENT_REDIRECT
        )

        headers["location"] = location
        await self.respond_empty(status=status, headers=headers, cookies=cookies)

    async def redirect_post_get(
        self,
        location: str,
        *,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
    ):
        """Response with HTTP status 303

        Used to send a redirect to a GET endpoint after a POST request, known as post/redirect/get
        https://en.wikipedia.org/wiki/Post/Redirect/Get

        :param location: Location to redirect to
        """

        headers = headers or {}
        headers["location"] = location
        await self.respond_empty(
            status=HTTPStatus.SEE_OTHER, headers=headers, cookies=cookies
        )

    async def __listen_for_disconnect(self, cancel_scope: anyio.CancelScope):
        while True:
            if cancel_scope.cancel_called:
                return

            try:
                message = await self._receive()
            except Exception:
                logger.exception("error while listening for client disconnect")
                break

            if message["type"] == "http.disconnect":
                break

        cancel_scope.cancel()

    # pylint: disable=too-many-arguments
    @asynccontextmanager
    async def response_writer(
        self,
        status=HTTPStatus.OK,
        *,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
        encoding=DEFAULT_ENCODING,
    ) -> AsyncGenerator[Callable[[bytes], Awaitable], None]:
        """Context manager for streaming data to the response

        .. code-block::

            import json
            response = Response(scope, receive, send)
            async with response.response_writer(
                media_type="application/x-ndjson"
            ) as write:
                for i in range(10):
                    await write(json.dump({"number": i}))

        :raise ClientDisconnectError: If the client disconnects while sending data
        """

        spec_version_str = self._scope.get("asgi", {}).get("spec_version", "2.0")
        spec_version = tuple(int(i) for i in spec_version_str.split("."))

        await self.response.start(
            status,
            media_type=media_type,
            content_length=content_length,
            headers=headers,
            cookies=cookies,
            encoding=encoding,
        )

        if spec_version < (2, 4):
            async with anyio.create_task_group() as tg:
                tg.start_soon(partial(self.__listen_for_disconnect, tg.cancel_scope))

                async def _write_tg(data: bytes | str):
                    if not isinstance(data, bytes):
                        data = data.encode(encoding)

                    if tg.cancel_scope.cancel_called:
                        raise ClientDisconnectError()

                    await self.response.write(data, more_body=True)

                try:
                    yield _write_tg
                finally:
                    tg.cancel_scope.cancel()
                    await self.response.end()
                return

        async def _write(data: bytes | str):
            if not isinstance(data, bytes):
                data = data.encode(encoding)

            try:
                await self.response.write(data, more_body=True)
            except OSError:
                # pylint: disable=raise-missing-from
                raise ClientDisconnectError()

        try:
            yield _write
        finally:
            await self.response.end()

    # pylint: disable=too-many-arguments
    async def respond_stream(
        self,
        stream: AsyncIterable[bytes | str],
        *,
        status=HTTPStatus.OK,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
        encoding: str = DEFAULT_ENCODING,
    ):
        """Respond with the given stream of data

        :raise ClientDisconnectError: If the client disconnects while sending data
        """

        async with self.response_writer(
            status,
            media_type=media_type,
            content_length=content_length,
            headers=headers,
            cookies=cookies,
            encoding=encoding,
        ) as write:
            async for chunk in stream:
                await write(chunk)

    # pylint: disable=too-many-arguments
    async def respond_file(
        self,
        path: str | os.PathLike,
        *,
        status=HTTPStatus.OK,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
        stat_result: os.stat_result = None,
    ):
        """Send the given file to the response"""

        headers = headers or {}

        if not media_type:
            media_type, _ = mimetypes.guess_type(path, strict=False)

        headers["content-type"] = media_type

        if not stat_result:
            stat_result = await run_sync(os.stat, path)

        if not content_length:
            content_length = stat_result.st_size

        last_modified = formatdate(stat_result.st_mtime, usegmt=True)
        etag_base = str(stat_result.st_mtime) + "-" + str(stat_result.st_size)
        etag = f'"{hashlib.md5(etag_base.encode(), usedforsecurity=False).hexdigest()}"'
        headers["last-modified"] = last_modified
        headers["etag"] = etag

        if "http.response.pathsend" in self._scope.get("extensions", {}):
            await self.response.start(
                status,
                media_type=media_type,
                content_length=content_length,
                headers=headers,
                cookies=cookies,
            )
            await self._send(
                {
                    "type": "http.response.pathsend",
                    "path": str(path),
                }
            )
            return

        try:
            async with async_file_stream(path) as stream:
                await self.respond_stream(
                    stream,
                    status=status,
                    media_type=media_type,
                    content_length=content_length,
                    headers=headers,
                    cookies=cookies,
                )
        except ClientDisconnectError:
            pass
