import os

from google import genai


def call_gemini(query, context_items):
    """
    Calls Gemini 2.5 Flash with the user's text query and the retrieved multi-modal context chunks.
    context_items is a list of metadata dicts returned from vector_store.py
    """

    # We use Google GenAI SDK for Gemini 2.5 Flash via AI Studio (Developer API).
    # We temporarily hide GOOGLE_CLOUD_PROJECT from the actual environment inside this function
    # to prevent the `genai` client from auto-routing to Vertex AI (which caused the 404 error).
    backup_project = os.environ.pop("GOOGLE_CLOUD_PROJECT", None)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if backup_project:
        os.environ["GOOGLE_CLOUD_PROJECT"] = backup_project

    contents = [
        "You are an intelligent Assistant with access to a multimodal database.",
        "Below is context retrieved from various files (Word, Excel, PPT, Image, Video, Audio).",
        "Use this context to answer the user's query.",
        "--- CONTEXT START ---",
    ]

    for i, item in enumerate(context_items):
        meta = item["metadata"]
        contents.append(
            f"\n[Source {i + 1}: {meta['filename']} - Type: {meta['type']}]"
        )

        if meta["type"] == "text_document":
            text = meta.get("content", "")
            # Cap at 50,000 characters per context chunk to prevent giant API requests
            contents.append(text[:50000])
        elif meta["type"] == "media":
            # For media, we must pass the actual file bytes to Gemini
            # (or use the File API if they are large, but for this demo we'll pass small images/video natively if supported,
            # but ideally the user uploads it via FileAPI.
            # Note: For strict RAG over video/audio, Google GenAI requires uploading via File API first.
            contents.append(
                f"(Media file {meta['filename']} was retrieved but is not inline. If the user asks about it, explain it's an external file)."
            )

    contents.append("--- CONTEXT END ---")
    contents.append(f"User Query: {query}")

    contents_str = "\n".join(contents)

    print("Calling Gemini 2.5 Flash...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents_str,
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini: {e}"


if __name__ == "__main__":
    print("Initialize LLM Chain.")
