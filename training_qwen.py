import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer
import os

# --- Configuration ---
MODEL_NAME = "Qwen/Qwen3-1.7b-Instruct"
DATASET_PATH = "train_data.jsonl"
OUTPUT_DIR = "./zima-qwen3-finetuned"

def train():
    # 1. Load Dataset
    print(f"Loading dataset from {DATASET_PATH}...")
    dataset = load_dataset("json", data_files=DATASET_PATH, split="train")

    # 2. Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token

    # 3. Model with 8-bit Quantization (to fit in free GPU)
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
    )

    print(f"Loading model {MODEL_NAME}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )

    model = prepare_model_for_kbit_training(model)

    # 4. LoRA Configuration
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )

    model = get_peft_model(model, peft_config)

    # 5. Training Arguments
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        logging_steps=10,
        num_train_epochs=3,
        save_steps=100,
        eval_strategy="no",
        fp16=True,
        push_to_hub=False,
        report_to="none"
    )

    # 6. Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="instruction", # Simple mapping, should ideally use a template
        max_seq_length=512,
        tokenizer=tokenizer,
        args=training_args,
    )

    # 7. Start Training
    print("Starting training...")
    trainer.train()

    # 8. Save Model
    print(f"Saving model to {OUTPUT_DIR}...")
    trainer.model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print("Training complete!")

if __name__ == "__main__":
    train()
