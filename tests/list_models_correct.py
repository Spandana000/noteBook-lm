import os
from google import genai
from dotenv import load_dotenv

# Try to load .env from backend folder
env_path = os.path.join(os.path.dirname(__file__), '..', 'backend', '.env')
load_dotenv(env_path)

api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
print(f"API Key found: {bool(api_key)}")

try:
    client = genai.Client(api_key=api_key)
    print("Listing models...")
    # list methods available on client.models
    pager = client.models.list()
    for model in pager:
        print(f"Name: {model.name}")
        print(f"  Display Name: {model.display_name}")
        print(f"  Supported Actions: {model.supported_actions}")
        print("-" * 20)
except Exception as e:
    print(f"Error listing models with new SDK: {e}")
    import traceback
    traceback.print_exc()

# Also try the old SDK just in case the new one is weird
print("\nTrying old SDK (google.generativeai)...")
try:
    import google.generativeai as genai_old
    genai_old.configure(api_key=api_key)
    for m in genai_old.list_models():
        print(f"Name: {m.name}")
        print(f"  Supported: {m.supported_generation_methods}")
except Exception as e:
    print(f"Error listing with old SDK: {e}")
