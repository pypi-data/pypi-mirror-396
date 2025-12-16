#!/usr/bin/env python3
"""
Example: Load .mle model and run inference
"""

import sys
import numpy as np
import mle_runtime

def main():
    if len(sys.argv) < 2:
        print("Usage: python run_inference.py <model.mle> [input.npy]")
        sys.exit(1)
    
    model_path = sys.argv[1]
    
    # Create engine
    try:
        engine = mle_runtime.Engine(mle_runtime.Device.CUDA)
        print("Using CUDA device")
    except:
        engine = mle_runtime.Engine(mle_runtime.Device.CPU)
        print("Using CPU device")
    
    # Load model
    print(f"Loading model: {model_path}")
    engine.load_model(model_path)
    
    # Prepare input
    if len(sys.argv) > 2:
        input_data = np.load(sys.argv[2])
    else:
        # Default: random input [1, 128]
        input_data = np.random.randn(1, 128).astype(np.float32)
    
    print(f"Input shape: {input_data.shape}")
    
    # Run inference
    import time
    start = time.perf_counter()
    outputs = engine.run([input_data])
    end = time.perf_counter()
    
    print(f"Inference time: {(end - start) * 1000:.2f} ms")
    print(f"Output shape: {outputs[0].shape}")
    print(f"Output (first 10): {outputs[0].flatten()[:10]}")
    print(f"Peak memory: {engine.peak_memory_usage() / 1024 / 1024:.2f} MB")

if __name__ == '__main__':
    main()
