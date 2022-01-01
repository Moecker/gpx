from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

fibonacci_module = Pybind11Extension(
    "fibonacci",
    [str(fname) for fname in Path("src").glob("*.cpp")],
    include_dirs=["include"],
    extra_compile_args=["-O3"],
)

setup(
    name="fibonacci",
    ext_modules=[fibonacci_module],
    cmdclass={"build_ext": build_ext},
)
