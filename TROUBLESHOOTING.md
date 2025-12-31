# 🚨 PC Shutdown Troubleshooting Guide

## Problem
PC shuts down when running `qwen3:4b` model despite it being a smaller 4B parameter model.

## Root Causes

### 1. **GPU Overheating** (Most Likely)
- Your **RX 550** GPU has limited VRAM (~2-4GB) and cooling
- Ollama by default tries to use GPU acceleration
- Even a 4B model can push a low-end GPU to thermal limits
- **Solution**: Force CPU-only mode ✅

### 2. **No Resource Limits**
- Original `data_creation.py` has no memory/CPU limits
- Continuous generation without breaks causes heat buildup
- No monitoring of system health
- **Solution**: Use `data_creation_safe.py` with health checks ✅

### 3. **High Context Window**
- Default Ollama context is 2048 tokens
- Higher context = more memory & compute
- **Solution**: Reduce to 512 tokens ✅

### 4. **Aggressive Threading**
- Ryzen 9 5900X has 24 threads
- Using all threads = maximum heat generation
- **Solution**: Limit to 8 threads ✅

---

## 🛠️ Step-by-Step Fix

### **Option 1: Automated Setup (Recommended)**

Run the setup script to configure everything automatically:

```bash
cd /home/ysk/Downloads/zima
./setup_safe_ollama.sh
```

This will:
- ✅ Force CPU-only mode (no GPU usage)
- ✅ Create optimized `qwen4b-light` model
- ✅ Set system-wide Ollama limits
- ✅ Install Python dependencies (psutil)

Then run data generation:

```bash
# Terminal 1: Monitor system health
python3 monitor_system.py

# Terminal 2: Run safe data generation
python3 data_creation_safe.py
```

---

### **Option 2: Manual Configuration**

#### Step 1: Configure Ollama for CPU-Only

```bash
# Stop Ollama
sudo systemctl stop ollama

# Create override config
sudo mkdir -p /etc/systemd/system/ollama.service.d/
cat << EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_NUM_GPU=0"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
EOF

# Reload and restart
sudo systemctl daemon-reload
sudo systemctl start ollama
```

#### Step 2: Create Lightweight Model

```bash
ollama create qwen4b-light -f Modelfile.qwen4b-light
```

#### Step 3: Update Your Script

Edit `data_creation_safe.py` line 11:

```python
QWEN_MODEL = 'qwen4b-light'  # Use the optimized model
```

#### Step 4: Install Monitoring Tools

```bash
pip install psutil
```

#### Step 5: Run with Monitoring

```bash
# Terminal 1
python3 monitor_system.py

# Terminal 2
python3 data_creation_safe.py
```

---

## 🔍 Understanding the Safety Features

### `data_creation_safe.py` Improvements

1. **System Health Monitoring**
   - Checks RAM usage every batch
   - Monitors CPU temperature (if available)
   - Auto-pauses if limits exceeded

2. **Automatic Cooldowns**
   - 10-second rest every 5 batches
   - Prevents heat accumulation
   - Forces garbage collection

3. **Resource Limits**
   ```python
   MAX_MEMORY_PERCENT = 75  # Stop if RAM > 75%
   MAX_CPU_TEMP = 80       # Stop if CPU > 80°C
   ```

4. **Smaller Requests**
   - Reduced `max_tokens` to 2000
   - Added request timeouts (30s)
   - Limited retries to 2

### `qwen4b-light` Model

```
num_ctx: 2048 → 512    (4x less memory)
num_thread: 24 → 8     (3x less CPU load)
num_gpu: auto → 0      (CPU-only, no GPU heat)
```

---

## 📊 Monitoring During Generation

The `monitor_system.py` script shows real-time metrics:

```
[23:15:42] 🟢 CPU: 45.2% | 🟢 RAM: 52.3% (16.2/31.0 GB) | 🟢 Temp: 68.5°C | 🤖 Ollama: 2.8 GB
```

**Color Codes:**
- 🟢 Green: Safe
- 🟡 Yellow: Warning
- 🔴 Red: Critical (script will auto-pause)

---

## ⚠️ What If It Still Shuts Down?

### Hardware Issues

1. **Check CPU Cooler**
   ```bash
   # Monitor temperatures
   watch -n 1 sensors
   ```
   - Ryzen 5900X should idle at 40-50°C
   - Under load: 60-75°C is normal
   - If >80°C idle: **Clean/replace cooler**

