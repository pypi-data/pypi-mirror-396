# auto-generated file
__all__ = ['lib', 'ffi']

import os
from pyroscope._native__ffi import ffi

lib = ffi.dlopen(os.path.join(os.path.dirname(__file__), '_native__lib.cpython-311-darwin.so'), 130)
del os
