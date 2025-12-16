import os
import re
import shutil
from collections.abc import AsyncGenerator, AsyncIterable
from dataclasses import dataclass
from io import BytesIO
from tempfile import SpooledTemporaryFile

from multipart import MultipartSegment, PushMultipartParser

from asgikit.exceptions import MultipartBoundaryError
from asgikit.multidict import MultiDict
from asgikit.sync import run_sync

__all__ = ("UploadedFile", "process_multipart")

MAX_SPOOL_FILE_SIZE = 4 * 1024 * 1024  # 4MB
RE_MULTIPART = re.compile(r"""boundary=\"?([\w-]+)\"?""")


@dataclass
class UploadedFile:
    """File uploaded in a multipart form"""

    file: SpooledTemporaryFile
    filename: str
    media_type: str
    size: int

    def __copy_file(self, dst: str | os.PathLike):
        with self.file as src_fd, open(dst, "wb") as dst_fd:
            shutil.copyfileobj(src_fd, dst_fd)

    async def copy_to(self, dst: str | os.PathLike):
        """Copy file into given path"""
        await run_sync(self.__copy_file, dst)


async def process_multipart(
    reader: AsyncIterable[bytes], content_type: str, charset: str = None
) -> MultiDict[str | UploadedFile]:
    result = []
    async for name, value in _process_multipart(reader, content_type, charset):
        result.append((name, value))

    return MultiDict(result)


async def _process_multipart(
    reader: AsyncIterable[bytes], content_type: str, charset: str = None
) -> AsyncGenerator[tuple[str, str | UploadedFile], None]:
    match = RE_MULTIPART.search(content_type)
    if not match:
        raise MultipartBoundaryError()

    boundary = match.group(1)

    current_segment: MultipartSegment = None
    current_value: BytesIO = None
    current_file: SpooledTemporaryFile = None
    current_is_file: bool = False

    with PushMultipartParser(boundary) as parser:
        async for chunk in reader:
            for result in parser.parse(chunk):
                if isinstance(result, MultipartSegment):
                    current_segment = result
                    if result.filename:
                        current_is_file = True
                        current_file = SpooledTemporaryFile(
                            max_size=MAX_SPOOL_FILE_SIZE,
                            mode="w+b",
                        )
                        current_value = None
                    else:
                        current_is_file = False
                        current_value = BytesIO()
                        current_file = None
                elif result:  # Non-empty bytearray
                    if current_is_file:
                        await run_sync(current_file.write, result)
                    else:
                        current_value.write(result)
                else:  # None
                    if current_is_file:
                        await run_sync(current_file.seek, 0)
                        uploaded_file = UploadedFile(
                            file=current_file,
                            filename=current_segment.filename,
                            media_type=current_segment.content_type,
                            size=current_segment.size,
                        )
                        yield current_segment.name, uploaded_file
                    else:
                        current_value.seek(0)
                        yield (
                            current_segment.name,
                            current_value.read().decode(charset),
                        )
        parser.close(check_complete=True)
