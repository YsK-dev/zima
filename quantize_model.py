import os
import subprocess

# --- Configuration ---
MODEL_DIR = "./zima-qwen3-finetuned"
GGUF_NAME = "zima-qwen3-1.7b.gguf"
QUANT_TYPE = "q4_k_m" # High quality 4-bit quantization

def quantize():
    print("--- Starting Quantization Process ---")
    
    # 1. Download llama.cpp if not present
    if not os.path.exists("llama.cpp"):
        print("Cloning llama.cpp...")
        subprocess.run(["git", "clone", "https://github.com/ggerganov/llama.cpp"], check=True)
        print("Building llama.cpp...")
        subprocess.run(["make", "-C", "llama.cpp", "-j"], check=True)

    # 2. Convert HF model to GGUF (FP16 initially)
    print("Converting model to GGUF FP16...")
    subprocess.run([
        "python3", "llama.cpp/convert_hf_to_gguf.py",
        MODEL_DIR,
        "--outfile", "temp_fp16.gguf",
        "--outtype", "f16"
    ], check=True)

    # 3. Quantize to 4-bit
    print(f"Quantizing to {QUANT_TYPE}...")
    subprocess.run([
        "./llama.cpp/llama-quantize",
        "temp_fp16.gguf",
        GGUF_NAME,
        QUANT_TYPE
    ], check=True)

    # 4. Cleanup
    os.remove("temp_fp16.gguf")
    
    print(f"\n--- Success! Quantized model saved as {GGUF_NAME} ---")
    print("You can now move this file to your Raspberry Pi 5.")

if __name__ == "__main__":
    quantize()
