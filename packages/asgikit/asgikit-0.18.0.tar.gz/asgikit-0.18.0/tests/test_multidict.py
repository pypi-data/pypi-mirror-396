import pytest

from asgikit.multidict import MultiDict, MutableMultiDict


def test_initial_data():
    result = MultiDict([("a", 1), ("b", 2)])
    assert result == {"a": [1], "b": [2]}


def test_from_dict():
    d = MutableMultiDict.from_dict({"a": [1, 2]})
    assert d == {"a": [1, 2]}


def test_add_single_value():
    d = MutableMultiDict()

    d.add("a", 1)
    assert d == {"a": [1]}

    d.add("a", 2)
    assert d == {"a": [1, 2]}


def test_set_single_value():
    d = MutableMultiDict()

    d.set("a", 1)
    assert d == {"a": [1]}

    d.set("a", 2)
    assert d == {"a": [2]}


def test_add_multiple_values():
    d = MutableMultiDict()

    d.add("a", 1, 2)
    assert d == {"a": [1, 2]}

    d.add("a", 3, 4)
    assert d == {"a": [1, 2, 3, 4]}


def test_set_multiple_values():
    d = MutableMultiDict()

    d.set("a", 1, 2)
    assert d == {"a": [1, 2]}

    d.set("a", 3, 4)
    assert d == {"a": [3, 4]}


def test_setitem_not_list_should_fail():
    d = MutableMultiDict()

    with pytest.raises(AssertionError):
        d["a"] = 1


def test_setitem():
    d = MutableMultiDict()

    d["a"] = [1, 2]
    assert d == {"a": [1, 2]}

    d["a"] = [3, 4]
    assert d == {"a": [3, 4]}


def test_get_first():
    d = MutableMultiDict.from_dict({"a": [1, 2]})
    assert d.get_first("a") == 1


def test_get_all():
    d = MutableMultiDict.from_dict({"a": [1, 2]})
    assert d.get("a") == [1, 2]


def test_getitem():
    d = MutableMultiDict.from_dict({"a": [1, 2]})
    assert d["a"] == [1, 2]


def test_delitem():
    d = MutableMultiDict.from_dict({"a": [1, 2]})
    del d["a"]
    assert d == {}


def test_mapping_methods():
    d = MutableMultiDict.from_dict({"a": 1, "b": [2, 3]})
    assert list(d.keys()) == ["a", "b"]
    assert list(d.values()) == [[1], [2, 3]]
    assert list(d.items()) == [("a", [1]), ("b", [2, 3])]
    assert len(d) == 2
    assert "a" in d
