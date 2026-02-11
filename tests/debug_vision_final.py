import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

async def test_vision():
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    client = genai.Client(api_key=api_key)
    
    # The model we found in the HTTP list
    model_name = "gemini-2.0-flash" 
    print(f"Testing model: {model_name}")

    dummy_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8e\x00\x00\x00\x00IEND\xaeB`\x82'

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                {"role": "user", "parts": [
                    {"inline_data": {"mime_type": "image/png", "data": dummy_image_data}},
                    {"text": "Describe this image."}
                ]}
            ]
        )
        print("SUCCESS! Vision Response:")
        print(response.text)
    except Exception as e:
        print(f"FAILED with {model_name}: {e}")
        
        # Try with prefix
        try:
            print(f"Retrying with models/{model_name}...")
            response = client.models.generate_content(
                model=f"models/{model_name}",
                contents=[
                    {"role": "user", "parts": [
                        {"inline_data": {"mime_type": "image/png", "data": dummy_image_data}},
                        {"text": "Describe this image."}
                    ]}
                ]
            )
            print("SUCCESS with prefix!")
            print(response.text)
        except Exception as e2:
             print(f"FAILED with prefix: {e2}")

if __name__ == "__main__":
    asyncio.run(test_vision())
