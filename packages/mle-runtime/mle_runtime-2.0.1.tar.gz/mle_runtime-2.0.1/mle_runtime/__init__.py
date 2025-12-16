"""
MLE Runtime - High-Performance Machine Learning Inference Engine

A next-generation ML inference runtime that dramatically outperforms traditional 
serialization tools like joblib with:
- 10-100x faster loading via memory-mapped binary format
- 50-90% smaller file sizes with optimized compression
- Zero Python overhead with native C++ execution
- Cross-platform deployment without Python dependencies
- Model versioning & security with built-in signatures

Version: 2.0.1
"""

__version__ = "2.0.1"
__author__ = "Vinay Kamble"
__email__ = "vinaykamble289@gmail.com"
__license__ = "MIT"

# Core imports
from .core import Engine, Device, load_model, inspect_model
from .mle_runtime import (
    MLERuntime, 
    MLEFormat, 
    CompressionUtils, 
    SecurityUtils,
    ModelInspector
)
from .exporters import (
    export_sklearn_model,
    export_pytorch_model, 
    export_tensorflow_model,
    export_xgboost_model,
    export_lightgbm_model,
    export_catboost_model
)

# Convenience functions
def export_model(model, output_path, input_shape=None, **kwargs):
    """
    Universal model exporter - automatically detects model type and exports
    
    Args:
        model: Trained model from any supported framework
        output_path: Path to save .mle file
        input_shape: Input shape tuple (required for some models)
        **kwargs: Additional export options
    
    Returns:
        dict: Export information and statistics
    """
    from .exporters.universal import UniversalExporter
    exporter = UniversalExporter()
    return exporter.export(model, output_path, input_shape, **kwargs)

def benchmark_model(model_path, inputs, num_runs=100):
    """
    Benchmark model performance
    
    Args:
        model_path: Path to .mle model file
        inputs: Input data for benchmarking
        num_runs: Number of benchmark iterations
    
    Returns:
        dict: Performance statistics
    """
    runtime = load_model(model_path)
    return runtime.benchmark(inputs, num_runs)

# Version info
def get_version_info():
    """Get comprehensive version information"""
    from .mle_runtime import get_version_info as _get_version_info
    return _get_version_info()

def get_supported_operators():
    """Get list of supported operators"""
    from .mle_runtime import get_supported_operators as _get_supported_operators
    return _get_supported_operators()

# Export public API
__all__ = [
    # Core classes
    'Engine', 'Device', 'MLERuntime', 'MLEFormat',
    'CompressionUtils', 'SecurityUtils', 'ModelInspector',
    
    # Main functions
    'load_model', 'inspect_model', 'export_model', 'benchmark_model',
    
    # Exporters
    'export_sklearn_model', 'export_pytorch_model', 'export_tensorflow_model',
    'export_xgboost_model', 'export_lightgbm_model', 'export_catboost_model',
    
    # Utilities
    'get_version_info', 'get_supported_operators'
]