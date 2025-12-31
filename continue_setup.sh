#!/bin/bash

# Continue setup now that Ollama is running
# Run this in a NEW terminal while ollama serve is running

set -e

echo "========================================="
echo "  Continuing Zima Setup"
echo "========================================="
echo ""

cd /home/ysk/Downloads/zima

# Step 1: Create optimized model
echo "1. Creating CPU-optimized Qwen model..."
if [ -f "Modelfile.qwen4b-light" ]; then
    ollama create qwen4b-light -f Modelfile.qwen4b-light
    echo "   ✓ Created 'qwen4b-light' model"
else
    echo "   ⚠ Modelfile.qwen4b-light not found"
    exit 1
fi

# Step 2: Verify
echo ""
echo "2. Verifying models..."
ollama list

# Step 3: Install Python dependencies
echo ""
echo "3. Installing Python dependencies..."
pip install psutil --quiet 2>/dev/null || pip3 install psutil

# Step 4: Set environment variable for Gemini (optional)
echo ""
echo "4. Setting up environment variables..."
if [ -z "$GEMINI_API_KEY" ]; then
    echo "   Setting GEMINI_API_KEY from list_models.py..."
    export GEMINI_API_KEY="AIzaSyAF0jRW5m446-N6Gp8UO_vWo8HYQWaAyIk"
    
    # Add to bashrc if not already there
    if ! grep -q "GEMINI_API_KEY" ~/.bashrc; then
        echo 'export GEMINI_API_KEY="AIzaSyAF0jRW5m446-N6Gp8UO_vWo8HYQWaAyIk"' >> ~/.bashrc
        echo "   ✓ Added GEMINI_API_KEY to ~/.bashrc"
    fi
else
    echo "   ✓ GEMINI_API_KEY already set"
fi

# Step 5: Run diagnostics
echo ""
echo "5. Running diagnostics..."
./diagnose.sh || true

echo ""
echo "========================================="
echo " ✅ Setup Complete!"
echo "========================================="
echo ""
echo "Ollama is running in CPU-ONLY mode (GPU disabled) ✓"
echo "This prevents the RX 550 from overheating."
echo ""
echo "To start data generation:"
echo ""
echo "  Terminal 1 (current): Keep 'ollama serve' running"
echo ""
echo "  Terminal 2 (NEW):"
echo "    cd /home/ysk/Downloads/zima"
echo "    python3 monitor_system.py"
echo ""
echo "  Terminal 3 (NEW):"
echo "    cd /home/ysk/Downloads/zima"
echo "    python3 data_creation_safe.py"
echo ""
echo "Or test with 20 samples first:"
echo "  1. Edit data_creation_safe.py line 69: TARGET_GENERATION_SIZE = 20"
echo "  2. python3 data_creation_safe.py"
echo ""
