#!/usr/bin/env python3
"""
Quick 5-minute test to verify system stability.
Generates just 50 samples with ultra-safe settings.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the ultra-safe module
import data_creation_ultra_safe as ultra_safe

# Override settings for quick test
ultra_safe.TARGET_GENERATION_SIZE = 50  # Just 50 samples
ultra_safe.COOLDOWN_EVERY_N_BATCHES = 2  # Very frequent cooldowns
ultra_safe.GEMINI_RATIO = 0.9  # 90% Gemini to minimize local stress

if __name__ == "__main__":
    print("=" * 80)
    print("🧪 QUICK STABILITY TEST (50 samples)")
    print("=" * 80)
    print(f"Target: {ultra_safe.TARGET_GENERATION_SIZE} samples")
    print(f"Cooldown: Every {ultra_safe.COOLDOWN_EVERY_N_BATCHES} batches")
    print(f"Gemini ratio: {ultra_safe.GEMINI_RATIO*100:.0f}%")
    print("\n⏱️  Expected duration: 5-10 minutes")
    print("💡 Watch the other terminal for temperature monitoring")
    print("=" * 80)
    print()
    
    # Run the test
    try:
        # 1. Prepare Seed Data
        seeds = ultra_safe.prepare_seed_data(ultra_safe.SEED_FILES, ultra_safe.SEED_SAMPLE_SIZE)
        
        # 2. Run Generation
        print(f"\nStarting test generation...")
        ultra_safe.generate_synthetic_data(
            seeds, 
            ultra_safe.TARGET_GENERATION_SIZE, 
            ultra_safe.gemini_client, 
            ultra_safe.qwen_client
        )
        
        print("\n" + "=" * 80)
        print("✅ TEST PASSED!")
        print("=" * 80)
        print("Your system handled the test successfully.")
        print("\nNext steps:")
        print("  1. Review monitor_enhanced.py output - were there any 🔴 red warnings?")
        print("  2. Check temperatures: run 'sensors' now")
        print("  3. If all looks good, proceed to full generation:")
        print("     python3 data_creation_ultra_safe.py")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        print("Check monitor output to see what triggered the interrupt.")
        
    except Exception as e:
        print(f"\n\n❌ TEST FAILED: {e}")
        print("\nTroubleshooting:")
        print("  1. Check monitor_enhanced.py for temperature issues")
        print("  2. Verify Ollama is running: systemctl status ollama")
        print("  3. Check GEMINI_API_KEY is set correctly")
        print("  4. Review ULTRA_SAFE_GUIDE.md for alternatives")
