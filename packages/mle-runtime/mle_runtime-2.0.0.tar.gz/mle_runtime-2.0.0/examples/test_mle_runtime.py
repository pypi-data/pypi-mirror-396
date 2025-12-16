#!/usr/bin/env python3
"""
Single test cases for mle_runtime
Run individual tests to verify specific functionality
"""

import sys
import os
import time
import numpy as np
from typing import Optional

try:
    import mle_runtime
    HAS_RUNTIME = True
    # Check if it's the C++ extension
    if not hasattr(mle_runtime, 'Engine'):
        print("Error: C++ extension not available")
        print("Build with: ./build-python-sdk.ps1 (Windows) or ./build-python-sdk.sh (Linux/Mac)")
        sys.exit(1)
except ImportError:
    print("Error: mle_runtime not installed")
    print("Build with: ./build-python-sdk.ps1 (Windows) or ./build-python-sdk.sh (Linux/Mac)")
    sys.exit(1)


def test_basic_inference(model_path: str):
    """Test basic model loading and inference"""
    print("Test: Basic Inference")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    input_data = np.random.randn(1, 128).astype(np.float32)
    output = engine.run([input_data])
    
    print(f"✓ Input shape: {input_data.shape}")
    print(f"✓ Output shape: {output[0].shape}")
    print(f"✓ Output dtype: {output[0].dtype}")
    print()


def test_device_selection():
    """Test CPU and GPU device selection"""
    print("Test: Device Selection")
    print("-" * 40)
    
    # Test CPU
    try:
        engine_cpu = mle_runtime.Engine(mle_runtime.Device.CPU)
        print("✓ CPU device available")
    except Exception as e:
        print(f"✗ CPU device failed: {e}")
    
    # Test CUDA
    try:
        engine_gpu = mle_runtime.Engine(mle_runtime.Device.CUDA)
        print("✓ CUDA device available")
    except Exception as e:
        print(f"✗ CUDA device not available: {e}")
    
    print()


def test_multiple_inputs(model_path: str):
    """Test inference with multiple input tensors"""
    print("Test: Multiple Inputs")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    # Single input
    input1 = np.random.randn(1, 128).astype(np.float32)
    output1 = engine.run([input1])
    print(f"✓ Single input: {input1.shape} → {output1[0].shape}")
    
    # Try multiple inputs (if model supports it)
    try:
        input2 = np.random.randn(1, 64).astype(np.float32)
        output2 = engine.run([input1, input2])
        print(f"✓ Multiple inputs: {len([input1, input2])} → {len(output2)} outputs")
    except:
        print("  Model expects single input only")
    
    print()


def test_batch_sizes(model_path: str):
    """Test different batch sizes"""
    print("Test: Batch Sizes")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    batch_sizes = [1, 2, 4, 8, 16]
    
    for bs in batch_sizes:
        try:
            input_data = np.random.randn(bs, 128).astype(np.float32)
            start = time.perf_counter()
            output = engine.run([input_data])
            elapsed = (time.perf_counter() - start) * 1000
            
            print(f"✓ Batch {bs:2d}: {elapsed:6.2f} ms ({elapsed/bs:5.2f} ms/sample)")
        except Exception as e:
            print(f"✗ Batch {bs:2d}: {e}")
    
    print()


def test_data_types(model_path: str):
    """Test different input data types"""
    print("Test: Data Types")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    dtypes = [
        (np.float32, "float32"),
        (np.float64, "float64"),
        (np.float16, "float16"),
        (np.int32, "int32"),
    ]
    
    for dtype, name in dtypes:
        try:
            input_data = np.random.randn(1, 128).astype(dtype)
            output = engine.run([input_data])
            print(f"✓ {name:8s}: accepted, output dtype = {output[0].dtype}")
        except Exception as e:
            print(f"✗ {name:8s}: {type(e).__name__}")
    
    print()


def test_invalid_inputs(model_path: str):
    """Test error handling with invalid inputs"""
    print("Test: Invalid Inputs")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    test_cases = [
        ("Wrong shape (64)", np.random.randn(1, 64).astype(np.float32)),
        ("Wrong shape (256)", np.random.randn(1, 256).astype(np.float32)),
        ("3D tensor", np.random.randn(1, 128, 1).astype(np.float32)),
        ("4D tensor", np.random.randn(1, 1, 128, 1).astype(np.float32)),
        ("Empty batch", np.random.randn(0, 128).astype(np.float32)),
        ("Negative batch", np.random.randn(-1, 128).astype(np.float32) if False else None),
    ]
    
    for name, input_data in test_cases:
        if input_data is None:
            continue
        try:
            engine.run([input_data])
            print(f"⚠ {name:20s}: Expected error but succeeded")
        except Exception as e:
            print(f"✓ {name:20s}: Caught {type(e).__name__}")
    
    print()


def test_memory_usage(model_path: str):
    """Test memory usage tracking"""
    print("Test: Memory Usage")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    input_data = np.random.randn(1, 128).astype(np.float32)
    
    # Run inference
    engine.run([input_data])
    
    try:
        peak_mem = engine.peak_memory_usage()
        print(f"✓ Peak memory: {peak_mem / 1024 / 1024:.2f} MB")
        print(f"  ({peak_mem / 1024:.2f} KB)")
    except AttributeError:
        print("  Memory tracking not available")
    
    print()


