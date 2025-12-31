#!/bin/bash

# Complete setup script to prevent PC shutdowns when running Qwen 4B

set -e

echo "========================================="
echo "  Zima Safe Ollama Configuration"
echo "========================================="
echo ""

# Step 1: Stop Ollama service
echo "1. Stopping Ollama service..."
sudo systemctl stop ollama 2>/dev/null || echo "   (Service not running)"
sleep 2

# Step 2: Create optimized model
echo ""
echo "2. Creating CPU-optimized Qwen model..."
if [ -f "Modelfile.qwen4b-light" ]; then
    ollama create qwen4b-light -f Modelfile.qwen4b-light
    echo "   ✓ Created 'qwen4b-light' model"
else
    echo "   ⚠ Modelfile.qwen4b-light not found, skipping"
fi

# Step 3: Set environment variables
echo ""
echo "3. Setting Ollama environment variables..."
sudo mkdir -p /etc/systemd/system/ollama.service.d/
cat << EOF | sudo tee /etc/systemd/system/ollama.service.d/override.conf
[Service]
Environment="OLLAMA_NUM_GPU=0"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_KEEP_ALIVE=5m"
EOF

echo "   ✓ CPU-only mode enabled"
echo "   ✓ Limited to 1 model in memory"
echo "   ✓ Sequential requests only"

# Step 4: Reload systemd
echo ""
echo "4. Reloading systemd configuration..."
sudo systemctl daemon-reload

# Step 5: Start Ollama
echo ""
echo "5. Starting Ollama service..."
sudo systemctl start ollama
sleep 3

# Step 6: Verify
echo ""
echo "6. Verifying Ollama status..."
if systemctl is-active --quiet ollama; then
    echo "   ✓ Ollama is running"
    ollama list
else
    echo "   ✗ Ollama failed to start"
    echo "   Check logs: sudo journalctl -u ollama -n 50"
    exit 1
fi

# Step 7: Install Python dependencies
echo ""
echo "7. Checking Python dependencies..."
python3 -c "import psutil" 2>/dev/null || pip install psutil

echo ""
echo "========================================="
echo " ✓ Setup Complete!"
echo "========================================="
echo ""
echo "To run data generation safely:"
echo "  1. Use the new lightweight model:"
echo "     Edit data_creation_safe.py and change QWEN_MODEL to 'qwen4b-light'"
echo ""
echo "  2. Or use the safe script with original model:"
echo "     python3 data_creation_safe.py"
echo ""
echo "The script will now:"
echo "  ✓ Monitor CPU temperature and RAM usage"
echo "  ✓ Auto-pause if system gets too hot"
echo "  ✓ Take cooldown breaks every 5 batches"
echo "  ✓ Force garbage collection to free memory"
echo ""
