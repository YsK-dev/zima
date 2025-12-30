import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "REMOVED_SECRET")

def list_models():
    client = genai.Client(api_key=GEMINI_API_KEY)
    print("--- Available Models ---")
    try:
        for model in client.models.list():
            print(f"Name: {model.name}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
