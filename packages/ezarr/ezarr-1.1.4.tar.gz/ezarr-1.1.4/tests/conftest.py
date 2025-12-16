from typing import Any

import numpy as np
from pytest import fixture

import ezarr


@fixture
def ez_dict():
    data = {"a": 1, "b": [1, 2, 3], "c": {"d": "test", "e": np.arange(100)}, "f": np.zeros((10, 10, 10))}

    return ezarr.EZDict[Any].from_dict(data, store={}, name="data")
