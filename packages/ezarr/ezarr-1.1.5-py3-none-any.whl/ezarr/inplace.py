"""
Functions for operating on zarr.Arrays inplace
"""

from typing import Any, cast
import warnings

import numpy as np
import numpy.typing as npt
import zarr
from numpy._typing import _ArrayLikeInt_co  # pyright: ignore[reportPrivateUsage]
from zarr.errors import UnstableSpecificationWarning


def delete[A: zarr.Array | npt.NDArray[Any], T: np.generic](
    arr: A, obj: _ArrayLikeInt_co | slice, axis: int | None = None
) -> A:
    if not isinstance(arr, zarr.Array):
        return np.delete(arr, obj, axis)

    if arr.ndim > 1 and axis is None:
        raise NotImplementedError("Cannot flatten zarr.Array while working inplace")

    if axis is None:
        axis = 0

    if not isinstance(obj, int | np.integer):
        raise NotImplementedError

    obj = cast(np.integer, obj)

    if obj > arr.shape[axis]:
        raise IndexError(f"Index {obj} is out of bounds for axis {axis} with size {arr.shape[axis]}.")

    elif obj < 0:
        obj = cast(np.integer, obj + arr.shape[axis])

    prefix = (slice(None),) * axis
    if obj < (arr.shape[axis] - 1):
        # transfer data one row to the left, starting from the column after the one to delete
        # matrix | 0 1 2 3 4 | with index of the column to delete = 2
        #   ==>  | 0 1 3 4 . |
        index_dest = prefix + (slice(obj, -1),)
        index_source = prefix + (slice(obj + 1, None),)
        arr[index_dest] = arr[index_source]

    # resize the arrays to drop the extra column at the end
    # matrix | 0 1 3 4 . |
    #   ==>  | 0 1 3 4 |
    new_shape = arr.shape[:axis] + (arr.shape[axis] - 1,) + arr.shape[axis + 1 :]

    with warnings.catch_warnings(action="ignore", category=UnstableSpecificationWarning):
        arr.resize(new_shape)

    return arr
