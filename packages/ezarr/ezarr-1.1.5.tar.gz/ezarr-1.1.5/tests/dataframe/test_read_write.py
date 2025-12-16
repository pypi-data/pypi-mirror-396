import numpy as np
import pandas as pd
import pytest
import zarr

from ezarr.dataframe import EZDataFrame


def test_can_write() -> None:
    ezdf = EZDataFrame(
        pd.DataFrame(
            {"col_int": [1, 2, 3], "col_str": ["a", "bc", "def"], "col_float": [1.5, 2.5, 3.5]}, index=["a", "b", "c"]
        )
    )

    store = zarr.create_group({})
    ezdf.save(store.store, name="data")

    assert set(store["data"].keys()) == {"index", "arrays"}  # pyright: ignore[reportUnknownArgumentType, reportAttributeAccessIssue]
    assert np.array_equal(store["data/index"], ["a", "b", "c"])  # pyright: ignore[reportArgumentType]
    assert set(store["data/arrays"].keys()) == {"col_float", "col_int", "col_str"}  # pyright: ignore[reportUnknownArgumentType, reportAttributeAccessIssue]
    assert np.array_equal(store["data/arrays/col_int"], [1, 2, 3])  # pyright: ignore[reportArgumentType]


@pytest.mark.filterwarnings("ignore")
def test_can_read() -> None:
    store = zarr.create_group({})

    store["data/index"] = np.array(["a", "b", "c"])
    store["data/arrays/col_int"] = np.array([1, 2, 3])
    store["data/arrays/col_str"] = np.array(["a", "bc", "def"])
    store["data/arrays"].attrs["columns_order"] = ["col_int", "col_str"]

    ezdf = EZDataFrame.open(store.store, name="data")
    assert np.array_equal(ezdf.index, ["a", "b", "c"])
    assert np.array_equal(ezdf.columns, ["col_int", "col_str"])
