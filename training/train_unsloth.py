#!/usr/bin/env python3
"""
Unsloth Training Script for Lightning.ai
Fine-tune Qwen 2.5 1.5B on geriatric health data
Optimized for NVIDIA L40 GPU
"""

import torch
from unsloth import FastLanguageModel, is_bfloat16_supported
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
from pathlib import Path
import json

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths - Lightning.ai compatible
DATA_DIR = Path("./data")
OUTPUT_DIR = Path("./outputs/zima_qwen_geriatric")
CHECKPOINT_DIR = Path("./checkpoints")

# Model Config
MODEL_NAME = "unsloth/Qwen2.5-1.5B-Instruct"
MAX_SEQ_LENGTH = 512
DTYPE = None  # Auto-detect
LOAD_IN_4BIT = True  # Use 4-bit quantization for efficiency

# LoRA Config
LORA_R = 16  # Rank
LORA_ALPHA = 32  # Alpha (typically 2x rank)
LORA_DROPOUT = 0.05
TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", 
                  "gate_proj", "up_proj", "down_proj"]

# Training Config
BATCH_SIZE = 8  # Per device
GRADIENT_ACCUMULATION_STEPS = 4  # Effective batch = 32
LEARNING_RATE = 2e-4
NUM_EPOCHS = 3
WARMUP_STEPS = 50
LOGGING_STEPS = 10
EVAL_STEPS = 100
SAVE_STEPS = 200
MAX_GRAD_NORM = 1.0
WEIGHT_DECAY = 0.01
LR_SCHEDULER_TYPE = "cosine"

# ============================================================================
# MAIN
# ============================================================================

def print_gpu_stats():
    """Print GPU memory usage"""
    if torch.cuda.is_available():
        gpu_stats = torch.cuda.get_device_properties(0)
        print(f"\n🖥️  GPU: {gpu_stats.name}")
        print(f"   Total VRAM: {gpu_stats.total_memory / 1024**3:.2f} GB")
        print(f"   Allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
        print(f"   Cached: {torch.cuda.memory_reserved() / 1024**3:.2f} GB\n")


def load_data():
    """Load prepared datasets"""
    print("📂 Loading datasets...")
    
    dataset = load_dataset(
        "json",
        data_files={
            "train": str(DATA_DIR / "train.jsonl"),
            "validation": str(DATA_DIR / "validation.jsonl")
        }
    )
    
    print(f"✅ Loaded:")
    print(f"   Training: {len(dataset['train'])} samples")
    print(f"   Validation: {len(dataset['validation'])} samples")
    
    return dataset


def format_prompts(examples):
    """Format examples using the 'text' field (already formatted with Alpaca template)"""
    return {"text": examples["text"]}


def main():
    print("="*70)
    print("ZIMA GERIATRIC HEALTH ASSISTANT - UNSLOTH TRAINING")
    print("="*70)
    
    # GPU check
    print_gpu_stats()
    
    # Load datasets
    dataset = load_data()
    
    # Load model with Unsloth optimizations
    print(f"\n🚀 Loading model: {MODEL_NAME}")
    print(f"   4-bit quantization: {LOAD_IN_4BIT}")
    print(f"   Max sequence length: {MAX_SEQ_LENGTH}")
    
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=MODEL_NAME,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=DTYPE,
        load_in_4bit=LOAD_IN_4BIT,
    )
    
    # Add LoRA adapters
    print(f"\n🔧 Adding LoRA adapters...")
    print(f"   Rank: {LORA_R}")
    print(f"   Alpha: {LORA_ALPHA}")
    print(f"   Dropout: {LORA_DROPOUT}")
    print(f"   Target modules: {', '.join(TARGET_MODULES)}")
    
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        target_modules=TARGET_MODULES,
        lora_alpha=LORA_ALPHA,
        lora_dropout=LORA_DROPOUT,
        bias="none",
        use_gradient_checkpointing="unsloth",  # Unsloth's optimized checkpointing
        random_state=42,
    )
    
    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\n📊 Model parameters:")
    print(f"   Trainable: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
    print(f"   Total: {total_params:,}")
    
    # Training arguments
    print(f"\n⚙️  Training configuration:")
    print(f"   Batch size: {BATCH_SIZE} (effective: {BATCH_SIZE * GRADIENT_ACCUMULATION_STEPS})")
    print(f"   Learning rate: {LEARNING_RATE}")
    print(f"   Epochs: {NUM_EPOCHS}")
    print(f"   LR scheduler: {LR_SCHEDULER_TYPE}")
    
    training_args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRADIENT_ACCUMULATION_STEPS,
        warmup_steps=WARMUP_STEPS,
        num_train_epochs=NUM_EPOCHS,
        learning_rate=LEARNING_RATE,
        fp16=not is_bfloat16_supported(),
        bf16=is_bfloat16_supported(),
        logging_steps=LOGGING_STEPS,
        eval_steps=EVAL_STEPS,
        eval_strategy="steps",
        save_steps=SAVE_STEPS,
        save_total_limit=3,
        max_grad_norm=MAX_GRAD_NORM,
        weight_decay=WEIGHT_DECAY,
        lr_scheduler_type=LR_SCHEDULER_TYPE,
        seed=42,
        optim="adamw_8bit",  # 8-bit Adam optimizer
        report_to="tensorboard",
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
    )
    
    # Create trainer
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        args=training_args,
        packing=False,  # Don't pack samples (better for eval)
    )
    
    # Print memory before training
    print_gpu_stats()
    
    # Train!
    print("\n" + "="*70)
    print("🚀 STARTING TRAINING")
    print("="*70 + "\n")
    
    trainer.train()
    
    # Save final model
    print("\n" + "="*70)
    print("💾 SAVING MODEL")
    print("="*70)
    
    final_model_path = OUTPUT_DIR / "final_model"
    model.save_pretrained(str(final_model_path))
    tokenizer.save_pretrained(str(final_model_path))
    
    print(f"✅ Model saved to: {final_model_path}")
    
    # Save training info
    training_info = {
        "model_name": MODEL_NAME,
        "train_samples": len(dataset["train"]),
        "val_samples": len(dataset["validation"]),
        "epochs": NUM_EPOCHS,
        "batch_size": BATCH_SIZE,
        "learning_rate": LEARNING_RATE,
        "lora_r": LORA_R,
        "lora_alpha": LORA_ALPHA,
        "final_loss": trainer.state.log_history[-1].get("eval_loss", "N/A"),
    }
    
    with open(OUTPUT_DIR / "training_info.json", 'w') as f:
        json.dump(training_info, f, indent=2)
    
    # Final GPU stats
    print_gpu_stats()
    
    print("\n" + "="*70)
    print("✅ TRAINING COMPLETE!")
    print("="*70)
    print(f"\n📁 Output directory: {OUTPUT_DIR}")
    print(f"   - final_model/ (ready for inference)")
    print(f"   - training_info.json")
    print(f"   - checkpoints/ (intermediate saves)")
    print(f"\n🎉 Your Zima geriatric health model is ready!")


if __name__ == "__main__":
    main()
