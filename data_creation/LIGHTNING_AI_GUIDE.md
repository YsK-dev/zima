# Lightning.ai Data Generation Guide 🚀

## Solution

**Lightning.ai** gives you:
- ✅ **NVIDIA L40 GPU** (48GB VRAM - enterprise grade!)
- ✅ **4 hours FREE** compute time
- ✅ **No PC stress** (runs on their servers)
- ✅ **Fast generation** (~15,000-20,000 samples in 4 hours)

---
ı got samples of around  10,000 had some problems with enthernet connection and want it to leave some tokens for the next session 

## Quick Start (5 Steps)

### 1. Create Lightning.ai Studio

1. Go to: **https://lightning.ai/**
2. Sign up (free)
3. Click **"Create Studio"**
4. Select **GPU** runtime (should show NVIDIA L40)

### 2. Upload Files

In the Lightning.ai file browser, upload these files from your PC:

```
/home/ysk/Downloads/zima/
├── data_creation_lightning.py   ← Main script
├── setup_lightning.sh            ← Setup script
├── intents.json                  ← Your seed data
├── claude.json                   ← Your seed data
└── gemini.json                   ← Your seed data
```

**How to upload:**
- Click the **upload button** (folder icon) in Lightning.ai
- Select all 5 files above

### 3. Run Setup

Open a terminal in Lightning.ai and run:

```bash
chmod +x setup_lightning.sh
./setup_lightning.sh
```

**This will:**
- ✓ Install Ollama
- ✓ Pull Qwen 2.5 14B model (~10 minutes)
- ✓ Install Python packages
- ✓ Verify GPU

### 4. Start Generation

```bash
python data_creation_lightning.py
```

**Monitor progress** in another terminal:
```bash
# Check sample count every 10 seconds
watch -n 10 'wc -l synthetic_geriatric_data.jsonl'

# Check GPU usage
watch -n 5 nvidia-smi
```

### 5. Download Results

After 3-4 hours when generation completes:

1. **Right-click** on `synthetic_geriatric_data.jsonl`
2. **Select "Download"**
3. **Save to**: `/home/ysk/Downloads/zima/`

---

## What to Expect

### Speed Estimates

With **NVIDIA L40 GPU** and **Qwen 14B** model:

| Time | Samples | Notes |
|------|---------|-------|
| 1 hour | ~5,000 | Warmup + initial generation |
| 2 hours | ~10,000 | Steady state |
| 3 hours | ~15,000 | Full speed |
| **3.5 hrs** | **~18,000** | Script auto-stops here |

**To generate 50k samples:** Run this **3 times** over 3 days (you get 4 hours/day free)

### Console Output

```
======================================================================
LIGHTNING.AI GPU-ACCELERATED DATA GENERATION
======================================================================
Hardware: NVIDIA L40 GPU (48GB VRAM)
Model: qwen2.5:14b
Batch Size: 20 samples/call
Target: 50000 samples
Time Limit: 3.5 hours
======================================================================

Found 3 seed file(s):
  - intents.json: /home/studio/intents.json
  - claude.json: /home/studio/claude.json
  - gemini.json: /home/studio/gemini.json
Prepared 500 seed samples.

🚀 LIGHTNING.AI GPU MODE - NVIDIA L40
   Target: 50000 samples
   Batch size: 20 samples/call
   Time limit: 3.5 hours
   Model: qwen2.5:14b (GPU-accelerated)

[Batch 1] qwen2.5:14b | 0/50000
[Batch 51] qwen2.5:14b | 1000/50000

📊 Checkpoint 100
   Progress: 2000/50000 (4.0%)
   Speed: 2105 samples/hour
   ETA: 22.8 hours
   Time remaining: 3.3 hours

[Batch 151] qwen2.5:14b | 3000/50000
...
```

---

## GPU Optimization Details

### Why Qwen 14B?

| Model | Size | Speed | Quality | L40 VRAM Usage |
|-------|------|-------|---------|----------------|
| qwen2.5:3b | 1.9GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 4GB (8%) |
| qwen2.5:7b | 4.7GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 8GB (17%) |
| **qwen2.5:14b** | **8.5GB** | **⭐⭐⭐** | **⭐⭐⭐⭐⭐** | **12GB (25%)** ✓ |
| qwen2.5:32b | 19GB | ⭐⭐ | ⭐⭐⭐⭐⭐ | 28GB (58%) |

