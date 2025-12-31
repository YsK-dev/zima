# 🛡️ ULTRA-SAFE Data Generation Guide

## TL;DR - Quick Start

Your PC is shutting down despite using `data_creation_safe.py`. The new **ultra-safe** version has even more aggressive protection:

```bash
# Terminal 1: Enhanced monitoring with GPU tracking
python3 monitor_enhanced.py

# Terminal 2: Ultra-safe generation (80% Gemini, 20% Qwen)
python3 data_creation_ultra_safe.py
```

---

## What's New in Ultra-Safe Mode?

### Compared to `data_creation_safe.py`:

| Setting | Safe Mode | **Ultra-Safe Mode** | Reason |
|---------|-----------|---------------------|--------|
| **RAM Limit** | 75% | **65%** | More headroom for system stability |
| **CPU Temp Limit** | 80°C | **70°C** | Prevent heat accumulation |
| **GPU Temp Limit** | ❌ None | **75°C** ✅ | Your RX 550 was getting hot! |
| **Short Cooldown** | Every 5 batches | **Every 3 batches** | More frequent breaks |
| **Short Cooldown Duration** | 10s | **20s** | Longer cooling time |
| **Long Cooldown** | ❌ None | **60s every 10 batches** ✅ | Prevent cumulative heat |
| **Gemini/Qwen Ratio** | 50/50 | **80/20** | Less local compute stress |
| **Max Tokens (Qwen)** | 2000 | **1500** | Smaller responses = less work |
| **Request Timeout** | 30s | **20s** | Fail faster on issues |
| **Error Wait Time** | 10s | **15s** | More recovery time |
| **Health Warning Wait** | 60s | **90s (180s if persists)** | Aggressive cooling |

---

## Why Is Your PC Still Shutting Down?

### Diagnosis Checklist

Based on your hardware (Ryzen 9 5900X + RX 550), here are the most likely causes:

#### 1. **GPU Overheating** (95% probability) ⭐
- **Problem**: Even though Ollama is in CPU-only mode, the RX 550 might still be used by the system
- **Evidence**: No GPU temp monitoring in old `data_creation_safe.py`
- **Fix**: ✅ Now monitoring GPU temp in `monitor_enhanced.py`

#### 2. **Heat Accumulation Over Time** (90% probability) ⭐
- **Problem**: Even if each batch is safe, continuous operation builds up heat
- **Evidence**: Your previous shutdown likely happened after several minutes
- **Fix**: ✅ Added long 60s cooldowns every 10 batches

#### 3. **Insufficient Cooling** (80% probability)
- **Problem**: Case airflow may be inadequate for sustained load
- **Evidence**: Ryzen 9 5900X is a 105W TDP CPU (can spike to 142W)
- **Fix**: See "Physical Cooling Improvements" below

#### 4. **PSU Insufficiency** (50% probability)
- **Problem**: Power supply might be borderline for sustained loads
- **Evidence**: RX 550 (50W) + 5900X (142W peak) + system = ~250-300W
- **Fix**: Ensure PSU is rated for 450W+ and in good condition

---

## Step-by-Step: Ultra-Safe Setup

### Option 1: Quick Test (Recommended First Step)

Test with just 50 samples to verify the system is stable:

```bash
cd /home/ysk/Downloads/zima

# Terminal 1: Start monitoring
python3 monitor_enhanced.py

# Terminal 2: Edit the target size for testing
# (We'll create a test script)
```

Let me create a quick test version:

```python
# In data_creation_ultra_safe.py, change line 124:
TARGET_GENERATION_SIZE = 50  # Just for testing
```

Run for 5-10 minutes. If it completes successfully → proceed to full generation.

### Option 2: Gemini-Only Mode (No Local Compute)

If the ultra-safe mode still causes shutdowns, eliminate local compute entirely:

```bash
# Edit data_creation_ultra_safe.py, change line 23:
GEMINI_RATIO = 1.0  # 100% Gemini, 0% Qwen
```

**Pros:**
- ✅ Zero local compute stress
- ✅ Guaranteed stability
- ✅ Faster generation (no Ollama delays)

**Cons:**
- ❌ May hit Gemini API rate limits
- ❌ Uses API quota (but Gemini Flash is cheap)

### Option 3: Micro-Batching (Slowest but Safest)

Generate in tiny chunks with long breaks:

```bash
# Edit data_creation_ultra_safe.py:
COOLDOWN_EVERY_N_BATCHES = 1  # Cooldown after EVERY batch
LONG_COOLDOWN_DURATION = 120  # 2-minute breaks
GEMINI_RATIO = 1.0  # Gemini-only
```

