import os
import uuid
import mimetypes
from google import genai
from groq import Groq
from duckduckgo_search import DDGS
from pypdf import PdfReader
import chromadb
from dotenv import load_dotenv

load_dotenv()

import logging
logger = logging.getLogger("lumina")

class RAGService:
    def __init__(self):
        # Professional Client Initialization
        self.google_client = genai.Client(api_key=os.getenv("GOOGLE_GENERATIVE_AI_API_KEY"))
        # Increase timeout to 60s for handling complex reasoning
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"), timeout=60.0)
        self.chroma_client = chromadb.PersistentClient(path="./chroma_db")
        self.collection = self.chroma_client.get_or_create_collection(name="lumina_notebook")

    async def process_file(self, file, session_id: str):
        """Intelligently processes PDF, Text, Code, or Images."""
        filename = file.filename
        mime_type, _ = mimetypes.guess_type(filename)
        content_to_embed = ""
        
        # 1. Image Processing (OCR & Vision)
        if mime_type and mime_type.startswith('image'):
            try:
                # Read image bytes
                file.file.seek(0)
                image_bytes = await file.read()
                
                # Direct HTTP Fallback for Vision Reliability
                import json
                import urllib.request
                import base64

                api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
                
                # Prepare JSON payload
                image_b64 = base64.b64encode(image_bytes).decode('utf-8')
                payload = {
                    "contents": [{
                        "parts": [
                            {"inline_data": {"mime_type": mime_type, "data": image_b64}},
                            {"text": "1. Transcribe ALL visible text in this image exactly as it appears. \n2. Describe the layout and visual elements in detail.\n\nOutput format:\nOCR TRANSCRIPTION:\n[Text here]\n\nVISUAL DESCRIPTION:\n[Description here]"}
                        ]
                    }]
                }
                
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json'}
                )
                
                try:
                    with urllib.request.urlopen(req) as response:
                        result = json.loads(response.read().decode())
                        # Extract text from complex response structure
                        image_description = result['candidates'][0]['content']['parts'][0]['text']
                        print(f"Vision Success: {image_description[:50]}...")
                except Exception as e:
                    print(f"HTTP Vision Failed: {e}")
                    image_description = f"[Image {file.filename}: Vision processing skipped due to error: {str(e)}]"
                
                content_to_embed = f"Filename: {filename}\nImage Content (OCR/Vision):\n{image_description}"
                
            except Exception as e:
                print(f"Vision processing failed for {filename}: {e}")
                content_to_embed = f"Image file: {filename}. (Vision processing skipped due to error)"

        # 2. PDF Processing
        elif filename.lower().endswith('.pdf'):
            reader = PdfReader(file.file)
            content_to_embed = "".join([p.extract_text().replace("\x00", "") for p in reader.pages if p.extract_text()])

        # 3. Text/Code Processing
        else:
            content_to_embed = (await file.read()).decode("utf-8", errors="ignore")

        if content_to_embed:
            try:
                # Chunk and Embed (Using Google for Embeddings)
                chunks = [content_to_embed[i:i+1200] for i in range(0, len(content_to_embed), 1200)]
                for chunk in chunks:
                    res = self.google_client.models.embed_content(model="models/gemini-embedding-001", contents=chunk)
                    self.collection.add(
                        ids=[str(uuid.uuid4())],
                        embeddings=[res.embeddings[0].values],
                        documents=[chunk],
                        metadatas=[{"filename": filename, "type": mime_type or "text", "session_id": session_id}]
                    )
                print(f"Successfully processed and embedded: {filename}")
            except Exception as e:
                print(f"Error embedding {filename}: {e}")
                raise e

    async def query(self, query: str, include_images: bool, session_id: str = None):
        try:
            # 1. Context Retrieval (Using Google Embeddings)
            q_res = self.google_client.models.embed_content(model="models/gemini-embedding-001", contents=query)
            where_filter = {"session_id": session_id} if session_id else None
            logger.info(f"DEBUG: Querying with session_id='{session_id}', where_filter={where_filter}")
            docs = self.collection.query(
                query_embeddings=[q_res.embeddings[0].values], 
                n_results=4,
                where=where_filter
            )
            logger.info(f"DEBUG: Retrieved docs metadata: {docs['metadatas']}")
            context = "\n".join(docs['documents'][0]) if docs['documents'] else "No document context found."

            # 2. Multimedia Search (Using Groq for reasoning-based query generation)
            images = []
            if include_images:
                try:
                    v_prompt = f"""
                    You are an expert visual researcher. Generate 3 SPECIFIC image search queries based on:
                    QUERY: {query}
                    CONTEXT fragments: {context[:2000]}
                    
                    Format: exactly 3 lines, "Search Query | Why relevant".
                    """
                    
                    # Groq (Llama 3.3) for smart search planning
                    v_resp = self.groq_client.chat.completions.create(
                        messages=[{"role": "user", "content": v_prompt}], 
                        model="llama-3.3-70b-versatile",
                        temperature=0.3
                    )
                    
                    for line in v_resp.choices[0].message.content.strip().split('\n')[:3]:
                        if "|" in line:
                            q_text, c_label = line.split("|")
                            with DDGS(timeout=10) as ddgs:
                                res = list(ddgs.images(q_text.strip(), max_results=1))
                                if res:
                                    images.append({
                                        "url": res[0]['image'], 
                                        "thumbnail": res[0]['thumbnail'], 
                                        "title": res[0]['title'],
                                        "context_label": c_label.strip()
                                    })
                except Exception as img_err:
                    print(f"Search failed: {img_err}")

            # 3. Chat Response (Using Groq for superior language quality)
            system_prompt = """You are Lumina AI. Use Markdown.
            
            INSTRUCTIONS:
            1. Check if the provided CONTEXT is relevant to the USER QUESTION.
            2. If relevant, answer using the context.
            3. If the context is IRRELEVANT or EMPTY, ignore it and answer using your General Knowledge.
            4. NEVER say "There is no mention in the context". Just answer the question directly.
            """
            
            chat_resp = self.groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"CONTEXT:\n{context}\n\nUSER QUESTION: {query}"}
                ],
                model="llama-3.3-70b-versatile"
            )
            
            return {
                "answer": chat_resp.choices[0].message.content,
                "images": images
            }
        except Exception as e:
            print(f"Query Error: {e}")
            return {"answer": f"Processing Error: {str(e)}", "images": []}

    async def define_word(self, word: str, context: str = ""):
        # Use Groq for context-aware definitions
        prompt = f"Define '{word}' in 1-2 sentences within this context: {context}"
        try:
            resp = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.3-70b-versatile"
            )
            return {"definition": resp.choices[0].message.content}
        except Exception:
            return {"definition": "Definition lookup failed."}

    def clear_storage(self):
        """Wipes the ChromaDB knowledge base."""
        try:
            self.chroma_client.delete_collection(name="lumina_notebook")
            self.collection = self.chroma_client.get_or_create_collection(name="lumina_notebook")
            print("ChromaDB knowledge base cleared.")
        except Exception as e:
            print(f"Error clearing ChromaDB: {e}")

rag_service = RAGService()
