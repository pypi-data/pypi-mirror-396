#!/usr/bin/env python3
"""
Complete workflow example: Train → Export → Load → Infer
Demonstrates the full pipeline from PyTorch to MLE runtime with comprehensive testing
"""

import sys
import os
import time
import torch
import torch.nn as nn
import numpy as np
from typing import List, Dict, Any

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../tools/exporter'))
from pytorch_to_mle import MLEExporter

try:
    # Try to import from bindings directory first
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../bindings/python'))
    import mle_runtime
    HAS_RUNTIME = True
    # Check if it's the C++ extension or pure Python wrapper
    HAS_CPP_EXTENSION = hasattr(mle_runtime, 'Engine')
    if not HAS_CPP_EXTENSION:
        print("Warning: C++ extension not available. Build with: ./build-python-sdk.ps1")
        HAS_RUNTIME = False
except ImportError as e:
    print(f"Warning: mle_runtime not installed. Build with: ./build-python-sdk.ps1")
    print(f"Error: {e}")
    HAS_RUNTIME = False
    HAS_CPP_EXTENSION = False


class SimpleClassifier(nn.Module):
    """Simple MLP classifier for demonstration"""
    def __init__(self, input_size=128, hidden_size=256, num_classes=10):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu1 = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.relu2 = nn.ReLU()
        self.fc3 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        x = self.fc1(x)
        x = self.relu1(x)
        x = self.fc2(x)
        x = self.relu2(x)
        x = self.fc3(x)
        return x


def train_model(epochs=5):
    """Train a simple model on synthetic data"""
    print("=" * 60)
    print("Step 1: Training PyTorch Model")
    print("=" * 60)
    
    # Create model
    model = SimpleClassifier()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.CrossEntropyLoss()
    
    # Synthetic data
    batch_size = 32
    input_size = 128
    num_classes = 10
    
    print(f"Model: {sum(p.numel() for p in model.parameters())} parameters")
    print(f"Training for {epochs} epochs...")
    
    model.train()
    for epoch in range(epochs):
        # Generate batch
        X = torch.randn(batch_size, input_size)
        y = torch.randint(0, num_classes, (batch_size,))
        
        # Forward pass
        outputs = model(X)
        loss = criterion(outputs, y)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        if (epoch + 1) % 1 == 0:
            print(f"  Epoch {epoch+1}/{epochs}, Loss: {loss.item():.4f}")
    
    model.eval()
    print("✓ Training complete\n")
    return model


def export_model(model, output_path="model.mle"):
    """Export PyTorch model to .mle format"""
    print("=" * 60)
    print("Step 2: Exporting to .mle Format")
    print("=" * 60)
    
    exporter = MLEExporter()
    input_shape = (1, 128)
    
    print(f"Exporting to: {output_path}")
    print(f"Input shape: {input_shape}")
    
    start = time.perf_counter()
    exporter.export_mlp(model, input_shape, output_path)
    end = time.perf_counter()
    
    print(f"✓ Export complete in {(end - start) * 1000:.2f} ms")
    print(f"  File size: {os.path.getsize(output_path) / 1024:.2f} KB\n")
    
    return output_path


def inspect_model(model_path):
    """Inspect .mle file"""
    print("=" * 60)
    print("Step 3: Inspecting .mle File")
    print("=" * 60)
    
    import struct
    import json
    
    with open(model_path, 'rb') as f:
        # Read header (actually 80 bytes: 2*uint32 + 7*uint64 + 16 reserved)
        header = f.read(80)
        if len(header) < 80:
            print(f"Error: File too small ({len(header)} bytes)")
            return
        # Unpack: magic(4) + version(4) + 7 uint64(56) + 16 reserved = 80 bytes
        data = struct.unpack('II QQQQQQQ 16s', header)
        magic, version, meta_off, meta_size, graph_off, graph_size, \
        weights_off, weights_size, sig_off = data[:9]
        
        print(f"Magic: 0x{magic:08x}")
        print(f"Version: {version}")
        print(f"Metadata size: {meta_size} bytes")
        print(f"Graph size: {graph_size} bytes")
        print(f"Weights size: {weights_size / 1024:.2f} KB")
        
        # Read metadata
        if meta_size > 0:
            f.seek(meta_off)
            meta_bytes = f.read(meta_size)
            try:
                metadata = json.loads(meta_bytes.decode('utf-8'))
                print(f"Model name: {metadata.get('model_name', 'N/A')}")
            except:
                print(f"Metadata: (binary, {meta_size} bytes)")
        
        # Read graph info
        f.seek(graph_off)
        num_nodes, num_tensors = struct.unpack('II', f.read(8))
        print(f"Graph nodes: {num_nodes}")
        print(f"Tensors: {num_tensors}")
    
    print("✓ Inspection complete\n")


