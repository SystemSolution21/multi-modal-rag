# src/multi_modal_rag/llm_chain.py

"""LLM chain module for the Multi-Modal RAG system.
This module provides functions to call Gemini API with the user's query and the retrieved context.
"""

# Import built-in modules
import logging
import os
import time

# Import third-party modules
from google import genai

# Import local modules
import config
from utils.logger import get_app_logger

# Initialize logger
logger: logging.Logger = get_app_logger()


def call_gemini(query, context_items):
    """
    Calls Gemini 2.5 Flash with the user's text query and the retrieved multi-modal context chunks.
    `context_items` is a list of metadata dicts returned from vector_store.py
    """

    # We use Google GenAI SDK for Gemini 2.5 Flash via AI Studio (Developer API).
    # We temporarily hide GOOGLE_CLOUD_PROJECT from the actual environment inside this function
    # to prevent the `genai` client from auto-routing to Vertex AI.
    backup_project = os.environ.pop("GOOGLE_CLOUD_PROJECT", None)
    api_key = config.GEMINI_API_KEY
    client = genai.Client(api_key=api_key)

    if backup_project:
        os.environ["GOOGLE_CLOUD_PROJECT"] = backup_project

    prompt_parts: list = [
        "You are an intelligent Assistant with access to a multimodal database.",
        "Below is context retrieved from various files (Text, Word, Excel, PPT, PDF, Image, Video, Audio).",
        "Use this context to answer the user's query.",
        "--- CONTEXT START ---",
    ]

    for i, item in enumerate(context_items):
        meta = item["metadata"]
        prompt_parts.append(
            f"\n[Source {i + 1}: {meta['filename']} - Type: {meta['type']}]"
        )

        if meta["type"] == "text_document":
            text = meta.get("content", "")
            prompt_parts.append(text[:50000])
        elif meta["type"] == "media":
            file_path = meta.get("path")
            if file_path and os.path.exists(file_path):
                logger.info(msg=f"Uploading {meta['filename']} to Gemini File API.....")
                try:
                    uploaded_file = client.files.upload(file=file_path)

                    # Wait for file to become ACTIVE
                    while (
                        uploaded_file.state and uploaded_file.state.name == "PROCESSING"
                    ):
                        time.sleep(1)
                        if uploaded_file.name:
                            uploaded_file = client.files.get(name=uploaded_file.name)
                        else:
                            logger.error(
                                f"Uploaded file {meta['filename']} has no name"
                            )
                            break

                    if uploaded_file.state and uploaded_file.state.name == "ACTIVE":
                        prompt_parts.append(uploaded_file)
                    else:
                        state_name = (
                            uploaded_file.state.name
                            if uploaded_file.state
                            else "UNKNOWN"
                        )
                        logger.error(
                            f"File {meta['filename']} failed to process: {state_name}"
                        )
                        prompt_parts.append(
                            f"(Failed to process media file: {meta['filename']})"
                        )
                except Exception as e:
                    logger.error(f"Could not upload {meta['filename']}: {e}")
                    prompt_parts.append(
                        f"(Failed to load media file: {meta['filename']})"
                    )
            else:
                prompt_parts.append(
                    f"(Media file not found at path: {meta['filename']})"
                )

    prompt_parts.append("--- CONTEXT END ---")
    prompt_parts.append(f"\nUser Query: {query}")

    logger.info(msg=f"Calling {config.GEMINI_MODEL} model.....")
    try:
        # The generate_content function accepts contents parameter
        response = client.models.generate_content(
            model=config.GEMINI_MODEL, contents=prompt_parts
        )
        if response.text:
            logger.info(
                msg=f"Assistant response: {response.text[:50]}..... (truncated)"
            )

        return response.text
    except Exception as e:
        logger.error(f"Error calling {config.GEMINI_MODEL} model: {e}")
        return f"Error calling {config.GEMINI_MODEL} model: {e}"


if __name__ == "__main__":
    logger.info(msg="Initialize LLM Chain.")
