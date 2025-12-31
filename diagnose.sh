#!/bin/bash

# Complete diagnostic script to check if your system is ready

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Zima PC Shutdown Diagnostic Tool                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track issues
ISSUES=0

echo "🔍 Checking System Requirements..."
echo ""

# 1. Check Ollama
echo -n "1. Ollama Status: "
if systemctl is-active --quiet ollama; then
    echo -e "${GREEN}✓ Running${NC}"
    
    # Check if CPU-only mode is set
    echo -n "   CPU-Only Mode: "
    if systemctl show ollama | grep -q "OLLAMA_NUM_GPU=0"; then
        echo -e "${GREEN}✓ Enabled${NC}"
    else
        echo -e "${YELLOW}⚠ Not configured (will use GPU)${NC}"
        echo "     Fix: Run ./setup_safe_ollama.sh"
        ((ISSUES++))
    fi
else
    echo -e "${RED}✗ Not running${NC}"
    echo "     Fix: sudo systemctl start ollama"
    ((ISSUES++))
fi

# 2. Check Models
echo ""
echo -n "2. Qwen Models: "
MODELS=$(ollama list 2>/dev/null | grep -E "(qwen3:4b|qwen4b-light)" | wc -l)
if [ $MODELS -ge 1 ]; then
    echo -e "${GREEN}✓ Found${NC}"
    ollama list | grep qwen | awk '{print "     -", $1, "(" $3 $4 ")"}'
    
    if ollama list | grep -q "qwen4b-light"; then
        echo -e "     ${GREEN}✓ Optimized model available${NC}"
    else
        echo -e "     ${YELLOW}⚠ qwen4b-light not found${NC}"
        echo "     Fix: Run ./setup_safe_ollama.sh"
        ((ISSUES++))
    fi
else
    echo -e "${RED}✗ Not found${NC}"
    echo "     Fix: ollama pull qwen3:4b"
    ((ISSUES++))
fi

# 3. Check Python Dependencies
echo ""
echo -n "3. Python Dependencies: "
if python3 -c "import psutil" 2>/dev/null; then
    echo -e "${GREEN}✓ psutil installed${NC}"
else
    echo -e "${RED}✗ psutil missing${NC}"
    echo "     Fix: pip install psutil"
    ((ISSUES++))
fi

if python3 -c "from google import genai" 2>/dev/null; then
    echo -e "   ${GREEN}✓ google-genai installed${NC}"
else
    echo -e "   ${YELLOW}⚠ google-genai missing (Gemini won't work)${NC}"
    echo "     Fix: pip install google-genai"
    ((ISSUES++))
fi

# 4. Check System Resources
echo ""
echo "4. System Resources:"

# RAM
TOTAL_RAM=$(free -g | awk '/^Mem:/{print $2}')
USED_RAM=$(free -g | awk '/^Mem:/{print $3}')
RAM_PERCENT=$(free | awk '/^Mem:/{printf "%.0f", $3/$2 * 100}')

echo -n "   RAM: $USED_RAM/${TOTAL_RAM}GB used ($RAM_PERCENT%) - "
if [ $RAM_PERCENT -lt 70 ]; then
    echo -e "${GREEN}✓ Available${NC}"
else
    echo -e "${YELLOW}⚠ High usage${NC}"
    echo "     Warning: Close other programs before starting"
    ((ISSUES++))
fi

# CPU
CPU_CORES=$(nproc)
echo "   CPU: $CPU_CORES cores (Ryzen 9 5900X)"

# Temperature (if available)
if command -v sensors >/dev/null 2>&1; then
    TEMP=$(sensors 2>/dev/null | grep -E "(Tctl|Package)" | head -1 | grep -oP '\+\K[0-9]+' || echo "N/A")
    if [ "$TEMP" != "N/A" ]; then
        echo -n "   CPU Temp: ${TEMP}°C - "
        if [ $TEMP -lt 60 ]; then
            echo -e "${GREEN}✓ Cool${NC}"
        elif [ $TEMP -lt 75 ]; then
            echo -e "${YELLOW}⚠ Warm${NC}"
        else
            echo -e "${RED}✗ Hot (may cause shutdown)${NC}"
            echo "     Warning: Clean CPU cooler or improve airflow"
            ((ISSUES++))
        fi
    fi
else
    echo -e "   ${YELLOW}⚠ Temperature monitoring not available${NC}"
    echo "     Optional: sudo apt install lm-sensors && sudo sensors-detect"
fi

# GPU
echo -n "   GPU: "
GPU=$(lspci | grep -i vga | grep -oP 'controller: \K.*' || echo "Unknown")
echo "$GPU"
if echo "$GPU" | grep -qi "radeon rx 550"; then
    echo -e "     ${YELLOW}⚠ Low-end GPU - CPU-only mode REQUIRED${NC}"
fi

# 5. Check Environment Variables
echo ""
echo "5. Environment Variables:"

if [ -n "$GEMINI_API_KEY" ]; then
    KEY_PREVIEW="${GEMINI_API_KEY:0:15}..."
    echo -e "   ${GREEN}✓ GEMINI_API_KEY set${NC} ($KEY_PREVIEW)"
else
    echo -e "   ${YELLOW}⚠ GEMINI_API_KEY not set (Gemini won't work)${NC}"
    echo "     Fix: export GEMINI_API_KEY='your-key-here'"
    ((ISSUES++))
fi

# 6. Check Files
echo ""
echo "6. Required Files:"

for file in data_creation_safe.py monitor_system.py setup_safe_ollama.sh Modelfile.qwen4b-light; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✓${NC} $file"
    else
        echo -e "   ${RED}✗${NC} $file (missing)"
        ((ISSUES++))
    fi
done

# Summary
echo ""
echo "═══════════════════════════════════════════════════════════"

if [ $ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! System ready to run.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Terminal 1: python3 monitor_system.py"
    echo "  2. Terminal 2: python3 data_creation_safe.py"
    echo ""
    echo "Or run automated setup first:"
    echo "  ./setup_safe_ollama.sh"
else
    echo -e "${YELLOW}⚠ Found $ISSUES issue(s) that need attention.${NC}"
    echo ""
    echo "Quick fix:"
    echo "  ./setup_safe_ollama.sh"
    echo ""
    echo "Then run diagnostics again:"
    echo "  ./diagnose.sh"
fi

echo "═══════════════════════════════════════════════════════════"
echo ""

exit $ISSUES
