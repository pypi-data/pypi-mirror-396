#!/usr/bin/env python3
"""
MLE Runtime - High-Performance Machine Learning Inference Engine
Setup script for PyPI distribution
"""

from setuptools import setup, find_packages
from pathlib import Path
import re

# Read version from __init__.py
def get_version():
    init_file = Path(__file__).parent / "mle_runtime" / "__init__.py"
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
        version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', content, re.M)
        if version_match:
            return version_match.group(1)
    raise RuntimeError("Unable to find version string")

# Read long description from README
def get_long_description():
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "High-performance machine learning inference engine"

# Read requirements
def get_requirements():
    req_file = Path(__file__).parent / "requirements.txt"
    if req_file.exists():
        with open(req_file, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return ['numpy>=1.19.0']

setup(
    name="mle-runtime",
    version=get_version(),
    author="MLE Runtime Team",
    author_email="contact@mle-runtime.org",
    description="High-performance machine learning inference engine that outperforms joblib by 10-100x",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/mle-runtime/mle-runtime",
    project_urls={
        "Bug Tracker": "https://github.com/mle-runtime/mle-runtime/issues",
        "Documentation": "https://mle-runtime.readthedocs.io/",
        "Source Code": "https://github.com/mle-runtime/mle-runtime",
    },
    packages=find_packages(exclude=["tests*", "examples*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: C++",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Archiving :: Compression",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "sklearn": ["scikit-learn>=1.0.0"],
        "pytorch": ["torch>=1.9.0"],
        "tensorflow": ["tensorflow>=2.6.0"],
        "xgboost": ["xgboost>=1.5.0"],
        "lightgbm": ["lightgbm>=3.2.0"],
        "catboost": ["catboost>=1.0.0"],
        "all": [
            "scikit-learn>=1.0.0",
            "torch>=1.9.0", 
            "tensorflow>=2.6.0",
            "xgboost>=1.5.0",
            "lightgbm>=3.2.0",
            "catboost>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mle-runtime=mle_runtime.cli:main",
            "mle-export=mle_runtime.exporters.cli:export_main",
            "mle-inspect=mle_runtime.cli:inspect_main",
            "mle-benchmark=mle_runtime.cli:benchmark_main",
        ],
    },
    include_package_data=True,
    package_data={
        "mle_runtime": ["*.so", "*.dll", "*.dylib"],  # Include compiled extensions
    },
    zip_safe=False,  # Required for C extensions
    keywords=[
        "machine learning", "inference", "runtime", "performance", 
        "joblib", "scikit-learn", "pytorch", "tensorflow", "compression",
        "serialization", "model deployment", "edge computing"
    ],
)