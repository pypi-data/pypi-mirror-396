from __future__ import annotations

from typing import Any, Self, override

import numpy as np
import pytest
import zarr

import ezarr
from ezarr import io
from ezarr.types import SupportsEZReadWrite


class O:  # noqa: E742
    """A Python object"""

    def __init__(self, v: float):
        self._v: float = v

    @override
    def __repr__(self) -> str:
        return f"O({self._v})"

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, O):
            return False

        return self._v == other._v


class P(SupportsEZReadWrite):
    """A Python object that is a SupportsEZReadWrite"""

    def __init__(self, l_: list[int]):
        self.l: list[int] = l_

    @override
    def __repr__(self) -> str:
        return f"P([{', '.join(map(str, self.l))}])"

    @override
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, P):
            return False

        return self.l == other.l

    @override
    @classmethod
    def __ez_read__(cls, values: ezarr.EZDict[Any]) -> Self:
        arr = values["l"]
        assert isinstance(arr, zarr.Array)

        return cls(list(arr[:].tolist()))  # pyright: ignore[reportUnknownArgumentType, reportAttributeAccessIssue]

    @override
    def __ez_write__(self, values: ezarr.EZDict[Any]) -> None:
        io.write_object(values, obj=self.l, name="l")


@pytest.fixture
def ez_list() -> ezarr.EZList[Any]:
    data = [1.0, 2, P([1, 2, 3]), "4.", O(5.0)]

    return ezarr.EZList[Any].from_list(data, store={}, name="data")


def test_list_repr(ez_list: ezarr.EZList[Any]):
    assert repr(ez_list) == "EZList[1.0, 2, P([1, 2, 3]), '4.', O(5.0)]"


def test_list_should_read_custom_object(ez_list: ezarr.EZList[Any]):
    assert isinstance(ez_list[4], O)


def test_list_should_read_custom_object_with_method(ez_list: ezarr.EZList[Any]):
    assert isinstance(ez_list[2], P)


def test_list_should_convert_to_regular_list(ez_list: ezarr.EZList[Any]):
    lst = ez_list.copy()
    assert lst == [1.0, 2, P([1, 2, 3]), "4.", O(5.0)]


def test_list_get_negative_index(ez_list: ezarr.EZList[Any]):
    assert ez_list[-2] == "4."


def test_list_can_append_value_to_list(ez_list: ezarr.EZList[Any]):
    ez_list.append(-1)
    assert ez_list[5] == -1


def test_list_can_append_array_to_list(ez_list: ezarr.EZList[Any]):
    ez_list.append([7, 8, 9])
    assert np.array_equal(ez_list[5], [7, 8, 9])


def test_list_can_create_deferred_list(ez_dict: ezarr.EZDict[Any]):
    ez_dict["z"] = ezarr.EZList.defer([])

    assert isinstance(ez_dict["z"], ezarr.EZList)


def test_list_can_create_deferred_list_with_values(ez_dict: ezarr.EZDict[Any]):
    ez_dict["zz"] = ezarr.EZList.defer([1, 2, 3])

    assert isinstance(ez_dict["zz"], ezarr.EZList)
    assert ez_dict["zz"] == [1, 2, 3]


def test_list_can_delete_last_item(ez_list: ezarr.EZList[Any]):
    del ez_list[-1]
    assert ez_list == [1.0, 2, P([1, 2, 3]), "4."]


def test_list_can_delete_from_middle(ez_list: ezarr.EZList[Any]):
    del ez_list[2]
    assert ez_list == [1.0, 2, "4.", O(5.0)]
