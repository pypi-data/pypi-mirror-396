#!/usr/bin/env python3
"""
Setup script for MLE Universal Model Exporter
"""

from setuptools import setup, find_packages
import os

# Read README
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mle-exporter',
    version='1.0.0',
    description='Universal ML/DL model exporter to efficient .mle format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='MLE Team',
    author_email='team@mle.ai',
    url='https://github.com/yourusername/mle',
    packages=find_packages(),
    py_modules=[
        'pytorch_to_mle',
        'sklearn_to_mle',
        'tensorflow_to_mle',
        'xgboost_to_mle',
        'universal_exporter',
    ],
    install_requires=[
        'numpy>=1.20.0',
    ],
    extras_require={
        'sklearn': ['scikit-learn>=1.0.0', 'joblib>=1.0.0'],
        'pytorch': ['torch>=1.10.0'],
        'tensorflow': ['tensorflow>=2.8.0'],
        'xgboost': ['xgboost>=1.5.0'],
        'lightgbm': ['lightgbm>=3.3.0'],
        'catboost': ['catboost>=1.0.0'],
        'all': [
            'scikit-learn>=1.0.0',
            'joblib>=1.0.0',
            'torch>=1.10.0',
            'tensorflow>=2.8.0',
            'xgboost>=1.5.0',
            'lightgbm>=3.3.0',
            'catboost>=1.0.0',
        ],
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
    },
    entry_points={
        'console_scripts': [
            'mle-export=universal_exporter:main',
            'mle-export-sklearn=sklearn_to_mle:main',
            'mle-export-pytorch=pytorch_to_mle:main',
            'mle-export-tensorflow=tensorflow_to_mle:main',
            'mle-export-xgboost=xgboost_to_mle:main',
            'mle-test-exporters=test_all_exporters:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    keywords='machine-learning deep-learning model-export pytorch tensorflow scikit-learn xgboost',
    project_urls={
        'Documentation': 'https://github.com/yourusername/mle/blob/main/tools/exporter/README.md',
        'Source': 'https://github.com/yourusername/mle',
        'Bug Reports': 'https://github.com/yourusername/mle/issues',
    },
)
