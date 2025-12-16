#!/bin/bash
# Python SDK Deployment Script
# Builds and publishes to PyPI

set -e

echo "========================================="
echo "Python SDK - Build & Deploy"
echo "========================================="
echo ""

# Check if twine is installed
if ! command -v twine &> /dev/null; then
    echo "Installing twine..."
    pip install twine
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/

# Build source distribution and wheel
echo "Building distribution packages..."
python setup.py sdist bdist_wheel

# Check packages
echo ""
echo "Checking packages..."
twine check dist/*

# Show what will be uploaded
echo ""
echo "Packages ready for upload:"
ls -lh dist/

echo ""
echo "========================================="
echo "Ready to deploy!"
echo "========================================="
echo ""
echo "To upload to PyPI:"
echo "  Test PyPI:  twine upload --repository testpypi dist/*"
echo "  Production: twine upload dist/*"
echo ""
echo "To test locally:"
echo "  pip install dist/mle_runtime-*.whl"
echo ""
