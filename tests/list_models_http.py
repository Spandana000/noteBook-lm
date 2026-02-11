import os
import urllib.request
import json
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

def check_models():
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    print(f"GET {url.replace(api_key, 'API_KEY')}")
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print("\nAVAILABLE MODELS:")
            for m in data.get('models', []):
                name = m.get('name')
                methods = m.get('supportedGenerationMethods', [])
                if 'generateContent' in methods:
                    print(f" - {name}")
    except Exception as e:
        print(f"HTTP Request Failed: {e}")

if __name__ == "__main__":
    check_models()
