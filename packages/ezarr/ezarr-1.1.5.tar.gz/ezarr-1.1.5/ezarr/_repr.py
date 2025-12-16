import itertools as it
import math
from typing import Any, cast

import numpy as np
import numpy.typing as npt
import zarr

import ezarr


def repr_element(elem: Any, prefix: str = "") -> str:
    if isinstance(elem, np.str_):
        return f"'{elem}'"

    if isinstance(elem, np.generic):
        return str(elem)

    if isinstance(elem, zarr.Group | ezarr.EZDict):
        return "{...}" if len(elem) else "{}"  # pyright: ignore[reportUnknownArgumentType]

    if isinstance(elem, zarr.Array):
        return repr_array(elem, prefix=prefix)

    return repr(elem)


def repr_array(arr: zarr.Array, prefix: str = "") -> str:
    if arr.size == 0:
        return "[]"

    if arr.ndim == 0:
        return repr_element(arr[()])

    data = cast(npt.NDArray[Any], arr.get_orthogonal_selection(tuple(_get_index(shape) for shape in arr.shape)))

    if np.issubdtype(data.dtype, np.integer):
        align = math.ceil(math.log10(data.max()))

    elif np.issubdtype(data.dtype, np.floating):
        data = np.vectorize(np.format_float_positional)(data)
        align = np.vectorize(len)(data).max()

    elif np.issubdtype(data.dtype, np.dtypes.StringDType()):
        align = np.vectorize(len)(data).max()

    else:
        data = data.astype(str)
        align = np.vectorize(len)(data).max()

    return _print3(data, list(arr.shape), align=align, prefix=prefix, ignore_prefix=True)


def _get_index(axis_shape: int) -> list[int]:
    if axis_shape <= 6:
        return list(range(axis_shape))

    return [0, 1, 2, -3, -2, -1]


def _print3(data: np.ndarray, shape: list[int], align: int, *, prefix: str = "", ignore_prefix: bool = False) -> str:
    if data.ndim == 1:
        if shape[0] <= 6:
            values = data
        else:
            values = it.chain(data[:3], ["..."], data[3:])

        return f"{'' if ignore_prefix else prefix}[{' '.join(map(lambda v: f'{v:>{align}}', values))}]"

    if shape[0] <= 6:
        rows = [
            _print3(data[idx], shape[1:], align, prefix=prefix + " ", ignore_prefix=idx == 0) for idx in range(shape[0])
        ]

    else:
        rows = [
            _print3(data[0], shape[1:], align, prefix=prefix + " ", ignore_prefix=True),
            _print3(data[1], shape[1:], align, prefix=prefix + " "),
            _print3(data[2], shape[1:], align, prefix=prefix + " "),
            f"{prefix} ...",
            _print3(data[3], shape[1:], align, prefix=prefix + " "),
            _print3(data[4], shape[1:], align, prefix=prefix + " "),
            _print3(data[5], shape[1:], align, prefix=prefix + " "),
        ]

    sep = "," + "\n" * max(1, len(shape) - 1)
    return f"{'' if ignore_prefix else prefix}[{sep.join(rows)}]"