def run_inference(model_path, pytorch_model):
    """Load .mle and run inference, compare with PyTorch"""
    if not HAS_RUNTIME:
        print("Skipping inference (mle_runtime not available)")
        return
    
    print("=" * 60)
    print("Step 4: Running Inference")
    print("=" * 60)
    
    # Try GPU first, fallback to CPU
    try:
        device = mle_runtime.Device.CUDA
        engine = mle_runtime.Engine(device)
        print("Using device: CUDA")
    except:
        device = mle_runtime.Device.CPU
        engine = mle_runtime.Engine(device)
        print("Using device: CPU")
    
    # Load model
    print(f"Loading model: {model_path}")
    start = time.perf_counter()
    engine.load_model(model_path)
    end = time.perf_counter()
    print(f"✓ Cold load time: {(end - start) * 1000:.2f} ms")
    
    # Create test input
    np.random.seed(42)
    input_data = np.random.randn(1, 128).astype(np.float32)
    
    # MLE inference
    print("\nRunning MLE inference...")
    start = time.perf_counter()
    outputs_mle = engine.run([input_data])
    end = time.perf_counter()
    mle_time = (end - start) * 1000
    output_mle = outputs_mle[0]
    
    print(f"✓ Inference time: {mle_time:.2f} ms")
    print(f"  Output shape: {output_mle.shape}")
    print(f"  Peak memory: {engine.peak_memory_usage() / 1024 / 1024:.2f} MB")
    
    # PyTorch inference for comparison
    print("\nRunning PyTorch inference for comparison...")
    pytorch_model.eval()
    with torch.no_grad():
        input_torch = torch.from_numpy(input_data)
        output_torch = pytorch_model(input_torch).numpy()
    
    # Compare outputs
    print("\nComparing outputs:")
    print(f"  MLE output (first 5): {output_mle.flatten()[:5]}")
    print(f"  PyTorch output (first 5): {output_torch.flatten()[:5]}")
    
    abs_error = np.abs(output_torch - output_mle)
    rel_error = abs_error / (np.abs(output_torch) + 1e-8)
    
    print(f"\nError metrics:")
    print(f"  Max absolute error: {np.max(abs_error):.6f}")
    print(f"  Max relative error: {np.max(rel_error):.6f}")
    print(f"  Mean absolute error: {np.mean(abs_error):.6f}")
    
    if np.max(rel_error) < 1e-3:
        print("✓ Outputs match within tolerance (< 1e-3)")
    else:
        print("⚠ Outputs differ more than expected")
    
    # Benchmark
    print("\nBenchmarking (100 iterations)...")
    times = []
    for _ in range(100):
        start = time.perf_counter()
        engine.run([input_data])
        end = time.perf_counter()
        times.append((end - start) * 1000)
    
    print(f"  Mean: {np.mean(times):.2f} ms")
    print(f"  Median: {np.median(times):.2f} ms")
    print(f"  P95: {np.percentile(times, 95):.2f} ms")
    print(f"  P99: {np.percentile(times, 99):.2f} ms")
    
    print("\n✓ Inference complete\n")


def test_batch_inference(model_path):
    """Test batch inference with different batch sizes"""
    if not HAS_RUNTIME:
        return
    
    print("=" * 60)
    print("Test 1: Batch Inference")
    print("=" * 60)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    batch_sizes = [1, 4, 8, 16, 32]
    for batch_size in batch_sizes:
        input_data = np.random.randn(batch_size, 128).astype(np.float32)
        
        start = time.perf_counter()
        outputs = engine.run([input_data])
        elapsed = (time.perf_counter() - start) * 1000
        
        print(f"Batch size {batch_size:2d}: {elapsed:.2f} ms ({elapsed/batch_size:.2f} ms/sample)")
    
    print("✓ Batch inference test complete\n")


