"""
Universal Model Exporter - Automatically detects and exports any model type
"""

import numpy as np
from typing import Any, Dict, Tuple, Optional, Union
from pathlib import Path

class UniversalExporter:
    """Universal exporter that automatically detects model type and exports appropriately"""
    
    def __init__(self):
        self.supported_frameworks = {
            'sklearn': self._detect_sklearn,
            'pytorch': self._detect_pytorch,
            'tensorflow': self._detect_tensorflow,
            'xgboost': self._detect_xgboost,
            'lightgbm': self._detect_lightgbm,
            'catboost': self._detect_catboost
        }
    
    def export(self, model: Any, output_path: Union[str, Path], 
               input_shape: Optional[Tuple] = None, **kwargs) -> Dict[str, Any]:
        """
        Automatically detect model type and export to MLE format
        
        Args:
            model: Trained model from any supported framework
            output_path: Path to save .mle file
            input_shape: Input shape tuple (required for some models)
            **kwargs: Additional export options
            
        Returns:
            dict: Export information and statistics
        """
        # Detect framework
        framework = self._detect_framework(model)
        
        if framework == 'sklearn':
            from .sklearn_exporter import export_sklearn_model
            return export_sklearn_model(model, output_path, input_shape, **kwargs)
        elif framework == 'pytorch':
            from .pytorch_exporter import export_pytorch_model
            return export_pytorch_model(model, output_path, input_shape, **kwargs)
        elif framework == 'tensorflow':
            from .tensorflow_exporter import export_tensorflow_model
            return export_tensorflow_model(model, output_path, input_shape, **kwargs)
        elif framework == 'xgboost':
            from .xgboost_exporter import export_xgboost_model
            return export_xgboost_model(model, output_path, input_shape, **kwargs)
        elif framework == 'lightgbm':
            from .xgboost_exporter import export_lightgbm_model
            return export_lightgbm_model(model, output_path, input_shape, **kwargs)
        elif framework == 'catboost':
            from .xgboost_exporter import export_catboost_model
            return export_catboost_model(model, output_path, input_shape, **kwargs)
        else:
            raise ValueError(f"Unsupported model type: {type(model)}. "
                           f"Supported frameworks: {list(self.supported_frameworks.keys())}")
    
    def _detect_framework(self, model: Any) -> str:
        """Detect which framework the model comes from"""
        for framework, detector in self.supported_frameworks.items():
            if detector(model):
                return framework
        return 'unknown'
    
    def _detect_sklearn(self, model: Any) -> bool:
        """Detect if model is from scikit-learn"""
        try:
            import sklearn.base
            return isinstance(model, sklearn.base.BaseEstimator)
        except ImportError:
            return False
    
    def _detect_pytorch(self, model: Any) -> bool:
        """Detect if model is from PyTorch"""
        try:
            import torch.nn
            return isinstance(model, torch.nn.Module)
        except ImportError:
            return False
    
    def _detect_tensorflow(self, model: Any) -> bool:
        """Detect if model is from TensorFlow/Keras"""
        try:
            import tensorflow as tf
            return isinstance(model, (tf.keras.Model, tf.keras.Sequential))
        except ImportError:
            return False
    
    def _detect_xgboost(self, model: Any) -> bool:
        """Detect if model is from XGBoost"""
        try:
            import xgboost as xgb
            return isinstance(model, (xgb.XGBClassifier, xgb.XGBRegressor, xgb.Booster))
        except ImportError:
            return False
    
    def _detect_lightgbm(self, model: Any) -> bool:
        """Detect if model is from LightGBM"""
        try:
            import lightgbm as lgb
            return isinstance(model, (lgb.LGBMClassifier, lgb.LGBMRegressor, lgb.Booster))
        except ImportError:
            return False
    
    def _detect_catboost(self, model: Any) -> bool:
        """Detect if model is from CatBoost"""
        try:
            import catboost as cb
            return isinstance(model, (cb.CatBoostClassifier, cb.CatBoostRegressor))
        except ImportError:
            return False