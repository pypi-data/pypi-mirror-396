import numpy as np
from mattress import initialize

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def test_dense():
    for dt in [np.float64, np.float32, np.int64, np.int32, np.int16, np.int8, np.uint64, np.uint32, np.uint16, np.uint8]:
        y = (np.random.rand(1000, 100) * 100).astype(dt, order="C")
        ptr = initialize(y)
        assert all(ptr.row(0) == y[0, :])
        assert all(ptr.column(1) == y[:, 1])
        assert ptr.shape == (1000, 100)
        assert ptr.dtype == np.float64


def test_dense_column_major():
    y = np.ndarray((1000, 100), order="F")
    y[:, :] = np.random.rand(1000, 100)
    assert y.flags["F_CONTIGUOUS"]
    ptr = initialize(y)
    assert all(ptr.row(0) == y[0, :])
    assert all(ptr.column(1) == y[:, 1])
