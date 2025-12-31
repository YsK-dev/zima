#!/bin/bash

# Simple manual startup for Ollama (bypassing systemd)
# Use this instead of systemd service

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     Starting Ollama in CPU-Only Mode (Manual)             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Set environment variables for this session
export OLLAMA_NUM_GPU=0
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_KEEP_ALIVE=5m
export OLLAMA_CONTEXT_LENGTH=512

echo "✅ Environment Variables Set:"
echo "   - OLLAMA_NUM_GPU=0 (CPU-only)"
echo "   - OLLAMA_MAX_LOADED_MODELS=1"
echo "   - OLLAMA_NUM_PARALLEL=1"
echo "   - OLLAMA_CONTEXT_LENGTH=512"
echo ""
echo "🚀 Starting Ollama server..."
echo "   Keep this terminal open while generating data"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Start Ollama
ollama serve
