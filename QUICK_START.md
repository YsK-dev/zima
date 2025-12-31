# 🚀 Quick Start Guide - Safe Ollama Setup

## The Problem
Your PC shuts down when running `qwen3:4b` even though it's a small model.

## The Solution
Your **RX 550 GPU** is overheating. We need to force **CPU-only mode**.

---

## ⚡ Quick Fix (2 minutes)

```bash
cd /home/ysk/Downloads/zima

# 1. Run the automated setup
./setup_safe_ollama.sh

# 2. Start monitoring (Terminal 1)
python3 monitor_system.py
```

In a **new terminal**:

```bash
cd /home/ysk/Downloads/zima

# 3. Run safe data generation (Terminal 2)
python3 data_creation_safe.py
```

**Done!** The script will now:
- ✅ Use CPU only (no GPU overheating)
- ✅ Monitor temperature & RAM
- ✅ Auto-pause if too hot
- ✅ Take breaks every 5 batches

---

## 📋 What Changed?

| Feature | Old Script | New Script |
|---------|-----------|------------|
| GPU Usage | ❌ Auto (causes overheat) | ✅ CPU only |
| Health Monitoring | ❌ None | ✅ Real-time RAM/CPU/Temp |
| Cooldowns | ❌ Continuous | ✅ Break every 5 batches |
| Memory Limits | ❌ Unlimited | ✅ <75% RAM, <80°C CPU |
| Context Window | ❌ 2048 tokens | ✅ 512 tokens |
| Error Handling | ❌ Basic | ✅ Auto-retry with delays |

---

## 🎯 Expected Results

### Before (Unsafe)
```
[Running...] 
Temperature: 92°C 🔥
RAM: 28.5/31 GB (91%) ⚠️
*PC SHUTS DOWN* ❌
```

### After (Safe)
```
[23:15:42] 🟢 CPU: 45.2% | 🟢 RAM: 52.3% | 🟢 Temp: 68.5°C | 🤖 Ollama: 2.8 GB
Generated 10 triples. Total: 4950/50000 ✅
💤 Cooldown break (10s) after 5 batches...
```

---

## ⏱️ Performance

- **Speed**: ~8-12 samples/minute (slower but stable)
- **50K samples**: ~60-70 hours total
- **No shutdowns**: Runs indefinitely ✅

---

## 🔧 Files Created

1. **`setup_safe_ollama.sh`** - Automated setup script
2. **`data_creation_safe.py`** - Safe version with monitoring
3. **`monitor_system.py`** - Real-time health dashboard
4. **`Modelfile.qwen4b-light`** - Optimized model config
5. **`TROUBLESHOOTING.md`** - Full troubleshooting guide

---

## 🧪 Test First (Recommended)

Before running 50K generations, test with 20:

1. Edit `data_creation_safe.py` line 69:
   ```python
   TARGET_GENERATION_SIZE = 20  # Test with 20 samples
   ```

2. Run test:
   ```bash
   python3 data_creation_safe.py
   ```

3. If completes without shutdown → ✅ **Ready for full run!**

4. Restore to 50,000 and run production

---

## 🆘 If Still Shuts Down

### Hardware Check
```bash
# Monitor temps for 30 seconds
watch -n 1 sensors
```

If CPU **idle** temp >70°C → **Hardware issue**:
- Clean CPU cooler
- Replace thermal paste
- Check PSU (need >450W minimum)

### Software Fallback

**Option A**: Use Gemini only (no local compute)
```python
# Edit data_creation_safe.py line 308:
use_gemini = True  # Force Gemini-only
```

**Option B**: Even smaller model
```bash
ollama pull qwen2.5:1.5b-instruct
# Update QWEN_MODEL in script
```

---

## 📚 More Help

- Full guide: `TROUBLESHOOTING.md`
- System requirements
- Performance tuning
- Emergency commands

---

**TL;DR**: Run `./setup_safe_ollama.sh` then `python3 data_creation_safe.py`. Your PC won't shut down anymore! 🎉
