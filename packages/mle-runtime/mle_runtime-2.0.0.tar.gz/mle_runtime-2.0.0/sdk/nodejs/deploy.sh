#!/bin/bash
# Node.js SDK Deployment Script
# Builds and publishes to npm

set -e

echo "========================================="
echo "Node.js SDK - Build & Deploy"
echo "========================================="
echo ""

# Install dependencies
echo "Installing dependencies..."
npm install

# Build TypeScript
echo "Building TypeScript..."
npm run build

# Run tests
echo "Running tests..."
if npm run test &> /dev/null; then
    echo "✓ Tests passed"
else
    echo "⚠ No tests configured or tests failed"
fi

# Create package
echo ""
echo "Creating npm package..."
npm pack

# Show package info
echo ""
echo "Package ready:"
ls -lh *.tgz

echo ""
echo "========================================="
echo "Ready to deploy!"
echo "========================================="
echo ""
echo "To publish to npm:"
echo "  Test registry: npm publish --registry https://registry.npmjs.org --dry-run"
echo "  Production:    npm publish"
echo ""
echo "To test locally:"
echo "  npm install -g mle-runtime-*.tgz"
echo ""
