# src/multi_modal_rag/main.py

"""
Multi-Modal MS Office & Media RAG System
"""

# Import built-in modules
import logging
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext
from typing import Any, List, Literal

# Import third-party modules
from dotenv import load_dotenv

# Import local modules
from config import config
from multi_modal_rag.embedder import get_embedding, init_vertex
from multi_modal_rag.ingestion import process_files
from multi_modal_rag.llm_chain import call_gemini
from multi_modal_rag.vector_store import VectorStore
from utils.logger import get_app_logger

# Validate configuration
config.validate_or_exit()

# Initialize logger
logger: logging.Logger = get_app_logger()


class ChatApplication(tk.Tk):
    """
    GUI application for the Multi-Modal RAG system.
    """

    def __init__(self, vector_store) -> None:
        super().__init__()
        self.vector_store: Any = vector_store

        # Initialize Environment and Vertex AI
        load_dotenv()
        init_vertex()

        self.title(string="Gemini Multi-Modal RAG System")
        self.geometry(newGeometry="800x600")

        self.configure(bg="#2d2d2d")
        self.create_widgets()

        # Attempt to load DB on startup
        self.after(ms=100, func=self.initial_load)

    def create_widgets(self) -> None:
        # Main frame
        main_frame = tk.Frame(master=self, bg="#2d2d2d")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Top frame for buttons
        top_frame = tk.Frame(master=main_frame, bg="#2d2d2d")
        top_frame.pack(fill=tk.X, pady=(0, 10))

        self.load_button = tk.Button(
            master=top_frame,
            text="Load Files",
            command=self.load_files,
            bg="#4a4a4a",
            fg="white",
            relief=tk.FLAT,
        )
        self.load_button.pack(side=tk.LEFT)

        self.status_label = tk.Label(
            master=top_frame, text="Initializing.....", bg="#2d2d2d", fg="lightgrey"
        )
        self.status_label.pack(side=tk.RIGHT)

        # Chat output area
        self.chat_output = scrolledtext.ScrolledText(
            master=main_frame,
            state="disabled",
            wrap=tk.WORD,
            bg="#1e1e1e",
            fg="white",
            font=("Helvetica", 10),
        )
        self.chat_output.pack(fill=tk.BOTH, expand=True)

        # Input frame
        input_frame = tk.Frame(master=main_frame, bg="#2d2d2d")
        input_frame.pack(fill=tk.X, pady=(10, 0))

        self.prompt_input = tk.Text(
            master=input_frame,
            height=3,
            wrap=tk.WORD,
            bg="#4a4a4a",
            fg="white",
            insertbackground="white",
            font=("Helvetica", 10),
        )
        self.prompt_input.pack(fill=tk.X, expand=True, side=tk.LEFT, padx=(0, 10))
        self.prompt_input.bind(sequence="<Return>", func=self.handle_send_event)

        self.send_button = tk.Button(
            master=input_frame,
            text="Send",
            command=self.send_prompt,
            bg="#007acc",
            fg="white",
            relief=tk.FLAT,
        )
        self.send_button.pack(side=tk.RIGHT, fill=tk.Y)

    def initial_load(self) -> None:
        """
        Load existing vector database.
        """
        self.status_label.config(text="Checking for existing database...")
        if self.vector_store.load():
            self.status_label.config(
                text=f"DB Loaded. {len(self.vector_store.metadata)} chunks."
            )
            self.add_message(
                sender="System", message="Existing vector database loaded successfully."
            )
        else:
            self.status_label.config(text="Ready. Load documents to begin.")
            self.add_message(
                sender="System",
                message="Welcome! Please load documents using the 'Load Files' button.",
            )

    def load_files(self) -> None:
        """
        Load files using file dialog.
        """
        documents_dir: str = os.path.join(os.getcwd(), "documents")
        os.makedirs(name=documents_dir, exist_ok=True)

        file_paths: tuple[str, ...] | Literal[""] = filedialog.askopenfilenames(
            title="Select Document Files",
            initialdir=documents_dir,
            filetypes=[
                (
                    "All Supported Files",
                    "*.docx *.xlsx *.pptx *.pdf *.png *.jpg *.jpeg *.mp3 *.wav *.mp4 *.txt",
                ),
                ("Word Documents", "*.docx"),
                ("Excel Spreadsheets", "*.xlsx"),
                ("PowerPoint Presentations", "*.pptx"),
                ("PDF Documents", "*.pdf"),
                ("Images", "*.png *.jpg *.jpeg"),
                ("Audio", "*.mp3 *.wav"),
                ("Video", "*.mp4"),
                ("Text Files", "*.txt"),
            ],
        )
        if not file_paths:
            return

        self.status_label.config(text="Processing files (this may take time)...")
        self.load_button.config(state="disabled")

        # Run processing in background thread
        threading.Thread(
            target=self.process_and_index_files, args=(list(file_paths),)
        ).start()

    def process_and_index_files(self, file_paths) -> None:
        """
        Processes the selected files and indexes them.
        """
        try:
            processed_items: list[dict[str, Any]] = process_files(file_paths=file_paths)

            for item in processed_items:
                # Update status on main thread
                self.after(
                    ms=0,
                    func=lambda name=item["filename"]: self.status_label.config(
                        text=f"Embedding {name}..."
                    ),
                )

                if item["type"] == "media":
                    emb: List[float] | None = get_embedding(item=item)
                    if emb is not None:
                        self.vector_store.add(embedding=emb, metadata=item)

                elif item["type"] == "text_document" and item["content"]:
                    text = item["content"]
                    chunk_size = 1000
                    chunks = [
                        text[i : i + chunk_size]
                        for i in range(0, len(text), chunk_size)
                    ]

                    for i, chunk in enumerate(iterable=chunks):
                        chunk_item = {
                            "type": "text_document",
                            "content": chunk,
                            "path": item["path"],
                            "filename": f"{item['filename']}_part{i + 1}",
                        }
                        emb = get_embedding(item=chunk_item)
                        if emb is not None:
                            self.vector_store.add(embedding=emb, metadata=chunk_item)

            # Success callback
            self.after(0, self.finish_loading, len(file_paths))

        except Exception as e:
            # Error callback
            error_msg = str(e)
            self.after(
                ms=0,
                func=lambda: messagebox.showerror(
                    title="Error", message=f"Failed to load files: {error_msg}"
                ),
            )
            self.after(
                ms=0,
                func=lambda: self.status_label.config(text="Error during loading."),
            )
            self.after(ms=0, func=lambda: self.load_button.config(state="normal"))

    def finish_loading(self, count) -> None:
        """
        Callback when file loading is complete.
        """
        self.status_label.config(
            text=f"Ready. {len(self.vector_store.metadata)} chunks loaded."
        )
        self.add_message(
            sender="System", message=f"Successfully loaded and indexed {count} file(s)."
        )
        self.load_button.config(state="normal")

    def handle_send_event(self, event):
        """
        Handles the Enter key press in the input field.
        """
        # Prevents the default Return key behavior (adding a newline)
        self.send_prompt()
        return "break"

    def send_prompt(self) -> None:
        """
        Sends the user's prompt for processing.
        """
        prompt = self.prompt_input.get("1.0", tk.END).strip()
        if not prompt:
            return

        self.add_message(sender="You", message=prompt)
        self.prompt_input.delete("1.0", tk.END)

        # Disable input while processing
        self.send_button.config(state="disabled")
        self.prompt_input.config(state="disabled")
        self.status_label.config(text="Thinking.....")

        # Run the query and LLM call in a separate thread
        thread = threading.Thread(target=self.process_in_background, args=(prompt,))
        thread.start()

    def process_in_background(self, prompt) -> None:
        """
        Processes the user's prompt in the background.
        """
        query_item = {
            "type": "text_document",
            "content": prompt,
            "path": "query",
            "filename": "query",
        }
        query_emb = get_embedding(query_item)

        results = self.vector_store.search(query_emb, top_k=10)

        # If query mentions media types, include all media files
        if any(
            word in prompt.lower()
            for word in ["video", "audio", "image", "mp4", "mp3", "jpg", "png"]
        ):
            media_items = [
                m for m in self.vector_store.metadata if m.get("type") == "media"
            ]
            results.extend(
                [
                    {"metadata": m}
                    for m in media_items
                    if m not in [r["metadata"] for r in results]
                ]
            )

        response = call_gemini(prompt, results)
        self.after(0, self.display_response, response)

    def display_response(self, response) -> None:
        """
        Displays the LLM response.
        """
        self.add_message("Assistant", response)

        # Re-enable input
        self.send_button.config(state="normal")
        self.prompt_input.config(state="normal")
        self.status_label.config(
            text=f"Ready. {len(self.vector_store.metadata)} chunks loaded."
        )
        self.prompt_input.focus_set()

    def add_message(self, sender, message):
        self.chat_output.config(state="normal")
        self.chat_output.insert(tk.END, f"{sender}:\n{message}\n\n")
        self.chat_output.config(state="disabled")
        self.chat_output.see(tk.END)


def main():
    """Initializes and runs the RAG GUI application."""
    # Create a sample document for testing
    documents_dir: Path = Path(config.DOCUMENTS_DIR)
    documents_dir.mkdir(exist_ok=True)
    with open("documents/sample_document.txt", "w") as f:
        f.write("The first rule of vector databases is persistence.\n\n")
        f.write("The second rule is ensuring your embeddings are consistent.\n\n")
        f.write("Tkinter is a standard GUI toolkit for Python.")

        # Log the creation of the sample document
        logger.info(msg="Sample document created.")

    # Initialize the core components
    store = VectorStore()
    app: ChatApplication = ChatApplication(vector_store=store)
    app.mainloop()


if __name__ == "__main__":
    main()
