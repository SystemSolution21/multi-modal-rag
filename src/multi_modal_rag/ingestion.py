# src/multi_modal_rag/ingestion.py

"""Ingestion module for the Multi-Modal RAG system.
This module provides functions to select and process multimodal files for indexing.
"""

# Import built-in modules
import logging
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Any

# Import third-party modules
from markitdown import MarkItDown

# Import local modules
import config
from utils.logger import get_app_logger

# Initialize logger
logger: logging.Logger = get_app_logger()


def select_files():
    """Opens a native OS file dialog for the user to select multimodal files."""
    root = tk.Tk()
    root.withdraw()  # Hide the main tk window

    # Open in the multi_modal_rag/documents directory if it exists
    initial_dir = Path(config.DOCUMENTS_DIR)
    if not initial_dir.exists():
        initial_dir = str(config.BASE_DIR)

    file_paths = filedialog.askopenfilenames(
        title="Select Documents and Media",
        initialdir=initial_dir,
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
    return list(file_paths)


def process_files(file_paths) -> list[dict[str, Any]]:
    """
    Processes the selected files.
    - Uses MarkItDown for Office and PDF files to extract clean Markdown.
    - Returns media files (images, audio, video) as-is for native Processing.

    Returns a list of dictionaries containing file metadata and extracted content (if any).
    """
    md = MarkItDown()
    processed_items = []

    office_pdf_exts = {".docx", ".xlsx", ".pptx", ".pdf", ".txt"}
    media_exts = {".png", ".jpg", ".jpeg", ".mp3", ".wav", ".mp4"}

    for path in file_paths:
        ext = os.path.splitext(path)[1].lower()

        file_item = {
            "path": path,
            "filename": os.path.basename(path),
            "type": "unknown",
            "content": None,
        }

        if ext in office_pdf_exts:
            try:
                logger.info(
                    msg=f"Extracting text from {file_item['filename']} via MarkItDown....."
                )
                result = md.convert(path)
                file_item["content"] = result.text_content
                file_item["type"] = "text_document"
                processed_items.append(file_item)
            except Exception as e:
                logger.error(msg=f"Error extracting {path}: {e}")

        elif ext in media_exts:
            file_item["type"] = "media"
            # We don't extract content for media, the GenAI API will handle the file directly
            processed_items.append(file_item)

        else:
            logger.warning(
                msg=f"Skipping unsupported file type: {file_item['filename']}"
            )

    return processed_items


if __name__ == "__main__":
    logger.info("Please select files...")
    files = select_files()
    logger.info(f"Selected {len(files)} files.")

    items = process_files(files)
    for item in items:
        if item["type"] == "text_document":
            preview = (
                item["content"][:100].replace("\n", " ") if item["content"] else "None"
            )
            logger.info(f"- [Text] {item['filename']}: {preview}...")
        else:
            logger.info(f"- [Media] {item['filename']}")
