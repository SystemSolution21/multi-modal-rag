# src/multi_modal_rag/embedder.py

"""Embedder module for the Multi-Modal RAG system.
This module provides functions to generate embeddings for multimodal data using Vertex AI.
"""

# Import built-in modules
import os
from pathlib import Path

# Import third-party modules
import vertexai
from google.cloud import speech_v1
from vertexai.vision_models import Image, MultiModalEmbeddingModel, Video

# Import local modules
from config import config
from utils.logger import get_app_logger

# Initialize logger
logger = get_app_logger()


def init_vertex():
    """Initializes Vertex AI. Requires GOOGLE_CLOUD_PROJECT in environment."""
    project_id = config.GOOGLE_CLOUD_PROJECT
    location = config.GOOGLE_CLOUD_LOCATION

    if not project_id:
        logger.warning(
            msg="WARNING: GOOGLE_CLOUD_PROJECT environment variable not set. Vertex AI may fail to authenticate."
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
        logger.error(msg=f"Error transcribing audio {Path(file_path).name}: {e}")
        return None


def get_embedding(item):
    """
    Takes a processed item from ingestion.py and returns a 1408-dimensional embedding.
    Supports text, images, video, and audio (via transcription).
    """
    model = MultiModalEmbeddingModel.from_pretrained("multimodalembedding@001")

    if item["type"] == "text_document" and item["content"]:
        logger.info(f"Embedding file: {item['filename']} .....")
        text = item["content"][:30000]
        embeddings = model.get_embeddings(contextual_text=text)
        if embeddings.text_embedding:
            logger.info(f"File embedded: {item['filename']}")
            return embeddings.text_embedding
        else:
            return None

    elif item["type"] == "media":
        ext = Path(item["path"]).suffix.lower()

        if ext in {".png", ".jpg", ".jpeg"}:
            logger.info(f"Embedding image file: {item['filename']} .....")
            img = Image.load_from_file(item["path"])
            embeddings = model.get_embeddings(image=img)
            if embeddings.image_embedding:
                logger.info(f"Image file embedded: {item['filename']}")
                return embeddings.image_embedding
            else:
                return None

        elif ext == ".mp4":
            logger.info(f"Embedding video file: {item['filename']} .....")
            video = Video.load_from_file(item["path"])
            embeddings = model.get_embeddings(video=video)
            if embeddings.video_embeddings:
                logger.info(f"Video file embedded: {item['filename']}")
                return embeddings.video_embeddings[0].embedding
            else:
                return None

        elif ext in {".mp3", ".wav"}:
            # Transcribe audio to text, then embed
            logger.info(f"Transcribing audio file: {item['filename']} .....")
            transcript = transcribe_audio(item["path"])

            if transcript:
                embeddings = model.get_embeddings(contextual_text=transcript)
                if embeddings.text_embedding:
                    logger.info(
                        msg=f"Audio file transcribed and embedded: {item['filename']}"
                    )
                    return embeddings.text_embedding
                else:
                    return None
            else:
                logger.error(msg=f"Could not transcribe audio: {item['filename']}")
                return None

        else:
            logger.error(msg=f"Unsupported media type for embeddings: {ext}")
            return None

    return None


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    init_vertex()
    logger.info(msg="Embedding module initialized.")
