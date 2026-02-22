import os

import vertexai
from vertexai.vision_models import Image, MultiModalEmbeddingModel, Video


def init_vertex():
    """Initializes Vertex AI. Requires GOOGLE_CLOUD_PROJECT in environment."""
    # Ensure you have run `gcloud auth application-default login` or set GOOGLE_APPLICATION_CREDENTIALS
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    if not project_id:
        print(
            "WARNING: GOOGLE_CLOUD_PROJECT environment variable not set. Vertex AI may fail to authenticate."
        )

    vertexai.init(project=project_id, location=location)


def get_embedding(item):
    """
    Takes a processed item from ingestion.py and returns a 1408-dimensional embedding.
    """
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")

    if item["type"] == "text_document" and item["content"]:
        # The model accepts text up to around 32k tokens, but it's best to chunk.
        # For this demo, we'll embed the first 30,000 characters if it's too long.
        text = item["content"][:30000]
        embeddings = model.get_embeddings(contextual_text=text)
        if embeddings.text_embedding:
            return embeddings.text_embedding
        else:
            return None

    elif item["type"] == "media":
        ext = os.path.splitext(item["path"])[1].lower()
        if ext in {".png", ".jpg", ".jpeg"}:
            img = Image.load_from_file(item["path"])
            embeddings = model.get_embeddings(image=img)
            if embeddings.image_embedding:
                return embeddings.image_embedding
            else:
                return None

        elif ext == ".mp4":
            video = Video.load_from_file(item["path"])
            # Get embedding for the first 120 seconds of the video as an example
            embeddings = model.get_embeddings(video=video)
            if embeddings.video_embeddings:
                return embeddings.video_embeddings[0].embedding
            else:
                return None
        else:
            print(f"Unsupported media type for embeddings: {ext}")
            return None

    return None


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    init_vertex()
    print("Embedder module ready.")
