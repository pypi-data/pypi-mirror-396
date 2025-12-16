import os
from typing import Union, Tuple, Sequence, List
import inspect
import numpy as np

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def _sanitize_subset(
    subset: Sequence[int], full: int
) -> Tuple[bool, Union[np.ndarray, None]]:
    is_noop = True
    if len(subset) == full:
        for i, x in enumerate(subset):
            if i != x:
                is_noop = False
                break
    else:
        is_noop = False

    if is_noop:
        return True, np.ndarray(0, dtype=np.uint32)

    if not isinstance(subset, np.ndarray):
        subset = np.array(subset, dtype=np.uint32)
    else:
        subset = subset.astype(
            np.uint32, copy=not (subset.flags.c_contiguous or subset.flags.f_contiguous)
        )

    return False, subset


def _contiguify(x: np.ndarray):
    if x.flags["C_CONTIGUOUS"] or x.flags["F_CONTIGUOUS"]:
        return x
    else:
        return x.copy('C')
