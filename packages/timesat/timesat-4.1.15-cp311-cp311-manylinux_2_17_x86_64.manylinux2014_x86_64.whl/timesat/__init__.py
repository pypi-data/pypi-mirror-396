# timesat/__init__.py
from ._timesat import *   # expose all Fortran functions
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.dev0"
__all__ = [name for name in dir() if not name.startswith("_")]