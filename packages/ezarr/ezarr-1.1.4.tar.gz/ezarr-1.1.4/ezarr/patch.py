from typing import Any, Literal
from collections.abc import Callable

import numpy as np
import numpy.typing as npt
import zarr


def zarr_astype(self: zarr.Array, dtype: npt.DTypeLike, order: Literal["K", "A", "C", "F"] = "K", copy: bool = True):
    return self[:].astype(dtype, order=order, copy=copy)  # pyright: ignore[reportUnknownVariableType]


# pyright: reportAttributeAccessIssue=false, reportUnknownLambdaType=false
zarr.Array.__len__ = lambda self: self.shape[0]
zarr.Array.astype = zarr_astype
zarr.Array.copy = lambda self: self[:]
zarr.Array.tolist = lambda self: np.asarray(self).tolist()


def _inplace(array: zarr.Array, func: Callable[..., Any], value: Any) -> zarr.Array:
    if array.read_only:
        raise ValueError("assignment destination is read-only")

    for chunk in array._iter_chunk_regions():  # pyright: ignore[reportPrivateUsage]
        array[chunk] = func(array[chunk], value)

    return array


# pyright: reportUnknownArgumentType=false
zarr.Array.__add__ = lambda self, other: np.add(self, other)
zarr.Array.__iadd__ = lambda self, other: _inplace(self, np.add, other)
zarr.Array.__sub__ = lambda self, other: np.subtract(self, other)
zarr.Array.__isub__ = lambda self, other: _inplace(self, np.subtract, other)
zarr.Array.__mul__ = lambda self, other: np.multiply(self, other)
zarr.Array.__imul__ = lambda self, other: _inplace(self, np.multiply, other)
zarr.Array.__truediv__ = lambda self, other: np.divide(self, other)
zarr.Array.__itruediv__ = lambda self, other: _inplace(self, np.divide, other)
zarr.Array.__mod__ = lambda self, other: np.mod(self, other)
zarr.Array.__imod__ = lambda self, other: _inplace(self, np.mod, other)
zarr.Array.__pow__ = lambda self, other: np.pow(self, other)
zarr.Array.__ipow__ = lambda self, other: _inplace(self, np.power, other)
zarr.Array.__or__ = lambda self, other: np.logical_or(self, other)
zarr.Array.__ior__ = lambda self, other: _inplace(self, np.logical_or, other)
zarr.Array.__and__ = lambda self, other: np.logical_and(self, other)
zarr.Array.__iand__ = lambda self, other: _inplace(self, np.logical_and, other)
zarr.Array.__xor__ = lambda self, other: np.logical_xor(self, other)
zarr.Array.__ixor__ = lambda self, other: _inplace(self, np.logical_xor, other)


# numpy functions compatibility
def _argsort(
    self: zarr.Array,
    axis: int | None = -1,
    kind: Literal["quicksort", "mergesort", "heapsort", "stable"] = "quicksort",
    order: str | list[str] | None = None,
    *,
    stable: bool | None = None,
):
    return np.argsort(self[:], axis=axis, kind=kind, order=order, stable=stable)


zarr.Array.argsort = _argsort
