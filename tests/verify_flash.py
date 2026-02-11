import os
import sys
from dotenv import load_dotenv
from google import genai

# Add backend to path to find .env
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def test_flash():
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    try:
        client = genai.Client(api_key=api_key)
        print("Testing model='gemini-1.5-flash'...")
        response = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents="Say 'Active' if you are working."
        )
        print(f"Response: {response.text}")
        print("SUCCESS: gemini-1.5-flash is available.")
    except Exception as e:
        print(f"FAILURE: {e}")

if __name__ == "__main__":
    test_flash()
