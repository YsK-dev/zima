# PC Shutdown Fix - Quick Summary

## 🚨 Problem
PC shuts down when running `data_creation_safe.py` despite safety measures.

## 🎯 Root Cause
1. **GPU not monitored** - RX 550 was overheating undetected
2. **Insufficient cooldowns** - Heat accumulated over time
3. **Too aggressive limits** - 80°C is already too hot
4. **No long-term heat management** - Continuous operation without breaks

## ✅ Solution
Created **ultra-safe** version with much more aggressive protection.

## 🚀 Quick Start

### Step 1: Run Quick Test (5-10 minutes)

```bash
# Terminal 1: Enhanced monitoring (with GPU temp tracking)
python3 monitor_enhanced.py

# Terminal 2: Quick stability test (50 samples)
python3 test_quick.py
```

**Watch Terminal 1 for:**
- 🟢 Green = Safe
- 🟡 Yellow = Warning
- 🔴 Red = Critical (script will auto-pause)

**If test completes successfully** → proceed to Step 2  
**If you see multiple 🔴 red warnings** → see "Alternative Approaches" below

---

### Step 2: Full Generation (After successful test)

```bash
# Terminal 1: Keep monitoring running
python3 monitor_enhanced.py

# Terminal 2: Full generation (50,000 samples, ~3-5 days)
python3 data_creation_ultra_safe.py
```

For long runs, use `screen` to survive disconnects:

```bash
screen -S zima
python3 monitor_enhanced.py &
python3 data_creation_ultra_safe.py
# Detach: Ctrl+A then D
# Re-attach later: screen -r zima
```

---

## 🛡️ What's Different in Ultra-Safe Mode?

| Feature | Old (Safe) | New (Ultra-Safe) |
|---------|-----------|------------------|
| RAM limit | 75% | **65%** |
| CPU temp limit | 80°C | **70°C** |
| GPU monitoring | ❌ None | ✅ **75°C limit** |
| Short cooldowns | Every 5 batches, 10s | Every 3 batches, **20s** |
| Long cooldowns | None | **60s every 10 batches** |
| Gemini/Qwen ratio | 50/50 | **80/20** (less local stress) |
| Warning cooldown | 60s | **90s (180s if persists)** |

---

## ⚠️ Alternative Approaches

### If Ultra-Safe Still Causes Issues:

#### Option A: Gemini-Only Mode (Recommended)
**Zero local compute** - eliminates all PC stress:

```bash
# Edit data_creation_ultra_safe.py line 23:
GEMINI_RATIO = 1.0  # 100% Gemini, 0% Qwen
```

**Pros:** 
- ✅ No PC stress at all
- ✅ Faster generation
- ✅ Guaranteed stability

**Cons:** 
- May hit API rate limits (unlikely with Gemini Flash)
- Uses API quota (but very cheap, ~$0.50-1.00 for 50K samples)

#### Option B: Improve Physical Cooling

**Immediate (Free):**
- Open case side panel
- Point desk fan at PC
- Clean dust from fans/filters

**Best Results (~$30-50):**
- Better CPU cooler (tower cooler)
- Additional case fans
- Reapply thermal paste

#### Option C: Micro-Batching

Generate in tiny chunks with long breaks:

```bash
# Generate 5,000 samples, then manually stop & cool for 1 hour
# Repeat 10 times to reach 50,000
TARGET_GENERATION_SIZE = 5000
```

---

## 📊 Monitoring

The enhanced monitor shows real-time stats:

```
[23:49:35] 🟢 CPU: 45% | 🟢 RAM: 52% | 🟢 CPU Temp: 68°C | 🟢 GPU Temp: 45°C | 🤖 Ollama: 2.8 GB
```

**What to watch:**
- CPU/GPU temps should stay in 🟢 green zone (<70°C)
- Multiple 🔴 red indicators = immediate danger
- Script will auto-pause on warnings

---

## 🔍 Troubleshooting

### Check current temps:
```bash
sensors
```

**Healthy idle temps:**
- CPU (Tctl): 40-50°C ✅
- GPU (edge): 35-45°C ✅

**If idle temps >60°C** → cooling problem, not software issue

### Verify Ollama CPU-only mode:
```bash
systemctl status ollama | grep -i gpu
```

Should show: `OLLAMA_NUM_GPU=0`

### Check for errors:
```bash
sudo journalctl -u ollama -n 50 --no-pager
```

---

## 📁 Files Created

1. **`data_creation_ultra_safe.py`** - Ultra-safe generation script
2. **`monitor_enhanced.py`** - Enhanced monitoring with GPU tracking
3. **`test_quick.py`** - Quick 5-minute stability test
4. **`ULTRA_SAFE_GUIDE.md`** - Comprehensive guide (read for details)
5. **`QUICK_FIX_SUMMARY.md`** - This file

---

## ⏱️ Expected Timeline

**Testing Phase:** 5-10 minutes  
**Full Generation (Ultra-Safe):** 3-5 days  
**Full Generation (Gemini-Only):** 2-3 days  

---

## 💡 Pro Tips

1. **Run at night** - Cooler ambient temperature = better thermals
2. **Monitor remotely** - SSH from phone to check progress
3. **Start with test** - Always validate with `test_quick.py` first
4. **Use screen/tmux** - Prevents loss if terminal disconnects
5. **Check daily** - Verify progress and temperatures

---

## 🆘 Emergency: If PC Gets Hot During Test

1. Press `Ctrl+C` in Terminal 2 (stop generation)
2. Let PC idle for 10 minutes
3. Check temps: `sensors`
4. **If idle temps >60°C** → Physical cooling issue
5. **If idle temps <50°C** → Try Gemini-only mode

---

## ✅ Next Steps

1. **Right now:** Run `test_quick.py` (5-10 min)
2. **If test passes:** Start full generation with `data_creation_ultra_safe.py`
3. **If test shows warnings:** Try Gemini-only mode or improve cooling
4. **Read for details:** `ULTRA_SAFE_GUIDE.md`

**Good luck! 🚀**

---

Last updated: 2025-12-30 23:49  
Hardware: Ryzen 9 5900X, 31GB RAM, RX 550 GPU