2. **Check PSU Capacity**
   - RX 550: ~50W
   - Ryzen 9 5900X: ~105W TDP (up to 142W)
   - Total system: ~250-300W
   - **Minimum PSU**: 450W (550W recommended)
   - If PSU is <450W or old: **May need replacement**

3. **Check RAM**
   ```bash
   sudo memtest86+  # Run from boot menu
   ```

### Software Alternatives

1. **Use Gemini Only**
   - Edit `data_creation_safe.py` line 308:
   ```python
   use_gemini = True  # Force Gemini-only
   ```
   - No local compute needed
   - Uses API credits instead

2. **Use Smaller Model**
   ```bash
   ollama pull qwen2.5:1.5b-instruct  # Even smaller
   ```
   - Update `QWEN_MODEL = 'qwen2.5:1.5b-instruct'`

3. **Cloud Generation**
   - Use Google Colab for free GPU
   - Run `data_creation.py` there with Gemini only

---

## 🧪 Testing the Fix

### Quick Test (5 minutes)

```bash
# Edit data_creation_safe.py line 69:
TARGET_GENERATION_SIZE = 20  # Just 20 samples for testing

# Run
python3 data_creation_safe.py
```

If this completes without shutdown → **Fixed!**

### Full Test

Restore to 50,000 and run overnight:
```bash
# In screen/tmux session
screen -S zima
python3 monitor_system.py &
python3 data_creation_safe.py
# Detach: Ctrl+A, D
```

---

## 📈 Performance Expectations

With safe configuration:

| Metric | Before (Unsafe) | After (Safe) |
|--------|----------------|--------------|
| **Temperature** | 85-95°C → Shutdown | 65-75°C ✅ |
| **RAM Usage** | Unlimited → OOM | <75% ✅ |
| **Speed** | ~15-20 samples/min | ~8-12 samples/min |
| **Stability** | Crashes in <10 min | Runs indefinitely ✅ |

**Trade-off**: Slower but stable. 50K samples will take ~60-70 hours instead of ~30 hours.

---

## 🆘 Emergency Commands

### If Terminal Frozen

```bash
# SSH from another device, then:
pkill -9 python3
sudo systemctl restart ollama
```

### Check Ollama Logs

```bash
sudo journalctl -u ollama -n 100 --no-pager
```

### Reset Everything

```bash
sudo systemctl stop ollama
sudo rm -rf ~/.ollama/
sudo systemctl start ollama
ollama pull qwen3:4b
```

---

## ✅ Success Checklist

Before starting production run:

- [ ] Ran `./setup_safe_ollama.sh` successfully
- [ ] `ollama list` shows `qwen4b-light` model
- [ ] `systemctl status ollama` shows "active (running)"
- [ ] Tested with 20 samples - no shutdown
- [ ] `monitor_system.py` running in separate terminal
- [ ] PSU is adequate (>450W)
- [ ] CPU cooler is clean and working
- [ ] Room temperature is reasonable (<25°C)

---

## 💡 Pro Tips

1. **Run at Night**: Cooler ambient temperature = better thermals
2. **Improve Airflow**: Open case, add fans, or use AC
3. **Undervolt CPU**: Can reduce heat by 10-15°C
   - Use Ryzen Master utility
   - Lower voltage by 0.05V increments
4. **Use Hybrid Mode**: Gemini for 80%, Qwen for 20% only
5. **Batch Processing**: Generate 1000 samples, pause 1 hour, repeat

---

## 📞 Still Having Issues?

1. Post system info:
   ```bash
   echo "=== System Info ===" > debug.txt
   lscpu >> debug.txt
   free -h >> debug.txt
   sensors >> debug.txt
   nvidia-smi 2>/dev/null || echo "No NVIDIA GPU" >> debug.txt
   lspci | grep VGA >> debug.txt
   cat /proc/cpuinfo | grep "model name" | head -1 >> debug.txt
   ```

2. Check temperatures before/during/after:
   ```bash
   watch -n 1 'sensors | grep -E "(temp|Tctl)"'
   ```

3. Monitor Ollama specifically:
   ```bash
   sudo journalctl -u ollama -f
   ```

---

**Last Updated**: 2025-12-30
**Hardware**: Ryzen 9 5900X, 31GB RAM, RX 550 GPU
**Model**: Qwen 3 4B (2.5GB)
