import pandas as pd

from ezarr.dataframe import EZDataFrame


def test_can_replace_column(ezdf: EZDataFrame) -> None:
    ezdf["col_int"] = [-1, -2, -3]
    assert ezdf["col_int"].equals(pd.Series([-1, -2, -3]))
