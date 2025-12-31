# Zima Geriatric Health Assistant - Training Guide

## 🚀 Quick Start on Lightning.ai

### Step 1: Upload Files to Lightning.ai

Upload these files to your Lightning.ai Studio:

```
training/
├── setup_training.sh     ← Setup script
├── prepare_data.py       ← Data preparation
├── train_unsloth.py      ← Training script
└── evaluate_model.py     ← Evaluation script

generated_data/
└── synthetic_geriatric_data (2).jsonl  ← Your 10,813 samples
```

### Step 2: Run Setup

Open terminal in Lightning.ai and run:

```bash
cd training
chmod +x setup_training.sh
./setup_training.sh
```

**Expected output:**
```
✅ Setup complete!
   GPU: NVIDIA L40
   VRAM: 48.0 GB
```

### Step 3: Prepare Data

```bash
python prepare_data.py
```

**Expected output:**
```
✅ Loaded 10813 samples
📊 Data Split:
   Training: 9731 samples (90%)
   Validation: 1082 samples (10%)
✅ Data preparation complete!
```

### Step 4: Start Training

```bash
python train_unsloth.py
```

**Training time:** 2-3 hours on L40 GPU

**Monitor progress:**
```bash
# In another terminal
watch -n 30 'tail -20 ../outputs/zima_qwen_geriatric/training.log'
```

### Step 5: Evaluate Model

After training completes:

```bash
python evaluate_model.py
```

---

## 📊 What to Expect

### Training Progress

```
Epoch 1/3:
  [████████████████████] Step 300/900 | Loss: 0.85 | ETA: 1.5h

Epoch 2/3:
  [████████████████████] Step 600/900 | Loss: 0.62 | ETA: 0.8h

Epoch 3/3:
  [████████████████████] Step 900/900 | Loss: 0.54 | Done!
```

### Expected Metrics

| Metric | Initial | Target | Final (Expected) |
|--------|---------|--------|------------------|
| Training Loss | ~2.5 | <0.8 | **~0.5-0.7** ✅ |
| Validation Loss | ~2.3 | <1.0 | **~0.6-0.9** ✅ |
| Perplexity | ~10-15 | <3.0 | **~2.0-2.5** ✅ |

### GPU Usage

| Phase | VRAM Usage | Utilization |
|-------|------------|-------------|
| Loading | 12-15 GB | 30% |
| Training | 20-25 GB | 80-95% |
| Inference | 8-12 GB | 40-60% |

---

## 📁 Output Structure

After training, you'll have:

```
outputs/
└── zima_qwen_geriatric/
    ├── final_model/           ← Trained model (download this!)
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   ├── tokenizer.json
    │   └── ...
    ├── checkpoint-200/        ← Intermediate checkpoints
    ├── checkpoint-400/
    ├── training_info.json     ← Training summary
    └── evaluation_results.json ← Evaluation metrics

data/
├── train.jsonl               ← Preprocessed training data
├── validation.jsonl          ← Preprocessed validation data
└── dataset_info.json
```

---

## 🔍 Monitoring Commands

### Check Training Progress

```bash
# Watch loss in real-time
tensorboard --logdir ../outputs/zima_qwen_geriatric --port 6006

# Count training steps completed
grep "Step" ../outputs/zima_qwen_geriatric/training.log | tail -1

# GPU usage
watch -n 5 nvidia-smi
```

### Check Data

```bash
# Verify data split
wc -l ../data/*.jsonl

# View sample
head -1 ../data/train.jsonl | jq .
```

---

## 🎯 Sample Output Quality

### Good Response Example ✅

**Input:**
```
Instruction: How can I prevent falls at home?
```

**Generated:**
```
Install handrails near stairs and in the bathroom. Use non-slip mats 
in the shower and bathtub. Keep floors clear of clutter and ensure 
good lighting throughout your home, especially in hallways and stairs.
```

### What to Look For

