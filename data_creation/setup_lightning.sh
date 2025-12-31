#!/bin/bash
# Lightning.ai Setup Script - Run this first in your Lightning.ai Studio

set -e

echo "=================================="
echo "Lightning.ai Data Generation Setup"
echo "=================================="
echo ""

# 1. Install Ollama
echo "📦 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# 2. Start Ollama server in background
echo "🚀 Starting Ollama server..."
nohup ollama serve > /tmp/ollama.log 2>&1 &
sleep 10

# Check if Ollama started
if pgrep -x ollama > /dev/null; then
    echo "✓ Ollama running (PID: $(pgrep -x ollama))"
else
    echo "❌ Ollama failed to start. Check /tmp/ollama.log"
    exit 1
fi

# 3. Pull Qwen 14B model (optimized for L40 GPU)
echo ""
echo "📥 Pulling Qwen 2.5 14B model (this takes ~5-10 minutes)..."
echo "   Model size: ~8GB"
ollama pull qwen2.5:14b

# Verify model is available
if ollama list | grep -q "qwen2.5:14b"; then
    echo "✓ Qwen 2.5 14B model ready"
else
    echo "⚠️  Model pull may have failed. Trying lighter 7B model..."
    ollama pull qwen2.5:7b
fi

# 4. Install Python dependencies
echo ""
echo "📦 Installing Python packages..."
pip install -q google-generativeai openai pandas

# 5. GPU Check
echo ""
echo "🎮 GPU Information:"
nvidia-smi --query-gpu=name,memory.total,memory.free --format=csv,noheader || echo "nvidia-smi not available"

# 6. Ready!
echo ""
echo "=================================="
echo "✅ SETUP COMPLETE!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Upload your seed JSON files (intents.json, claude.json, gemini.json)"
echo "2. Run: python data_creation_lightning.py"
echo "3. Wait ~3-4 hours"
echo "4. Download synthetic_geriatric_data.jsonl"
echo ""
echo "To monitor progress:"
echo "  watch -n 10 'wc -l synthetic_geriatric_data.jsonl'"
echo ""
echo "To check GPU usage:"
echo "  watch -n 5 nvidia-smi"
echo ""