def test_concurrent_inference(model_path):
    """Test concurrent inference from multiple threads"""
    if not HAS_RUNTIME:
        return
    
    print("=" * 60)
    print("Test 2: Concurrent Inference")
    print("=" * 60)
    
    import threading
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    results = []
    errors = []
    
    def worker(thread_id, num_runs):
        try:
            for i in range(num_runs):
                input_data = np.random.randn(1, 128).astype(np.float32)
                output = engine.run([input_data])
                results.append((thread_id, i, output[0].shape))
        except Exception as e:
            errors.append((thread_id, str(e)))
    
    num_threads = 4
    runs_per_thread = 25
    
    print(f"Running {num_threads} threads, {runs_per_thread} inferences each...")
    
    start = time.perf_counter()
    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i, runs_per_thread))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    elapsed = time.perf_counter() - start
    
    print(f"✓ Completed {len(results)} inferences in {elapsed:.2f}s")
    print(f"  Throughput: {len(results)/elapsed:.1f} inferences/sec")
    if errors:
        print(f"⚠ Errors: {len(errors)}")
        for tid, err in errors[:3]:
            print(f"    Thread {tid}: {err}")
    print()


def test_memory_management(model_path):
    """Test memory usage and cleanup"""
    if not HAS_RUNTIME:
        return
    
    print("=" * 60)
    print("Test 3: Memory Management")
    print("=" * 60)
    
    # Test multiple load/unload cycles
    for i in range(5):
        engine = mle_runtime.Engine(mle_runtime.Device.CPU)
        engine.load_model(model_path)
        
        input_data = np.random.randn(1, 128).astype(np.float32)
        engine.run([input_data])
        
        peak_mem = engine.peak_memory_usage() / 1024 / 1024
        print(f"Cycle {i+1}: Peak memory = {peak_mem:.2f} MB")
        
        del engine
    
    print("✓ Memory management test complete\n")


def test_error_handling(model_path):
    """Test error handling with invalid inputs"""
    if not HAS_RUNTIME:
        return
    
    print("=" * 60)
    print("Test 4: Error Handling")
    print("=" * 60)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    test_cases = [
        ("Wrong shape", np.random.randn(1, 64).astype(np.float32)),
        ("Wrong dtype", np.random.randn(1, 128).astype(np.float64)),
        ("3D input", np.random.randn(1, 128, 1).astype(np.float32)),
        ("Empty batch", np.random.randn(0, 128).astype(np.float32)),
    ]
    
    for name, input_data in test_cases:
        try:
            engine.run([input_data])
            print(f"  {name}: ⚠ Expected error but succeeded")
        except Exception as e:
            print(f"  {name}: ✓ Caught error - {type(e).__name__}")
    
    print("✓ Error handling test complete\n")


def test_model_metadata(model_path):
    """Test model metadata retrieval"""
    if not HAS_RUNTIME:
        return
    
    print("=" * 60)
    print("Test 5: Model Metadata")
    print("=" * 60)
    
    try:
        loader = mle_runtime.ModelLoader(model_path)
        metadata = loader.get_metadata()
        print(f"Metadata: {metadata}")
    except Exception as e:
        print(f"  Metadata not available: {e}")
    
    print("✓ Metadata test complete\n")


def test_warmup_performance(model_path):
    """Test cold start vs warm inference performance"""
    if not HAS_RUNTIME:
        return
    
    print("=" * 60)
    print("Test 6: Warmup Performance")
    print("=" * 60)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    
    # Cold start
    start = time.perf_counter()
    engine.load_model(model_path)
    cold_load = (time.perf_counter() - start) * 1000
    
    input_data = np.random.randn(1, 128).astype(np.float32)
    
    # First inference (cold)
    start = time.perf_counter()
    engine.run([input_data])
    cold_infer = (time.perf_counter() - start) * 1000
    
    # Warm inferences
    warm_times = []
    for _ in range(100):
        start = time.perf_counter()
        engine.run([input_data])
        warm_times.append((time.perf_counter() - start) * 1000)
    
    print(f"Cold load time: {cold_load:.2f} ms")
    print(f"Cold inference: {cold_infer:.2f} ms")
    print(f"Warm inference (mean): {np.mean(warm_times):.2f} ms")
    print(f"Warm inference (median): {np.median(warm_times):.2f} ms")
    print(f"Speedup: {cold_infer / np.mean(warm_times):.2f}x")
    
    print("✓ Warmup performance test complete\n")


