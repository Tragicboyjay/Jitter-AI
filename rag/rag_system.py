import os
import re
import hashlib
from typing import List
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from rag.rag_file_parser import text_file_rag, pdf_file_rag, html_file_rag, csv_file_rag, md_file_rag

# ---------------------------
# Config
# ---------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, 'files')
HASH_STORE = os.path.join(BASE_DIR, 'processed_files.txt')
CHROMA_DIR = os.path.join(BASE_DIR, ".chromadb")

print("[RAG] Loading embedding model...")
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL_NAME)

print("[RAG] Initializing Chroma client...")
client = PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="rag_chunks", embedding_function=embedding_fn)

# ---------------------------
# Utility Functions
# ---------------------------

def hash_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def make_chunk_id(source_id, chunk):
    return hashlib.sha256(f"{source_id}-{chunk}".encode()).hexdigest()

def get_chunks_from_file(file_path):
    if file_path.endswith('.txt'):
        return text_file_rag(file_path)
    elif file_path.endswith('.pdf'):
        return pdf_file_rag(file_path)
    elif file_path.endswith('.html') or file_path.endswith('.htm'):
        return html_file_rag(file_path)
    elif file_path.endswith('.csv'):
        return csv_file_rag(file_path)
    elif file_path.endswith('.md'):
        return md_file_rag(file_path)
    else:
        print(f"[get_chunks_from_file] Unsupported file type: {file_path}")
        return []

def load_processed_hashes():
    if not os.path.exists(HASH_STORE):
        return {}
    with open(HASH_STORE, "r") as f:
        lines = f.read().splitlines()
    return dict(line.split(":", 1) for line in lines)

def save_processed_hashes(file_hashes):
    with open(HASH_STORE, "w") as f:
        for path, file_hash in file_hashes.items():
            f.write(f"{path}:{file_hash}\n")

# ---------------------------
# Add Chunks Manually
# ---------------------------

def add_chunks_to_db(chunks: List[str], source_id: str = "manual"):
    if not chunks:
        print("[add_chunks_to_db] No chunks provided.")
        return

    ids = [make_chunk_id(source_id, chunk) for chunk in chunks]
    metadatas = [{"source": source_id} for _ in chunks]

    try:
        collection.add(documents=chunks, metadatas=metadatas, ids=ids)
        print(f"[add_chunks_to_db] Added {len(chunks)} chunks from '{source_id}' to the collection.")
    except Exception as e:
        print(f"[add_chunks_to_db] Error adding chunks: {e}")

# ---------------------------
# Ingest Files from Folder
# ---------------------------

def ingest_data():
    if not os.path.exists(FILES_DIR):
        print(f"[ingest_data] Directory '{FILES_DIR}' does not exist.")
        return

    files_to_process = [os.path.join(FILES_DIR, f) for f in os.listdir(FILES_DIR)]
    print(f"\n[ingest_data] Found files: {[os.path.basename(f) for f in files_to_process]}")

    processed_hashes = load_processed_hashes()
    updated_hashes = processed_hashes.copy()

    for file_path in files_to_process:
        try:
            file_hash = hash_file(file_path)
            if processed_hashes.get(file_path) == file_hash:
                continue  # Skip unchanged

            print(f"[ingest_data] Processing: {file_path}")
            chunks = get_chunks_from_file(file_path)
            if not chunks:
                continue

            ids = [make_chunk_id(file_path, chunk) for chunk in chunks]
            metadatas = [{"file_path": file_path} for _ in chunks]

            collection.add(documents=chunks, metadatas=metadatas, ids=ids)
            updated_hashes[file_path] = file_hash

        except Exception as e:
            print(f"[ingest_data] Error processing {file_path}: {e}")

    save_processed_hashes(updated_hashes)
    print(f"[ingest_data] Ingestion complete. Collection now contains {collection.count()} documents.\n")

# ---------------------------
# Search Function
# ---------------------------

def search_rag(query: str, top_k: int = 20):
    if collection.count() == 0:
        return "Knowledge base is empty. Add files to the 'files' directory and run ingestion."

    results = collection.query(query_texts=[query], n_results=top_k)
    documents = results.get("documents", [[]])[0]
    if not documents:
        return "No relevant information found."

    return "\n".join(documents)
