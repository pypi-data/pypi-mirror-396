import zarr
import numpy as np

import ezarr.inplace as ezi


def test_delete():
    array = zarr.create_array({}, data=np.array([[1, 2, 3], [4, 5, 6]]))
    assert np.array_equal(ezi.delete(array, 1, axis=1), np.array([[1, 3], [4, 6]]))
