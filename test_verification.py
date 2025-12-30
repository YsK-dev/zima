import os
import json
from google import genai
from google.genai import types
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
GEMINI_MODEL = 'gemini-3-flash-preview'
QWEN_MODEL = 'qwen3:30b'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAF0jRW5m446-N6Gp8UO_vWo8HYQWaAyIk")
QWEN_API_BASE = os.getenv("QWEN_API_BASE", "http://localhost:11434/v1")

def test_gemini():
    print(f"\n--- Testing Gemini ({GEMINI_MODEL}) ---")
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents="Say 'Hello from Gemini!'",
        )
        print(f"Gemini Success: {response.text.strip()}")
        return True
    except Exception as e:
        print(f"Gemini Failed: {e}")
        return False

def test_qwen():
    print(f"\n--- Testing Qwen Local ({QWEN_MODEL}) ---")
    try:
        client = OpenAI(api_key="ollama", base_url=QWEN_API_BASE)
        response = client.chat.completions.create(
            model=QWEN_MODEL,
            messages=[{"role": "user", "content": "Say 'Hello from Qwen Local!'"}]
        )
        print(f"Qwen Success: {response.choices[0].message.content.strip()}")
        return True
    except Exception as e:
        print(f"Qwen Failed: {e}")
        return False

if __name__ == "__main__":
    g_res = test_gemini()
    q_res = test_qwen()
    
    if g_res and q_res:
        print("\n✅ All teacher models are online and ready!")
    else:
        print("\n❌ One or more teacher models are offline. Please check your setup.")