**Qwen 14B = Best balance** of quality and speed for L40 GPU.

### Optimizations Applied

1. **Batch size: 20** (vs 10) - Generate more per call
2. **Cooldown: 1s** (vs 30s) - L40 can handle continuous load
3. **max_tokens: 3000** (vs 800) - Larger responses
4. **No safety monitoring** - Lightning.ai has proper cooling
5. **GPU acceleration** - All compute on L40

---

## Multiple Session Strategy

Lightning.ai free tier: **4 hours/day**

To generate 50,000 samples:

### Session 1 (Today)
- Generate ~18,000 samples (3.5 hours)
- Download `synthetic_geriatric_data.jsonl`
- **Keep this file!**

### Session 2 (Tomorrow)
- Upload your **existing** `synthetic_geriatric_data.jsonl`
- Script will **append** to it
- Generate ~18,000 more (total: ~36,000)
- Download updated file

### Session 3 (Day 3)
- Upload `synthetic_geriatric_data.jsonl` from Session 2
- Generate final ~14,000 (total: **50,000** ✓)
- Download final file

---

## Monitoring & Debugging

### Check if Ollama is Running

```bash
pgrep -x ollama
# Should return a process ID
```

### Check Ollama Logs

```bash
tail -f /tmp/ollama.log
```

### Check GPU Status

```bash
nvidia-smi

# Should show:
# - GPU: NVIDIA L40
# - Memory: 48GB total
# - Utilization: 50-90% when running
```

### Check Generation Progress

```bash
# Live count
wc -l synthetic_geriatric_data.jsonl

# Sample one entry
head -1 synthetic_geriatric_data.jsonl | jq .
```

### If Generation Stops

```bash
# Restart Ollama
pkill ollama
sleep 5
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 10

# Resume generation (appends to file)
python data_creation_lightning.py
```

---

## Cost Analysis

| Platform | GPU | Free Tier | 50k Samples | Cost |
|----------|-----|-----------|-------------|------|
| Your PC | RX 550 | ∞ | **SHUTDOWN** ❌ | $0 |
| Colab | T4 | 12 hrs once | 2-3 days | $0 |
| **Lightning.ai** | **L40** | **4 hrs/day** | **3 days** | **$0** ✓ |
| AWS EC2 | A10G | None | 6 hours | ~$15 |

**Lightning.ai = Best FREE option!** 🏆

---

## Pro Tips

1. **Start generation immediately** after setup (maximize 4-hour window)
2. **Monitor GPU usage** with nvidia-smi to ensure it's being used
3. **Download ASAP** when session ends (files may be deleted)
4. **Save intermediate results** by downloading every hour
5. **Use screen/tmux** if you want to disconnect and reconnect

### Running in Background

```bash
# Install screen
sudo apt-get install -y screen

# Start screen session
screen -S datagen

# Run generation
python data_creation_lightning.py

# Detach: Press Ctrl+A, then D
# Reattach: screen -r datagen
```

---

## Files Reference

| File | Purpose | Size |
|------|---------|------|
| `data_creation_lightning.py` | Main generation script | 15KB |
| `setup_lightning.sh` | Installation script | 2KB |
| `intents.json` | Mental health seed data | Your file |
| `claude.json` | First aid seed data | Your file |
| `gemini.json` | Medical advice seed data | Your file |
| `synthetic_geriatric_data.jsonl` | **OUTPUT** | ~50MB for 50k samples |

---

## Next Steps

1. ✅ **Upload files to Lightning.ai Studio**
2. ✅ **Run `./setup_lightning.sh`**
3. ✅ **Run `python data_creation_lightning.py`**
4. ⏰ **Wait 3.5 hours**
5. 📥 **Download `synthetic_geriatric_data.jsonl`**
6. 🔁 **Repeat tomorrow for more samples**

**No more PC shutdowns! Let Lightning.ai's L40 GPU do the heavy lifting!** 💪🚀
