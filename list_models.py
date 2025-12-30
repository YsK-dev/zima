import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAF0jRW5m446-N6Gp8UO_vWo8HYQWaAyIk")

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
