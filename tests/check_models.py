import os
import sys
from dotenv import load_dotenv
from google import genai

# Add backend to path to find .env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def list_models():
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    if not api_key:
        print("Error: GOOGLE_GENERATIVE_AI_API_KEY not found in .env")
        return

    try:
        client = genai.Client(api_key=api_key)
        print("Listing available models...")
        # Note: The method to list models might vary slightly by SDK version, 
        # but usually it's client.models.list() or similar. 
        # For the new google-genai SDK, let's try strict client usage.
        
        # Pager object iteration
        for model in client.models.list(config={"page_size": 100}):
            if "flash" in model.name.lower():
                print(f"- {model.name} (Display: {model.display_name})")
            
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
