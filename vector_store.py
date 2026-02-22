import json
import os

import numpy as np


class SimpleVectorStore:
    def __init__(self, filename="vector_db.npz", meta_filename="vector_meta.json"):
        self.filename = filename
        self.meta_filename = meta_filename
        self.vectors = []
        self.metadata = []
        self._load()

    def _load(self):
        if os.path.exists(self.filename) and os.path.exists(self.meta_filename):
            data = np.load(self.filename)
            self.vectors = data["vectors"].tolist()
            with open(self.meta_filename, "r") as f:
                self.metadata = json.load(f)

    def _save(self):
        if self.vectors:
            np.savez(self.filename, vectors=np.array(self.vectors))
            with open(self.meta_filename, "w") as f:
                json.dump(self.metadata, f, indent=4)

    def add(self, embedding, metadata):
        """Adds a single embedded vector and its related metadata."""
        if embedding is None:
            return
        # Ensure it's a list for JSON compatibility
        if isinstance(embedding, np.ndarray):
            embedding = embedding.tolist()

        self.vectors.append(embedding)
        self.metadata.append(metadata)
        self._save()

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

    def clear(self):
        """Delete local DB"""
        self.vectors = []
        self.metadata = []
        if os.path.exists(self.filename):
            os.remove(self.filename)
        if os.path.exists(self.meta_filename):
            os.remove(self.meta_filename)


if __name__ == "__main__":
    print("Initializing local numpy DB...")
    store = SimpleVectorStore()
    store.clear()
    print("Local database cleared.")
