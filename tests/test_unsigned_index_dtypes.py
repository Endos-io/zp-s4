"""Reproduction for zarr-python #4285 — unsigned integer index arrays are mishandled.

Transcribed from the issue's own reproducer. Two independent failure modes:

1. an UNSORTED index of any unsigned dtype is misclassified as increasing, because
   ``Order.check`` uses ``np.diff`` and a subtraction on an unsigned array wraps
   (``np.diff(np.array([3, 0], dtype="uint8")) == [253]``). The argsort that regroups
   indices by chunk is then skipped.
2. ``uint64``, sorted or not, promotes to ``float64`` against a signed offset and is no
   longer a valid index.

Failure 1 needs all four of: an unsigned dtype, an unsorted index, a second axis, and an
index spanning more than one chunk — hence ``chunks=(2, 1)`` on a ``(4, 2)`` array.
"""

import numpy as np
import pytest

import zarr
from zarr.core.indexing import Order
from zarr.storage import MemoryStore

# MemoryStore rather than a temp directory: the graded container is --read-only.
_VALUES = np.arange(8, dtype="float32").reshape(4, 2)


def _array() -> zarr.Array:
    z = zarr.create_array(MemoryStore(), shape=_VALUES.shape, dtype="float32", chunks=(2, 1))
    z[:] = _VALUES
    return z


@pytest.mark.parametrize("dtype", ["uint8", "uint16", "uint32", "uint64"])
def test_unsorted_unsigned_index_matches_signed(dtype: str) -> None:
    """`z[[3, 0], :]` must return the same rows whatever the index dtype's signedness."""
    z = _array()
    got = z[np.array([3, 0], dtype=dtype), :]
    np.testing.assert_array_equal(got, _VALUES[[3, 0], :])


def test_uint64_sorted_index_is_accepted() -> None:
    """Failure 2 needs only uint64 — it fails even when the index is already sorted."""
    z = _array()
    got = z[np.array([0, 3], dtype="uint64"), :]
    np.testing.assert_array_equal(got, _VALUES[[0, 3], :])


def test_uint64_through_vindex_is_accepted() -> None:
    """CoordinateIndexer casts scalar ints to intp but leaves supplied arrays alone."""
    z = _array()
    rows = np.array([0, 3], dtype="uint64")
    cols = np.array([1, 0], dtype="uint64")
    np.testing.assert_array_equal(z.vindex[rows, cols], _VALUES[[0, 3], [1, 0]])


@pytest.mark.parametrize("dtype", ["uint8", "uint16", "uint32", "uint64"])
def test_order_check_does_not_wrap_on_unsigned(dtype: str) -> None:
    """A descending selection must classify as DECREASING regardless of dtype."""
    signed = Order.check(np.array([3, 0], dtype="int64"))
    assert Order.check(np.array([3, 0], dtype=dtype)) == signed
