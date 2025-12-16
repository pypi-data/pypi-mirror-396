from typing import Literal
import numpy as np
import pandas as pd
import pytest

from ezarr.dataframe import EZDataFrame


def test_can_map_function(ezdf: EZDataFrame) -> None:
    res = ezdf.col_int.map(lambda x: x**2)

    assert np.array_equal(res, [1, 4, 9])


@pytest.mark.parametrize("klass", ["pandas", "ezarr"])
def test_can_test_equality(ezdf: EZDataFrame, klass: Literal["pandas", "ezarr"]) -> None:
    other = pd.DataFrame({"col_int": [1, 2, 3], "col_str": ["a", "bc", "def"], "col_float": [1.5, 2.5, 3.5]})

    if klass == "ezarr":
        other = EZDataFrame(other)

    assert np.array_equal(ezdf, other)
