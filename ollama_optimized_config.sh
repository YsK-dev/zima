#!/bin/bash

# Optimized Ollama configuration to prevent PC shutdowns
# Run this before starting data_creation.py

# Force CPU-only mode (prevents GPU overheating)
export OLLAMA_NUM_GPU=0

# Limit parallel requests to 1 (reduces memory spikes)
export OLLAMA_MAX_LOADED_MODELS=1

# Reduce context window (saves memory)
export OLLAMA_NUM_PARALLEL=1

# Set conservative memory limits
export OLLAMA_MAX_QUEUE=1

echo "=== Optimized Ollama Environment ==="
echo "GPU Layers: ${OLLAMA_NUM_GPU:-CPU ONLY}"
echo "Max Models: ${OLLAMA_MAX_LOADED_MODELS}"
echo "Parallel Requests: ${OLLAMA_NUM_PARALLEL}"
echo ""
echo "Starting Ollama server with conservative settings..."
echo "To apply these settings for data generation:"
echo "  1. Stop Ollama: sudo systemctl stop ollama"
echo "  2. Source this file: source ollama_optimized_config.sh"
echo "  3. Start Ollama manually: ollama serve"
echo ""
echo "Or run: sudo systemctl restart ollama"
