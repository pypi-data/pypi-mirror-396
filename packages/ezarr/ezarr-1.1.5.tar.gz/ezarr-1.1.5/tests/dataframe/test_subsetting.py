import pytest
import numpy as np
import pandas as pd
from ezarr.dataframe import EZDataFrame


def test_loc(ezdf: EZDataFrame) -> None:
    assert np.all(ezdf.loc[2].values == np.array([3, "def", 3.5], dtype=object))


def test_loc_multi(ezdf: EZDataFrame) -> None:
    assert np.all(ezdf.loc[[2, 1]].values == np.array([[3, "def", 3.5], [2, "bc", 2.5]], dtype=object))


def test_loc_single_value(ezdf: EZDataFrame) -> None:
    value = ezdf.loc[1, "col_str"]
    assert value.ndim == 0  # pyright: ignore[reportAttributeAccessIssue]
    assert np.issubdtype(value.dtype, np.dtypes.StringDType())  # pyright: ignore[reportUnknownArgumentType, reportAttributeAccessIssue]
    assert value == "bc"


def test_get_column(ezdf: EZDataFrame) -> None:
    assert ezdf["col_str"].equals(pd.Series(["a", "bc", "def"], name="col_str"))


def test_get_column_regular_df(ezdf: EZDataFrame):
    df = pd.DataFrame({"col_str": ["a", "bc", "def"]})
    assert df["col_str"].equals(pd.Series(["a", "bc", "def"], name="col_str"))

    assert ezdf["col_str"].equals(df["col_str"])


@pytest.mark.xfail
def test_compare_with_regular_df(ezdf: EZDataFrame):
    # TODO: maybe one day find a fix, for now can only use h5dataframe.equals(), pd.DataFrame.equals() fails
    df = pd.DataFrame({"col_str": ["a", "bc", "def"]})
    assert df["col_str"].equals(ezdf["col_str"])


def test_iterrows(ezdf: EZDataFrame):
    _, row = next(ezdf.iterrows())
    assert row.equals(pd.Series([1, "a", 1.5], index=["col_int", "col_str", "col_float"]))
