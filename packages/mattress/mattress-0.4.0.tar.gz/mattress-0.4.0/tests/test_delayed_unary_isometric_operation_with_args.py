import numpy as np
import delayedarray as da
from mattress import initialize

__author__ = "ltla, jkanche"
__copyright__ = "ltla, jkanche"
__license__ = "MIT"


def test_delayed_unary_isometric_arith_scalar():
    y = np.random.rand(1000, 100)

    # Addition.
    x = da.DelayedArray(y) + 1
    assert isinstance(x.seed, da.UnaryIsometricOpWithArgs)
    ptr = initialize(x)
    ref = y + 1
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = 2 + da.DelayedArray(y)
    ptr = initialize(x)
    ref = y + 2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Subtraction.
    x = da.DelayedArray(y) - 5.5
    ptr = initialize(x)
    ref = y - 5.5
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = 2.3 - da.DelayedArray(y)
    ptr = initialize(x)
    ref = 2.3 - y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Multiplication.
    x = da.DelayedArray(y) * 3.5
    ptr = initialize(x)
    ref = y * 3.5
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = 2.3 * da.DelayedArray(y)
    ptr = initialize(x)
    ref = 2.3 * y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Division.
    x = da.DelayedArray(y) / 2.5
    ptr = initialize(x)
    ref = y / 2.5
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = 2.3 / da.DelayedArray(y)
    ptr = initialize(x)
    ref = 2.3 / y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Modulo.
    x = da.DelayedArray(y) % 0.2
    ptr = initialize(x)
    ref = y % 0.2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = 199 % da.DelayedArray(y)
    ptr = initialize(x)
    ref = 199 % y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Integer division.
    x = da.DelayedArray(y) // 0.1
    ptr = initialize(x)
    ref = y // 0.1
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = 2 // da.DelayedArray(y)
    ptr = initialize(x)
    ref = 2 // y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Power.
    x = da.DelayedArray(y) ** 3.1
    ptr = initialize(x)
    ref = y**3.1
    assert np.allclose(ptr.row(0), ref[0, :])
    assert np.allclose(ptr.column(1), ref[:, 1])

    x = 2 ** da.DelayedArray(y)
    ptr = initialize(x)
    ref = 2**y
    assert np.allclose(ptr.row(0), ref[0, :])
    assert np.allclose(ptr.column(1), ref[:, 1])


def test_delayed_unary_isometric_arith_vector():
    y = np.random.rand(1000, 100)
    v1 = np.random.rand(100)
    v2 = np.random.rand(1000, 1)

    # Addition.
    x = da.DelayedArray(y) + v1
    assert isinstance(x.seed, da.UnaryIsometricOpWithArgs)
    ptr = initialize(x)
    ref = y + v1
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v2 + da.DelayedArray(y)
    ptr = initialize(x)
    ref = y + v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Subtraction.
    x = da.DelayedArray(y) - v2
    ptr = initialize(x)
    ref = y - v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v1 - da.DelayedArray(y)
    ptr = initialize(x)
    ref = v1 - y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Multiplication.
    x = da.DelayedArray(y) * v2
    ptr = initialize(x)
    ref = y * v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v1 * da.DelayedArray(y)
    ptr = initialize(x)
    ref = v1 * y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Division.
    x = da.DelayedArray(y) / v1
    ptr = initialize(x)
    ref = y / v1
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v2 / da.DelayedArray(y)
    ptr = initialize(x)
    ref = v2 / y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Modulo.
    x = da.DelayedArray(y) % v2
    ptr = initialize(x)
    ref = y % v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v1 % da.DelayedArray(y)
    ptr = initialize(x)
    ref = v1 % y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Integer division.
    x = da.DelayedArray(y) // v1
    ptr = initialize(x)
    ref = y // v1
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v2 // da.DelayedArray(y)
    ptr = initialize(x)
    ref = v2 // y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Power.
    x = da.DelayedArray(y) ** v2
    ptr = initialize(x)
    ref = y**v2
    assert np.allclose(ptr.row(0), ref[0, :])
    assert np.allclose(ptr.column(1), ref[:, 1])

    x = v1 ** da.DelayedArray(y)
    ptr = initialize(x)
    ref = v1**y
    assert np.allclose(ptr.row(0), ref[0, :])
    assert np.allclose(ptr.column(1), ref[:, 1])


