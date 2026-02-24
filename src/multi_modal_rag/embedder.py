import os

import vertexai
from google.cloud import speech_v1
from vertexai.vision_models import Image, MultiModalEmbeddingModel, Video


def init_vertex():
    """Initializes Vertex AI. Requires GOOGLE_CLOUD_PROJECT in environment."""
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")

    if not project_id:
        print(
            "WARNING: GOOGLE_CLOUD_PROJECT environment variable not set. Vertex AI may fail to authenticate."
        )

    vertexai.init(project=project_id, location=location)


def transcribe_audio(file_path):
    """Transcribe audio file to text using Google Cloud Speech-to-Text."""
    try:
        client = speech_v1.SpeechClient()

        with open(file_path, "rb") as audio_file:
            content = audio_file.read()

        audio = speech_v1.RecognitionAudio(content=content)

        # Determine encoding based on file extension
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".wav":
            encoding = speech_v1.RecognitionConfig.AudioEncoding.LINEAR16
        elif ext == ".mp3":
            encoding = speech_v1.RecognitionConfig.AudioEncoding.MP3
        else:
            encoding = speech_v1.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED

        config = speech_v1.RecognitionConfig(
            encoding=encoding,
            language_code="en-US",
        )

        response = client.recognize(config=config, audio=audio)

        # Extract transcript from response
        transcript = ""
        for result in response.results:
            transcript += result.alternatives[0].transcript

        return transcript if transcript else None
    except Exception as e:
        print(f"Error transcribing audio {file_path}: {e}")
        return None


def get_embedding(item):
    """
    Takes a processed item from ingestion.py and returns a 1408-dimensional embedding.
    Supports text, images, video, and audio (via transcription).
    """
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")

    if item["type"] == "text_document" and item["content"]:
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
            embeddings = model.get_embeddings(video=video)
            if embeddings.video_embeddings:
                return embeddings.video_embeddings[0].embedding
            else:
                return None

        elif ext in {".mp3", ".wav"}:
            # Transcribe audio to text, then embed
            print(f"Transcribing audio file: {item['path']}")
            transcript = transcribe_audio(item["path"])

            if transcript:
                embeddings = model.get_embeddings(contextual_text=transcript)
                if embeddings.text_embedding:
                    return embeddings.text_embedding
                else:
                    return None
            else:
                print(f"Could not transcribe audio: {item['path']}")
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
