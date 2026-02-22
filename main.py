from embedder import get_embedding, init_vertex
from ingestion import process_files, select_files
from llm_chain import call_gemini
from vector_store import SimpleVectorStore


def main():
    print("Welcome to the Multi-Modal MS Office & Media RAG System!")
    print("Initializing Google Vertex AI...")
    from dotenv import load_dotenv

    load_dotenv()

    # Needs GOOGLE_CLOUD_PROJECT + GEMINI_API_KEY
    init_vertex()

    # Initialize DB
    print("\n[Step 1] Please select your MS Office and Media files from the dialog...")
    filepaths = select_files()

    if not filepaths:
        print("No files selected. Exiting.")
        return

    print(f"Selected {len(filepaths)} files. Processing...\n")
    processed_items = process_files(filepaths)

    # We instantiate a fresh DB for the session
    db = SimpleVectorStore()
    db.clear()

    print(
        "\n[Step 2] Generating multi-modal embeddings using Vertex AI (this takes time)..."
    )
    for item in processed_items:
        print(f"Embedding {item['filename']}...")
        emb = get_embedding(item)
        if emb is not None:
            db.add(embedding=emb, metadata=item)
            print(f" -> Added {item['filename']} to Vector DB.")
        else:
            print(f" -> Failed to embed {item['filename']}.")

    print("\n[Step 3] Ready for Queries! (Type 'quit' or 'exit' to stop)\n")

    while True:
        try:
            query = input("You: ")
            if query.lower() in ["quit", "exit"]:
                break

            # Embed user query using text-embedding
            print("  [Searching DB...]")
            query_item = {
                "type": "text_document",
                "content": query,
                "path": "query",
                "filename": "query",
            }
            q_emb = get_embedding(query_item)

            # Retrieve nearest neighbors
            results = db.search(q_emb, top_k=3)

            if not results:
                print("No relevant context found in the files.")
                continue

            print(
                "  [Retrieved Context from:]",
                ", ".join([r["metadata"]["filename"] for r in results]),
            )

            # Pass to Gemini
            print("  [Generating Response...]")
            answer = call_gemini(query, results)

            print(f"\nGemini:\n{answer}\n\n{'-' * 40}\n")

        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
