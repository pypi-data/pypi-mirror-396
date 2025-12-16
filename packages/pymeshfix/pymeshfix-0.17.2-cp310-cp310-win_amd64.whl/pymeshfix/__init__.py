"""PyMeshFix module."""


# start delvewheel patch
def _delvewheel_patch_1_11_2():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'pymeshfix.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_2()
del _delvewheel_patch_1_11_2
# end delvewheel patch

from pymeshfix import _meshfix  # noqa: F401
from pymeshfix._meshfix import PyTMesh, clean_from_arrays, clean_from_file  # noqa: F401
from pymeshfix._version import __version__  # noqa: F401
from pymeshfix.meshfix import MeshFix  # noqa: F401
