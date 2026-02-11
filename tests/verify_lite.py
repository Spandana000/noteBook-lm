import os
import sys
from dotenv import load_dotenv
from google import genai

# Add backend to path to find .env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def test_lite_model():
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    # MODEL_NAME = "gemini-2.0-flash-lite-preview-02-05" 
    # Let's try the generic "gemini-2.0-flash-lite" first as seen in list
    MODEL_NAME = "gemini-2.0-flash-lite-preview-02-05" 
    # Actually from the previous list: "models/gemini-2.0-flash-lite"
    
    # Wait, the list showed: "models/gemini-2.0-flash-lite"
    # Let's use that.
    MODEL_NAME = "gemini-2.0-flash-lite"

    try:
        client = genai.Client(api_key=api_key)
        print(f"Testing model='{MODEL_NAME}' for TEXT...")
        response = client.models.generate_content(
            model=MODEL_NAME, 
            contents="Say 'Lite works'."
        )
        print(f"Text Response: {response.text}")
        
        # We can't easily test vision without an image file, 
        # but Flash models are implicitly multimodal. 
        # If text works, we assume vision works for now or strict verification later.
        print("SUCCESS: Model is available.")
        
    except Exception as e:
        print(f"FAILURE: {e}")
        # Fallback to check if 'gemini-1.5-flash' is actually safer choice if lite fails?
        # The user was adamant about "very less and efficient". 
        # If 'gemini-2.0-flash-lite' fails, 'gemini-1.5-flash' was 404.
        # Maybe 'gemini-flash-lite-latest'?

if __name__ == "__main__":
    test_lite_model()
