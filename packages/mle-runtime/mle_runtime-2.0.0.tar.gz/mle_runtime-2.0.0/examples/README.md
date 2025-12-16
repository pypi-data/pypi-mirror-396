# MLE Runtime Examples

This directory contains comprehensive examples and tests for the MLE Runtime.

## Prerequisites

Before running these examples, you need to build and install the MLE Runtime with C++ extensions.

### Building from Source

The MLE Runtime requires the C++ bindings to be built. Use the provided build scripts:

#### Windows

```powershell
# Build and install Python package with C++ bindings
.\build-python-sdk.ps1
```

#### Linux/macOS

```bash
# Build and install Python package with C++ bindings
chmod +x build-python-sdk.sh
./build-python-sdk.sh
```

#### Manual Build (if scripts don't work)

```bash
# Install pybind11
pip install pybind11

# Build and install
cd bindings/python
pip install -e .
cd ../..
```

### Verify Installation

```python
import mle_runtime
print(mle_runtime.__version__)

# Test basic functionality
engine = mle_runtime.MLEEngine(mle_runtime.Device.CPU)
print("✓ MLE Runtime installed successfully")
```

## Examples

### 1. Complete Workflow (`complete_workflow.py`)

Full pipeline from training a PyTorch model to running inference with comprehensive testing.

```bash
# Run complete workflow
python examples/complete_workflow.py

# Run specific test
python examples/complete_workflow.py --test batch
python examples/complete_workflow.py --test concurrent
python examples/complete_workflow.py --test all
```

**Available tests:**
- `batch` - Batch inference with different sizes
- `concurrent` - Multi-threaded inference
- `memory` - Memory management
- `error` - Error handling
- `metadata` - Model metadata
- `warmup` - Cold vs warm performance
- `precision` - Numerical precision
- `all` - Run all tests

### 2. Single Test Cases (`test_mle_runtime.py`)

Individual test cases for specific functionality.

```bash
# Run all tests
python examples/test_mle_runtime.py model.mle --test all

# Run specific test
python examples/test_mle_runtime.py model.mle --test basic
python examples/test_mle_runtime.py model.mle --test benchmark --iterations 1000
```

**Available tests:**
- `basic` - Basic inference
- `device` - Device selection (CPU/CUDA)
- `multi-input` - Multiple input tensors
- `batch` - Different batch sizes
- `dtype` - Data type handling
- `invalid` - Invalid input handling
- `memory` - Memory usage tracking
- `benchmark` - Performance benchmark
- `concurrent` - Thread-safe access
- `reload` - Model reload cycles
- `consistency` - Output consistency

## Troubleshooting

### ImportError: cannot import name 'Engine'

This means the C++ extension wasn't built. Solutions:

1. **Use build script** (recommended):
   ```powershell
   # Windows
   .\build-python-sdk.ps1
   
   # Linux/Mac
   ./build-python-sdk.sh
   ```

2. **Manual build**:
   ```bash
   pip install pybind11
   cd bindings/python
   pip uninstall -y mle-runtime
   pip install -e .
   cd ../..
   ```

3. **Check build requirements**:
   - C++20 compatible compiler (MSVC 2019+, GCC 10+, Clang 10+)
   - Python 3.8+
   - pybind11
   - Python development headers

### Model file not found

Make sure to run `complete_workflow.py` first to generate a test model:

```bash
python examples/complete_workflow.py
# This creates example_model.mle
```

Then use it with test cases:

```bash
python examples/test_mle_runtime.py example_model.mle --test all
```

### CUDA not available

If you see "CUDA device not available", the examples will automatically fall back to CPU. To enable CUDA:

1. Install CUDA Toolkit 11.0+
2. Rebuild with CUDA support:
   ```bash
   cd cpp_core/build
   cmake .. -DUSE_CUDA=ON
   cmake --build . --config Release
   ```

## Performance Tips

1. **Warmup**: First inference is slower due to initialization
2. **Batch size**: Larger batches improve throughput
3. **Memory**: Use context manager for automatic cleanup
4. **Threading**: Engine is thread-safe for concurrent inference

## Example Output

```
============================================================
Complete Workflow: PyTorch → .mle → Inference + Testing
============================================================

Step 1: Training PyTorch Model
Model: 67850 parameters
Training for 5 epochs...
✓ Training complete

Step 2: Exporting to .mle Format
✓ Export complete in 45.23 ms
  File size: 264.12 KB

Step 3: Inspecting .mle File
Magic: 0x4d4c4546
Version: 1
✓ Inspection complete

Step 4: Running Inference
Using device: CPU
✓ Cold load time: 12.34 ms
✓ Inference time: 2.45 ms
✓ Outputs match within tolerance (< 1e-3)

Test 1: Batch Inference
Batch size  1: 2.45 ms (2.45 ms/sample)
Batch size  4: 3.12 ms (0.78 ms/sample)
Batch size  8: 4.56 ms (0.57 ms/sample)
✓ Batch inference test complete

============================================================
All Tests Complete!
============================================================
```

## Next Steps

1. Try with your own PyTorch models
2. Experiment with different architectures
3. Measure performance on your hardware
4. Integrate into your production pipeline

## Support

For issues or questions:
- Check the main README.md
- Review SDK documentation in sdk/README.md
- Open an issue on GitHub
