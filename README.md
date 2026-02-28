# Multi-Modal RAG System for MS Office & Media

This is a simple a multi-modal RAG system that can handle MS Office documents, PDFs, images, audio, and video. It uses Google Vertex AI for embeddings and Google Gemini 2.5 Flash for LLMs.

```multi-modal-rag/
├── db/
│   └── (empty, will be auto-populated)
├── documents/
│   └── sample_document.txt
│
├── src/
|   └── multi_modal_rag/
|        ├── __init__.py
|        ├── embedder.py
|        ├── ingestion.py
|        ├── llm_interface.py
|        ├── main.py
|        └── vector_store.py
|
├── .env.example
├── .gitignore
├── .python-version
├── LICENSE.txt
├── pyproject.toml
├── README.md
└── uv.lock
```

## Prerequisites

- Python 3.13
- Google Cloud Platform account with Vertex AI and Gemini 2.5 Flash enabled
- `gcloud` CLI installed and authenticated
- `uv` package manager installed (`pip install uv`)

## Usage

1. Clone this repo and `cd multi-modal-rag` into it.
2. Run `uv sync` to install dependencies into virtual environment `.venv` from `pyproject.toml`.
3. Replace the name `.env.example` to `.env` file in the root of the project and add your Google Cloud project ID and Gemini API key:

   ```.env
   GOOGLE_CLOUD_PROJECT=your-project-id
   GEMINI_API_KEY=your-api-key
   ```

4. Run `gcloud config set project <your-project-id>` to set your Google Cloud project.
5. Run `gcloud services enable speech.googleapis.com` to enable the Speech API.
6. Run `uv run multi-modal-rag` to start the application.

## Distribution Options

### 1. Native Executables (PyInstaller)

- ✅ No dependencies required
- ✅ Fast startup
- ⚠️ Must build on each platform
- 📦 ~150-200MB per platform

**Build:** See [BUILD.md](BUILD.md)

### 2. Docker (Recommended for Cross-Platform)

- ✅ True cross-platform (one image for all)
- ✅ Consistent environment
- ✅ Easy updates
- ⚠️ Requires Docker
- 📦 ~500MB compressed

**Build:** See [DOCKER.md](DOCKER.md)

### 3. Python Package (For Developers)

- ✅ Smallest size
- ✅ Easy to modify
- ⚠️ Requires Python 3.13+
- 📦 ~50MB

**Install:** `uv sync && uv run multi-modal-rag`

## Quick Start

### Docker (All Platforms)

```bash
# Pull and run
docker pull ghcr.io/yourusername/multi-modal-rag:latest
docker run -it --rm -v $(pwd)/.env:/app/.env multimodal-rag:latest

# Or use docker-compose
docker compose up
```

### Native Executable

```bash
# Download from releases
# Extract and run:

# Windows
MultiModalRAG.exe

# macOS
open MultiModalRAG.app

# Linux
./MultiModalRAG
```

### Python Development

```bash
uv sync
uv run multi-modal-rag
```

## Documentation

- [BUILD.md](BUILD.md) - Build native executables
- [DOCKER.md](DOCKER.md) - Docker distribution guide
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

## Supported Platforms

| Platform | Docker | Native Exe | Python |
|----------|--------|------------|--------|
| Windows 10/11 | ✅ | ✅ | ✅ |
| macOS (Intel) | ✅ | ✅ | ✅ |
| macOS (Apple Silicon) | ✅ | ✅ | ✅ |
| Linux (x86_64) | ✅ | ✅ | ✅ |
| Linux (ARM64) | ✅ | ⚠️ | ✅ |
