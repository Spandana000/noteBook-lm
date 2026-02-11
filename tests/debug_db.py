import sys
import os
import chromadb
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def inspect_db():
    print("--- Inspecting ChromaDB ---")
    try:
        # Backend runs in /backend, so from root it is at ./backend/chroma_db
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend', 'chroma_db'))
        print(f"Connecting to DB at: {db_path}")
        client = chromadb.PersistentClient(path=db_path)
        print(f"Collections: {[c.name for c in client.list_collections()]}")
        
        try:
            coll = client.get_collection("lumina_notebook")
            print(f"Count: {coll.count()}")
            if coll.count() > 0:
                print("Peeking first 5 items:")
                peek = coll.peek(limit=5)
                # Print filenames and snippets
                if peek['metadatas']:
                    for i, meta in enumerate(peek['metadatas']):
                        doc_snip = peek['documents'][i][:100].replace('\n', ' ') if peek['documents'] else "NO DOC"
                        print(f"[{i}] File: {meta.get('filename')} | Type: {meta.get('type')} | Content: {doc_snip}...")
            else:
                print("Collection is empty.")
                
        except Exception as e:
            print(f"Could not get collection: {e}")

    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    inspect_db()
