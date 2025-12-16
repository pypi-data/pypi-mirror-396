"""Temporary script to build _coxnet and _coxph_loss extensions."""
import os
import sys
from pathlib import Path

from packaging.version import Version
from setuptools import Extension, setup
from Cython.Build import cythonize

CYTHON_MIN_VERSION = Version("3.0.10")

def _check_cython_version():
    try:
        import Cython
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            f"Please install Cython with a version >= {CYTHON_MIN_VERSION} in order to build masurvival from source."
        )

    if Version(Cython.__version__) < CYTHON_MIN_VERSION:
        raise ValueError(
            f"Please install Cython with a version >= {CYTHON_MIN_VERSION}. "
            f"The current version of Cython is {Cython.__version__}."
        )

def _check_eigen_source():
    eigen_src = Path("masurvival/linear_model/src/eigen/Eigen")
    if not eigen_src.is_dir():
        raise RuntimeError(
            f"{eigen_src.resolve()} directory not found. You might have to run 'git submodule update --init'."
        )

if __name__ == "__main__":
    _check_cython_version()
    _check_eigen_source()
    
    import numpy
    numpy_includes = [numpy.get_include()]
    
    # Build all extensions needed for RandomSurvivalForest
    extensions = [
        Extension(
            name="masurvival.linear_model._coxnet",
            sources=["masurvival/linear_model/_coxnet.pyx"],
            include_dirs=numpy_includes + [
                "masurvival/linear_model/src",
                "masurvival/linear_model/src/eigen"
            ],
            extra_compile_args=["-std=c++17"],
            language="c++",
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        Extension(
            name="masurvival.ensemble._coxph_loss",
            sources=["masurvival/ensemble/_coxph_loss.pyx"],
            include_dirs=numpy_includes,
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        Extension(
            name="masurvival.tree._criterion",
            sources=["masurvival/tree/_criterion.pyx"],
            include_dirs=numpy_includes,
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        Extension(
            name="masurvival.tree._splitter",
            sources=["masurvival/tree/_splitter.pyx"],
            include_dirs=numpy_includes,
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
        Extension(
            name="masurvival.tree._tree",
            sources=["masurvival/tree/_tree.pyx"],
            include_dirs=numpy_includes,
            language="c++",
            define_macros=[("NPY_NO_DEPRECATED_API", "NPY_1_7_API_VERSION")],
        ),
    ]
    
    extensions = cythonize(
        extensions,
        compiler_directives={"language_level": "3"},
        build_dir="build"
    )
    
    setup(
        ext_modules=extensions,
        script_args=["build_ext", "--inplace"]
    )

