# Docker Distribution Guide

## Overview

Docker provides a **truly cross-platform** solution that works on:
- ✅ Linux (amd64, arm64)
- ✅ macOS (Intel & Apple Silicon)
- ✅ Windows (with Docker Desktop or WSL2)

## Quick Start

### Option 1: Pull from Registry (Recommended)

```bash
# Pull the image
docker pull ghcr.io/yourusername/multi-modal-rag:latest

# Run
docker run -it --rm \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/db:/app/db \
  -v $(pwd)/documents:/app/documents \
  multimodal-rag:latest
```

### Option 2: Build Locally

```bash
# Linux/macOS
chmod +x build/docker-build.sh
build/docker-build.sh

# Windows
build\docker-build.ps1
```

### Option 3: Use Docker Compose

```bash
# Setup
cp .env.example .env
# Edit .env with your credentials

# Run
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

## Building Multi-Platform Images

### For Distribution

```bash
# Build for amd64 and arm64
export PLATFORMS="linux/amd64,linux/arm64"
build/docker-build.sh

# Package for distribution
build/docker-package.sh
```

### Push to Registry

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Build and push
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --target production \
  --tag ghcr.io/yourusername/multi-modal-rag:latest \
  --push \
  .
```

## GUI Support

### Linux

```bash
# Allow Docker to access X11
xhost +local:docker

# Run with GUI
docker run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:ro \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/db:/app/db \
  -v $(pwd)/documents:/app/documents \
  multimodal-rag:latest
```

### macOS

```bash
# Install XQuartz
brew install --cask xquartz

# Start XQuartz and allow connections
xhost + 127.0.0.1

# Run with GUI
docker run -it --rm \
  -e DISPLAY=host.docker.internal:0 \
  -v $(pwd)/.env:/app/.env \
  -v $(pwd)/db:/app/db \
  -v $(pwd)/documents:/app/documents \
  multimodal-rag:latest
```

### Windows

```powershell
# Install VcXsrv from https://sourceforge.net/projects/vcxsrv/
# Start XLaunch with "Disable access control" checked

# Run with GUI
docker run -it --rm `
  -e DISPLAY=host.docker.internal:0.0 `
  -v ${PWD}/.env:/app/.env `
  -v ${PWD}/db:/app/db `
  -v ${PWD}/documents:/app/documents `
  multimodal-rag:latest
```

## Development Workflow

### Live Development

```bash
# Start with source code mounted
docker compose up

# Code changes are reflected immediately
# (Python files are mounted as read-only volumes)
```

### Rebuild After Changes

```bash
# Rebuild image
docker compose build

# Restart
docker compose up -d
```

## Distribution Packages

### Create Distribution Package

```bash
# Build image
build/docker-build.sh

# Package for distribution
build/docker-package.sh
```

This creates:
```
MultiModalRAG-Docker-latest/
├── multimodal-rag-latest.tar.gz  # ~500MB compressed image
├── docker-compose.yml
├── .env.example
├── run.sh                         # Quick start script (Linux/Mac)
├── run.ps1                        # Quick start script (Windows)
└── README.txt
```

### End User Installation

```bash
# 1. Extract package
tar -xzf MultiModalRAG-Docker-latest.tar.gz
cd MultiModalRAG-Docker-latest

# 2. Load image
docker load < multimodal-rag-latest.tar.gz

# 3. Configure
cp .env.example .env
# Edit .env

# 4. Run
./run.sh  # Linux/macOS
# or
.\run.ps1  # Windows
```

## Comparison: Docker vs Native Executables

| Feature | Docker | PyInstaller |
|---------|--------|-------------|
| **Cross-platform** | ✅ True (one image) | ⚠️ Build per OS |
| **Size** | ~500MB compressed | ~150-200MB |
| **Startup** | Fast | Faster |
| **Dependencies** | Docker required | None |
| **Updates** | Pull new image | Download new exe |
| **Development** | Live reload | Rebuild required |
| **GUI** | Needs X11 setup | Native |
| **Distribution** | Single package | 3 packages |

## Best Practices

### For Developers

```bash
# Use docker-compose for development
docker compose up

# Build multi-platform for testing
PLATFORMS="linux/amd64,linux/arm64" build/docker-build.sh
```

### For End Users

```bash
# Use pre-built images from registry
docker pull ghcr.io/yourusername/multi-modal-rag:latest

# Or use provided distribution package
# (no internet required after download)
```

### For CI/CD

```yaml
# GitHub Actions automatically builds for:
# - linux/amd64
# - linux/arm64
# And pushes to GitHub Container Registry
```

## Troubleshooting

### Image too large

```dockerfile
# Use multi-stage builds (already implemented)
# Remove unnecessary dependencies
# Use .dockerignore
```

### Slow builds

```bash
# Use BuildKit cache
export DOCKER_BUILDKIT=1

# Use GitHub Actions cache
# (already configured in .github/workflows/docker.yml)
```

### GUI not working

```bash
# Linux: Check X11 permissions
xhost +local:docker

# macOS: Restart XQuartz
killall XQuartz
open -a XQuartz

# Windows: Check VcXsrv settings
# Ensure "Disable access control" is checked
```

## Advanced Usage

### Custom Build Arguments

```bash
# Build with specific Python version
docker build --build-arg PYTHON_VERSION=3.13 .

# Build for specific platform only
docker buildx build --platform linux/arm64 .
```

### Multi-Stage Builds

```bash
# Build development image
docker build --target development -t multimodal-rag:dev .

# Build production image
docker build --target production -t multimodal-rag:prod .
```

### Export Binaries from Container

```bash
# Extract built files
docker create --name temp multimodal-rag:latest
docker cp temp:/app/dist ./dist
docker rm temp
```