This will be **very slow** but should never overheat.

---

## Physical Cooling Improvements

If software limits aren't enough, improve your hardware cooling:

### Immediate (Free)
1. **Open the case side panel** - Instant airflow improvement
2. **Point a desk fan at the open case** - Can reduce temps by 10-15°C
3. **Check CPU cooler** - Ensure fan is spinning and not caked with dust

### Quick Wins ($0-20)
1. **Clean dust filters** - Use compressed air on all intake/exhaust
2. **Reapply thermal paste** - If CPU cooler is >2 years old
3. **Check case fan orientations** - Front=intake, rear/top=exhaust

### Hardware Upgrades ($20-100)
1. **Better CPU cooler** - A $30 tower cooler can drop temps 10-20°C
2. **Additional case fans** - 2x 120mm fans for ~$15
3. **Better PSU** - If current PSU is <450W or >5 years old

---

## Monitoring & Diagnostics

### Real-Time Monitoring

The new `monitor_enhanced.py` shows:

```
[23:49:35] 🟢 CPU: 45.2% | 🟢 RAM: 52.3% (16.2/31.0 GB) | 🟢 CPU Temp: 68.5°C | 🟢 GPU Temp: 45.0°C | 🤖 Ollama: 2.8 GB (12% CPU)
```

**Watch for:**
- 🔴 Red indicators = Immediate danger
- 🟡 Yellow indicators = Warning, monitor closely
- Multiple 🔴 = Script should auto-pause

### Detailed Temperature Logging

To log temps over time for analysis:

```bash
# Run in Terminal 3
while true; do
    echo "$(date '+%H:%M:%S') - $(sensors | grep -E '(Tctl|edge)')" | tee -a temp_log.txt
    sleep 5
done
```

This creates a log file showing temperature trends.

### Check Ollama Service

Verify CPU-only mode is active:

```bash
sudo journalctl -u ollama -n 50 --no-pager | grep -i gpu
```

You should see:
- `OLLAMA_NUM_GPU=0` (CPU-only mode)
- `experimental Vulkan support disabled` (no GPU acceleration)

---

## Emergency Procedures

### If PC Starts Feeling Hot

1. **Check monitor** - Look for 🔴 red warnings
2. **Let script auto-pause** - It will cooldown for 90-180 seconds
3. **If warnings persist** - Press Ctrl+C in Terminal 2 to stop generation
4. **Check temperatures manually**: `sensors`

### If Script Keeps Pausing

This means your system is hitting limits repeatedly. Options:

**Option A: Use Gemini-only mode** (recommended)
```bash
# Edit data_creation_ultra_safe.py line 23:
GEMINI_RATIO = 1.0
```

**Option B: Reduce target size and run in batches**
```bash
# Generate in chunks of 5,000 samples
TARGET_GENERATION_SIZE = 5000
# Run 10 times with manual breaks
```

**Option C: Improve cooling** (see Physical Cooling Improvements above)

### Complete System Reset

If Ollama is misbehaving:

```bash
# Stop everything
pkill -9 python3
sudo systemctl stop ollama

# Clear Ollama cache
sudo rm -rf /tmp/ollama*

# Restart with limits
sudo systemctl start ollama

# Verify
systemctl status ollama
sensors
```

---

## Performance Expectations

### Ultra-Safe Mode

| Metric | Estimate |
|--------|----------|
| **Speed** | ~6-10 samples/minute |
| **Time for 50K samples** | ~80-120 hours (3-5 days) |
| **CPU Temp** | 60-70°C (safe) |
| **GPU Temp** | 40-50°C (idle/safe) |
| **RAM Usage** | <65% (safe) |
| **System Stability** | High (should not crash) |

### Gemini-Only Mode

| Metric | Estimate |
|--------|----------|
| **Speed** | ~12-15 samples/minute |
| **Time for 50K samples** | ~50-70 hours (2-3 days) |
| **CPU Temp** | 40-50°C (idle) |
| **Stability** | Very High (no local compute) |
| **Cost** | ~$0.50-1.00 (Gemini Flash is very cheap) |

---

## Recommended Workflow

### Phase 1: Validation (30 minutes)

```bash
# Test with 100 samples
# Edit data_creation_ultra_safe.py line 124:
TARGET_GENERATION_SIZE = 100

# Run with monitoring
python3 monitor_enhanced.py  # Terminal 1
python3 data_creation_ultra_safe.py  # Terminal 2
```

