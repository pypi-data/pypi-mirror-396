from http import HTTPStatus
from logging import getLogger
import mimetypes

from asgikit._constants import (
    DEFAULT_ENCODING,
    IS_FINISHED,
    IS_STARTED,
    RESPONSE,
    SCOPE_ASGIKIT,
    STATUS,
)

from asgikit.cookies import Cookies
from asgikit.exceptions import (
    ResponseAlreadyEndedError,
    ResponseAlreadyStartedError,
    ResponseNotStartedError,
    WebSocketResponseNotSupportedError,
)
from asgikit.headers import encode_headers

__all__ = ("Response",)

logger = getLogger(__name__)

mimetypes.add_type("image/x-icon", ".ico")


class Response:
    """Response object used to interact with the client"""

    __slots__ = ("_scope", "_receive", "_send", "__type")

    def __init__(self, scope, receive, send):
        scope.setdefault(SCOPE_ASGIKIT, {})
        scope[SCOPE_ASGIKIT].setdefault(RESPONSE, {})
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_STARTED, False)
        scope[SCOPE_ASGIKIT][RESPONSE].setdefault(IS_FINISHED, False)

        self._scope = scope
        self._receive = receive
        self._send = send
        self.__type = "http" if scope["type"] == "http" else "websocket.http"

    @property
    def is_started(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED]

    def __set_started(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_STARTED] = True

    @property
    def is_finished(self) -> bool:
        """Tells whether the response is started or not"""

        return self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED]

    def __set_finished(self):
        self._scope[SCOPE_ASGIKIT][RESPONSE][IS_FINISHED] = True

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    @staticmethod
    def _encode_headers(
        status: HTTPStatus,
        media_type: str | None,
        content_length: int | None,
        headers: dict[str, str],
        cookies: Cookies | None,
        encoding: str,
    ) -> list[tuple[bytes, bytes]]:
        headers = headers or {}

        if media_type is not None:
            headers["content-type"] = media_type
            if media_type.startswith("text/") and "charset=" not in media_type:
                media_type += f"; charset={encoding}"

        if (
            content_length is not None
            and not (
                status < HTTPStatus.OK
                or status in (HTTPStatus.NO_CONTENT, HTTPStatus.NOT_MODIFIED)
            )
            and "content-length" not in headers
        ):
            headers["content-length"] = str(content_length)

        encoded_headers = encode_headers(headers)

        if cookies:
            encoded_headers.extend(cookies.encode())

        return encoded_headers

    # pylint: disable=too-many-arguments
    async def start(
        self,
        status: HTTPStatus,
        *,
        media_type: str = None,
        content_length: int = None,
        headers: dict[str, str] = None,
        cookies: Cookies = None,
        encoding: str = DEFAULT_ENCODING,
    ):
        """Start the response

        Must be called before calling ``write()`` or ``end()``

        :raise ResponseAlreadyStartedError: If the response is already started
        :raise ResponseAlreadyEndedError: If the response is finished
        :raise WebSocketResponseNotSupportedError: When sending websocket denial
            response on server that does not support it
        """

        if self._scope["type"] == "websocket" and (
            "websocket.http.response" not in self._scope.get("extensions", {})
        ):
            raise WebSocketResponseNotSupportedError()

        if self.is_finished:
            raise ResponseAlreadyEndedError()

        if self.is_started:
            raise ResponseAlreadyStartedError()

        self.__set_started()

        encoded_headers = self._encode_headers(
            status, media_type, content_length, headers, cookies, encoding
        )

        self._scope[SCOPE_ASGIKIT][RESPONSE][STATUS] = status

        await self._send(
            {
                "type": f"{self.__type}.response.start",
                "status": status,
                "headers": encoded_headers,
            }
        )

    async def write(self, body: bytes, *, more_body=False):
        """Write data to the response

        :raise ResponseNotStartedError: If the response is not started
        """

        if not isinstance(body, bytes):
            raise TypeError("body must be bytes")

        if self.is_finished:
            raise ResponseAlreadyEndedError()

        if not self.is_started:
            raise ResponseNotStartedError()

        await self._send(
            {
                "type": f"{self.__type}.response.body",
                "body": body,
                "more_body": more_body,
            }
        )

        if not more_body:
            self.__set_finished()

    async def end(self):
        """Finish the response

        Should be called when no more data will be written to the response

        Does nothing if the response already ended

        :raise ResponseNotStartedError: If the response is not started
        """

        if self.is_finished:
            logger.warning("Response already ended")
            return

        if not self.is_started:
            raise ResponseNotStartedError()

        await self.write(b"", more_body=False)
