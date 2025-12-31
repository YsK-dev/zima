# Zima Training Pipeline - Quick Start

## ⚡ Lightning.ai Setup (5 minutes)

### 1. Upload to Lightning.ai

Upload entire `training/` folder and `generated_data/` folder to Lightning.ai Studio.

### 2. Run Commands

```bash
cd training
./setup_training.sh          # Install dependencies (2-3 min)
python train_unsloth.py      # Train model (2-3 hours)
python evaluate_model.py     # Evaluate (5 min)
```

### 3. Download Model

After training:
- Right-click `outputs/zima_qwen_geriatric/final_model/`
- Download to your PC

---

## 📊 Expected Results

- **Training time**: 2-3 hours on L40 GPU
- **Final loss**: ~0.5-0.7
- **Perplexity**: ~2.0-2.5
- **Model size**: ~3GB (with LoRA adapters)

---

## 📁 What You'll Get

```
outputs/zima_qwen_geriatric/
└── final_model/              ← Download this!
    ├── adapter_model.safetensors
    ├── adapter_config.json
    ├── tokenizer files
    └── ...
```

---

## 🔍 Monitor Training

```bash
# Watch GPU
nvidia-smi

# Watch progress
tail -f ../train ing/train.log
```

---

**Full guide:** See `TRAINING_GUIDE.md` for detailed instructions.
