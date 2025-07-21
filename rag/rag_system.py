import os
import sqlite3
import hashlib
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

from rag.rag_file_parser import text_file_rag, pdf_file_rag, html_file_rag, csv_file_rag, md_file_rag

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "memory", "agent_memory.db")
INDEX_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_index.faiss")
MODEL_NAME = 'all-MiniLM-L6-v2'

print("[RAG] Loading embedding model...")
model = SentenceTransformer(MODEL_NAME)
DIM = model.get_sentence_embedding_dimension()

# SQLite connection and table creation will be handled by setup_database in app lifecycle
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Load or create FAISS index
if os.path.exists(INDEX_PATH):
    print("[RAG] Loading existing FAISS index.")
    index = faiss.read_index(INDEX_PATH)
else:
    print("[RAG] No FAISS index found, creating a new one.")
    index = faiss.IndexIDMap(faiss.IndexFlatL2(DIM))

def hash_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

def get_chunks_from_file(file_path):
    if file_path.endswith('.txt'):
        chunks = text_file_rag(file_path)
    elif file_path.endswith('.pdf'):
        chunks = pdf_file_rag(file_path)
    elif file_path.endswith('.html') or file_path.endswith('.htm'):
        chunks = html_file_rag(file_path)
    elif file_path.endswith('.csv'):
        chunks = csv_file_rag(file_path)
    elif file_path.endswith('.md'):
        chunks = md_file_rag(file_path)
    else:
        print(f"[get_chunks_from_file] Unsupported file type: {file_path}")
        return []
    print(f"[get_chunks_from_file] {file_path} -> {len(chunks)} chunks")
    return chunks

def ingest_data():
    files_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'files')
    if not os.path.exists(files_dir):
        print(f"Directory '{files_dir}' does not exist.")
        return

    files_to_process = [os.path.join(files_dir, f) for f in os.listdir(files_dir)]
    print(f"\n[ingest_data] Files found: {[os.path.basename(f) for f in files_to_process]}\n")
    new_vectors_added = False

    # --- Cleanup: Remove DB entries for files no longer present ---
    cursor.execute("SELECT DISTINCT file_path FROM vector_chunks")
    db_file_paths = set(row[0] for row in cursor.fetchall())
    current_file_paths = set(files_to_process)
    removed_files = db_file_paths - current_file_paths
    if removed_files:
        removed_files_info = [f"{os.path.basename(f)} ({os.path.splitext(f)[1]})" for f in removed_files]
        print(f"\n[ingest_data] Removing DB entries for deleted files: {removed_files_info}\n")
        for file_path in removed_files:
            cursor.execute("DELETE FROM vector_chunks WHERE file_path = ?", (file_path,))
            cursor.execute("DELETE FROM processed_files WHERE file_path = ?", (file_path,))
        conn.commit()

    for file_path in files_to_process:
        try:
            current_hash = hash_file(file_path)
            cursor.execute("SELECT file_hash FROM processed_files WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()

            if row and row[0] == current_hash:
                continue  # Skip if file is unchanged

            print(f"Processing new/modified file: {file_path}")

            chunks = get_chunks_from_file(file_path)
            if not chunks:
                continue


            # Insert each chunk individually, fetch its rowid, and use as FAISS vector ID
            vector_ids = []
            valid_chunks = []
            for chunk in chunks:
                cursor.execute(
                    "INSERT INTO vector_chunks (file_path, chunk_text) VALUES (?, ?)",
                    (file_path, chunk)
                )
                rowid = cursor.lastrowid
                vector_ids.append(rowid)
                valid_chunks.append(chunk)

            if valid_chunks:
                embeddings = model.encode(valid_chunks, convert_to_numpy=True).astype('float32')
                index.add_with_ids(embeddings, np.array(vector_ids))
                new_vectors_added = True

            cursor.execute(
                "REPLACE INTO processed_files (file_path, file_hash) VALUES (?, ?)",
                (file_path, current_hash)
            )

        except Exception as e:
            print(f"Error processing {file_path}: {e}")

    if new_vectors_added:
        print("Committing changes to database and saving FAISS index...")
        conn.commit()
        faiss.write_index(index, INDEX_PATH)
        print(f"Ingestion complete. Index now contains {index.ntotal} vectors.")
    else:
        print("No new file changes detected. System is up to date.")

def search_rag(query: str, top_k: int = 3):
    if index.ntotal == 0:
        return "The knowledge base is empty. Please add files to the 'files' directory and run the ingestion process."

    query_embedding = model.encode([query], convert_to_numpy=True).astype('float32')
    distances, ids = index.search(query_embedding, top_k)

    retrieved_chunks = []
    for i in ids[0]:
        if i != -1:
            cursor.execute("SELECT chunk_text FROM vector_chunks WHERE id = ?", (int(i),))
            result = cursor.fetchone()
            if result:
                retrieved_chunks.append(result[0])

    if not retrieved_chunks:
        return "No relevant information found in the knowledge base."

    return "\n".join(retrieved_chunks)
