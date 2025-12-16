"""
MLE Runtime v2.0 - Python Client Library
Fast ML inference runtime with advanced neural network operators,
compression, security features, and memory-mapped loading
"""

from typing import List, Optional, Dict, Any
import numpy as np
import sys
import os

__version__ = "2.0.0"

# Import native bindings
from .engine import Engine, GraphExecutor, ModelLoader, Device, DType

class ModelMetadata:
    """Model metadata from .mle file"""
    
    def __init__(self, data: Dict[str, Any]):
        self.model_name = data.get("model_name", "")
        self.framework = data.get("framework", "")
        self.version = data.get("version", {})
        self.input_shapes = data.get("input_shapes", [])
        self.output_shapes = data.get("output_shapes", [])
        self.export_timestamp = data.get("export_timestamp")
    
    def __repr__(self):
        return (f"ModelMetadata(name='{self.model_name}', "
                f"framework='{self.framework}', "
                f"version={self.version})")

# Import enhanced runtime features
try:
    from .enhanced_runtime import (
        EnhancedMLERuntime, ModelInspector, 
        load_model, inspect_model,
        __supported_operators__
    )
    _has_enhanced_features = True
except ImportError as e:
    _has_enhanced_features = False
    EnhancedMLERuntime = None
    ModelInspector = None
    load_model = None
    inspect_model = None
    __supported_operators__ = []

# Import all exporters from local modules
try:
    from .pytorch_to_mle import MLEExporter
    from .sklearn_to_mle import SklearnMLEExporter
    from .tensorflow_to_mle import TensorFlowMLEExporter
    from .xgboost_to_mle import GradientBoostingMLEExporter
    from .universal_exporter import export_model
    _has_exporters = True
except ImportError as e:
    _has_exporters = False
    MLEExporter = None
    SklearnMLEExporter = None
    TensorFlowMLEExporter = None
    GradientBoostingMLEExporter = None
    export_model = None

# MLEEngine is just an alias for Engine  
MLEEngine = Engine

class MLEUtils:
    """Utility functions for MLE"""
    
    @staticmethod
    def inspect_model(path: str) -> ModelMetadata:
        """
        Inspect .mle file and return metadata
        
        Args:
            path: Path to .mle file
            
        Returns:
            Model metadata
        """
        import json
        loader = ModelLoader(path)
        metadata_json = loader.get_metadata()
        return ModelMetadata(json.loads(metadata_json))
    
    @staticmethod
    def verify_model(path: str, public_key: str) -> bool:
        """
        Verify model signature
        
        Args:
            path: Path to .mle file
            public_key: ED25519 public key (hex string)
            
        Returns:
            True if signature is valid
        """
        loader = ModelLoader(path)
        # Convert hex string to bytes
        key_bytes = bytes.fromhex(public_key)
        return loader.verify_signature(key_bytes)

__all__ = [
    "Device",
    "DType",
    "Engine",
    "GraphExecutor",
    "ModelLoader",
    "ModelMetadata",
    "MLEEngine",
    "MLEUtils",
]

if _has_enhanced_features:
    __all__.extend([
        "EnhancedMLERuntime",
        "ModelInspector", 
        "load_model",
        "inspect_model",
    ])

if _has_exporters:
    __all__.extend([
        "MLEExporter",
        "SklearnMLEExporter",
        "TensorFlowMLEExporter",
        "GradientBoostingMLEExporter",
        "export_model",
    ])
