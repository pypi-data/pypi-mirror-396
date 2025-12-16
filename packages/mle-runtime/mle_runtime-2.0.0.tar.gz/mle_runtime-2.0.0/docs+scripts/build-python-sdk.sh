#!/bin/bash
# Build and install Python SDK with C++ bindings

set -e

echo "============================================================"
echo "Building MLE Runtime Python SDK with C++ Extensions"
echo "============================================================"
echo ""

# Check Python
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python not found. Please install Python 3.8+"
    exit 1
fi
python3 --version
echo "✓ Python found"
echo ""

# Check pybind11
echo "Checking pybind11..."
if ! python3 -c "import pybind11" 2>/dev/null; then
    echo "Installing pybind11..."
    pip3 install pybind11
fi
echo "✓ pybind11 installed"
echo ""

# Build C++ bindings
echo "Building C++ bindings..."
cd bindings/python

# Uninstall old version
echo "Removing old installation..."
pip3 uninstall -y mle-runtime 2>/dev/null || true

# Build and install
echo "Building extension..."
python3 setup.py build_ext --inplace

echo "Installing package..."
pip3 install -e .

cd ../..

echo "✓ C++ bindings built and installed"
echo ""

# Verify installation
echo "Verifying installation..."
python3 -c "import mle_runtime; print('Version:', getattr(mle_runtime, '__version__', 'N/A'))"
echo "✓ Installation verified"
echo ""

echo "============================================================"
echo "Build Complete!"
echo "============================================================"
echo ""
echo "You can now run examples:"
echo "  python3 examples/complete_workflow.py"
echo "  python3 examples/test_mle_runtime.py example_model.mle --test all"
echo ""
