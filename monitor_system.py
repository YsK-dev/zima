#!/usr/bin/env python3
"""
Real-time system monitor to watch for issues while running data generation.
Run this in a separate terminal while data_creation_safe.py is running.
"""

import psutil
import time
import os
from datetime import datetime

def get_cpu_temp():
    """Get CPU temperature (AMD Ryzen)."""
    try:
        temps = psutil.sensors_temperatures()
        if 'k10temp' in temps:
            return max([t.current for t in temps['k10temp']])
        elif 'coretemp' in temps:
            return max([t.current for t in temps['coretemp']])
    except:
        pass
    return None

def monitor_system(interval=5):
    """Monitor system health in real-time."""
    print("🔍 System Monitor Started")
    print("=" * 60)
    print("Monitoring CPU, RAM, and Temperature")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            # Get metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            cpu_temp = get_cpu_temp()
            
            # Get Ollama process info
            ollama_running = False
            ollama_mem = 0
            for proc in psutil.process_iter(['name', 'memory_info']):
                try:
                    if 'ollama' in proc.info['name'].lower():
                        ollama_running = True
                        ollama_mem += proc.info['memory_info'].rss / (1024**3)  # GB
                except:
                    pass
            
            # Display
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\r[{timestamp}] ", end="")
            
            # CPU
            cpu_color = "🟢" if cpu_percent < 70 else "🟡" if cpu_percent < 90 else "🔴"
            print(f"{cpu_color} CPU: {cpu_percent:5.1f}% | ", end="")
            
            # RAM
            ram_color = "🟢" if mem.percent < 70 else "🟡" if mem.percent < 85 else "🔴"
            print(f"{ram_color} RAM: {mem.percent:5.1f}% ({mem.used/(1024**3):.1f}/{mem.total/(1024**3):.1f} GB) | ", end="")
            
            # Temperature
            if cpu_temp:
                temp_color = "🟢" if cpu_temp < 70 else "🟡" if cpu_temp < 80 else "🔴"
                print(f"{temp_color} Temp: {cpu_temp:5.1f}°C | ", end="")
            
            # Ollama
            if ollama_running:
                print(f"🤖 Ollama: {ollama_mem:.2f} GB", end="")
            else:
                print("⚫ Ollama: OFF", end="")
            
            print(" " * 10, end="", flush=True)  # Clear rest of line
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n✓ Monitor stopped")

if __name__ == "__main__":
    monitor_system()
