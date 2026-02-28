#!/bin/bash
# Package script for macOS/Linux

set -e

# Get project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

echo "Packaging Multi-Modal RAG application..."

# Detect platform and architecture
if [[ "$OSTYPE" == "darwin"* ]]; then
    PLATFORM="macOS"
    ARCH=$(uname -m)
else
    PLATFORM="Linux"
    ARCH=$(uname -m)
fi

PACKAGE_DIR="MultiModalRAG-${PLATFORM}-${ARCH}"

# Clean previous package
if [ -d "$PACKAGE_DIR" ]; then
    rm -rf "$PACKAGE_DIR"
fi
mkdir -p "$PACKAGE_DIR"

# Copy executable
echo "Copying executable..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: Copy .app bundle if it exists, otherwise copy binary
    if [ -d "dist/MultiModalRAG.app" ]; then
        cp -r "dist/MultiModalRAG.app" "$PACKAGE_DIR/"
    else
        cp "dist/MultiModalRAG" "$PACKAGE_DIR/"
        chmod +x "$PACKAGE_DIR/MultiModalRAG"
    fi
else
    # Linux: Copy binary
    cp "dist/MultiModalRAG" "$PACKAGE_DIR/"
    chmod +x "$PACKAGE_DIR/MultiModalRAG"
fi

# Copy .env.example and rename to .env
echo "Copying configuration..."
cp .env.example "$PACKAGE_DIR/.env"

# Create directories
echo "Creating directories..."
mkdir -p "$PACKAGE_DIR/documents"
mkdir -p "$PACKAGE_DIR/db"
mkdir -p "$PACKAGE_DIR/logs"

# Create README
cat > "$PACKAGE_DIR/README.txt" << 'EOF'
# Multi-Modal RAG System

## Quick Start

1. Edit the .env file with your credentials:
   - GOOGLE_CLOUD_PROJECT=your-project-id
   - GOOGLE_CLOUD_LOCATION=your-cloud-location
   - GEMINI_API_KEY=your-api-key

2. Run the application:
   - macOS: Double-click MultiModalRAG.app (or ./MultiModalRAG)
   - Linux: ./MultiModalRAG

3. The application will create:
   - documents/ - Place your files here
   - db/ - Vector database storage
   - logs/ - Application logs

## First Run

The application automatically creates a sample document on first run.
You can load your own documents using the "Load Files" button.

## Troubleshooting

If the application doesn't start:
1. Check that .env file has valid credentials
2. Check logs/app.log for error messages
3. Run from terminal to see console output

## Support

For issues: https://github.com/SystemSolution21/multi-modal-rag
EOF

# Create tarball
TARBALL="${PACKAGE_DIR}.tar.gz"
if [ -f "$TARBALL" ]; then
    rm -f "$TARBALL"
fi
tar -czf "$TARBALL" "$PACKAGE_DIR"

echo ""
echo "✓ Packaging complete!"
echo "Package location: $TARBALL"
echo ""
echo "Contents:"
echo "  - MultiModalRAG executable"
echo "  - .env (pre-configured template)"
echo "  - documents/ (empty, ready for files)"
echo "  - db/ (empty, will store vectors)"
echo "  - logs/ (empty, will store logs)"
echo "  - README.txt"