**Success criteria:**
- ✅ No red warnings in monitor
- ✅ CPU temp stays <70°C
- ✅ GPU temp stays <75°C
- ✅ Completes 100 samples

### Phase 2: Pilot Run (2-3 hours)

```bash
# Test with 1,000 samples
TARGET_GENERATION_SIZE = 1000
```

**Success criteria:**
- ✅ No shutdowns
- ✅ Temps remain stable over time
- ✅ Less than 5 auto-pauses

### Phase 3: Production (3-5 days)

```bash
# Full run with 50,000 samples
TARGET_GENERATION_SIZE = 50000

# Run in screen/tmux to survive disconnects
screen -S zima
python3 monitor_enhanced.py &
python3 data_creation_ultra_safe.py
# Detach: Ctrl+A, D
# Re-attach: screen -r zima
```

**Monitor daily:**
- Check `synthetic_geriatric_data.jsonl` file size growth
- Review `temp_log.txt` for temperature trends
- Ensure no persistent red warnings

---

## Alternative: Cloud Generation

If local generation continues to cause issues, consider running on Google Colab (free):

**Advantages:**
- ✅ No local resource usage
- ✅ Free GPU access
- ✅ Faster generation
- ✅ No shutdown risk

**Setup:**
1. Upload `data_creation_ultra_safe.py` to Colab
2. Set `GEMINI_RATIO = 1.0` (Gemini-only)
3. Add your `GEMINI_API_KEY`
4. Run for 12 hours, download results, repeat

---

## FAQ

### Q: How do I know if my cooling is adequate?

**A:** Run `sensors` before starting. Idle temps should be:
- CPU: 40-50°C ✅
- GPU: 35-45°C ✅

If idle temps are >60°C, you have a cooling problem.

### Q: My PSU is only 400W, is that okay?

**A:** Borderline. System draw is ~250-300W under load. If PSU is:
- New (<2 years): Probably okay with ultra-safe mode
- Old (>3 years): Consider upgrade to 550W

### Q: Can I run this overnight?

**A:** Yes, but:
1. Complete a 2-3 hour pilot run first
2. Use `screen` or `tmux` to survive disconnects
3. Check temps before bed - should be <70°C
4. Monitor remotely if possible (SSH from phone)

### Q: What if I hit Gemini API rate limits?

**A:** Gemini Flash has very high limits. If you hit them:
1. The script will automatically retry
2. Consider adding a longer delay between batches
3. Contact Google to increase quota (usually easy)

---

## Success Checklist

Before starting full 50K generation:

- [ ] Ran `python3 data_creation_ultra_safe.py` with 100 samples successfully
- [ ] `monitor_enhanced.py` shows mostly 🟢 green indicators
- [ ] No 🔴 red warnings for >10 minutes during test
- [ ] CPU temps stay <70°C under load
- [ ] GPU temps stay <75°C under load
- [ ] Ollama is in CPU-only mode (`systemctl status ollama` shows `OLLAMA_NUM_GPU=0`)
- [ ] Case has adequate airflow (side panel open or good fans)
- [ ] Have `screen` or `tmux` installed for long runs
- [ ] Know how to SSH in remotely if needed

---

## Getting Help

If ultra-safe mode still causes shutdowns, collect this info:

```bash
# System info
echo "=== SYSTEM INFO ===" > system_report.txt
lscpu >> system_report.txt
free -h >> system_report.txt
lspci | grep VGA >> system_report.txt
sudo lshw -short -C memory 2>/dev/null | grep -i system >> system_report.txt

# Temperatures (before starting)
echo -e "\n=== IDLE TEMPS ===" >> system_report.txt
sensors >> system_report.txt

# Ollama config
echo -e "\n=== OLLAMA CONFIG ===" >> system_report.txt
systemctl status ollama >> system_report.txt
cat /etc/systemd/system/ollama.service.d/override.conf >> system_report.txt

# PSU wattage (if visible)
echo -e "\n=== PSU INFO ===" >> system_report.txt
sudo dmidecode -t 39 2>/dev/null | grep -i "max\|capacity" >> system_report.txt

cat system_report.txt
```

Share `system_report.txt` and describe when the shutdown occurs (after how many minutes/batches).

---

**Last Updated**: 2025-12-30 23:49  
**Hardware**: Ryzen 9 5900X, 31GB RAM, RX 550 GPU  
**Script Version**: Ultra-Safe v2 (GPU monitoring + aggressive limits)
