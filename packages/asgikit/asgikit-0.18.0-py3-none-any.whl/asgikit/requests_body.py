import json
import logging
import re
from collections.abc import AsyncIterable
from typing import Any
from urllib.parse import parse_qsl

from asgikit._constants import (
    CHARSET,
    CONTENT_LENGTH,
    CONTENT_TYPE,
    DEFAULT_ENCODING,
    HEADER_ENCODING,
    IS_CONSUMED,
    REQUEST,
    SCOPE_ASGIKIT,
)
from asgikit.exceptions import (
    AsgiException,
    ClientDisconnectError,
    RequestAlreadyConsumedError,
)
from asgikit.forms import UploadedFile, process_multipart
from asgikit.multidict import MultiDict

__all__ = ("Body",)

RE_CHARSET = re.compile(r"""charset="?([\w-]+)"?""")

FORM_URLENCODED_CONTENT_TYPE = "application/x-www-urlencoded"
FORM_MULTIPART_CONTENT_TYPE = "multipart/form-data"
FORM_CONTENT_TYPES = (FORM_URLENCODED_CONTENT_TYPE, FORM_MULTIPART_CONTENT_TYPE)

logger = logging.getLogger(__name__)


class Body:
    """Request body

    Provides methods to read the request body
    """

    __slots__ = ("_scope", "_receive")

    def __init__(self, scope, receive):
        self._scope = scope
        self._receive = receive

        content_type = None
        content_length = None
        for name, value in scope["headers"]:
            if name.lower() == b"content-type":
                content_type = value.decode(HEADER_ENCODING)
            if name.lower() == b"content-length":
                content_length = int(value.decode(HEADER_ENCODING))
            if content_type and content_length:
                break

        self._scope.setdefault(SCOPE_ASGIKIT, {})
        self._scope[SCOPE_ASGIKIT].setdefault(REQUEST, {})
        self._scope[SCOPE_ASGIKIT][REQUEST].setdefault(IS_CONSUMED, False)

        if CONTENT_TYPE not in scope[SCOPE_ASGIKIT][REQUEST]:
            self._scope[SCOPE_ASGIKIT][REQUEST][CONTENT_TYPE] = content_type

        if CONTENT_LENGTH not in scope[SCOPE_ASGIKIT][REQUEST]:
            self._scope[SCOPE_ASGIKIT][REQUEST][CONTENT_LENGTH] = content_length

        if CHARSET not in self._scope[SCOPE_ASGIKIT][REQUEST]:
            if content_type:
                values = RE_CHARSET.findall(content_type)
                charset = values[0] if values else DEFAULT_ENCODING
            else:
                charset = DEFAULT_ENCODING
            self._scope[SCOPE_ASGIKIT][REQUEST][CHARSET] = charset

    @property
    def content_type(self) -> str | None:
        """Content type of the request body"""

        return self._scope[SCOPE_ASGIKIT][REQUEST][CONTENT_TYPE]

    @property
    def content_length(self) -> int | None:
        """Content length of the request body"""

        return self._scope[SCOPE_ASGIKIT][REQUEST].get(CONTENT_LENGTH)

    @property
    def charset(self) -> str | None:
        """Charset of the request"""

        return self._scope[SCOPE_ASGIKIT][REQUEST][CHARSET]

    @property
    def is_consumed(self) -> bool:
        """Verifies whether the request body is consumed or not"""
        return self._scope[SCOPE_ASGIKIT][REQUEST][IS_CONSUMED]

    def __set_consumed(self):
        self._scope[SCOPE_ASGIKIT][REQUEST][IS_CONSUMED] = True

    async def __aiter__(self) -> AsyncIterable[bytes]:
        """Iterate over the bytes of the request body

        :raise RequestBodyAlreadyConsumedError: If the request body is already consumed
        :raise ClientDisconnectError: If the client is disconnected while reading the request body
        :raise AsgiException: if an invalid asgi message is received
        """

        if self.is_consumed:
            raise RequestAlreadyConsumedError()

        while True:
            message = await self._receive()

            if message["type"] == "http.request":
                data = message["body"]

                if not message["more_body"]:
                    self.__set_consumed()

                yield data

                if self.is_consumed:
                    break
            elif message["type"] == "http.disconnect":
                raise ClientDisconnectError()
            else:
                raise AsgiException(f"invalid message type: '{message['type']}'")

    async def read_bytes(self) -> bytes:
        """Read the full request body"""

        data = bytearray()

        async for chunk in self:
            data.extend(chunk)

        return bytes(data)

    async def read_text(self, encoding: str = None) -> str:
        """Read the full request body as str"""

        data = await self.read_bytes()
        return data.decode(encoding or self.charset)

    async def read_json(self) -> Any:
        """Read the full request body and parse it as json"""

        if data := await self.read_bytes():
            return json.loads(data)

        return None

    @staticmethod
    def _is_form_multipart(content_type: str) -> bool:
        return content_type.startswith(FORM_MULTIPART_CONTENT_TYPE)

    async def read_form(self) -> MultiDict[str | UploadedFile]:
        """Read the full request body and parse it as form encoded"""

        if self._is_form_multipart(self.content_type):
            return await process_multipart(self, self.content_type, self.charset)

        if data := await self.read_text():
            return MultiDict(parse_qsl(data, keep_blank_values=True))

        return MultiDict()
