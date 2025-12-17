# _common.pxi - shared code included by all .pyx modules

import array
import os
import time

cimport cpython.array as array

from libc.stdlib cimport srand, malloc, free
from libc.stdio cimport FILE, fopen, fclose, stdout


def seed(unsigned int seed_value=0):
    """
    Seed the C random number generator used for weight initialization.

    If seed_value is 0 (default), uses current time.
    Call this before creating networks for reproducible results.
    """
    if seed_value == 0:
        seed_value = <unsigned int>time.time()
    srand(seed_value)


cdef bytes _as_bytes_path(object path):
    candidate = path
    if hasattr(candidate, "__fspath__"):
        candidate = os.fspath(candidate)
    if isinstance(candidate, bytes):
        return candidate
    if isinstance(candidate, str):
        return candidate.encode("utf-8")
    raise TypeError("path must be str, bytes, or os.PathLike")
