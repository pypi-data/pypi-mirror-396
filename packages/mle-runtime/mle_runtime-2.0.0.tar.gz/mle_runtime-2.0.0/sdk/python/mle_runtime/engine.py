"""
MLE Engine wrapper - imports native C++ extension
"""

try:
    # Import from the bundled extension module
    from mle_runtime._mle_core import Engine, GraphExecutor, ModelLoader, Device, DType
except ImportError as e:
    raise ImportError(
        "Failed to import MLE native bindings. "
        "Make sure the package was installed correctly with: pip install mle-runtime\n"
        f"Original error: {e}"
    )

__all__ = ['Engine', 'GraphExecutor', 'ModelLoader', 'Device', 'DType']
