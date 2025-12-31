#!/bin/bash

echo "================================================"
echo "QWEN ULTRA-SAFE DATA GENERATION"
echo "================================================"
echo ""
echo "Current status:"
wc -l synthetic_geriatric_data.jsonl 2>/dev/null || echo "  No samples yet"
echo ""
echo "Target: 50,000 samples"
echo "Estimated time: ~9 days (8 hours/day)"
echo ""
echo "Safety measures:"
echo "  ✓ 30s cooldown after each batch"
echo "  ✓ 3min cooldown every 5 batches  
echo "  ✓ Auto-pause if temp > 60°C"
echo "  ✓ CPU-only (no GPU stress)"
echo ""
echo "================================================"
echo ""

# Check if Ollama is configured safely
if ! ps aux | grep -v grep | grep "ollama serve" > /dev/null; then
    echo "⚠️  Ollama not running!"
    echo "   Starting with safe configuration..."
    echo ""
    
    # Stop any existing Ollama
    sudo systemctl stop ollama 2>/dev/null
    pkill -9 ollama 2>/dev/null
    sleep 2
    
    # Start with safe settings
    export OLLAMA_NUM_GPU=0
    export OLLAMA_MAX_LOADED_MODELS=1
    export OLLAMA_NUM_PARALLEL=1
    export OLLAMA_NUM_THREAD=4
    
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 5
    
    echo "✓ Ollama started in safe mode"
    echo ""
fi

# Check if model exists
if ! ollama list | grep -q "qwen2.5:3b"; then
    echo "Downloading qwen2.5:3b (ultra-light model)..."
    ollama pull qwen2.5:3b
    echo ""
fi

echo "Starting data generation..."
echo "Press Ctrl+C to stop (progress is saved automatically)"
echo ""
echo "Tip: Open another terminal and run:"
echo "  watch -n 5 'wc -l synthetic_geriatric_data.jsonl'"
echo ""
echo "================================================"
echo ""

# Run the generation script
python data_creation_qwen_ultra_safe.py
