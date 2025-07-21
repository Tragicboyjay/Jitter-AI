
import os
import sqlite3

# Paths (adjust if needed)
DB_PATH = os.path.join(os.path.dirname(__file__), "memory", "agent_memory.db")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "rag", "rag_index.faiss")

# Remove all vector data from SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("DELETE FROM vector_chunks;")
cursor.execute("DELETE FROM processed_files;")
conn.commit()
conn.close()
print("Cleared vector_chunks and processed_files tables.")

# Remove the FAISS index file
if os.path.exists(INDEX_PATH):
    os.remove(INDEX_PATH)
    print("Deleted FAISS index file.")
else:
    print("FAISS index file not found.")
