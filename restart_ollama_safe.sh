#!/bin/bash

# Stop Ollama service
echo "Stopping Ollama..."
sudo systemctl stop ollama 2>/dev/null || pkill -9 ollama

# Wait for process to fully stop
sleep 3

# Set ultra-conservative environment variables for CPU-only operation
export OLLAMA_NUM_GPU=0                    # Force CPU only (no GPU usage)
export OLLAMA_MAX_LOADED_MODELS=1          # Only one model in memory
export OLLAMA_NUM_PARALLEL=1               # No parallel processing
export OLLAMA_MAX_QUEUE=1                  # Minimal queue
export OLLAMA_NUM_THREAD=4                 # Limit to 4 CPU threads (out of 24 on Ryzen 9 5900X)
export OLLAMA_HOST=127.0.0.1:11434         # Localhost only

echo "=== Ultra-Safe Ollama Configuration ==="
echo "GPU Layers: DISABLED (CPU ONLY)"
echo "Max Models: 1"
echo "Parallel Requests: 1"
echo "CPU Threads: 4 (very conservative)"
echo ""

# Start Ollama in background with these settings
echo "Starting Ollama with ultra-safe settings..."
nohup ollama serve > /tmp/ollama.log 2>&1 &

# Wait for it to start
sleep 5

# Verify it's running
if pgrep -x ollama > /dev/null; then
    echo "✓ Ollama started successfully"
    echo "  Process ID: $(pgrep -x ollama)"
    echo "  Log: /tmp/ollama.log"
    
    # Pull the ultra-light 3B model if not already available
    echo ""
    echo "Ensuring qwen2.5:3b model is available..."
    ollama pull qwen2.5:3b
    
    echo ""
    echo "✓ Ready! Ollama is running in ULTRA-SAFE mode."
    echo "  - CPU-only (no GPU)"
    echo "  - Limited to 4 threads"
    echo "  - Will be used VERY sparingly (5% of the time)"
else
    echo "❌ Failed to start Ollama"
    exit 1
fi
