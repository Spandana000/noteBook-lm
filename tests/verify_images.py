import sys
import os
import asyncio
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

# Load env from backend
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

from services.rag_service import rag_service

async def test_image_logic():
    print("--- Starting Image Logic Verification ---")
    
    # 1. Simulate a document context (since we might not have files loaded)
    # We will inject a fake context into the collection for testing if needed, 
    # but let's try to just query first. If empty, we might need to rely on general knowledge 
    # logic which we have a fallback for? No, the prompt requires "Document Context".
    # Let's add a dummy document.
    print("Adding dummy 'Solar Panel' text to ChromaDB...")
    
    # RESET Collection to match 768 dimensions (Google Embedding)
    try:
        rag_service.chroma_client.delete_collection("lumina_notebook")
        print("Existing collection deleted (schema update).")
    except Exception:
        pass
    
    rag_service.collection = rag_service.chroma_client.get_or_create_collection(name="lumina_notebook")
    
    doc_text = "A solar panel is a device that converts sunlight into electricity using photovoltaic (PV) cells. PV cells are made of materials like silicon. When sunlight hits the cells, it knocks electrons loose from their atoms, allowing them to flow through the material to produce electricity. This process is called the photovoltaic effect. A typical solar panel module consists of 60 or 72 cells protected by a glass sheet and a metal frame. Monocrystalline panels are more efficient but expensive, while Polycrystalline are cheaper."
    
    # Generate embedding using the same model as the service
    emb_res = rag_service.google_client.models.embed_content(
        model="text-embedding-004",
        contents=doc_text
    )
    
    rag_service.collection.add(
        ids=["test_doc_1"],
        embeddings=[emb_res.embeddings[0].values],
        documents=[doc_text],
        metadatas=[{"filename": "test_solar.txt", "type": "text"}]
    )
    
    query = "How do solar panels work?"
    print(f"\nQuerying: '{query}' with include_images=True")
    
    result = await rag_service.query(query, include_images=True)
    
    images = result.get('images', [])
    print(f"\nResponse received. Images count: {len(images)}")
    
    if len(images) == 0:
        print("FAILED: No images returned.")
        return

    print("\n--- Image Results ---")
    for i, img in enumerate(images):
        print(f"Image {i+1}:")
        print(f"  URL: {img.get('url')}")
        print(f"  Context Label: {img.get('context_label')}")
        print(f"  Title: {img.get('title')}")
        
    # Validation Checks
    if len(images) != 3:
        print(f"\nWARNING: Expected 3 images, got {len(images)}")
    else:
        print("\nSUCCESS: Exactly 3 images returned.")
        
    labels = [img.get('context_label') for img in images]
    if len(set(labels)) == len(labels):
         print("SUCCESS: Context labels are unique.")
    else:
         print("WARNING: Duplicate context labels found.")

    print("\n--- End Verification ---")

if __name__ == "__main__":
    asyncio.run(test_image_logic())
