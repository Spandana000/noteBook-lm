import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

async def list_models():
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    print("Listing available models:")
    try:
        # The syntax might differ depending on library version, trying standard first
        from google.generativeai import list_models
        import google.generativeai as genai_old
        genai_old.configure(api_key=api_key)
        for m in genai_old.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
    except Exception as e:
        print(f"Standard list failed: {e}")
        # Try new client method if available
        try:
             # Just try a known one or print help
             print("Trying manual check...")
        except:
            pass

if __name__ == "__main__":
    asyncio.run(list_models())
