import numpy as np
import delayedarray as da
from mattress import initialize

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def test_delayed_bind():
    y1 = np.random.rand(1000, 100)
    y2 = np.random.rand(1000, 50)

    com = np.concatenate((da.DelayedArray(y1), da.DelayedArray(y2)), axis=1)
    ref = np.concatenate((y1, y2), axis=1)
    assert isinstance(com.seed, da.Combine)
    ptr = initialize(com)
    assert all(ptr.row(0) == ref[0, :])
    assert all(ptr.column(1) == ref[:, 1])

    y1 = np.random.rand(1000, 10)
    y2 = np.random.rand(500, 10)
    y3 = np.random.rand(200, 10)

    com = np.concatenate(
        (da.DelayedArray(y1), da.DelayedArray(y2), da.DelayedArray(y3))
    )
    ref = np.concatenate((y1, y2, y3))
    assert isinstance(com.seed, da.Combine)
    ptr = initialize(com)
    assert all(ptr.row(0) == ref[0, :])
    assert all(ptr.column(1) == ref[:, 1])
