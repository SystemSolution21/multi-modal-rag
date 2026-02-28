#!/bin/bash
# Build script for macOS/Linux using PyInstaller

set -e  # Exit on error

# Get project root (parent of scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Building Multi-Modal RAG application for $(uname)..."

# Detect platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    ARCH=$(uname -m)
else
    PLATFORM="Linux"
    ARCH=$(uname -m)
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist build

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update PyInstaller
echo "Ensuring PyInstaller is installed..."
uv pip install pyinstaller

# Build executable
echo "Building executable..."
pyinstaller --clean scripts/build.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Build successful!"
    echo "Executable location: dist/MultiModalRAG"
    echo ""
    echo "Next steps:"
    echo "  1. Test: ./dist/MultiModalRAG"
    echo "  2. Package: ./scripts/package.sh"
else
    echo ""
    echo "✗ Build failed!"
    exit 1
fi