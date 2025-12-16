"""
MLE Runtime Core - Main inference engine interface
"""

from enum import Enum
from typing import List, Union, Optional
from pathlib import Path
import numpy as np

class Device(Enum):
    """Supported compute devices"""
    CPU = "cpu"
    CUDA = "cuda"
    AUTO = "auto"

class Engine:
    """Main MLE inference engine"""
    
    def __init__(self, device: Device = Device.CPU):
        self.device = device
        self._model_loaded = False
        
    def load_model(self, path: Union[str, Path]) -> None:
        """Load MLE model file"""
        # This would interface with the C++ core
        self._model_loaded = True
        
    def run(self, inputs: List[np.ndarray]) -> List[np.ndarray]:
        """Run inference"""
        if not self._model_loaded:
            raise RuntimeError("No model loaded")
        # This would call the C++ inference engine
        return inputs  # Placeholder

def load_model(path: Union[str, Path], device: str = "cpu") -> 'MLERuntime':
    """Load MLE model with enhanced features"""
    from .mle_runtime import MLERuntime
    runtime = MLERuntime(device=device)
    runtime.load_model(path)
    return runtime

def inspect_model(path: Union[str, Path]) -> dict:
    """Inspect MLE model and return information"""
    from .mle_runtime import ModelInspector
    return ModelInspector.analyze_model(path)