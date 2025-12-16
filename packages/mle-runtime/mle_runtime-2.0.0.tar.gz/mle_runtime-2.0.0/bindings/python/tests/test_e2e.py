#!/usr/bin/env python3
"""
End-to-end test: Train PyTorch model, export to .mle, load and compare outputs
"""

import pytest
import torch
import torch.nn as nn
import numpy as np
import sys
import os

# Add tools to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../tools/exporter'))
from pytorch_to_mle import MLEExporter

import mle_runtime


class SimpleMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(128, 256)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(256, 128)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(128, 10)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.fc3(x)
        return x


def test_e2e_inference():
    """Test end-to-end: PyTorch -> .mle -> inference"""
    
    # Create and initialize model
    torch.manual_seed(42)
    model = SimpleMLP()
    model.eval()
    
    # Export to .mle
    exporter = MLEExporter()
    mle_path = '/tmp/test_model.mle'
    exporter.export_mlp(model, (1, 128), mle_path)
    
    # Create test input
    np.random.seed(42)
    input_data = np.random.randn(1, 128).astype(np.float32)
    input_torch = torch.from_numpy(input_data)
    
    # Get PyTorch output
    with torch.no_grad():
        output_torch = model(input_torch).numpy()
    
    # Load with MLE runtime
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(mle_path)
    
    # Run inference
    outputs_mle = engine.run([input_data])
    output_mle = outputs_mle[0]
    
    # Compare outputs
    print(f"PyTorch output: {output_torch.flatten()[:5]}")
    print(f"MLE output: {output_mle.flatten()[:5]}")
    
    # Check relative error
    rel_error = np.abs(output_torch - output_mle) / (np.abs(output_torch) + 1e-8)
    max_rel_error = np.max(rel_error)
    
    print(f"Max relative error: {max_rel_error}")
    
    assert max_rel_error < 1e-3, f"Outputs don't match: max rel error = {max_rel_error}"
    
    # Cleanup
    os.remove(mle_path)
    
    print("✓ E2E test passed!")


def test_cold_load_time():
    """Test cold load time"""
    import time
    
    # Create model
    torch.manual_seed(42)
    model = SimpleMLP()
    model.eval()
    
    # Export
    exporter = MLEExporter()
    mle_path = '/tmp/test_model_load.mle'
    exporter.export_mlp(model, (1, 128), mle_path)
    
    # Measure load time
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    
    start = time.perf_counter()
    engine.load_model(mle_path)
    end = time.perf_counter()
    
    load_time_ms = (end - start) * 1000
    print(f"Cold load time: {load_time_ms:.2f} ms")
    
    # Check against target (<50ms)
    if load_time_ms > 50:
        print(f"⚠ Warning: Load time {load_time_ms:.2f} ms exceeds target of 50 ms")
    else:
        print(f"✓ Load time within target")
    
    # Cleanup
    os.remove(mle_path)


if __name__ == '__main__':
    test_e2e_inference()
    test_cold_load_time()
