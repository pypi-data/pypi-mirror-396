from collections.abc import Iterable
from typing import Self

from asgikit._constants import HEADER_ENCODING
from asgikit.multidict import MultiDict

__all__ = ("Headers", "encode_headers")


class Headers(MultiDict[str]):
    """Immutable headers backed by multivalue dict"""

    __slots__ = ()

    def __init__(self, data: Iterable[tuple[bytes, bytes]] = None):
        if not data:
            super().__init__()
            return

        super().__init__(
            (key.decode(HEADER_ENCODING).lower(), value.decode(HEADER_ENCODING))
            for key, value in data
        )

    @classmethod
    def from_dict(cls, data: dict[str, list[str]]) -> Self:
        instance = cls()
        instance._data = {
            key.lower(): value if isinstance(value, list) else [value]
            for key, value in data.items()
        }

        return instance

    def get_first(self, key: str, default: str = None) -> str | None:
        return super().get_first(key.lower(), default)

    def get(self, key: str, default: list[str] = None) -> list[str] | None:
        return super().get(key.lower(), default)

    def __getitem__(self, key: str) -> list[str]:
        return super().__getitem__(key.lower())

    def __contains__(self, key: str) -> bool:
        return super().__contains__(key.lower())


def encode_headers(headers: dict[str, str]) -> list[tuple[bytes, bytes]]:
    return [
        (key.encode(HEADER_ENCODING), value.encode(HEADER_ENCODING))
        for key, value in headers.items()
    ]
