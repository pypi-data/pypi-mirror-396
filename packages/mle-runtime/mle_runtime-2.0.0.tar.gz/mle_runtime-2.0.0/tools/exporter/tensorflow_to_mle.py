#!/usr/bin/env python3
"""
TensorFlow/Keras to .mle exporter
Converts TensorFlow and Keras models to custom .mle format
"""

import struct
import json
import numpy as np
from pathlib import Path
from typing import Any, Dict, List
import time
import os

try:
    import tensorflow as tf
    from tensorflow import keras
    HAS_TF = True
except ImportError:
    HAS_TF = False
    print("Warning: TensorFlow not installed")

# Import MLE exporter base
import sys
sys.path.insert(0, os.path.dirname(__file__))
from pytorch_to_mle import MLEExporter, MLE_MAGIC, MLE_VERSION, DTYPE_MAP, OP_TYPE_MAP


class TensorFlowMLEExporter(MLEExporter):
    """Export TensorFlow/Keras models to .mle format"""
    
    def __init__(self):
        super().__init__()
        self.model_type = None
        
    def export_keras(self, model: Any, output_path: str, 
                    input_shape: tuple = None, model_name: str = None):
        """
        Export Keras model to .mle format
        
        Args:
            model: Keras model
            output_path: Output .mle file path
            input_shape: Input shape (batch_size, features)
            model_name: Optional model name
        """
        
        if not HAS_TF:
            raise ImportError("TensorFlow not installed")
        
        start_time = time.perf_counter()
        
        self.model_type = model.__class__.__name__
        
        # Get input shape from model if not provided
        if input_shape is None:
            input_shape = tuple(model.input_shape)
            if input_shape[0] is None:
                input_shape = (1,) + input_shape[1:]
        
        # Create dummy input
        dummy_input = np.zeros(input_shape, dtype=np.float32)
        
        # Export layers
        self._export_keras_model(model, dummy_input)
        
        # Build metadata
        metadata = self._build_metadata(model, input_shape, model_name)
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
        print(f"Tensors: {len(self.tensors)}")
        print(f"Nodes: {len(self.nodes)}")
        print(f"Export time: {export_time:.2f} ms")
        print(f"File size: {mle_size / 1024:.2f} KB")
        print(f"{'='*60}\n")
        
        return output_path
    
    def _export_keras_model(self, model, dummy_input):
        """Export Keras model layers"""
        import torch
        
        # Add input tensor
        input_tensor = torch.from_numpy(dummy_input)
        current_id = self.add_tensor(input_tensor, "input", is_placeholder=True)
        
        # Process each layer
        for i, layer in enumerate(model.layers):
            layer_name = f"layer{i}_{layer.name}"
            
            if isinstance(layer, keras.layers.Dense):
                # Get weights and bias
                weights = layer.get_weights()
                if len(weights) == 2:
                    weight, bias = weights
                    # TensorFlow Dense: [in_features, out_features]
                    # We need: [out_features, in_features]
                    weight_id = self.add_tensor(
                        torch.from_numpy(weight.T.astype(np.float32)),
                        f"{layer_name}.weight"
                    )
                    bias_id = self.add_tensor(
                        torch.from_numpy(bias.astype(np.float32)),
                        f"{layer_name}.bias"
                    )
                    
                    # Output tensor
                    output_shape = (dummy_input.shape[0], layer.units)
                    output_tensor = torch.zeros(output_shape)
                    output_id = self.add_tensor(output_tensor, f"{layer_name}.output", is_placeholder=True)
                    
                    self.add_node('Linear',
                                 inputs=[current_id],
                                 outputs=[output_id],
                                 params=[weight_id, bias_id])
                    
                    current_id = output_id
            
            elif isinstance(layer, keras.layers.Activation):
                activation = layer.activation.__name__
                prev_shape = self.tensors[current_id]['shape']
                output_tensor = torch.zeros([s for s in prev_shape if s > 0])
                output_id = self.add_tensor(output_tensor, f"{layer_name}.output", is_placeholder=True)
                
                if activation == 'relu':
                    self.add_node('ReLU',
                                 inputs=[current_id],
                                 outputs=[output_id],
                                 params=[])
                elif activation in ['gelu', 'swish']:
                    self.add_node('GELU',
                                 inputs=[current_id],
                                 outputs=[output_id],
                                 params=[])
                elif activation == 'softmax':
                    self.add_node('Softmax',
                                 inputs=[current_id],
                                 outputs=[output_id],
                                 params=[])
                
                current_id = output_id
            
            elif isinstance(layer, (keras.layers.ReLU, keras.layers.LeakyReLU)):
                prev_shape = self.tensors[current_id]['shape']
                output_tensor = torch.zeros([s for s in prev_shape if s > 0])
                output_id = self.add_tensor(output_tensor, f"{layer_name}.output", is_placeholder=True)
                
                self.add_node('ReLU',
                             inputs=[current_id],
                             outputs=[output_id],
                             params=[])
                
                current_id = output_id
            
            elif isinstance(layer, keras.layers.Softmax):
                prev_shape = self.tensors[current_id]['shape']
                output_tensor = torch.zeros([s for s in prev_shape if s > 0])
                output_id = self.add_tensor(output_tensor, f"{layer_name}.output", is_placeholder=True)
                
                self.add_node('Softmax',
                             inputs=[current_id],
                             outputs=[output_id],
                             params=[])
                
                current_id = output_id
            
            elif isinstance(layer, keras.layers.LayerNormalization):
                weights = layer.get_weights()
                if len(weights) == 2:
                    gamma, beta = weights
                    gamma_id = self.add_tensor(
                        torch.from_numpy(gamma.astype(np.float32)),
                        f"{layer_name}.gamma"
                    )
                    beta_id = self.add_tensor(
                        torch.from_numpy(beta.astype(np.float32)),
                        f"{layer_name}.beta"
                    )
                    
                    prev_shape = self.tensors[current_id]['shape']
                    output_tensor = torch.zeros([s for s in prev_shape if s > 0])
                    output_id = self.add_tensor(output_tensor, f"{layer_name}.output", is_placeholder=True)
                    
                    self.add_node('LayerNorm',
                                 inputs=[current_id],
                                 outputs=[output_id],
                                 params=[gamma_id, beta_id])
                    
                    current_id = output_id
            
            elif isinstance(layer, keras.layers.Dropout):
                # Skip dropout during inference
                pass
            
            elif isinstance(layer, keras.layers.Flatten):
                # Flatten is implicit in our format
                pass
    
    def _build_metadata(self, model, input_shape, model_name):
        """Build metadata for Keras model"""
        metadata = {
            'model_name': model_name or self.model_type,
            'framework': 'tensorflow',
            'framework_version': tf.__version__,
            'model_type': self.model_type,
            'input_shapes': [list(input_shape)],
            'export_timestamp': int(time.time()),
            'export_tool': 'tensorflow_to_mle',
            'export_tool_version': '1.0.0',
            
            'model_params': {
                'num_layers': len(model.layers),
                'trainable_params': model.count_params(),
            },
            
            'version': {
                'major': 1,
                'minor': 0,
                'patch': 0
            },
            
            'performance': {
                'recommended_device': 'cpu',
                'memory_footprint_mb': len(self.weights_data) / 1024 / 1024
            }
        }
        
        return metadata


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description='Export TensorFlow/Keras model to .mle'
    )
    parser.add_argument('--model', type=str, help='Path to saved Keras model')
    parser.add_argument('--out', type=str, required=True, help='Output .mle path')
    parser.add_argument('--input-shape', type=str, help='Input shape (comma-separated)')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    if args.demo or not args.model:
        print("Running TensorFlow/Keras demo\n")
        
        # Create demo model
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(20,)),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(3, activation='softmax')
        ])
        
        # Compile (required for some operations)
        model.compile(optimizer='adam', loss='categorical_crossentropy')
        
        # Export
        exporter = TensorFlowMLEExporter()
        exporter.export_keras(model, 'keras_model.mle', input_shape=(1, 20))
        
    else:
        model = keras.models.load_model(args.model)
        
        input_shape = None
        if args.input_shape:
            input_shape = tuple(map(int, args.input_shape.split(',')))
        
        exporter = TensorFlowMLEExporter()
        exporter.export_keras(model, args.out, input_shape)


if __name__ == '__main__':
    main()
