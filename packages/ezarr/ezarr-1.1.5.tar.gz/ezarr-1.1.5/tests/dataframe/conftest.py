import tempfile
from collections.abc import Generator

import pandas as pd
import pytest

from ezarr.dataframe import EZDataFrame


@pytest.fixture
def ezdf() -> Generator[EZDataFrame, None, None]:
    with tempfile.TemporaryDirectory() as path:
        ezdf = EZDataFrame(
            pd.DataFrame({"col_int": [1, 2, 3], "col_str": ["a", "bc", "def"], "col_float": [1.5, 2.5, 3.5]})
        )

        ezdf.save(path, name="data")

        yield EZDataFrame.open(path, name="data")
