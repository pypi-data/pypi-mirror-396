# timesat/__init__.py


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'timesat.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

from ._timesat import *   # expose all Fortran functions
try:
    from ._version import __version__
except ImportError:
    __version__ = "0.0.dev0"
__all__ = [name for name in dir() if not name.startswith("_")]
