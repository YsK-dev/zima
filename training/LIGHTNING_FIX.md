# ✅ All Lightning.ai Path Fixes Applied

## Files Updated

### 1. prepare_data.py
```python
DATA_DIR = Path(".")  # Current directory
OUTPUT_DIR = Path("./data")
INPUT_FILE = "synthetic_geriatric_data (2).jsonl"
```

### 2. train_unsloth.py
```python
DATA_DIR = Path("./data")
OUTPUT_DIR = Path("./outputs/zima_qwen_geriatric")
CHECKPOINT_DIR = Path("./checkpoints")
```

### 3. evaluate_model.py
```python
DATA_DIR = Path("./data")
MODEL_DIR = Path("./outputs/zima_qwen_geriatric/final_model")
OUTPUT_FILE = Path("./outputs/evaluation_results.json")
```

---

##  Now Run Training!

```bash
python train_unsloth.py
```

**Expected:**
- Training starts immediately
- GPU: NVIDIA L4 (22GB VRAM) - perfect for this task!
- Training time: ~2-3 hours
- Final model in: `./outputs/zima_qwen_geriatric/final_model/`

**Monitor progress in another terminal:**
```bash
watch -n 30 nvidia-smi
```

---

## Results Summary

- ✅ **10,743 valid samples** (70 bad ones auto-filtered)
- ✅ **9,700 training** / 1,078 validation
- ✅ **All paths fixed** for Lightning.ai
- ✅ **Ready for 2-3 hour training run!**

🚀 Let's train your geriatric health model!
