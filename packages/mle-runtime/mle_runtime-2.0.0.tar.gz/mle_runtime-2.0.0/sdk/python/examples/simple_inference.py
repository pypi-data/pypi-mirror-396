"""
Simple inference example using MLE Python SDK
"""

import sys
import numpy as np
import mle_runtime


def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_inference.py <model.mle>")
        sys.exit(1)
    
    model_path = sys.argv[1]
    
    try:
        # Create engine
        engine = mle_runtime.MLEEngine(mle_runtime.Device.CPU)
        
        # Load model
        print(f"Loading model: {model_path}")
        engine.load_model(model_path)
        
        # Print metadata
        metadata = engine.metadata
        if metadata:
            print(f"Model: {metadata.model_name}")
            print(f"Framework: {metadata.framework}")
        
        # Create input tensor (example: 1x20 features)
        input_data = np.arange(20, dtype=np.float32) * 0.1
        input_data = input_data.reshape(1, 20)
        
        # Run inference
        print("Running inference...")
        outputs = engine.run([input_data])
        
        # Print results
        print(f"Output shape: {outputs[0].shape}")
        print(f"First output value: {outputs[0][0]}")
        print(f"Peak memory usage: {engine.peak_memory_usage() / 1024:.2f} KB")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
