import os
from setuptools import setup, find_packages, Extension
from setuptools.command.build_ext import build_ext

# Robustly find the README in the root directory
here = os.path.abspath(os.path.dirname(__file__))
# Point to the PyPI-specific README
local_readme = os.path.join(here, "README_PyPI.md")

try:
    with open(local_readme, encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = "CMFO: Continuous Modal Fractal Oscillation Engine (Experimental)"


# Custom build_ext to make C++ extension optional
class OptionalBuildExt(build_ext):
    """Build extension, but don't fail if C++ compiler is not available"""
    def build_extensions(self):
        try:
            super().build_extensions()
        except Exception as e:
            print(f"WARNING: C++ extension build failed: {e}")
            print("Installing without native acceleration (pure Python mode)")
            # Remove failed extensions
            self.extensions = []


# Try to build C++ extension, but make it optional
ext_modules = []
try:
    ext_modules = [
        Extension(
            "cmfo_core_native",
            sources=["native_src/matrix_engine.cpp"],
            include_dirs=["native_src"],
            language="c++",
            extra_compile_args=["/O2", "/fp:fast", "/openmp", "/std:c++17"] if os.name == 'nt' else ["-O3", "-ffast-math", "-fopenmp", "-std=c++17"],
            extra_link_args=["/OPENMP"] if os.name == 'nt' else ["-fopenmp"],
            optional=True
        )
    ]
except Exception as e:
    print(f"WARNING: Could not configure C++ extension: {e}")
    ext_modules = []

setup(
    name="cmfo-fractal",
    version="0.1.5",
    author="Jonathan Montero Viques",
    author_email="jesuslocopor@gmail.com",
    description="Experimental framework for deterministic fractal computation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "numpy>=1.20",
    ],
    ext_modules=ext_modules,
    cmdclass={'build_ext': OptionalBuildExt},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Physics",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Documentation": "https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-/tree/main/docs",
        "Source": "https://github.com/1JONMONTERV/CMFO-COMPUTACION-FRACTAL-",
    },
    entry_points={
        "console_scripts": [
            "cmfo=cmfo.cli:main",
        ],
    },
)
