# 🏥 Zima - Geriatric Health Assistant

A fine-tuned AI model to provide compassionate, actionable health advice for elderly individuals (70+).

## 🎯 Project Overview

**Model**: Qwen 2.5 1.5B fine-tuned with LoRA  
**Dataset**: 10,743 synthetic samples  
**Perplexity**: 1.51 (excellent)  

## 🔗 HuggingFace

- **Model**: [YsK-dev/zima-qwen-geriatric-1.5b](https://huggingface.co/YsK-dev/zima-qwen-geriatric-1.5b)
- **Dataset**: [YsK-dev/geriatric-health-advice](https://huggingface.co/datasets/YsK-dev/geriatric-health-advice)

## 📁 Project Structure

```
zima/
├── data_creation/           # Data generation scripts
│   ├── data_creation_lightning.py  # Main generation script
│   ├── setup_lightning.sh          # Lightning.ai setup
│   └── LIGHTNING_AI_GUIDE.md       # Usage guide
│
├── training/                # Model training
│   ├── prepare_data.py      # Data preprocessing
│   ├── train_unsloth.py     # Unsloth fine-tuning
│   ├── evaluate_model.py    # Model evaluation
│   └── setup_training.sh    # Environment setup
│
├── generated_data/          # Training data
│   └── synthetic_geriatric_data (2).jsonl
│
├── seed_data/               # Initial seed prompts
│
├── trainde_model/Model files (LoRA adapter):
│   ├── adapter_model.safetensors
│   ├── adapter_config.json
│   └── tokenizer files
│
├── MODEL_CARD.md            # HuggingFace model docs
├── DATASET_CARD.md          # HuggingFace dataset docs
```

## 🚀 Quick Start

### Load from HuggingFace

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "YsK-dev/zima-qwen-geriatric-1.5b",
    max_seq_length=512,
    load_in_4bit=True,
)
```

### Replicate Training

```bash
# 1. Generate data (Lightning.ai)
cd data_creation
./setup_lightning.sh
python data_creation_lightning.py

# 2. Train model (Lightning.ai)
cd training
./setup_training.sh
python prepare_data.py
python train_unsloth.py
python evaluate_model.py
```

## 📊 Results

| Metric | Value |
|--------|-------|
| Training Loss | 0.32 |
| Validation Loss | 0.40 |
| Perplexity | 1.51 |
| Samples | 10,743 |

## 📄 License

Apache 2.0