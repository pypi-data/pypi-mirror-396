import numpy as np

from ezarr.dataframe import EZDataFrame


def test_can_map_function(ezdf: EZDataFrame) -> None:
    res = ezdf.col_int.map(lambda x: x**2)

    assert np.array_equal(res, [1, 4, 9])