def test_numerical_precision(model_path, pytorch_model):
    """Test numerical precision across different inputs"""
    if not HAS_RUNTIME:
        return
    
    print("=" * 60)
    print("Test 7: Numerical Precision")
    print("=" * 60)
    
    engine = mle_runtime.Engine(mle_runtime.Device.CPU)
    engine.load_model(model_path)
    
    pytorch_model.eval()
    
    test_inputs = [
        ("Random normal", np.random.randn(1, 128).astype(np.float32)),
        ("All zeros", np.zeros((1, 128), dtype=np.float32)),
        ("All ones", np.ones((1, 128), dtype=np.float32)),
        ("Large values", np.random.randn(1, 128).astype(np.float32) * 100),
        ("Small values", np.random.randn(1, 128).astype(np.float32) * 0.01),
    ]
    
    for name, input_data in test_inputs:
        output_mle = engine.run([input_data])[0]
        
        with torch.no_grad():
            output_torch = pytorch_model(torch.from_numpy(input_data)).numpy()
        
        abs_error = np.abs(output_torch - output_mle)
        rel_error = abs_error / (np.abs(output_torch) + 1e-8)
        
        print(f"{name:15s}: max_abs={np.max(abs_error):.6f}, max_rel={np.max(rel_error):.6f}")
    
    print("✓ Numerical precision test complete\n")


def run_all_tests(model_path, pytorch_model):
    """Run all test suites"""
    print("\n" + "=" * 60)
    print("MLE Runtime Test Suite")
    print("=" * 60 + "\n")
    
    if not HAS_RUNTIME:
        print("⚠ mle_runtime not available. Skipping tests.")
        return
    
    test_batch_inference(model_path)
    test_concurrent_inference(model_path)
    test_memory_management(model_path)
    test_error_handling(model_path)
    test_model_metadata(model_path)
    test_warmup_performance(model_path)
    test_numerical_precision(model_path, pytorch_model)
    
    print("=" * 60)
    print("All Tests Complete!")
    print("=" * 60 + "\n")


def main():
    print("\n" + "=" * 60)
    print("Complete Workflow: PyTorch -> .mle -> Inference + Testing")
    print("=" * 60 + "\n")
    
    # Step 1: Train
    model = train_model(epochs=5)
    
    # Step 2: Export
    model_path = export_model(model, "example_model.mle")
    
    # Step 3: Inspect
    inspect_model(model_path)
    
    # Step 4: Basic Inference
    run_inference(model_path, model)
    
    # Step 5: Comprehensive Testing
    run_all_tests(model_path, model)
    
    print("=" * 60)
    print("Workflow Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Try with your own PyTorch model")
    print("  2. Experiment with different architectures")
    print("  3. Measure performance on your hardware")
    print("  4. Run individual tests: python complete_workflow.py --test <test_name>")
    print()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='MLE Runtime Complete Workflow')
    parser.add_argument('--test', choices=['batch', 'concurrent', 'memory', 'error', 
                                           'metadata', 'warmup', 'precision', 'all'],
                       help='Run specific test suite')
    args = parser.parse_args()
    
    if args.test:
        # Quick setup for testing
        model = train_model(epochs=2)
        model_path = export_model(model, "test_model.mle")
        
        if args.test == 'batch':
            test_batch_inference(model_path)
        elif args.test == 'concurrent':
            test_concurrent_inference(model_path)
        elif args.test == 'memory':
            test_memory_management(model_path)
        elif args.test == 'error':
            test_error_handling(model_path)
        elif args.test == 'metadata':
            test_model_metadata(model_path)
        elif args.test == 'warmup':
            test_warmup_performance(model_path)
        elif args.test == 'precision':
            test_numerical_precision(model_path, model)
        elif args.test == 'all':
            run_all_tests(model_path, model)
    else:
        main()
