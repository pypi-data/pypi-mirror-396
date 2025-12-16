import numpy as np
import pandas as pd

from ezarr.dataframe import EZDataFrame


def test_create_empty() -> None:
    ezdf = EZDataFrame()
    assert (
        repr(ezdf)
        == """\
Empty EZDataFrame
Columns: []
Index: []
[RAM]"""
    )


def test_can_create_from_pandas_DataFrame(ezdf: EZDataFrame) -> None:
    assert isinstance(ezdf, EZDataFrame)


def test_has_correct_columns(ezdf: EZDataFrame) -> None:
    assert np.array_equal(ezdf.columns, ["col_int", "col_str", "col_float"])


def test_has_correct_repr(ezdf: EZDataFrame) -> None:
    assert (
        repr(ezdf)
        == """\
   col_int col_str  col_float
0        1       a        1.5
1        2      bc        2.5
2        3     def        3.5
[Local]
[3 rows x 3 columns]"""
    )


def test_convert_to_pandas(ezdf: EZDataFrame) -> None:
    df = ezdf.copy()

    assert isinstance(df, pd.DataFrame)
    assert np.array_equal(df.index, [0, 1, 2])
    assert np.array_equal(df.columns, ["col_int", "col_str", "col_float"])
    assert np.array_equal(df.col_int, [1, 2, 3])
    assert np.array_equal(df.col_str, ["a", "bc", "def"])


def test_can_get_column_from_getattr(ezdf: EZDataFrame) -> None:
    assert np.array_equal(ezdf.col_str, ["a", "bc", "def"])


def test_can_set_existing_column(ezdf: EZDataFrame) -> None:
    ezdf["col_int"] = -1
    assert np.array_equal(ezdf["col_int"], [-1, -1, -1])


def test_can_set_new_column_str(ezdf: EZDataFrame) -> None:
    ezdf["new"] = "new!"
    assert np.array_equal(ezdf["new"], ["new!", "new!", "new!"])


def test_can_set_new_column_int(ezdf: EZDataFrame) -> None:
    ezdf["new"] = [-1, -2, -3]
    assert np.array_equal(ezdf["new"], [-1, -2, -3])


def test_can_set_column_no_index() -> None:
    ezdf = EZDataFrame(pd.DataFrame(columns=["value"], dtype=int))
    ezdf["value"] = [1, 2, 3]

    assert np.array_equal(ezdf["value"], [1, 2, 3])


def test_set_value_sets_in_h5_file(ezdf: EZDataFrame) -> None:
    ezdf.loc[1, "col_str"] = "test"

    assert np.array_equal(ezdf._data_store["arrays"]["col_str"], ["a", "test", "def"])
