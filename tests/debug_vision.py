import os
import asyncio
from google import genai
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'backend', '.env'))

async def test_vision():
    api_key = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_GENERATIVE_AI_API_KEY not found.")
        return

    print(f"Using API Key: {api_key[:5]}...")
    
    try:
        client = genai.Client(api_key=api_key)
        
        # Test specific version which is often more stable
        model_name = "gemini-1.5-flash-002" 
        print(f"Testing model: {model_name}")

        # Create a tiny dummy image (1x1 pixel PNG)
        # 1x1 red pixel
        dummy_image_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xcf\xc0\x00\x00\x03\x01\x01\x00\x18\xdd\x8e\x00\x00\x00\x00IEND\xaeB`\x82'

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
        print(f"\nCRITICAL FAILURE for {model_name}:")
        print(e)
        
        # Try fallback
        print("\nTrying fallback model: gemini-1.5-flash")
        try:
             response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[
                    {"role": "user", "parts": [
                        {"inline_data": {"mime_type": "image/png", "data": dummy_image_data}},
                        {"text": "Describe this image."}
                    ]}
                ]
            )
             print("SUCCESS with fallback! Vision Response:")
             print(response.text)
        except Exception as e2:
             print(f"Fallback failed too: {e2}")

if __name__ == "__main__":
    asyncio.run(test_vision())
