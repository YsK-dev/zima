import gradio as gr
import torch
from pathlib import Path
import os
import sys
from threading import Lock

# Configuration
ADAPTER_PATH = "/home/ysk/Downloads/zima/trained_model"
BASE_MODEL_ID = "Qwen/Qwen2.5-1.5B-Instruct" 

print(f"Initializing Zima Demo (Side-by-Side Comparison)...")
print(f"Adapter Path: {ADAPTER_PATH}")

# Model loading variables
model = None
tokenizer = None
USE_GPU = torch.cuda.is_available()
generate_lock = Lock() # Prevent concurrent interference with adapter toggling

if USE_GPU:
    try:
        print("🚀 GPU detected. Attempting to use Unsloth for acceleration...")
        from unsloth import FastLanguageModel
        
        # Load from the adapter path
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name = ADAPTER_PATH,
            max_seq_length = 2048,
            dtype = None,
            load_in_4bit = True,
        )
        FastLanguageModel.for_inference(model)
        print("✅ loaded with Unsloth (GPU)")
    except Exception as e:
        print(f"⚠️  Unsloth load failed: {e}")
        print("🔄 Falling back to standard Transformers...")
        USE_GPU = False 

if not USE_GPU:
    print(f"🖥️  Running in CPU/Compatibility Mode using Base Model: {BASE_MODEL_ID}")
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel
    
    try:
        # Load base model
        print("Loading base model...")
        base_model = AutoModelForCausalLM.from_pretrained(
            BASE_MODEL_ID,
            device_map="cpu",
            torch_dtype=torch.float32,
            trust_remote_code=True
        )
        
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained(
            BASE_MODEL_ID,
            trust_remote_code=True
        )
        
        # Load adapters
        print("Loading LoRA adapters...")
        model = PeftModel.from_pretrained(base_model, ADAPTER_PATH)
        print("✅ Loaded with Transformers + PEFT (CPU)")
        
    except Exception as e:
        print(f"❌ Critical Error loading model: {e}")
        sys.exit(1)

def run_generate(prompt):
    """Core generation helper"""
    device = "cuda" if USE_GPU else "cpu"
    inputs = tokenizer([prompt], return_tensors = "pt").to(device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens = 512,
            use_cache = True,
            temperature = 0.7,
            top_p = 0.9,
            do_sample = True
        )
    
    response = tokenizer.batch_decode(outputs)[0]
    
    # Cleaning
    response_start = response.find("### Response:")
    if response_start != -1:
        clean_response = response[response_start + len("### Response:"):].strip()
    else:
        clean_response = response
        
    if tokenizer.eos_token in clean_response:
        clean_response = clean_response.replace(tokenizer.eos_token, "").strip()
        
    return clean_response

def generate_comparison(instruction, patient_context, progress=gr.Progress()):
    """
    Generate responses from BOTH Base Model and Zima Fine-Tuned Model.
    """
    prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{patient_context}

### Response:
"""
    
    # We use a lock because we are modifying global model state (enabling/disabling adapters)
    with generate_lock:
        try:
            # 1. Generate with ZIMA (Adapters Active)
            progress(0.3, desc="Generating Zima Response...")
            
            # Ensure adapters are active
            if hasattr(model, "enable_adapter_layers"): # Unsloth 
                 # Unsloth is always active by default in this flow, usually handles it differently
                 # For Unsloth specifically, disabling is tricky dynamically without reloading sometimes
                 # So we might trust it's active.
                 pass
            elif hasattr(model, "enable_adapter"): # PEFT
                # Sometimes peft uses 'default' adapter name
                try: 
                    model.enable_adapter("default")
                except: 
                    pass
            
            zima_output = run_generate(prompt)
            
            # 2. Generate with BASE MODEL (Adapters Disabled)
            progress(0.7, desc="Generating Base Model Response...")
            
            if USE_GPU:
                # Unsloth specific disable
                # Unsloth doesn't easily support dynamic disable in 4bit inference mode same as PEFT
                # Hack: For Unsloth, we might just say "Not supported in 4bit optimized mode" or try a specific context
                # But actual PeftModel (CPU fallback) supports it perfectly.
                # Let's try PEFT context manager if applicable, or skip if strictly Unsloth objects don't support it
                try:
                    with model.disable_adapter():
                         base_output = run_generate(prompt)
                except:
                     base_output = "(Comparison not available in accelerated unsloth 4-bit mode)"
            else:
                # PEFT (CPU) supports this perfectly
                with model.disable_adapter():
                    base_output = run_generate(prompt)
                    
        except Exception as e:
            return f"Error: {e}", f"Error: {e}"

    return base_output, zima_output

# Define the Gradio Interface
# Note: theme moved to launch() in newer gradio, but kept here for compat with some versions.
# We will pass it to launch anyway to be safe? No, Blocks(theme=...) is standard.
# The error 'show_copy_button' suggests older gradio version or mismatch. We remove it for safety.

with gr.Blocks(theme=gr.themes.Soft(primary_hue="teal", secondary_hue="blue")) as app:
    gr.Markdown(
        """
        # 🏥 Zima Geriatric Health Assistant - Comparison Demo
        
        Compare the **Base Qwen 2.5 Model** versus the **Fine-Tuned Zima Model**.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=1):
            instruction_input = gr.Textbox(
                label="Health Question / Instruction",
                placeholder="e.g., What can I do about my swollen ankle?",
                lines=2
            )
            context_input = gr.Textbox(
                label="Patient Context (Age, Symptoms, Conditions)",
                placeholder="e.g., Patient is 76, twisted ankle yesterday, has mild pain.",
                lines=3
            )
            
            with gr.Accordion("System Info", open=True):
                 mode_label = "GPU (Accelerated)" if USE_GPU else "CPU (Compatibility Mode)"
                 gr.Markdown(f"**Running Mode:** {mode_label}")
                 gr.Markdown(f"**Adpaters:** Active")
            
            submit_btn = gr.Button("Compare Models", variant="primary", size="lg")
            
        with gr.Column(scale=1):
            with gr.Row():
                base_output = gr.Textbox(
                    label="🧠 Base Model (Generic)",
                    lines=12,
                    interactive=False
                )
                zima_output = gr.Textbox(
                    label="🏥 Zima (Fine-Tuned)",
                    lines=12,
                    interactive=False
                )
            
    # Example queries
    gr.Examples(
        examples=[
            ["What can I do about constipation?", "Patient is 73 years old, reports infrequent bowel movements."],
            ["I have a headache.", "Patient is 82, history of migraines, took aspirin 2 hours ago."],
            ["My knee hurts when I walk.", "Patient is 70, no history of injury, pain started 2 days ago."]
        ],
        inputs=[instruction_input, context_input]
    )

    submit_btn.click(
        fn=generate_comparison,
        inputs=[instruction_input, context_input],
        outputs=[base_output, zima_output]
    )

if __name__ == "__main__":
    print("Starting Gradio Server...")
    # share=True creates a public link
    app.launch(share=True)
