from pathlib import Path

from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

example_module = Pybind11Extension(
    'pybind_11_example',
    [str(fname) for fname in Path('src').glob('*.cpp')],
    include_dirs=['include'],
    extra_compile_args=['-O3']
)

setup(
    name='pybind_11_example',
    version=0.1,
    author='Joe Bloggs',
    author_email='joe_bloggs@email.com',
    description='Barebones pybind11+setup.py example project',
    ext_modules=[example_module],
    cmdclass={"build_ext": build_ext},
)
