import os
from collections.abc import AsyncGenerator, AsyncIterable
from contextlib import asynccontextmanager

import anyio

__all__ = ("async_file_stream",)

DEFAULT_ASYNC_FILE_CHUNK_SIZE = "4096"
_CHUNK_SIZE = int(
    os.getenv("ASGIKIT_ASYNC_FILE_CHUNK_SIZE", DEFAULT_ASYNC_FILE_CHUNK_SIZE)
)


@asynccontextmanager
async def async_file_stream(
    path: str | os.PathLike,
) -> AsyncGenerator[AsyncIterable[bytes]]:
    file = await anyio.open_file(path, mode="rb")

    async def _stream():
        while data := await file.read(_CHUNK_SIZE):
            yield data

    try:
        yield _stream()
    finally:
        await file.aclose()
