#!/bin/bash
# Setup script for Raspberry Pi 5

echo "--- Installing System Dependencies ---"
sudo apt update
sudo apt install -y python3-pip cmake build-essential git

echo "--- Building llama.cpp for ARM ---"
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j$(nproc)
cd ..

echo "--- Installing Python Requirements ---"
pip3 install fastapi uvicorn llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

echo "--- Deployment Ready ---"
echo "Place your .gguf model in this directory and run api_server.py"
