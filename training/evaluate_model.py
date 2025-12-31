#!/usr/bin/env python3
"""
Model Evaluation Script
Evaluate trained Qwen model on validation set
"""

import torch
from unsloth import FastLanguageModel
from datasets import load_dataset
from pathlib import Path
import json
from tqdm import tqdm
import time

# Paths - Lightning.ai compatible
DATA_DIR = Path("./data")
MODEL_DIR = Path("./outputs/zima_qwen_geriatric/final_model")
OUTPUT_FILE = Path("./outputs/evaluation_results.json")

# Config
MAX_SEQ_LENGTH = 512
NUM_SAMPLES = 50  # Number of samples to generate for manual review


def load_model(model_path: Path):
    """Load trained model"""
    print(f"📂 Loading model from: {model_path}")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=str(model_path),
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,
        load_in_4bit=True,
    )
    
    # Enable inference mode
    FastLanguageModel.for_inference(model)
    
    print("✅ Model loaded")
    return model, tokenizer


def extract_instruction_input(text: str) -> tuple:
    """Extract instruction and input from Alpaca-formatted text"""
    try:
        inst_start = text.find("### Instruction:") + len("### Instruction:")
        inst_end = text.find("### Input:")
        instruction = text[inst_start:inst_end].strip()
        
        input_start = text.find("### Input:") + len("### Input:")
        input_end = text.find("### Response:")
        input_text = text[input_start:input_end].strip()
        
        return instruction, input_text
    except:
        return "", ""


def generate_response(model, tokenizer, instruction: str, input_text: str = "") -> str:
    """Generate response for given instruction"""
    prompt = f"""Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input_text}

### Response:
"""
    
    inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=256,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
        use_cache=True,
    )
    
    response = tokenizer.batch_decode(outputs)[0]
    
    # Extract just the response part
    if "### Response:" in response:
        response = response.split("### Response:")[-1].strip()
        # Remove EOS token if present
        if tokenizer.eos_token in response:
            response = response.split(tokenizer.eos_token)[0].strip()
    
    return response


def calculate_perplexity(model, tokenizer, dataset, max_samples=100):
    """Calculate perplexity on validation set"""
    print(f"\n📊 Calculating perplexity on {max_samples} samples...")
    
    total_loss = 0
    total_tokens = 0
    
    for i, sample in enumerate(tqdm(dataset.select(range(min(max_samples, len(dataset)))))):
        text = sample["text"]
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_SEQ_LENGTH).to("cuda")
        
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss
            total_loss += loss.item() * inputs["input_ids"].size(1)
            total_tokens += inputs["input_ids"].size(1)
    
    perplexity = torch.exp(torch.tensor(total_loss / total_tokens))
    return perplexity.item()


def main():
    print("="*70)
    print("ZIMA GERIATRIC HEALTH ASSISTANT - MODEL EVALUATION")
    print("="*70)
    
    # Load validation data
    print("\n📂 Loading validation dataset...")
    dataset = load_dataset(
        "json",
        data_files={"validation": str(DATA_DIR / "validation.jsonl")}
    )["validation"]
    
    print(f"✅ Loaded {len(dataset)} validation samples")
    
    # Load model
    model, tokenizer = load_model(MODEL_DIR)
    
    # Calculate perplexity
    perplexity = calculate_perplexity(model, tokenizer, dataset, max_samples=100)
    print(f"\n📈 Perplexity: {perplexity:.2f}")
    
    # Generate sample responses
    print(f"\n🎯 Generating {NUM_SAMPLES} sample responses...")
    
    samples = []
    for i in tqdm(range(min(NUM_SAMPLES, len(dataset)))):
        sample = dataset[i]
        instruction, input_text = extract_instruction_input(sample["text"])
        
        # Extract expected output
        expected = sample["output"]
        
        # Generate response
        start_time = time.time()
        generated = generate_response(model, tokenizer, instruction, input_text)
        gen_time = time.time() - start_time
        
        samples.append({
            "instruction": instruction,
            "input": input_text,
            "expected": expected,
            "generated": generated,
            "generation_time": f"{gen_time:.2f}s"
        })
    
    # Save results
    print(f"\n💾 Saving evaluation results...")
    
    results = {
        "perplexity": perplexity,
        "validation_samples": len(dataset),
        "generated_samples": len(samples),
        "samples": samples
    }
    
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Results saved to: {OUTPUT_FILE}")
    
    # Print sample outputs
    print("\n" + "="*70)
    print("SAMPLE OUTPUTS (First 3)")
    print("="*70)
    
    for i, sample in enumerate(samples[:3]):
        print(f"\n【Sample {i+1}】")
        print(f"Instruction: {sample['instruction']}")
        if sample['input']:
            print(f"Input: {sample['input']}")
        print(f"\n✅ Expected:\n{sample['expected']}")
        print(f"\n🤖 Generated:\n{sample['generated']}")
        print(f"\n⏱️  Time: {sample['generation_time']}")
        print("-" * 70)
    
    print("\n" + "="*70)
    print("✅ EVALUATION COMPLETE!")
    print("="*70)
    print(f"\n📊 Summary:")
    print(f"   Perplexity: {perplexity:.2f}")
    print(f"   Samples evaluated: {len(samples)}")
    print(f"   Results: {OUTPUT_FILE}")
    print(f"\n💡 Review the samples to assess quality!")


if __name__ == "__main__":
    main()