def test_performance_benchmark(model_path: str, iterations: int = 100):
    """Benchmark inference performance"""
    print(f"Test: Performance Benchmark ({iterations} iterations)")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    input_data = np.random.randn(1, 128).astype(np.float32)
    
    # Warmup
    for _ in range(10):
        engine.run([input_data])
    
    # Benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        engine.run([input_data])
        times.append((time.perf_counter() - start) * 1000)
    
    times = np.array(times)
    
    print(f"✓ Mean:   {np.mean(times):.3f} ms")
    print(f"✓ Median: {np.median(times):.3f} ms")
    print(f"✓ Std:    {np.std(times):.3f} ms")
    print(f"✓ Min:    {np.min(times):.3f} ms")
    print(f"✓ Max:    {np.max(times):.3f} ms")
    print(f"✓ P95:    {np.percentile(times, 95):.3f} ms")
    print(f"✓ P99:    {np.percentile(times, 99):.3f} ms")
    print()


def test_concurrent_access(model_path: str):
    """Test thread-safe concurrent access"""
    print("Test: Concurrent Access")
    print("-" * 40)
    
    import threading
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    results = []
    errors = []
    
    def worker(thread_id: int, num_runs: int):
        try:
            for i in range(num_runs):
                input_data = np.random.randn(1, 128).astype(np.float32)
                output = engine.run([input_data])
                results.append((thread_id, i, output[0].shape))
        except Exception as e:
            errors.append((thread_id, str(e)))
    
    num_threads = 4
    runs_per_thread = 10
    
    threads = []
    start = time.perf_counter()
    
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i, runs_per_thread))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed = time.perf_counter() - start
    
    print(f"✓ Threads: {num_threads}")
    print(f"✓ Total inferences: {len(results)}")
    print(f"✓ Time: {elapsed:.2f}s")
    print(f"✓ Throughput: {len(results)/elapsed:.1f} inferences/sec")
    
    if errors:
        print(f"✗ Errors: {len(errors)}")
        for tid, err in errors[:3]:
            print(f"  Thread {tid}: {err}")
    
    print()


def test_model_reload(model_path: str):
    """Test loading and unloading models"""
    print("Test: Model Reload")
    print("-" * 40)
    
    for i in range(5):
        engine = mle_runtime.Engine(mle_runtime.Device.CPU)
        
        start = time.perf_counter()
        engine.load_model(model_path)
        load_time = (time.perf_counter() - start) * 1000
        
        input_data = np.random.randn(1, 128).astype(np.float32)
        engine.run([input_data])
        
        print(f"✓ Cycle {i+1}: Load time = {load_time:.2f} ms")
        
        del engine
    
    print()


def test_output_consistency(model_path: str):
    """Test output consistency across multiple runs"""
    print("Test: Output Consistency")
    print("-" * 40)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    # Fixed input
    np.random.seed(42)
    input_data = np.random.randn(1, 128).astype(np.float32)
    
    # Run multiple times
    outputs = []
    for i in range(10):
        output = engine.run([input_data])
        outputs.append(output[0].copy())
    
    # Check consistency
    reference = outputs[0]
    all_match = True
    
    for i, output in enumerate(outputs[1:], 1):
        if not np.allclose(reference, output, rtol=1e-6, atol=1e-6):
            print(f"✗ Run {i+1} differs from reference")
            all_match = False
    
    if all_match:
        print(f"✓ All {len(outputs)} runs produced identical outputs")
    
    print()


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MLE Runtime Single Test Cases')
    parser.add_argument('model_path', help='Path to .mle model file')
    parser.add_argument('--test', choices=[
        'basic', 'device', 'multi-input', 'batch', 'dtype', 
        'invalid', 'memory', 'benchmark', 'concurrent', 
        'reload', 'consistency', 'all'
    ], default='all', help='Test to run')
    parser.add_argument('--iterations', type=int, default=100,
                       help='Number of iterations for benchmark')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.model_path):
        print(f"Error: Model file not found: {args.model_path}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("MLE Runtime Single Test Cases")
    print("=" * 60 + "\n")
    
    tests = {
        'basic': lambda: test_basic_inference(args.model_path),
        'device': test_device_selection,
        'multi-input': lambda: test_multiple_inputs(args.model_path),
        'batch': lambda: test_batch_sizes(args.model_path),
        'dtype': lambda: test_data_types(args.model_path),
        'invalid': lambda: test_invalid_inputs(args.model_path),
        'memory': lambda: test_memory_usage(args.model_path),
        'benchmark': lambda: test_performance_benchmark(args.model_path, args.iterations),
        'concurrent': lambda: test_concurrent_access(args.model_path),
        'reload': lambda: test_model_reload(args.model_path),
        'consistency': lambda: test_output_consistency(args.model_path),
    }
    
    if args.test == 'all':
        for test_func in tests.values():
            test_func()
    else:
        tests[args.test]()
    
    print("=" * 60)
    print("Testing Complete!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    main()
