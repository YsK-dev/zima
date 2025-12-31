# Lightning.ai Setup Guide - Jupyter Notebook vs Terminal

## 🎯 Two Ways to Run

Lightning.ai has **2 interfaces**:

### Option 1: Jupyter Notebook (Recommended) ✅
- Visual interface with code cells
- **Use**: `lightning_ai_generation.ipynb`
- Commands need `!` prefix

### Option 2: Terminal/Console
- Command-line interface
- **Use**: `setup_lightning.sh` + `data_creation_lightning.py`
- No `!` prefix needed

---

## 📓 Jupyter Notebook Method (EASIEST)

### Upload Files:
```
✅ lightning_ai_generation.ipynb  ← Upload this notebook
✅ intents.json
✅ claude.json
✅ gemini.json
```

### Run:
1. Open `lightning_ai_generation.ipynb` in Lightning.ai
2. Click **"Run All"** or run cells one by one
3. Wait ~3.5 hours
4. Download `synthetic_geriatric_data.jsonl`

**That's it!** The notebook handles everything.

---

## 💻 Terminal Method (Alternative)

### Upload Files:
```
✅ data_creation_lightning.py
✅ setup_lightning.sh
✅ intents.json
✅ claude.json
✅ gemini.json
```

### Run in Terminal:
```bash
# Open Terminal in Lightning.ai (not notebook!)
chmod +x setup_lightning.sh
./setup_lightning.sh
python data_creation_lightning.py
```

---

## ⚠️ Common Error

**If you see this in Jupyter:**
```
SyntaxError: invalid syntax
chmod +x setup_lightning.sh
      ^
```

**Solution**: You're in a Jupyter notebook but using terminal commands!

Either:
1. ✅ **Use the notebook**: `lightning_ai_generation.ipynb`
2. ✅ **Add `!` prefix**: `!chmod +x setup_lightning.sh`
3. ✅ **Switch to Terminal**: Open a Terminal in Lightning.ai

---

## 🔧 Jupyter Shell Commands

In Jupyter notebooks, shell commands need `!`:

| Terminal | Jupyter Notebook |
|----------|------------------|
| `ls` | `!ls` |
| `chmod +x script.sh` | `!chmod +x script.sh` |
| `python script.py` | `!python script.py` |
| `nvidia-smi` | `!nvidia-smi` |

---

## 📋 Recommended Approach

**Use the Jupyter Notebook** (`lightning_ai_generation.ipynb`):

1. Upload `lightning_ai_generation.ipynb` + 3 seed JSON files
2. Open the notebook
3. Run all cells
4. Monitor progress in the output
5. Download results

**Why?**
- ✅ Easier (visual interface)
- ✅ All commands have correct `!` prefix
- ✅ Step-by-step with explanations
- ✅ Can see progress in real-time
- ✅ No syntax errors

---

## 🚀 Quick Start

1. **Go to**: https://lightning.ai/
2. **Create Studio** (GPU runtime)
3. **Upload**:
   - `lightning_ai_generation.ipynb`
   - `intents.json`
   - `claude.json`
   - `gemini.json`
4. **Open** `lightning_ai_generation.ipynb`
5. **Click** "Run All"
6. **Wait** ~3.5 hours
7. **Download** `synthetic_geriatric_data.jsonl`

---

**Use the notebook for a smoother experience!** 📓✨