✅ **Specific actions** (install handrails, use mats)  
✅ **Age-appropriate** (simple language)  
✅ **Multiple suggestions** (3-5 concrete steps)  
✅ **Safety-focused** (no risky advice)  
✅ **Actionable** (can do today)  

❌ **Generic** ("Be careful")  
❌ **Too technical** (medical jargon)  
❌ **Just "see doctor"** (unless emergency)  

---

## ⚡ Tips for Lightning.ai

### Maximize Free Tier

- **Auto-stop:** Script stops at step 900 (fits in 3 hours)
- **Save often:** Checkpoints every 200 steps
- **Download early:** Get model before session ends
- **Monitor:** Watch VRAM to avoid OOM

### If Training Stops

```bash
# Resume from checkpoint
python train_unsloth.py --resume_from_checkpoint ../outputs/zima_qwen_geriatric/checkpoint-400
```

### If Out of Memory

Edit `train_unsloth.py`:
```python
BATCH_SIZE = 4  # Reduce from 8
GRADIENT_ACCUMULATION_STEPS = 8  # Increase from 4
```

---

## 🐛 Troubleshooting

### "CUDA out of memory"

**Solution:** Reduce batch size or enable more gradient checkpointing

### "Model not found"

**Solution:** Check paths are correct (`../data/`, `../outputs/`)

### "Dataset is empty"

**Solution:** Run `prepare_data.py` first

### Slow training (< 100 samples/hour)

**Solution:** Verify GPU is being used with `nvidia-smi`

---

## 📥 Download Trained Model

After training completes:

1. In Lightning.ai file browser, navigate to:
   ```
   outputs/zima_qwen_geriatric/final_model/
   ```

2. Right-click folder → **Download**

3. Save to your PC:
   ```
   /home/ysk/Downloads/zima/models/zima_qwen_geriatric/
   ```

---

## 🎓 Next Steps After Training

### 1. Evaluate Quality
```bash
python evaluate_model.py
# Review outputs/evaluation_results.json
```

### 2. Test Locally
```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "outputs/zima_qwen_geriatric/final_model",
    max_seq_length=512,
)

# Test it out!
instruction = "I keep forgetting to take my pills"
# ... (see evaluate_model.py for full code)
```

### 3. Quantize for Raspberry Pi 5
```bash
# Convert to GGUF format (4-bit quantization)
# Coming in next phase!
```

### 4. Deploy to RPi5
```bash
# Set up API server
# Coming in next phase!
```

---

## 📊 Training Log Example

```
GPU: NVIDIA L40
Total VRAM: 48.00 GB

Loading model: unsloth/Qwen2.5-1.5B-Instruct
✅ Model loaded

Adding LoRA adapters...
   Rank: 16
   Alpha: 32
   
Model parameters:
   Trainable: 12,845,056 (1.23%)
   Total: 1,543,987,200

Starting training...

Epoch 1/3:
  Step 100/900 | Loss: 1.24 | LR: 1.8e-4 | Time: 12:34
  Step 200/900 | Loss: 0.95 | LR: 2.0e-4 | Time: 25:08
  Step 300/900 | Loss: 0.78 | LR: 1.9e-4 | Time: 37:42

Epoch 2/3:
  Step 400/900 | Loss: 0.69 | LR: 1.6e-4 | Time: 50:16
  Step 500/900 | Loss: 0.63 | LR: 1.3e-4 | Time: 1:02:50
  Step 600/900 | Loss: 0.58 | LR: 9.2e-5 | Time: 1:15:24

Epoch 3/3:
  Step 700/900 | Loss: 0.55 | LR: 5.8e-5 | Time: 1:27:58
  Step 800/900 | Loss: 0.52 | LR: 2.4e-5 | Time: 1:40:32
  Step 900/900 | Loss: 0.51 | LR: 1.0e-6 | Time: 1:53:06

✅ Training complete!
Final validation loss: 0.67
```

---

**Ready to train your Zima model!** 🚀

*Estimated total time: 3-4 hours (setup + training + evaluation)*
