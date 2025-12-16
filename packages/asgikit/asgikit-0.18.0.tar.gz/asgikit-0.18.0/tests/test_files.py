from pytest import fixture

from asgikit.files import async_file_stream


@fixture
def tmp_file(tmp_path):
    file = tmp_path / "test_file"
    file.write_text("test")
    return file


async def test_read_file_path(tmp_file):
    data = b""
    async with async_file_stream(tmp_file) as stream:
        async for chunk in stream:
            data += chunk

    assert data == b"test"


async def test_read_file_str_path(tmp_file):
    data = b""
    async with async_file_stream(str(tmp_file)) as stream:
        async for chunk in stream:
            data += chunk

    assert data == b"test"


async def test_read_file_chunks(tmp_file, monkeypatch):
    monkeypatch.setenv("ASGIKIT_ASYNC_FILE_CHUNK_SIZE", "1")

    # pylint: disable=import-outside-toplevel
    import importlib

    # pylint: disable=import-outside-toplevel
    from asgikit import files

    importlib.reload(files)

    # pylint: disable=reimported
    from asgikit.files import async_file_stream

    data = []
    async with async_file_stream(tmp_file) as stream:
        async for chunk in stream:
            data.append(chunk)

    assert data == [b"t", b"e", b"s", b"t"]
