import pytest

from asgikit.headers import Headers, encode_headers


@pytest.mark.parametrize(
    "raw,parsed",
    [
        ([(b"a", b"1"), (b"b", b"2")], {"a": ["1"], "b": ["2"]}),
        ([(b"a", b"1, 2"), (b"b", b"3, 4")], {"a": ["1, 2"], "b": ["3, 4"]}),
        (
            [(b"a", b"1"), (b"a", b"2"), (b"b", b"3"), (b"b", b"4")],
            {"a": ["1", "2"], "b": ["3", "4"]},
        ),
        ([], {}),
    ],
)
def test_parse(raw, parsed):
    result = Headers(raw)
    assert result == parsed


def test_encode_headers():
    result = encode_headers({"a": "1", "b": "2"})
    assert result == [(b"a", b"1"), (b"b", b"2")]


@pytest.mark.parametrize(
    "data,expected",
    [
        ({"a": "1", "b": "2"}, {"a": ["1"], "b": ["2"]}),
        ({"a": ["1"], "b": "1"}, {"a": ["1"], "b": ["1"]}),
        ({"a": "1", "b": ["1"]}, {"a": ["1"], "b": ["1"]}),
        ({"a": ["1"], "b": ["1"]}, {"a": ["1"], "b": ["1"]}),
    ],
)
def test_from_dict(data, expected):
    result = Headers.from_dict(data)
    assert result == expected


def test_get_first():
    h = Headers.from_dict({"A": ["1", "2"]})
    assert h.get_first("a") == "1"


def test_get_all():
    h = Headers.from_dict({"A": ["1", "2"]})
    assert h.get("a") == ["1", "2"]


def test_getitem():
    h = Headers.from_dict({"A": ["1", "2"]})
    assert h["a"] == ["1", "2"]


def test_mapping_methods():
    d = Headers.from_dict({"a": "1", "b": ["2", "3"]})
    assert list(d.keys()) == ["a", "b"]
    assert list(d.values()) == [["1"], ["2", "3"]]
    assert list(d.items()) == [("a", ["1"]), ("b", ["2", "3"])]
    assert len(d) == 2
    assert "a" in d
