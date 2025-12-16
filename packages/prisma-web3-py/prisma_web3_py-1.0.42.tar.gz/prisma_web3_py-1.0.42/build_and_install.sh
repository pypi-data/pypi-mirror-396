#!/bin/bash
# Build and install script for prisma-web3-py

set -e

echo "=== Building prisma-web3-py package ==="

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Install build tools if needed
echo "Installing build tools..."
pip install --upgrade pip setuptools wheel build

# Build the package
echo "Building package..."
python -m build

echo ""
echo "=== Build completed ==="
echo "Distribution files created in ./dist/"
ls -lh dist/

echo ""
echo "=== Installation Options ==="
echo ""
echo "1. Install locally (editable mode):"
echo "   pip install -e ."
echo ""
echo "2. Install from wheel:"
echo "   pip install dist/prisma_web3_py-*.whl"
echo ""
echo "3. Install from source distribution:"
echo "   pip install dist/prisma-web3-py-*.tar.gz"
echo ""
