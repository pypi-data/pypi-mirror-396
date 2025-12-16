#!/bin/bash
# Build MLE Runtime Python package for deployment

set -e

CLEAN=false
TEST=false
UPLOAD=false
REPOSITORY="pypi"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --test)
            TEST=true
            shift
            ;;
        --upload)
            UPLOAD=true
            shift
            ;;
        --repository)
            REPOSITORY="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "================================================================================"
echo "MLE Runtime - Build Deployable Package"
echo "================================================================================"

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Clean previous builds
if [ "$CLEAN" = true ]; then
    echo -e "\n[1/6] Cleaning previous builds..."
    
    rm -rf dist build mle_runtime.egg-info
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    
    echo "✓ Cleaned"
fi

# Check dependencies
echo -e "\n[2/6] Checking build dependencies..."

for pkg in setuptools wheel build twine; do
    if ! python -m pip show $pkg >/dev/null 2>&1; then
        echo "Installing $pkg..."
        python -m pip install $pkg --quiet
    fi
done

echo "✓ Dependencies ready"

# Build source distribution
echo -e "\n[3/6] Building source distribution..."
python -m build --sdist

echo "✓ Source distribution built"

# Build wheel distribution
echo -e "\n[4/6] Building wheel distribution..."
python -m build --wheel

echo "✓ Wheel distribution built"

# List built packages
echo -e "\n[5/6] Built packages:"
ls -lh dist/ | tail -n +2 | awk '{print "  - " $9 " (" $5 ")"}'

# Run tests
if [ "$TEST" = true ]; then
    echo -e "\n[6/6] Running tests..."
    
    # Install package in development mode
    python -m pip install -e ".[dev]" --quiet
    
    # Run pytest
    python -m pytest tests/ -v
    
    echo "✓ All tests passed"
else
    echo -e "\n[6/6] Skipping tests (use --test to run)"
fi

# Check package with twine
echo -e "\nChecking package integrity..."
python -m twine check dist/*

echo "✓ Package integrity verified"

# Upload to PyPI
if [ "$UPLOAD" = true ]; then
    echo -e "\nUploading to $REPOSITORY..."
    
    if [ "$REPOSITORY" = "pypi" ]; then
        python -m twine upload dist/*
    elif [ "$REPOSITORY" = "testpypi" ]; then
        python -m twine upload --repository testpypi dist/*
    else
        python -m twine upload --repository $REPOSITORY dist/*
    fi
    
    echo "✓ Uploaded successfully"
else
    echo -e "\nSkipping upload (use --upload to publish)"
fi

# Summary
echo -e "\n================================================================================"
echo "BUILD COMPLETE!"
echo "================================================================================"

echo -e "\nPackages ready in: $SCRIPT_DIR/dist"
echo -e "\nInstallation commands:"
echo "  Local:  pip install dist/mle_runtime-*.whl"
echo "  PyPI:   pip install mle-runtime"
echo -e "\nWith extras:"
echo "  pip install mle-runtime[sklearn]      # Scikit-learn support"
echo "  pip install mle-runtime[pytorch]      # PyTorch support"
echo "  pip install mle-runtime[tensorflow]   # TensorFlow support"
echo "  pip install mle-runtime[all]          # Everything"
