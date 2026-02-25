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
