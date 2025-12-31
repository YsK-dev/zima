# Gemini-Primary Data Generation (Safe for Limited API)

## The Problem
- Local Qwen models cause PC shutdowns due to CPU/GPU stress
- Gemini API has usage limits
- Need to balance cloud vs local generation

## The Solution
**`data_creation_gemini_primary.py`** uses:
- **95% Gemini API** (fast, cloud-based, no hardware stress)
- **5% Local Qwen** (ultra-rare, with extreme safety measures)

## Safety Features

### For Gemini (95% of calls)
- ✓ No hardware stress
- ✓ Fast generation
- ✓ 5-second cooldown between batches

### For Qwen (5% of calls)
- ✓ Limited to **max 10 calls per hour**
- ✓ Uses ultra-light **qwen2.5:3b** model (smaller than 4b)
- ✓ **2-minute mandatory cooldown** after EACH Qwen call
- ✓ CPU-only mode (4 threads max, no GPU)
- ✓ Automatic skip if system health warnings detected
- ✓ Reduced token limit (1000 vs 1500)

### System Health Monitoring
Monitors every batch:
- RAM usage (stops if > 60%)
- CPU temp (stops if > 65°C)
- GPU temp (stops if > 70°C)
- CPU load (stops if > 85%)

If ANY warning detected:
1. Pauses for 2 minutes
2. Forces garbage collection
3. Skips Qwen for that cycle

## How to Use

### Step 1: Restart Ollama with Ultra-Safe Settings
```bash
./restart_ollama_safe.sh
```

This will:
- Stop current Ollama instance
- Configure CPU-only mode (NO GPU)
- Limit to 4 CPU threads (very conservative)
- Pull qwen2.5:3b (ultra-lightweight model)

### Step 2: Run Data Generation
```bash
python data_creation_gemini_primary.py
```

### Step 3: Monitor Progress
Watch the output for:
- **"Using gemini-2.0-flash-exp"** ← Most common (95%)
- **"Using qwen2.5:3b (rare)"** ← Very rare (5%)
- **Health warnings** ← System automatically pauses if detected

## Expected Behavior

### Normal Operation
```
[Batch 1] Using gemini-2.0-flash-exp | Topic: Hydration...
✓ Generated 10 triples. Total: 10/50000
💤 Short cooldown (5s)...

[Batch 2] Using gemini-2.0-flash-exp | Topic: Managing pain...
✓ Generated 10 triples. Total: 20/50000
💤 Short cooldown (5s)...

...

[Batch 20] Using qwen2.5:3b | Topic: Fall prevention...
  ⚠️  Using local Qwen (rare) - monitoring closely...
✓ Generated 10 triples. Total: 200/50000
😴 LONG cooldown after Qwen (120s)...
```

### If System Gets Warm
```
🚨 SYSTEM HEALTH WARNING 🚨
  🔥 CPU temp at 68°C (limit: 65°C)
⏸️  Pausing for 2 minutes to cool down...
```

## API Usage Estimate

For 50,000 samples:
- **Gemini**: ~4,750 batches × 10 samples = 47,500 samples
- **Qwen**: ~250 batches × 10 samples = 2,500 samples

At **10 samples per Gemini call**, that's **~4,750 API calls total**.

### Gemini API Limits (Free Tier)
- **gemini-2.0-flash-exp**: 10 RPM (requests per minute)
- At this rate: 4,750 calls = ~8 hours of runtime

## If You Still Get Shutdowns

If the PC still shuts down:
1. **Disable Qwen completely**: Edit the script and set `GEMINI_RATIO = 1.0`
2. **Use Gemini-only mode**: This becomes 100% cloud-based
3. **Alternative**: Use my previous `data_creation_gemini_only.py` script

## Files
- `data_creation_gemini_primary.py` ← Main script (USE THIS)
- `restart_ollama_safe.sh` ← Ollama configuration
- `synthetic_geriatric_data.jsonl` ← Output file (appended incrementally)

## Pro Tips
1. **Monitor temperature**: Open another terminal and run `watch sensors`
2. **Check progress**: `wc -l synthetic_geriatric_data.jsonl`
3. **If Qwen causes issues**: Set `GEMINI_RATIO = 1.0` in the script (line 26)
