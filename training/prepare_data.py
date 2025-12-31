#!/usr/bin/env python3
"""
Data Preparation Script for Unsloth Fine-tuning
Prepares synthetic geriatric data for training Qwen 1.7B
"""

import json
import random
from pathlib import Path
from typing import Dict, List
from datasets import Dataset

# Paths - Lightning.ai compatible (current directory)
DATA_DIR = Path(".")
OUTPUT_DIR = Path("./data")
INPUT_FILE = "synthetic_geriatric_data (2).jsonl"

# Config
TRAIN_SPLIT = 0.9
RANDOM_SEED = 42

# Alpaca-style prompt template for Qwen
ALPACA_PROMPT = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Input:
{input}

### Response:
{output}"""


def load_jsonl(file_path: Path) -> List[Dict]:
    """Load JSONL file into list of dicts, filtering out invalid samples"""
    print(f"📂 Loading data from: {file_path}")
    
    data = []
    skipped = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                sample = json.loads(line.strip())
                # Filter out samples with missing or empty outputs
                if not sample.get("output") or len(sample.get("output", "").strip()) < 10:
                    skipped += 1
                    continue
                data.append(sample)
            except json.JSONDecodeError as e:
                print(f"⚠️  Skipping line {i}: {e}")
                skipped += 1
                continue
    
    print(f"✅ Loaded {len(data)} valid samples")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} samples with missing/empty outputs")
    return data


def format_sample(sample: Dict) -> Dict:
    """Format sample with Alpaca prompt template"""
    return {
        "text": ALPACA_PROMPT.format(
            instruction=sample["instruction"],
            input=sample.get("input", ""),
            output=sample["output"]
        ),
        "instruction": sample["instruction"],
        "input": sample.get("input", ""),
        "output": sample["output"]
    }


def split_data(data: List[Dict], train_ratio: float = 0.9) -> tuple:
    """Split data into train and validation sets"""
    random.seed(RANDOM_SEED)
    random.shuffle(data)
    
    split_idx = int(len(data) * train_ratio)
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    
    print(f"\n📊 Data Split:")
    print(f"   Training: {len(train_data)} samples ({train_ratio*100:.0f}%)")
    print(f"   Validation: {len(val_data)} samples ({(1-train_ratio)*100:.0f}%)")
    
    return train_data, val_data


def save_jsonl(data: List[Dict], output_path: Path):
    """Save data to JSONL file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        for sample in data:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"💾 Saved to: {output_path}")


def create_hf_dataset(data: List[Dict]) -> Dataset:
    """Create HuggingFace Dataset"""
    return Dataset.from_list(data)


def validate_data(data: List[Dict]):
    """Validate data quality"""
    print("\n🔍 Validating data...")
    
    required_fields = ["instruction", "output"]
    issues = []
    
    for i, sample in enumerate(data):
        # Check required fields
        for field in required_fields:
            if field not in sample or not sample[field]:
                issues.append(f"Sample {i}: Missing or empty '{field}'")
        
        # Check reasonable length
        if len(sample.get("output", "")) < 10:
            issues.append(f"Sample {i}: Output too short ({len(sample['output'])} chars)")
    
    if issues:
        print(f"⚠️  Found {len(issues)} issues:")
        for issue in issues[:10]:  # Show first 10
            print(f"   - {issue}")
        if len(issues) > 10:
            print(f"   ... and {len(issues) - 10} more")
    else:
        print("✅ All samples validated successfully")
    
    return len(issues) == 0


def main():
    print("="*70)
    print("ZIMA GERIATRIC HEALTH ASSISTANT - DATA PREPARATION")
    print("="*70)
    
    # Load data
    raw_data = load_jsonl(INPUT_FILE)
    
    # Validate
    if not validate_data(raw_data):
        print("\n⚠️  Data has validation issues but continuing...")
    
    # Format samples
    print(f"\n🔄 Formatting {len(raw_data)} samples with Alpaca template...")
    formatted_data = [format_sample(sample) for sample in raw_data]
    
    # Split
    train_data, val_data = split_data(formatted_data, TRAIN_SPLIT)
    
    # Save to JSONL
    print(f"\n💾 Saving processed data...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    save_jsonl(train_data, OUTPUT_DIR / "train.jsonl")
    save_jsonl(val_data, OUTPUT_DIR / "validation.jsonl")
    
    # Create HF datasets
    print(f"\n📦 Creating HuggingFace Datasets...")
    train_dataset = create_hf_dataset(train_data)
    val_dataset = create_hf_dataset(val_data)
    
    # Save dataset info
    dataset_info = {
        "total_samples": len(raw_data),
        "train_samples": len(train_data),
        "val_samples": len(val_data),
        "train_split": TRAIN_SPLIT,
        "random_seed": RANDOM_SEED,
        "source_file": str(INPUT_FILE),
        "fields": ["text", "instruction", "input", "output"]
    }
    
    with open(OUTPUT_DIR / "dataset_info.json", 'w') as f:
        json.dump(dataset_info, f, indent=2)
    
    # Print sample
    print(f"\n📄 Sample formatted data:")
    print("-" * 70)
    print(train_data[0]["text"][:500] + "...")
    print("-" * 70)
    
    # Summary
    print(f"\n✅ Data preparation complete!")
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"   - train.jsonl ({len(train_data)} samples)")
    print(f"   - validation.jsonl ({len(val_data)} samples)")
    print(f"   - dataset_info.json")
    print(f"\n🚀 Ready for training!")
    print("="*70)


if __name__ == "__main__":
    main()
