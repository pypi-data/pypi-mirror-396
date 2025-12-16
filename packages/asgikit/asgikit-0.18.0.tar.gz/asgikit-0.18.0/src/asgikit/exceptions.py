class AsgiException(Exception):
    """Generic ASGI exception"""


class HttpException(AsgiException):
    """Generic HTTP exception"""


class ClientDisconnectError(HttpException):
    """Client disconnected"""


class RequestAlreadyConsumedError(HttpException):
    """Tried to consume a request body that is already consumed"""


class ResponseAlreadyStartedError(HttpException):
    """Tried to start a response that has already started"""


class ResponseNotStartedError(HttpException):
    """Interacted with a response that has not yet started"""


class ResponseAlreadyEndedError(HttpException):
    """Interacted with a response that has already ended"""


class WebSocketException(AsgiException):
    """Generic websocket exception"""


class WebSocketClosedError(WebSocketException):
    """Tried to interact with a closed websocket"""


class WebSocketStateError(WebSocketException):
    """Websocket is in the wrong state for the interaction"""


class WebSocketDisconnect(WebSocketException):
    """Websocket client disconnected"""

    def __init__(self, code: int, reason: str | None):
        self.code = code
        self.reason = reason
        super().__init__(f"websocket disconnected: code={code} reason='{reason}'")


class WebSocketResponseNotSupportedError(WebSocketException):
    """Asgi server does not support websocket denial response"""


class MultipartBoundaryError(Exception):
    """Failed to find the multipart boundary"""
