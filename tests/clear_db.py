import sys
import os
import chromadb

def clear_backend_db():
    print("--- Clearing Backend ChromaDB ---")
    try:
        # Backend runs in /backend, so from root it is at ./backend/chroma_db
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'chroma_db'))
        print(f"Target DB: {db_path}")
        
        client = chromadb.PersistentClient(path=db_path)
        collections = client.list_collections()
        print(f"Found collections: {[c.name for c in collections]}")
        
        for c in collections:
            print(f"Deleting collection: {c.name}")
            client.delete_collection(c.name)
            
        print("Database cleared successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    clear_backend_db()
