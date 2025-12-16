import numpy as np
import delayedarray as da
from mattress import initialize

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def test_delayed_transpose():
    y = np.random.rand(1000, 100)
    x = da.DelayedArray(y)

    t = x.T
    ptr = initialize(t)
    assert all(ptr.row(0) == y[:, 0])
    assert all(ptr.column(1) == y[1, :])

    noop = np.transpose(x, axes=(0, 1))
    x2 = da.DelayedArray(noop)
    ptr = initialize(x2)
    assert all(ptr.row(0) == y[0, :])
    assert all(ptr.column(1) == y[:, 1])
