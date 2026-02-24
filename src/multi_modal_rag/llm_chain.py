import os

from google import genai


def call_gemini(query, context_items):
    """
    Calls Gemini 2.5 Flash with the user's text query and the retrieved multi-modal context chunks.
    `context_items` is a list of metadata dicts returned from vector_store.py
    """

    # We use Google GenAI SDK for Gemini 2.5 Flash via AI Studio (Developer API).
    # We temporarily hide GOOGLE_CLOUD_PROJECT from the actual environment inside this function
    # to prevent the `genai` client from auto-routing to Vertex AI.
    backup_project = os.environ.pop("GOOGLE_CLOUD_PROJECT", None)

    api_key = os.environ.get("GEMINI_API_KEY")
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
            # Cap at 50,000 characters per context chunk to prevent giant API requests
            prompt_parts.append(text[:50000])
        elif meta["type"] == "media":
            file_path = meta.get("path")
            if file_path and os.path.exists(file_path):
                print(f"Uploading {meta['filename']} to Gemini File API...")
                try:
                    # The File API is the most robust way to handle video/audio
                    uploaded_file = client.files.upload(file=file_path)
                    prompt_parts.append(uploaded_file)
                except Exception as e:
                    print(f"Could not upload {meta['filename']}: {e}")
                    prompt_parts.append(
                        f"(Failed to load media file: {meta['filename']})"
                    )
            else:
                prompt_parts.append(
                    f"(Media file not found at path: {meta['filename']})"
                )

    prompt_parts.append("--- CONTEXT END ---")
    prompt_parts.append(f"\nUser Query: {query}")

    print("Calling Gemini 2.5 Flash...")
    try:
        # The generate_content function accepts contents parameter
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt_parts
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {e}"


if __name__ == "__main__":
    print("Initialize LLM Chain.")
