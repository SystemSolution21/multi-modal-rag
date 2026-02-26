# src/multi_modal_rag/vector_store.py

"""Vector store module for the Multi-Modal RAG system.
This module provides a simple in-memory vector store for storing and searching embeddings.
It uses Numpy for fast vector operations and JSON for metadata storage.
The vector store is persisted to the /db directory as vectors.npz and metadata.json.
"""

# Import built-in modules
import json
import logging
from pathlib import Path
from typing import Any

# Import third-party modules
import numpy as np

# Import local modules
from config import config
from utils.logger import get_app_logger

# Initialize logger
logger: logging.Logger = get_app_logger()

# Vector store constants

DB_DIR: Path = config.DB_DIR
VECTORS_FILE: Path = Path(DB_DIR / "vectors.npz")
METADATA_FILE: Path = Path(DB_DIR / "metadata.json")


class VectorStore:
    def __init__(self) -> None:
        """Initializes the VectorStore, trying to load an existing DB."""
        self.vectors = []
        self.metadata = []
        DB_DIR.mkdir(exist_ok=True)

    def load(self):
        """
        Loads the vector database from the /db directory.

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        # Check if database files exist
        if not VECTORS_FILE.exists() or not METADATA_FILE.exists():
            logger.error(msg="No existing database found.")
            return False

        try:
            logger.info(msg="Loading existing vector database.....")
            data: Any = np.load(file=VECTORS_FILE)
            self.vectors = data["vectors"].tolist()
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            logger.info(msg="Database loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            # Reset on failure
            self.vectors = []
            self.metadata = []
            return False

    def save(self):
        """Saves the current vector database to the /db directory."""
        if not self.vectors:
            logger.warning(msg="Nothing to save.")
            return

        logger.info(msg="Saving vector database.....")
        try:
            np.savez_compressed(VECTORS_FILE, vectors=np.array(self.vectors))
            with open(METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=4)
            logger.info(msg="Database saved successfully.")
        except Exception as e:
            logger.error(f"Error saving database: {e}")

    def add(self, embedding, metadata) -> None:
        """
        Adds a single embedded vector and its related metadata.
        """
        if embedding is None:
            return

        # Ensure it's a list for JSON/Numpy compatibility
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()

        self.vectors.append(embedding)
        self.metadata.append(metadata)
        self.save()

    def search(self, query_embedding, top_k=3):
        """
        Performs Cosine Similarity search over the stored vectors.
        """
        if not self.vectors or query_embedding is None:
            return []

        # Convert to numpy arrays for fast calculation
        query_vec = np.array(query_embedding)
        db_vecs = np.array(self.vectors)

        # Normalize the vectors
        db_vecs_norm = np.linalg.norm(db_vecs, axis=1, keepdims=True)
        query_vec_norm = np.linalg.norm(query_vec)

        # Avoid division by zero
        db_vecs_norm[db_vecs_norm == 0] = 1.0
        if query_vec_norm == 0:
            query_vec_norm = 1.0

        # Cosine similarity calculation
        db_vecs_normalized = db_vecs / db_vecs_norm
        query_vec_normalized = query_vec / query_vec_norm

        similarities = np.dot(db_vecs_normalized, query_vec_normalized)

        # Get the top k indices
        top_k_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_k_indices:
            results.append(
                {"score": float(similarities[idx]), "metadata": self.metadata[idx]}
            )

        return results
