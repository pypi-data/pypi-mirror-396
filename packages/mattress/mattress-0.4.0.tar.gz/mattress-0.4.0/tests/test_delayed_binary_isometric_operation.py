import numpy as np
import delayedarray as da
from mattress import initialize

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def test_delayed_binary_isometric_arith():
    y1 = np.random.rand(1000, 100)
    y2 = np.random.rand(1000, 100)

    x = da.DelayedArray(y1) + da.DelayedArray(y2)
    assert isinstance(x.seed, da.BinaryIsometricOp)
    ptr = initialize(x)
    ref = y1 + y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) - da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 - y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) * da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 * y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) / da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 / y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) % da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 % y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) // da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 // y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) ** da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1**y2
    assert np.allclose(ptr.row(0), ref[0, :])
    assert np.allclose(ptr.column(1), ref[:, 1])


def test_delayed_binary_isometric_compare():
    y1 = np.random.rand(1000, 100)
    y2 = np.random.rand(1000, 100)

    x = da.DelayedArray(y1) == da.DelayedArray(y2)
    assert isinstance(x.seed, da.BinaryIsometricOp)
    ptr = initialize(x)
    ref = y1 == y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) != da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 != y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) > da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 > y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) >= da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 >= y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) < da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 < y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = da.DelayedArray(y1) <= da.DelayedArray(y2)
    ptr = initialize(x)
    ref = y1 <= y2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()


def test_delayed_binary_isometric_logical():
    y1 = np.random.rand(1000, 100)
    y2 = np.random.rand(1000, 100)

    x = np.logical_or(da.DelayedArray(y1), da.DelayedArray(y2))
    assert isinstance(x.seed, da.BinaryIsometricOp)
    ptr = initialize(x)
    ref = np.logical_or(y1, y2)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_and(da.DelayedArray(y1), da.DelayedArray(y2))
    ptr = initialize(x)
    ref = np.logical_and(y1, y2)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_xor(da.DelayedArray(y1), da.DelayedArray(y2))
    ptr = initialize(x)
    ref = np.logical_xor(y1, y2)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()
