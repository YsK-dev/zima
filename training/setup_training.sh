#!/bin/bash
# Setup script for Unsloth training on Lightning.ai
# Run this first to install all dependencies

set -e  # Exit on error

echo "======================================================================"
echo "ZIMA GERIATRIC HEALTH ASSISTANT - TRAINING ENVIRONMENT SETUP"
echo "======================================================================"

echo ""
echo "🔧 Installing Unsloth..."
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git" --quiet

echo ""
echo "📦 Installing dependencies..."
pip install --quiet \
    torch \
    transformers \
    datasets \
    accelerate \
    peft \
    trl \
    bitsandbytes \
    tensorboard \
    tqdm

echo ""
echo "🖥️  Verifying GPU..."
nvidia-smi

echo ""
echo "📊 GPU Information:"
python3 << EOF
import torch
if torch.cuda.is_available():
    gpu = torch.cuda.get_device_properties(0)
    print(f"   GPU: {gpu.name}")
    print(f"   VRAM: {gpu.total_memory / 1024**3:.1f} GB")
    print(f"   CUDA Version: {torch.version.cuda}")
else:
    print("   ⚠️  No GPU detected!")
EOF

echo ""
echo "📁 Creating directories..."
mkdir -p ../data
mkdir -p ../outputs
mkdir -p ../checkpoints
mkdir -p ../logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "======================================================================"
echo "NEXT STEPS:"
echo "======================================================================"
echo "1. Prepare data:"
echo "   python prepare_data.py"
echo ""
echo "2. Start training:"
echo "   python train_unsloth.py"
echo ""
echo "3. Evaluate model:"
echo "   python evaluate_model.py"
echo "======================================================================"
