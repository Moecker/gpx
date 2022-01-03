from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

point_module = Pybind11Extension(
    "point",
    [str(fname) for fname in Path("src").glob("*.cpp")],
    include_dirs=["include"],
    extra_compile_args=["-g"],
    debug=1,
)

setup(
    name="point",
    ext_modules=[point_module],
    cmdclass={"build_ext": build_ext},
)
