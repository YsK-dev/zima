from llama_cpp import Llama
from fastapi import FastAPI
import uvicorn
import os

# --- Configuration ---
MODEL_PATH = os.getenv("MODEL_PATH", "zima-qwen3-1.7b-q4_k_m.gguf")

print(f"Loading model from {MODEL_PATH}...")
llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=512,
    n_threads=4, # RPi5 has 4 cores
    n_gpu_layers=0 # CPU only
)

app = FastAPI()

SYSTEM_PROMPT = """You are an AI Geriatric Health Assistant. Your mission is to provide safe, simple, non-diagnostic, and proactive daily wellness and common medical advice tailored for an ELDERLY POPULATION (70+ years old).

STRICT SAFETY RULES:
1. CRITICAL: For severe symptoms (e.g., chest pain, stroke signs), immediately advise contacting emergency services (911).
2. NEVER diagnose or suggest medication dosages.
"""

@app.post("/chat")
async def chat(request: dict):
    instruction = request.get("instruction", "")
    context = request.get("input", "Patient is 75 years old.")
    
    prompt = f"### System:\n{SYSTEM_PROMPT}\n\n### Instruction:\n{instruction}\n\n### Input:\n{context}\n\n### Response:\n"
    
    output = llm(
        prompt,
        max_tokens=256,
        temperature=0.7,
        stop=["###", "\n\n"]
    )
    
    return {"response": output["choices"][0]["text"].strip()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
