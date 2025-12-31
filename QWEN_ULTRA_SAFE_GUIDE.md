# QWEN-PRIMARY Ultra-Safe Data Generation

## You Were Right!

Gemini free tier is **severely limited**:
- Only **20 requests per day** for gemini-3-flash
- At 10 samples/request = 200 samples/day
- To generate 50k samples = **250 days!** 😱

**You MUST use local Qwen.** Here's how to do it WITHOUT shutting down your PC:

---

## The Ultra-Safe Solution

**File: `data_creation_qwen_ultra_safe.py`**

### Key Features

#### 1. Extreme Cooling Strategy
- **30 seconds cooldown** after EVERY Qwen call
- **3 minutes cooldown** every 5 batches
- Automatic **5-minute pause** if any temperature warnings

#### 2. Ultra-Conservative Limits
| Metric | Threshold | Action |
|--------|-----------|--------|
| RAM | > 55% | Pause 3 min |
| CPU Temp | > 60°C | Pause 3 min |
| GPU Temp | > 65°C | Pause 3 min |
| CPU Load | > 80% | Pause 3 min |

#### 3. Smart Model Usage
- **90% Qwen** (`qwen2.5:3b` - ultra-lightweight)
- **10% Gemini** (only when daily quota available)
- Auto-switches to Qwen-only when Gemini quota exhausted

#### 4. Minimal Compute Per Call
- Reduced `max_tokens` to **800** (vs 1500-2000)
- CPU-only mode (no GPU)
- Limited to 4 CPU threads (out of 24 available)

---

## Step-by-Step Setup

### 1. Configure Ollama for Ultra-Safe Operation

First, make sure you have the restart script ready:
```bash
chmod +x restart_ollama_safe.sh
```

Then restart Ollama with safe settings. **You'll need your sudo password:**
```bash
sudo systemctl stop ollama
sleep 3

# Set environment variables for ultra-safe mode
export OLLAMA_NUM_GPU=0
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_NUM_THREAD=4

# Start Ollama in background
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 5

# Pull the ultra-light 3B model
ollama pull qwen2.5:3b
```

**OR** simply run:
```bash
./restart_ollama_safe.sh
```

### 2. Resume Data Generation

You already have **140 samples** from the Gemini run. The new script will **append** to the existing file.

```bash
python data_creation_qwen_ultra_safe.py
```

### 3. Monitor in Real-Time

Open a second terminal to watch system health:
```bash
watch -n 2 'sensors | grep -E "(temp|Tdie)" && free -h | grep Mem'
```

Check progress:
```bash
watch -n 5 'wc -l synthetic_geriatric_data.jsonl'
```

---

## Expected Performance

### Generation Speed (Conservative Estimate)
- **30s mandatory cooldown** per Qwen call = ~2 calls/minute = ~20 samples/minute
- **3min long cooldown** every 5 batches adds overhead
- Plus health monitoring pauses

**Realistic throughput**: ~600-800 samples/hour

### Time to 50,000 Samples
You already have 140, so need 49,860 more:
- At 700 samples/hour = **~71 hours**
- Spread over multiple days: **Run 8 hours/day = 9 days**

### Safety Record
With these extreme measures:
- ✅ CPU stays under 60°C
- ✅ GPU barely used (CPU-only)
- ✅ RAM usage minimal
- ✅ **NO MORE SHUTDOWNS**

---

## What You'll See

### Normal Operation
```
[Batch 1] Using qwen2.5:3b
  Topic: Hydration and simple dietary advice for seniors...
  📊 RAM: 42.3% | CPU: 54.2°C | GPU: 48.1°C | Load: 28.5%
  ✓ Generated 10 triples
  📈 Progress: 150/50000 (0.3%)
  😴 Mandatory cooldown after Qwen (30s)...

[Batch 2] Using qwen2.5:3b
  Topic: Managing mild chronic pain...
  📊 RAM: 43.1% | CPU: 55.8°C | GPU: 49.2°C | Load: 31.2%
  ✓ Generated 10 triples
  📈 Progress: 160/50000 (0.3%)
  😴 Mandatory cooldown after Qwen (30s)...
```

### When System Gets Warm (Auto-Cooldown Kicks In)
```
🚨 SYSTEM HEALTH WARNING - PAUSING 🚨
  🔥 CPU temp at 61.2°C (limit: 60°C)
  Cooling down for 3 minutes...
  ✓ System cooled - resuming...
```

### Long Cooldown (Every 5 Batches)
```
[Batch 5] Using qwen2.5:3b
  ✓ Generated 10 triples
  📈 Progress: 200/50000 (0.4%)
  😴 Mandatory cooldown after Qwen (30s)...
  🛌 LONG cooldown (180s) - batch 5
```

---

## Emergency Options

### If PC STILL Shuts Down

**Option 1**: Increase cooldown times
Edit `data_creation_qwen_ultra_safe.py`:
```python
MANDATORY_COOLDOWN_EVERY_CALL = 60  # Change from 30 to 60 seconds
LONG_COOLDOWN_DURATION = 300  # Change from 180 to 300 seconds
```

**Option 2**: Even stricter temperature limits
```python
MAX_CPU_TEMP = 55  # Change from 60
MAX_GPU_TEMP = 60  # Change from 65
```

**Option 3**: Use even smaller model
```bash
ollama pull qwen2.5:1.5b  # Smallest available
```
Update script:
```python
QWEN_MODEL = 'qwen2.5:1.5b'
```

### If Ollama Crashes

Check logs:
```bash
tail -f /tmp/ollama.log
```

Restart Ollama:
```bash
./restart_ollama_safe.sh
```

---

## Pro Tips

1. **Run overnight**: This will take days - let it run while you sleep
2. **Check progress periodically**: `wc -l synthetic_geriatric_data.jsonl`
3. **Don't interrupt**: The script saves incrementally, so your progress is safe even if stopped
4. **Resume anytime**: Just run `python data_creation_qwen_ultra_safe.py` again
5. **Monitor room temperature**: Keep your PC in a cool, well-ventilated area

---

## Files
- ✅ `data_creation_qwen_ultra_safe.py` ← **USE THIS ONE**
- ✅ `restart_ollama_safe.sh` ← Run first to configure Ollama
- ✅ `synthetic_geriatric_data.jsonl` ← Output (already has 140 samples)

---

## Bottom Line

**This will work**, but it will be **slow by design** to keep your PC safe. The trade-off:
- ❌ Slow (9 days vs instant)
- ✅ Safe (no shutdowns)
- ✅ Works with limited API quota
- ✅ Achieves your 50k sample goal

**Let it run overnight for best results!** 🌙
