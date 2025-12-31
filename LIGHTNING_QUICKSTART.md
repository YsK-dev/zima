# 🚀 LIGHTNING.AI SETUP - Quick Reference

## What You Need to Upload

From your PC (`/home/ysk/Downloads/zima/`), upload these **5 files** to Lightning.ai:

```
✅ data_creation_lightning.py    (Main script - 100% local)
✅ setup_lightning.sh             (Setup script)
✅ intents.json                   (Your seed data)
✅ claude.json                    (Your seed data)
✅ gemini.json                    (Your seed data)
```

---

## 3 Simple Commands

Once files are uploaded, run these **in order**:

### 1️⃣ Setup (First time only - ~10 min)
```bash
chmod +x setup_lightning.sh
./setup_lightning.sh
```

### 2️⃣ Generate Data (~3.5 hours)
```bash
python data_creation_lightning.py
```

### 3️⃣ Download Result
Right-click `synthetic_geriatric_data.jsonl` → Download

---

## Expected Results

**100% Local GPU Generation** (No API limits!)

| Session | Runtime | Samples Generated | Total |
|---------|---------|-------------------|-------|
| Day 1 | 3.5 hrs | ~18,000 | 18,000 |
| Day 2 | 3.5 hrs | ~18,000 | 36,000 |
| Day 3 | 3.5 hrs | ~14,000 | **50,000** ✓ |

---

## Key Advantages

✅ **100% Local** - No external API dependencies  
✅ **No quota limits** - Generate as much as the GPU allows  
✅ **Faster** - GPU-accelerated Qwen 14B model  
✅ **No API keys needed** - Pure local generation  
✅ **No rate limits** - Continuous generation  

---

## Monitoring (Optional)

### Check Progress
```bash
watch -n 10 'wc -l synthetic_geriatric_data.jsonl'
```

### Check GPU Usage
```bash
watch -n 5 nvidia-smi
```

---

## Why This Works

| Your PC | Lightning.ai |
|---------|--------------|
| ❌ RX 550 (2GB) | ✅ **NVIDIA L40 (48GB)** |
| ❌ Shutdowns | ✅ **Stable** |
| ❌ Safety limits | ✅ **Full speed** |
| ❌ Slow | ✅ **~5,000 samples/hour** |
| ❌ API quotas | ✅ **No quotas** |

**No more PC shutdowns! No more API limits!** 🎉

---

## Support

- **Full Guide**: Read `LIGHTNING_AI_GUIDE.md`
- **Lightning.ai**: https://lightning.ai/
- **Free tier**: 4 GPU hours/day

---

**Ready? Go to lightning.ai and create your Studio now!** →
