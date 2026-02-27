# Multi-Modal RAG System - Developer Reference

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Application Workflow](#application-workflow)
3. [Module Reference](#module-reference)
4. [Function Reference](#function-reference)
5. [Data Flow](#data-flow)
6. [Configuration](#configuration)

---

## Architecture Overview

The Multi-Modal RAG (Retrieval-Augmented Generation) system is built with the following components:

```flowchart
┌─────────────────────────────────────────────────────────────┐
│                     GUI Layer (Tkinter)                      │
│                    main.py: ChatApplication                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
┌──────────────┐ ┌──────────┐ ┌─────────────┐
│  Ingestion   │ │ Embedder │ │ Vector Store│
│ ingestion.py │ │embedder.py│ │vector_store.py│
└──────────────┘ └──────────┘ └─────────────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
              ┌────────────────┐
              │   LLM Chain    │
              │ llm_chain.py   │
              └────────────────┘
                       │
                       ▼
              ┌────────────────┐
              │  Gemini 2.5    │
              │     Flash      │
              └────────────────┘
```

---

## Application Workflow

### 1. **Application Startup**

**Entry Point:** `main.py::main()`

```python
def main():
    """Initializes and runs the RAG GUI application."""
```

**Steps:**

1. Creates sample document in `documents/sample_document.txt`
2. Initializes `VectorStore()` instance
3. Creates `ChatApplication(vector_store=store)` GUI
4. Calls `app.mainloop()` to start the event loop

**Modules Involved:**

- `main.py`
- `vector_store.py`
- `config.py`
- `utils/logger.py`

---

### 2. **Database Initialization**

**Function:** `ChatApplication.__init__()` → `initial_load()`

```python
def initial_load(self) -> None:
    """Load existing vector database."""
```

**Steps:**

1. Checks for existing database in `db/` directory
2. Calls `vector_store.load()` to load `vectors.npz` and `metadata.json`
3. Updates UI status with chunk count
4. Displays welcome message

**Modules Involved:**

- `main.py::ChatApplication.initial_load()`
- `vector_store.py::VectorStore.load()`

---

### 3. **File Loading Workflow**

**Trigger:** User clicks "Load Files" button

**Function:** `ChatApplication.load_files()`

```python
def load_files(self) -> None:
    """Load files using file dialog."""
```

**Steps:**

#### 3.1 File Selection

1. Opens file dialog with supported formats:
   - Office: `.docx`, `.xlsx`, `.pptx`
   - Documents: `.pdf`, `.txt`
   - Images: `.png`, `.jpg`, `.jpeg`
   - Audio: `.mp3`, `.wav`
   - Video: `.mp4`
2. User selects one or more files
3. Spawns background thread for processing

#### 3.2 File Processing

**Function:** `process_and_index_files(file_paths)`

```python
def process_and_index_files(self, file_paths) -> None:
    """Processes the selected files and indexes them."""
```

**Calls:** `ingestion.py::process_files(file_paths)`

```python
def process_files(file_paths) -> list[dict[str, Any]]:
    """
    Processes the selected files.
    - Uses MarkItDown for Office and PDF files
    - Returns media files as-is for native processing
    """
```

**Processing Logic:**

**For Office/PDF/Text files** (`.docx`, `.xlsx`, `.pptx`, `.pdf`, `.txt`):

1. Uses `MarkItDown` library to extract text content
2. Returns item with:

   ```python
   {
       "type": "text_document",
       "content": "extracted text...",
       "path": "/full/path/to/file.pdf",
       "filename": "file.pdf",
       "original_filename": "file.pdf"
   }
   ```

**For Media files** (`.png`, `.jpg`, `.mp3`, `.wav`, `.mp4`):

1. Returns item as-is (no content extraction):

   ```python
   {
       "type": "media",
       "content": None,
       "path": "/full/path/to/image.png",
       "filename": "image.png"
   }
   ```

#### 3.3 Text Chunking

**Location:** `main.py::process_and_index_files()`

For text documents with content:

```python
chunk_size = 700  # Conservative limit for multi-byte characters
chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]
```

Each chunk becomes:

```python
chunk_item = {
    "type": "text_document",
    "content": chunk,
    "path": item["path"],
    "filename": item["filename"],  # Original filename preserved
    "original_filename": item["filename"],
    "chunk_index": i + 1,
    "total_chunks": len(chunks)
}
```

#### 3.4 Embedding Generation

**Function:** `embedder.py::get_embedding(item)`

```python
def get_embedding(item):
    """
    Returns a 1408-dimensional embedding.
    Supports text, images, video, and audio (via transcription).
    """
```

**For Text Documents:**

```python
# Limit by bytes (not characters) for multi-byte support
max_bytes = 900  # Stay under 1024 byte limit
encoded = text.encode('utf-8')[:max_bytes]
text = encoded.decode('utf-8', errors='ignore')

embeddings = model.get_embeddings(contextual_text=text)
return embeddings.text_embedding  # 1408-dim vector
```

**For Images:**

```python
image = Image.load_from_file(item["path"])
embeddings = model.get_embeddings(image=image)
return embeddings.image_embedding
```

**For Video:**

```python
video = Video.load_from_file(item["path"])
embeddings = model.get_embeddings(video=video)
return embeddings.video_embeddings[0]
```

**For Audio:**

```python
# Step 1: Transcribe audio using Google Speech-to-Text
transcript = transcribe_audio(item["path"])

# Step 2: Embed the transcript as text
embeddings = model.get_embeddings(contextual_text=transcript)
return embeddings.text_embedding
```

**Audio Transcription Function:**

```python
def transcribe_audio(file_path: str) -> str | None:
    """Transcribes audio file using Google Cloud Speech-to-Text API."""
    client = speech_v1.SpeechClient()
    
    with open(file_path, "rb") as audio_file:
        content = audio_file.read()
    
    audio = speech_v1.RecognitionAudio(content=content)
    config = speech_v1.RecognitionConfig(
        encoding=speech_v1.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code="en-US",
    )
    
    response = client.recognize(config=config, audio=audio)
    transcript = "".join([result.alternatives[0].transcript for result in response.results])
    return transcript
```

#### 3.5 Vector Storage

**Function:** `vector_store.py::VectorStore.add(embedding, metadata)`

```python
def add(self, embedding: List[float], metadata: dict) -> None:
    """Add a new embedding and its metadata to the store."""
    self.embeddings.append(embedding)
    self.metadata.append(metadata)
    self.save()  # Auto-save after each addition
```

**Storage Format:**

- `db/vectors.npz`: NumPy array of embeddings (shape: [N, 1408])
- `db/metadata.json`: List of metadata dictionaries

#### 3.6 Completion

**Function:** `finish_loading(count)`

```python
def finish_loading(self, count) -> None:
    """Callback when file loading is complete."""
    self.status_label.config(text=f"Ready. {len(self.vector_store.metadata)} chunks loaded.")
    self.add_message(sender="System", message=f"Successfully loaded and indexed {count} file(s).")
```

**Modules Involved:**

- `main.py::ChatApplication`
- `ingestion.py::process_files()`
- `embedder.py::get_embedding()`, `transcribe_audio()`
- `vector_store.py::VectorStore.add()`, `VectorStore.save()`

---

### 4. **Query Processing Workflow**

**Trigger:** User types a question and presses Enter or clicks "Send"

**Function:** `ChatApplication.send_prompt()`

```python
def send_prompt(self) -> None:
    """Sends the user's prompt for processing."""
```

**Steps:**

#### 4.1 Input Handling

1. Extracts prompt from text input
2. Displays user message in chat
3. Disables input during processing
4. Spawns background thread

#### 4.2 Hybrid Search

**Function:** `process_in_background(prompt)`

```python
def process_in_background(self, prompt) -> None:
    """
    Processes the user's prompt in the background.
    Uses hybrid search: keyword matching + semantic search.
    """
```

**Search Strategy (3-tier fallback):**

- **Tier 1: Explicit Filename Matching**

```python
mentioned_files = [
    m for m in self.vector_store.metadata
    if m.get("filename", "").lower() in prompt.lower()
    or Path(m.get("path", "")).stem.lower() in prompt.lower()
]
if mentioned_files:
    results = [{"metadata": m, "score": 1.0} for m in mentioned_files]
```

- **Tier 2: Media Type Keywords**

```python
media_keywords = {
    "audio": [".mp3", ".wav"],
    "video": [".mp4"],
    "image": [".jpg", ".jpeg", ".png"],
}

for keyword, exts in media_keywords.items():
    if keyword in prompt.lower():
        results = [
            {"metadata": m, "score": 1.0}
            for m in self.vector_store.metadata
            if m.get("type") == "media" and any(m.get("path", "").endswith(e) for e in exts)
        ]
        break
```

- **Tier 3: Semantic Search (Fallback)**

```python
query_item = {
    "type": "text_document",
    "content": prompt,
    "path": "query",
    "filename": "query",
}
query_emb = get_embedding(query_item)
results = self.vector_store.search(query_emb, top_k=config.VERTEX_AI_TOP_K)
```

#### 4.3 Vector Search

**Function:** `vector_store.py::VectorStore.search(query_embedding, top_k)`

```python
def search(self, query_embedding: List[float], top_k: int = 5) -> List[dict]:
    """Search for similar embeddings using cosine similarity."""
```

**Algorithm:**

```python
# Convert to numpy arrays
query_vec = np.array(query_embedding).reshape(1, -1)
all_vecs = np.array(self.embeddings)

# Normalize vectors
query_norm = query_vec / np.linalg.norm(query_vec)
all_norms = all_vecs / np.linalg.norm(all_vecs, axis=1, keepdims=True)

# Compute cosine similarity
similarities = np.dot(all_norms, query_norm.T).flatten()

# Get top-k indices
top_indices = np.argsort(similarities)[::-1][:top_k]

# Return results with metadata
results = [
    {"metadata": self.metadata[i], "score": float(similarities[i])}
    for i in top_indices
]
```

#### 4.4 Deduplication

```python
seen_paths = set()
unique_results = []
for r in results:
    path = r["metadata"].get("path")
    if path not in seen_paths:
        seen_paths.add(path)
        unique_results.append(r)
```

#### 4.5 LLM Call

**Function:** `llm_chain.py::call_gemini(query, context_items)`

```python
def call_gemini(query, context_items):
    """
    Calls Gemini 2.5 Flash with the user's text query and retrieved context.
    """
```

**Prompt Construction:**

```python
prompt_parts = [
    "You are an intelligent Assistant with access to a multimodal database.",
    "Below is context retrieved from various files.",
    "Use this context to answer the user's query.",
    "--- CONTEXT START ---",
]

for i, item in enumerate(context_items):
    meta = item["metadata"]
    prompt_parts.append(f"\n[Source {i + 1}: {meta['filename']} - Type: {meta['type']}]")
    
    if meta["type"] == "text_document":
        prompt_parts.append(f"Content: {meta['content'][:500]}...")
    elif meta["type"] == "media":
        # Upload file to Gemini for native processing
        uploaded_file = genai.upload_file(path=meta["path"])
        prompt_parts.append(uploaded_file)

prompt_parts.append("--- CONTEXT END ---")
prompt_parts.append(f"\nUser Query: {query}")
```

**API Call:**

```python
client = genai.Client(api_key=config.GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents=prompt_parts
)
return response.text
```

#### 4.6 Response Display

**Function:** `display_response(response)`

```python
def display_response(self, response) -> None:
    """Displays the LLM response."""
    self.add_message("Assistant", response)
    self.send_button.config(state="normal")
    self.prompt_input.config(state="normal")
```

**Modules Involved:**

- `main.py::ChatApplication`
- `embedder.py::get_embedding()`
- `vector_store.py::VectorStore.search()`
- `llm_chain.py::call_gemini()`

---

### 5. **Application Shutdown**

**Trigger:** User closes window or presses Ctrl+C

#### 5.1 GUI Close

**Function:** `ChatApplication.on_closing()`

```python
def on_closing(self) -> None:
    """Handle application shutdown."""
    logger.info(msg="Application closing. Saving vector database...")
    self.vector_store.save()
    logger.info(msg="Application closed successfully.")
    self.destroy()
```

#### 5.2 Keyboard Interrupt

**Function:** `main()` exception handler

```python
except KeyboardInterrupt:
    logger.info(msg="Keyboard interrupt received. Shutting down...")
    if store is not None:
        store.save()
    logger.info(msg="Application terminated by user.")
```

**Modules Involved:**

- `main.py`
- `vector_store.py::VectorStore.save()`

---

## Module Reference

### `main.py`

**Purpose:** GUI application and orchestration

**Key Classes:**

- `ChatApplication(tk.Tk)`: Main GUI window

**Key Methods:**

- `__init__(vector_store)`: Initialize GUI
- `initial_load()`: Load existing database
- `load_files()`: File selection dialog
- `process_and_index_files(file_paths)`: Background file processing
- `send_prompt()`: Handle user query
- `process_in_background(prompt)`: Hybrid search + LLM call
- `on_closing()`: Cleanup on exit

---

### `ingestion.py`

**Purpose:** File processing and text extraction

**Key Functions:**

- `process_files(file_paths) -> list[dict]`: Extract content from files using MarkItDown

**Supported Formats:**

- Office: `.docx`, `.xlsx`, `.pptx` (via MarkItDown)
- Documents: `.pdf`, `.txt` (via MarkItDown)
- Media: `.png`, `.jpg`, `.jpeg`, `.mp3`, `.wav`, `.mp4` (pass-through)

---

### `embedder.py`

**Purpose:** Generate embeddings for multimodal data

**Key Functions:**

- `init_vertex()`: Initialize Vertex AI
- `get_embedding(item) -> List[float]`: Generate 1408-dim embedding
- `transcribe_audio(file_path) -> str`: Audio-to-text transcription

**Embedding Model:** `multimodalembedding@001` (Vertex AI)

**Constraints:**

- Text: Max 900 bytes (UTF-8 encoded)
- Images: Supported formats (PNG, JPG, JPEG)
- Video: MP4 format
- Audio: Transcribed to text first

---

### `vector_store.py`

**Purpose:** In-memory vector database with persistence

**Key Class:**

- `VectorStore`: Manages embeddings and metadata

**Key Methods:**

- `add(embedding, metadata)`: Add new vector
- `search(query_embedding, top_k) -> List[dict]`: Cosine similarity search
- `save()`: Persist to `db/vectors.npz` and `db/metadata.json`
- `load() -> bool`: Load from disk

**Storage:**

- `db/vectors.npz`: NumPy array (N × 1408)
- `db/metadata.json`: JSON array of metadata dicts

---

### `llm_chain.py`

**Purpose:** Interface with Gemini 2.5 Flash

**Key Functions:**

- `call_gemini(query, context_items) -> str`: Generate response

**Model:** `gemini-2.0-flash-exp` (via Google GenAI SDK)

**Features:**

- Multimodal input (text + images/video/audio)
- File upload for native media processing
- Context-aware responses

---

### `config.py`

**Purpose:** Configuration management

**Key Settings:**

- `GOOGLE_CLOUD_PROJECT`: GCP project ID
- `GEMINI_API_KEY`: API key for Gemini
- `VERTEX_AI_MODEL`: Embedding model name
- `VERTEX_AI_TOP_K`: Number of search results
- `DOCUMENTS_DIR`: Document storage path
- `DB_DIR`: Vector database path

---

### `utils/logger.py`

**Purpose:** Logging configuration

**Key Functions:**

- `setup_logger(name, log_file) -> logging.Logger`: Configure logger
- `get_app_logger() -> logging.Logger`: Get main app logger

**Log Files:**

- `logs/app.log`: Application logs

---

## Function Reference

### Embedding Functions

#### `get_embedding(item) -> List[float] | None`

**Location:** `embedder.py`

**Parameters:**

- `item`: Dict with keys `type`, `content`, `path`, `filename`

**Returns:**

- 1408-dimensional embedding vector or `None` on error

**Logic:**

```python
if item["type"] == "text_document":
    # Byte-safe truncation for multi-byte characters
    max_bytes = 900
    encoded = text.encode('utf-8')[:max_bytes]
    text = encoded.decode('utf-8', errors='ignore')
    embeddings = model.get_embeddings(contextual_text=text)
    return embeddings.text_embedding

elif item["type"] == "media":
    ext = Path(item["path"]).suffix.lower()
    
    if ext in {".png", ".jpg", ".jpeg"}:
        image = Image.load_from_file(item["path"])
        embeddings = model.get_embeddings(image=image)
        return embeddings.image_embedding
    
    elif ext == ".mp4":
        video = Video.load_from_file(item["path"])
        embeddings = model.get_embeddings(video=video)
        return embeddings.video_embeddings[0]
    
    elif ext in {".mp3", ".wav"}:
        transcript = transcribe_audio(item["path"])
        embeddings = model.get_embeddings(contextual_text=transcript)
        return embeddings.text_embedding
```

---

#### `transcribe_audio(file_path) -> str | None`

**Location:** `embedder.py`

**Parameters:**

- `file_path`: Path to audio file

**Returns:**

- Transcribed text or `None` on error

**Uses:** Google Cloud Speech-to-Text API

---

### Vector Store Functions

#### `VectorStore.add(embedding, metadata) -> None`

**Location:** `vector_store.py`

**Parameters:**

- `embedding`: 1408-dim vector
- `metadata`: Dict with file information

**Side Effects:**

- Appends to `self.embeddings` and `self.metadata`
- Calls `self.save()` to persist

---

#### `VectorStore.search(query_embedding, top_k) -> List[dict]`

**Location:** `vector_store.py`

**Parameters:**

- `query_embedding`: 1408-dim query vector
- `top_k`: Number of results (default: 5)

**Returns:**

```python
[
    {
        "metadata": {...},
        "score": 0.95  # Cosine similarity
    },
    ...
]
```

**Algorithm:** Cosine similarity with L2 normalization

---

#### `VectorStore.save() -> None`

**Location:** `vector_store.py`

**Side Effects:**

- Writes `db/vectors.npz` (NumPy compressed)
- Writes `db/metadata.json` (JSON)

---

#### `VectorStore.load() -> bool`

**Location:** `vector_store.py`

**Returns:**

- `True` if database loaded successfully
- `False` if no database found

**Side Effects:**

- Populates `self.embeddings` and `self.metadata`

---

### LLM Functions

#### `call_gemini(query, context_items) -> str`

**Location:** `llm_chain.py`

**Parameters:**

- `query`: User's question (string)
- `context_items`: List of search results with metadata

**Returns:**

- Generated response text

**Process:**

1. Constructs multimodal prompt
2. Uploads media files to Gemini
3. Calls `gemini-2.0-flash-exp` model
4. Returns response text

---

## Data Flow

### File Upload Flow

```file-upload-flow
User selects files
    ↓
load_files() → filedialog
    ↓
process_and_index_files() [background thread]
    ↓
process_files() → MarkItDown extraction
    ↓
Text chunking (700 chars)
    ↓
For each chunk:
    get_embedding() → Vertex AI
    ↓
    VectorStore.add() → Save to db/
    ↓
finish_loading() → Update UI
```

### Query Flow

```query-flow
User enters query
    ↓
send_prompt() → Extract text
    ↓
process_in_background() [background thread]
    ↓
Hybrid Search:
    1. Filename matching
    2. Media type keywords
    3. Semantic search (get_embedding + VectorStore.search)
    ↓
Deduplication
    ↓
call_gemini() → Gemini 2.5 Flash
    ↓
display_response() → Show in chat
```

---

## Configuration

### Environment Variables (`.env`)

```env
GOOGLE_CLOUD_PROJECT=your-project-id
GEMINI_API_KEY=your-api-key
```

### Config Constants (`config.py`)

```python
VERTEX_AI_MODEL = "multimodalembedding@001"
VERTEX_AI_TOP_K = 5
DOCUMENTS_DIR = "documents"
DB_DIR = "db"
```

### Chunk Size Limits

- **Text chunks:** 700 characters (conservative for multi-byte)
- **Embedding input:** 900 bytes (UTF-8 encoded)
- **Vertex AI limit:** 1024 bytes

---

## Error Handling

### Common Errors

- **1. "Text field must be smaller than 1024 characters"**

  - **Cause:** Multi-byte characters (Japanese, Chinese, etc.) exceed byte limit
  - **Solution:** Byte-safe truncation in `get_embedding()`

- **2. "No existing database found"**

  - **Cause:** First run or deleted `db/` directory
  - **Solution:** Load files to create database

- **3. File processing errors**

- **Logged in:** `logs/app.log`
- **Handled by:** Try-except in `process_and_index_files()`

---

## Performance Considerations

### Embedding Generation

- **Text:** ~1-2 seconds per chunk
- **Images:** ~2-3 seconds per image
- **Audio:** ~5-10 seconds (transcription + embedding)
- **Video:** ~10-15 seconds

### Search Performance

- **Vector search:** O(N) cosine similarity (N = number of chunks)
- **Optimized with:** NumPy vectorization
- **Typical latency:** <100ms for 1000 chunks

### Database Size

- **Embeddings:** ~5.6 KB per chunk (1408 floats × 4 bytes)
- **Metadata:** ~200-500 bytes per chunk (JSON)
- **Example:** 1000 chunks ≈ 6 MB total

---

## Development Tips

### Adding New File Types

1. Update `office_pdf_exts` or `media_exts` in `ingestion.py`
2. Add extraction logic in `process_files()`
3. Update `get_embedding()` if special handling needed

### Debugging

- Check `logs/app.log` for detailed logs
- Enable debug logging: `logger.setLevel(logging.DEBUG)`
- Print search results: Already logged in `process_in_background()`

### Testing

- Use `documents/sample_document.txt` for basic tests
- Test multi-byte characters with Japanese/Chinese PDFs
- Test media files with small samples first

---

## API Dependencies

### Google Cloud APIs

- **Vertex AI:** Multimodal embeddings
- **Speech-to-Text:** Audio transcription
- **Gemini API:** LLM responses

### Python Libraries

- `google-cloud-aiplatform`: Vertex AI SDK
- `google-cloud-speech`: Speech-to-Text
- `google-genai`: Gemini SDK
- `markitdown`: Document extraction
- `numpy`: Vector operations
- `tkinter`: GUI framework

---

## License

MIT License - See `LICENSE.txt`

---

**Last Updated:** 2026-02-27  
**Version:** 0.1.0
