from setuptools import setup, Extension
from pybind11.setup_helpers import Pybind11Extension, build_ext
import sys
import os

# Determine if CUDA is available
enable_cuda = os.environ.get('ENABLE_CUDA', '0') == '1'

extra_compile_args = []
extra_link_args = []
libraries = []
library_dirs = []
include_dirs = ['../../cpp_core/include']

if sys.platform == 'win32':
    extra_compile_args = ['/O2', '/std:c++17']
else:
    extra_compile_args = ['-O3', '-std=c++17']

if enable_cuda:
    extra_compile_args.append('-DENABLE_CUDA')
    libraries.extend(['cudart', 'cublas'])
    
    # Add CUDA paths
    cuda_home = os.environ.get('CUDA_HOME', '/usr/local/cuda')
    include_dirs.append(os.path.join(cuda_home, 'include'))
    library_dirs.append(os.path.join(cuda_home, 'lib64'))

ext_modules = [
    Pybind11Extension(
        'mle_runtime',
        sources=[
            'src/bindings.cpp',
            '../../cpp_core/src/loader.cpp',
            '../../cpp_core/src/engine.cpp',
            '../../cpp_core/src/ops_cpu.cpp',
            '../../cpp_core/src/executor.cpp',
        ],
        include_dirs=include_dirs,
        library_dirs=library_dirs,
        libraries=libraries,
        extra_compile_args=extra_compile_args,
        extra_link_args=extra_link_args,
    ),
]

setup(
    name='mle-runtime',
    version='0.1.0',
    author='No-Code ML Team',
    description='Python bindings for MLE runtime',
    ext_modules=ext_modules,
    cmdclass={'build_ext': build_ext},
    install_requires=['numpy'],
    python_requires='>=3.8',
)
