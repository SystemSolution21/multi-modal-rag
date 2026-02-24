import json
import os

import numpy as np

DB_DIR = "db"
VECTORS_FILE = os.path.join(DB_DIR, "vectors.npz")
METADATA_FILE = os.path.join(DB_DIR, "metadata.json")


class VectorStore:
    def __init__(self):
        """Initializes the VectorStore, trying to load an existing DB."""
        self.vectors = []
        self.metadata = []
        os.makedirs(DB_DIR, exist_ok=True)

    def load(self):
        """
        Loads the vector database from the /db directory.

        Returns:
            bool: True if loaded successfully, False otherwise.
        """
        if not os.path.exists(VECTORS_FILE) or not os.path.exists(METADATA_FILE):
            print("No existing database found.")
            return False

        try:
            print("Loading existing vector database...")
            data = np.load(VECTORS_FILE)
            self.vectors = data["vectors"].tolist()
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            print("Database loaded successfully.")
            return True
        except Exception as e:
            print(f"Error loading database: {e}")
            # Reset on failure
            self.vectors = []
            self.metadata = []
            return False

    def save(self):
        """Saves the current vector database to the /db directory."""
        if not self.vectors:
            print("Nothing to save.")
            return

        print("Saving vector database...")
        try:
            np.savez_compressed(VECTORS_FILE, vectors=np.array(self.vectors))
            with open(METADATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, indent=4)
            print("Database saved successfully.")
        except Exception as e:
            print(f"Error saving database: {e}")

    def add(self, embedding, metadata):
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
