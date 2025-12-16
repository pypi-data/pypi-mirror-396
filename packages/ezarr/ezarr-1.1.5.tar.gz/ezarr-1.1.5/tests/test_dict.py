from typing import Any, Self, cast, override
import numpy as np
import zarr

import ezarr
from ezarr.types import SupportsEZReadWrite


def test_dict_creation(ez_dict: ezarr.EZDict[Any]):
    assert isinstance(ez_dict, ezarr.EZDict)


def test_dict_can_iterate_through_keys(ez_dict: ezarr.EZDict[Any]):
    assert sorted(iter(ez_dict)) == ["a", "b", "c", "f"]


def test_dict_has_correct_keys(ez_dict: ezarr.EZDict[Any]):
    assert sorted(ez_dict.keys()) == ["a", "b", "c", "f"]


def test_dict_can_get_regular_values(ez_dict: ezarr.EZDict[Any]):
    assert ez_dict["a"] == 1


def test_dict_can_get_string(ez_dict: ezarr.EZDict[Any]):
    assert ez_dict["c"]["d"] == "test"


def test_dict_can_get_Array(ez_dict: ezarr.EZDict[Any]):
    assert isinstance(ez_dict["c"]["e"], zarr.Array)


def test_dict_should_return_string(ez_dict: ezarr.EZDict[Any]):
    assert isinstance(ez_dict["c"]["d"], str)


def test_dict_gets_nested_ez_dicts(ez_dict: ezarr.EZDict[Any]):
    assert isinstance(ez_dict["c"], ezarr.EZDict)


def test_dict_has_correct_values(ez_dict: ezarr.EZDict[Any]):
    assert ez_dict["a"] == 1
    assert np.array_equal(ez_dict["b"], [1, 2, 3])
    assert sorted(ez_dict["c"].keys()) == ["d", "e"]
    assert ez_dict["f"].shape == (10, 10, 10)


def test_dict_can_set_regular_value(ez_dict: ezarr.EZDict[Any]):
    ez_dict["a"] = 5

    assert ez_dict["a"] == 5


def test_dict_can_set_array_value(ez_dict: ezarr.EZDict[Any]):
    ez_dict["b"][1] = 6

    assert np.array_equal(ez_dict["b"], [1, 6, 3])


def test_dict_can_set_new_regular_value(ez_dict: ezarr.EZDict[Any]):
    ez_dict["x"] = 9

    assert ez_dict["x"] == 9


def test_dict_can_set_new_array(ez_dict: ezarr.EZDict[Any]):
    ez_dict["y"] = np.array([1, 2, 3])

    assert np.array_equal(ez_dict["y"], [1, 2, 3])


def test_dict_can_set_new_zarray(ez_dict: ezarr.EZDict[Any]):
    arr = zarr.create_array({}, data=np.array([1, 2, 3]))
    ez_dict["zy"] = arr

    assert np.array_equal(ez_dict["zy"], [1, 2, 3])


def test_dict_can_set_new_dict(ez_dict: ezarr.EZDict[Any]):
    ez_dict["z"] = {"l": 10, "m": [10, 11, 12], "n": {"o": 13}}

    assert (
        isinstance(ez_dict["z"], ezarr.EZDict)
        and ez_dict["z"]["l"] == 10
        and np.array_equal(ez_dict["z"]["m"], [10, 11, 12])
        and isinstance(ez_dict["z"]["n"], ezarr.EZDict)
        and ez_dict["z"]["n"]["o"] == 13
    )


def test_dict_can_replace_dict(ez_dict: ezarr.EZDict[Any]):
    ez_dict["c"] = {"d2": "test", "e": np.arange(10, 20)}

    assert isinstance(ez_dict["c"], ezarr.EZDict)
    assert "d" not in ez_dict["c"].keys()
    assert ez_dict["c"]["d2"] == "test"
    assert np.array_equal(ez_dict["c"]["e"], np.arange(10, 20))


def test_dict_can_union(ez_dict: ezarr.EZDict[Any]):
    ez_dict["c"] |= {"d": "new_val", "g": -1, "h": {"i": "nested"}}

    assert sorted(ez_dict["c"].keys()) == ["d", "e", "g", "h"]
    assert ez_dict["c"]["d"] == "new_val"
    assert np.array_equal(ez_dict["c"]["e"], np.arange(100))
    assert ez_dict["c"]["g"] == -1
    assert ez_dict["c"]["h"]["i"] == "nested"


def test_dict_can_delete_regular_value(ez_dict: ezarr.EZDict[Any]):
    del ez_dict["a"]

    assert "a" not in ez_dict.keys()


def test_dict_can_delete_array(ez_dict: ezarr.EZDict[Any]):
    del ez_dict["b"]

    assert "b" not in ez_dict.keys()


def test_dict_can_delete_dict(ez_dict: ezarr.EZDict[Any]):
    del ez_dict["c"]

    assert "c" not in ez_dict.keys()


def test_dict_copy_should_be_regular_dict(ez_dict: ezarr.EZDict[Any]):
    c = ez_dict.copy()

    assert isinstance(c, dict)


def test_dict_copy_should_have_same_keys(ez_dict: ezarr.EZDict[Any]):
    c = ez_dict.copy()

    assert c.keys() == ez_dict.keys()


def test_dict_copy_nested_ez_dict_should_be_dict(ez_dict: ezarr.EZDict[Any]):
    c = ez_dict.copy()

    assert isinstance(c["c"], dict)


def test_dict_copy_dataset_proxy_should_be_array(ez_dict: ezarr.EZDict[Any]):
    c = ez_dict.copy()

    assert type(c["b"]) == np.ndarray  # noqa: E721


class ComplexObject(SupportsEZReadWrite):
    def __init__(self, value: int):
        self.value: int = value

    @override
    def __repr__(self) -> str:
        return f"CO({self.value})"

    @override
    def __ez_write__(self, values: ezarr.EZDict[Any]) -> None:
        values.attrs["value"] = self.value

    @override
    @classmethod
    def __ez_read__(cls, values: ezarr.EZDict[Any]) -> Self:
        return cls(cast(int, values.attrs["value"]))


def test_dict_can_store_complex_objects(ez_dict: ezarr.EZDict[Any]):
    ez_dict["g"] = {"a": ComplexObject(1), "b": ComplexObject(2)}

    assert isinstance(ez_dict["g"]["a"], ComplexObject)


def test_dict_can_be_destructured_in_pattern_matching(ez_dict: ezarr.EZDict[Any]):
    match ez_dict:
        case ezarr.EZDict(grp):  # pyright: ignore[reportUnknownVariableType, reportGeneralTypeIssues]
            assert isinstance(grp, zarr.Group)

        case _:
            raise ValueError
