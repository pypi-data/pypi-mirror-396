import copy
from collections.abc import Iterable
from typing import Generic, Self, TypeVar

__all__ = ("MultiDict", "MutableMultiDict")

T = TypeVar("T")


class MultiDict(Generic[T]):
    """dict that can hold multiple values in a single key"""

    __slots__ = ("_data",)

    def __init__(self, data: Iterable[tuple[str, T]] = None):
        self._data = {}

        if not data:
            return

        for key, value in data:
            if key not in self._data:
                self._data[key] = []

            self._data[key].append(value)

    @classmethod
    def from_dict(cls, data: dict[str, T | list[T]]) -> Self:
        instance = cls()
        instance._data = {
            key: value if isinstance(value, list) else [value]
            for key, value in data.items()
        }

        return instance

    def get_first(self, key: str, default: T = None) -> T | None:
        """Get the first item in the given key"""

        if value := self._data.get(key):
            return value[0]

        return default

    def get(self, key: str, default: list[T] = None) -> list[T] | None:
        """Get all items in the given key"""
        return self._data.get(key, default)

    def keys(self) -> Iterable[str]:
        """Iterate over all keys"""
        return self._data.keys()

    def values(self) -> Iterable[list[T]]:
        """Iterate over all values"""
        return self._data.values()

    def items(self) -> Iterable[tuple[str, T]]:
        """Iterate over all items"""
        return self._data.items()

    def __getitem__(self, key: str) -> list[T]:
        return self._data[key]

    def __contains__(self, key: str):
        return key in self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self) -> Iterable[str]:
        return self._data.__iter__()

    def __copy__(self):
        return MultiDict(copy.copy(self._data))

    def __deepcopy__(self, memo):
        return MultiDict(copy.deepcopy(self._data, memo=memo))

    def __eq__(self, other):
        if isinstance(other, MultiDict):
            return self._data == other._data
        if isinstance(other, dict):
            return self._data == other

        return False

    def __str__(self):
        return str(self._data)

    def __repr__(self):
        return repr(self._data)


class MutableMultiDict(MultiDict[T]):
    """Mutable version of MultiValueDict"""

    def add(self, key: str, *args: T):
        """Add items in the given key. If the key already exists, the value is appended"""

        if key not in self._data:
            self._data[key] = list(args)
            return

        self._data[key].extend(args)

    def set(self, key: str, *args: T):
        """Set items in the given key. Overwrite the existing value"""
        self._data[key] = list(args)

    def __setitem__(self, key: str, value: list[T]):
        """Set all items in the given key"""
        assert isinstance(value, list)
        self._data[key] = value

    def __delitem__(self, key: str):
        """Remove an item in the given key"""
        del self._data[key]
