#!/usr/bin/env python3
"""
XGBoost/LightGBM/CatBoost to .mle exporter
Converts gradient boosting models to custom .mle format
"""

import struct
import json
import numpy as np
from pathlib import Path
from typing import Any, Dict, List
import time
import os

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False
    print("Warning: XGBoost not installed")

try:
    import lightgbm as lgb
    HAS_LGB = True
except ImportError:
    HAS_LGB = False
    print("Warning: LightGBM not installed")

try:
    import catboost as cb
    HAS_CB = True
except ImportError:
    HAS_CB = False
    print("Warning: CatBoost not installed")

# Import MLE exporter base
import sys
sys.path.insert(0, os.path.dirname(__file__))
from pytorch_to_mle import MLEExporter, MLE_MAGIC, MLE_VERSION


class GradientBoostingMLEExporter(MLEExporter):
    """Export gradient boosting models to .mle format"""
    
    def __init__(self):
        super().__init__()
        self.model_type = None
        
    def export_xgboost(self, model: Any, output_path: str, 
                      input_shape: tuple = None, model_name: str = None):
        """
        Export XGBoost model to .mle format
        
        Args:
            model: XGBoost model (Booster or XGBClassifier/XGBRegressor)
            output_path: Output .mle file path
            input_shape: Input shape (batch_size, features)
            model_name: Optional model name
        """
        
        if not HAS_XGB:
            raise ImportError("XGBoost not installed")
        
        start_time = time.perf_counter()
        
        self.model_type = type(model).__name__
        
        # Get booster
        if hasattr(model, 'get_booster'):
            booster = model.get_booster()
        else:
            booster = model
        
        # Get model dump
        trees = booster.get_dump(dump_format='json')
        
        # Infer input shape
        if input_shape is None:
            # Try to get from model
            if hasattr(model, 'n_features_in_'):
                input_shape = (1, model.n_features_in_)
            else:
                raise ValueError("Cannot infer input shape, please provide input_shape")
        
        # Export trees
        self._export_xgb_trees(trees, input_shape)
        
        # Build metadata
        metadata = self._build_metadata_xgb(model, booster, input_shape, model_name)
        metadata_json = json.dumps(metadata, indent=2).encode('utf-8')
        
        # Build graph IR
        graph_ir = self._build_graph_ir([0], [self.tensor_id_counter - 1])
        
        # Write .mle file
        self._write_mle(output_path, metadata_json, graph_ir)
        
        export_time = (time.perf_counter() - start_time) * 1000
        mle_size = os.path.getsize(output_path)
        
        print(f"\n{'='*60}")
        print(f"Export Complete: {output_path}")
        print(f"{'='*60}")
        print(f"Model type: {self.model_type}")
        print(f"Trees: {len(trees)}")
        print(f"Tensors: {len(self.tensors)}")
        print(f"Export time: {export_time:.2f} ms")
        print(f"File size: {mle_size / 1024:.2f} KB")
        print(f"{'='*60}\n")
        
        return output_path
    
    def export_lightgbm(self, model: Any, output_path: str, 
                       input_shape: tuple = None, model_name: str = None):
        """
        Export LightGBM model to .mle format
        """
        
        if not HAS_LGB:
            raise ImportError("LightGBM not installed")
        
        start_time = time.perf_counter()
        
        self.model_type = type(model).__name__
        
        # Get model dump
        model_dict = model.dump_model()
        trees = model_dict['tree_info']
        
        # Infer input shape
        if input_shape is None:
            if hasattr(model, 'n_features_'):
                input_shape = (1, model.n_features_)
            else:
                raise ValueError("Cannot infer input shape, please provide input_shape")
        
        # Export trees
        self._export_lgb_trees(trees, input_shape)
        
        # Build metadata
        metadata = self._build_metadata_lgb(model, model_dict, input_shape, model_name)
        metadata_json = json.dumps(metadata, indent=2).encode('utf-8')
        
        # Build graph IR
        graph_ir = self._build_graph_ir([0], [self.tensor_id_counter - 1])
        
        # Write .mle file
        self._write_mle(output_path, metadata_json, graph_ir)
        
        export_time = (time.perf_counter() - start_time) * 1000
        mle_size = os.path.getsize(output_path)
        
        print(f"\n{'='*60}")
        print(f"Export Complete: {output_path}")
        print(f"{'='*60}")
        print(f"Model type: {self.model_type}")
        print(f"Trees: {len(trees)}")
        print(f"Export time: {export_time:.2f} ms")
        print(f"File size: {mle_size / 1024:.2f} KB")
        print(f"{'='*60}\n")
        
        return output_path
    
    def export_catboost(self, model: Any, output_path: str, 
                       input_shape: tuple = None, model_name: str = None):
        """
        Export CatBoost model to .mle format
        """
        
        if not HAS_CB:
            raise ImportError("CatBoost not installed")
        
        start_time = time.perf_counter()
        
        self.model_type = type(model).__name__
        
        # Get model info
        tree_count = model.tree_count_
        
        # Infer input shape
        if input_shape is None:
            if hasattr(model, 'feature_names_'):
                input_shape = (1, len(model.feature_names_))
            else:
                raise ValueError("Cannot infer input shape, please provide input_shape")
        
        # Export model structure
        self._export_catboost_model(model, input_shape)
        
        # Build metadata
        metadata = self._build_metadata_catboost(model, input_shape, model_name)
        metadata_json = json.dumps(metadata, indent=2).encode('utf-8')
        
        # Build graph IR
        graph_ir = self._build_graph_ir([0], [self.tensor_id_counter - 1])
        
        # Write .mle file
        self._write_mle(output_path, metadata_json, graph_ir)
        
        export_time = (time.perf_counter() - start_time) * 1000
        mle_size = os.path.getsize(output_path)
        
        print(f"\n{'='*60}")
        print(f"Export Complete: {output_path}")
        print(f"{'='*60}")
        print(f"Model type: {self.model_type}")
        print(f"Trees: {tree_count}")
        print(f"Export time: {export_time:.2f} ms")
        print(f"File size: {mle_size / 1024:.2f} KB")
        print(f"{'='*60}\n")
        
        return output_path
    
    def _export_xgb_trees(self, trees, input_shape):
        """Export XGBoost trees"""
        import torch
        import json as json_lib
        
        # Create input tensor
        dummy_input = np.zeros(input_shape, dtype=np.float32)
        input_id = self.add_tensor(torch.from_numpy(dummy_input), "input", is_placeholder=True)
        
        # Serialize all trees
        tree_data = []
        for i, tree_json in enumerate(trees):
            tree_dict = json_lib.loads(tree_json)
            tree_data.append(tree_dict)
        
        # Store tree structure as JSON string in a tensor
        tree_json_str = json_lib.dumps(tree_data)
        tree_bytes = tree_json_str.encode('utf-8')
        tree_array = np.frombuffer(tree_bytes, dtype=np.uint8)
        tree_id = self.add_tensor(torch.from_numpy(tree_array), "trees")
        
        # Output tensor
        output_shape = (input_shape[0], 1)
        output_tensor = torch.zeros(output_shape)
        output_id = self.add_tensor(output_tensor, "output", is_placeholder=True)
        
        self.add_node('XGBoost',
                     inputs=[input_id],
                     outputs=[output_id],
                     params=[tree_id])
    
    def _export_lgb_trees(self, trees, input_shape):
        """Export LightGBM trees"""
        import torch
        import json as json_lib
        
        # Create input tensor
        dummy_input = np.zeros(input_shape, dtype=np.float32)
        input_id = self.add_tensor(torch.from_numpy(dummy_input), "input", is_placeholder=True)
        
        # Store tree structure as JSON
        tree_json_str = json_lib.dumps(trees)
        tree_bytes = tree_json_str.encode('utf-8')
        tree_array = np.frombuffer(tree_bytes, dtype=np.uint8)
        tree_id = self.add_tensor(torch.from_numpy(tree_array), "trees")
        
        # Output tensor
        output_shape = (input_shape[0], 1)
        output_tensor = torch.zeros(output_shape)
        output_id = self.add_tensor(output_tensor, "output", is_placeholder=True)
        
        self.add_node('LightGBM',
                     inputs=[input_id],
                     outputs=[output_id],
                     params=[tree_id])
    
    def _export_catboost_model(self, model, input_shape):
        """Export CatBoost model"""
        import torch
        
        # Create input tensor
        dummy_input = np.zeros(input_shape, dtype=np.float32)
        input_id = self.add_tensor(torch.from_numpy(dummy_input), "input", is_placeholder=True)
        
        # Save model to temp file and read as bytes
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.cbm', delete=False) as tmp:
            model.save_model(tmp.name)
            with open(tmp.name, 'rb') as f:
                model_bytes = f.read()
            os.unlink(tmp.name)
        
        # Store model bytes
        model_array = np.frombuffer(model_bytes, dtype=np.uint8)
        model_id = self.add_tensor(torch.from_numpy(model_array), "model")
        
        # Output tensor
        output_shape = (input_shape[0], 1)
        output_tensor = torch.zeros(output_shape)
        output_id = self.add_tensor(output_tensor, "output", is_placeholder=True)
        
        self.add_node('CatBoost',
                     inputs=[input_id],
                     outputs=[output_id],
                     params=[model_id])
    
    def _build_metadata_xgb(self, model, booster, input_shape, model_name):
        """Build metadata for XGBoost"""
        config = booster.save_config()
        
        metadata = {
            'model_name': model_name or self.model_type,
            'framework': 'xgboost',
            'framework_version': xgb.__version__,
            'model_type': self.model_type,
            'input_shapes': [list(input_shape)],
            'export_timestamp': int(time.time()),
            'export_tool': 'xgboost_to_mle',
            'export_tool_version': '1.0.0',
            
            'model_params': {
                'num_trees': booster.num_boosted_rounds(),
            },
            
            'version': {
                'major': 1,
                'minor': 0,
                'patch': 0
            }
        }
        
        return metadata
    
    def _build_metadata_lgb(self, model, model_dict, input_shape, model_name):
        """Build metadata for LightGBM"""
        metadata = {
            'model_name': model_name or self.model_type,
            'framework': 'lightgbm',
            'framework_version': lgb.__version__,
            'model_type': self.model_type,
            'input_shapes': [list(input_shape)],
            'export_timestamp': int(time.time()),
            'export_tool': 'lightgbm_to_mle',
            'export_tool_version': '1.0.0',
            
            'model_params': {
                'num_trees': len(model_dict['tree_info']),
            },
            
            'version': {
                'major': 1,
                'minor': 0,
                'patch': 0
            }
        }
        
        return metadata
    
    def _build_metadata_catboost(self, model, input_shape, model_name):
        """Build metadata for CatBoost"""
        metadata = {
            'model_name': model_name or self.model_type,
            'framework': 'catboost',
            'framework_version': cb.__version__,
            'model_type': self.model_type,
            'input_shapes': [list(input_shape)],
            'export_timestamp': int(time.time()),
            'export_tool': 'catboost_to_mle',
            'export_tool_version': '1.0.0',
            
            'model_params': {
                'num_trees': model.tree_count_,
            },
            
            'version': {
                'major': 1,
                'minor': 0,
                'patch': 0
            }
        }
        
        return metadata


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Export XGBoost/LightGBM/CatBoost model to .mle'
    )
    parser.add_argument('--framework', type=str, choices=['xgboost', 'lightgbm', 'catboost'],
                       required=True, help='Framework type')
    parser.add_argument('--model', type=str, help='Path to saved model')
    parser.add_argument('--out', type=str, required=True, help='Output .mle path')
    parser.add_argument('--input-shape', type=str, help='Input shape (comma-separated)')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    exporter = GradientBoostingMLEExporter()
    
    if args.demo or not args.model:
        print(f"Running {args.framework} demo\n")
        
        # Create demo data
        from sklearn.datasets import make_classification
        X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
        
        if args.framework == 'xgboost':
            model = xgb.XGBClassifier(n_estimators=100, max_depth=3)
            model.fit(X, y)
            exporter.export_xgboost(model, args.out, input_shape=(1, 20))
        
        elif args.framework == 'lightgbm':
            model = lgb.LGBMClassifier(n_estimators=100, max_depth=3)
            model.fit(X, y)
            exporter.export_lightgbm(model, args.out, input_shape=(1, 20))
        
        elif args.framework == 'catboost':
            model = cb.CatBoostClassifier(iterations=100, depth=3, verbose=0)
            model.fit(X, y)
            exporter.export_catboost(model, args.out, input_shape=(1, 20))
    
    else:
        input_shape = None
        if args.input_shape:
            input_shape = tuple(map(int, args.input_shape.split(',')))
        
        if args.framework == 'xgboost':
            model = xgb.Booster()
            model.load_model(args.model)
            exporter.export_xgboost(model, args.out, input_shape)
        
        elif args.framework == 'lightgbm':
            model = lgb.Booster(model_file=args.model)
            exporter.export_lightgbm(model, args.out, input_shape)
        
        elif args.framework == 'catboost':
            model = cb.CatBoost()
            model.load_model(args.model)
            exporter.export_catboost(model, args.out, input_shape)


if __name__ == '__main__':
    main()