def test_delayed_unary_isometric_compare_scalar():
    y = np.random.rand(1000, 100)
    first = float(y[0, 0])

    # Equality.
    x = da.DelayedArray(y) == first
    assert isinstance(x.seed, da.UnaryIsometricOpWithArgs)
    ptr = initialize(x)
    ref = y == first
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = first == da.DelayedArray(y)
    ptr = initialize(x)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Non-equality.
    x = da.DelayedArray(y) != first
    ptr = initialize(x)
    ref = y != first
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = first != da.DelayedArray(y)
    ptr = initialize(x)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Greater than.
    x = da.DelayedArray(y) > first
    ptr = initialize(x)
    ref = y > first
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = first > da.DelayedArray(y)
    ptr = initialize(x)
    ref = first > y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Greater than or equal to.
    x = da.DelayedArray(y) >= first
    ptr = initialize(x)
    ref = y >= first
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = first >= da.DelayedArray(y)
    ptr = initialize(x)
    ref = first >= y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Less than.
    x = da.DelayedArray(y) < first
    ptr = initialize(x)
    ref = y < first
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = first < da.DelayedArray(y)
    ptr = initialize(x)
    ref = first < y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Less than or equal to
    x = da.DelayedArray(y) <= first
    ptr = initialize(x)
    ref = y <= first
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = first <= da.DelayedArray(y)
    ptr = initialize(x)
    ref = first <= y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()


def test_delayed_unary_isometric_compare_vector():
    y = np.random.rand(1000, 100)
    v1 = y[:, [0]]
    v2 = y[0, :]

    # Equality.
    x = da.DelayedArray(y) == v1
    assert isinstance(x.seed, da.UnaryIsometricOpWithArgs)
    ptr = initialize(x)
    ref = y == v1
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v2 == da.DelayedArray(y)
    ptr = initialize(x)
    ref = v2 == y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Non-equality.
    x = da.DelayedArray(y) != v2
    ptr = initialize(x)
    ref = y != v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v1 != da.DelayedArray(y)
    ref = v1 != y
    ptr = initialize(x)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Greater than.
    x = da.DelayedArray(y) > v1
    ptr = initialize(x)
    ref = y > v1
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v2 > da.DelayedArray(y)
    ptr = initialize(x)
    ref = v2 > y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Greater than or equal to.
    x = da.DelayedArray(y) >= v2
    ptr = initialize(x)
    ref = y >= v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v1 >= da.DelayedArray(y)
    ptr = initialize(x)
    ref = v1 >= y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Less than.
    x = da.DelayedArray(y) < v2
    ptr = initialize(x)
    ref = y < v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v1 < da.DelayedArray(y)
    ptr = initialize(x)
    ref = v1 < y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # Less than or equal to
    x = da.DelayedArray(y) <= v2
    ptr = initialize(x)
    ref = y <= v2
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = v1 <= da.DelayedArray(y)
    ptr = initialize(x)
    ref = v1 <= y
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()


def test_delayed_unary_isometric_logical_scalar():
    y = np.random.rand(1000, 100)

    # OR.
    x = np.logical_or(da.DelayedArray(y), True)
    assert isinstance(x.seed, da.UnaryIsometricOpWithArgs)
    ptr = initialize(x)
    ref = np.logical_or(y, True)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_or(False, da.DelayedArray(y))
    ptr = initialize(x)
    ref = np.logical_or(False, y)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # AND.
    x = np.logical_and(da.DelayedArray(y), False)
    ptr = initialize(x)
    ref = np.logical_and(y, False)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_and(True, da.DelayedArray(y))
    ptr = initialize(x)
    ref = np.logical_or(True, y)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # XOR.
    x = np.logical_xor(da.DelayedArray(y), True)
    ptr = initialize(x)
    ref = np.logical_xor(y, True)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_xor(False, da.DelayedArray(y))
    ptr = initialize(x)
    ref = np.logical_xor(False, y)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()


def test_delayed_unary_isometric_logical_vector():
    y = np.random.rand(1000, 100)
    v1 = np.random.rand(100) > 0.5
    v2 = np.random.rand(1000, 1) > 0.5

    # OR.
    x = np.logical_or(da.DelayedArray(y), v1)
    assert isinstance(x.seed, da.UnaryIsometricOpWithArgs)
    ptr = initialize(x)
    ref = np.logical_or(y, v1)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_or(v2, da.DelayedArray(y))
    ptr = initialize(x)
    ref = np.logical_or(v2, y)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # AND.
    x = np.logical_and(da.DelayedArray(y), v2)
    ptr = initialize(x)
    ref = np.logical_and(y, v2)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_and(v1, da.DelayedArray(y))
    ptr = initialize(x)
    ref = np.logical_and(v1, y)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    # XOR.
    x = np.logical_xor(da.DelayedArray(y), v1)
    ptr = initialize(x)
    ref = np.logical_xor(y, v1)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()

    x = np.logical_xor(v2, da.DelayedArray(y))
    ptr = initialize(x)
    ref = np.logical_xor(v2, y)
    assert (ptr.row(0) == ref[0, :]).all()
    assert (ptr.column(1) == ref[:, 1]).all()
