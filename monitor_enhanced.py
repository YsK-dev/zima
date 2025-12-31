#!/usr/bin/env python3
"""
Enhanced real-time system monitor with GPU support and alerts.
Run this in a separate terminal while data_creation_ultra_safe.py is running.
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

def get_gpu_temp():
    """Get GPU temperature (AMD GPU)."""
    try:
        temps = psutil.sensors_temperatures()
        if 'amdgpu' in temps:
            # Look for 'edge' temperature specifically
            for sensor in temps['amdgpu']:
                if hasattr(sensor, 'label') and 'edge' in sensor.label:
                    return sensor.current
            # Fallback: return max temp
            return max([t.current for t in temps['amdgpu']])
    except:
        pass
    return None

def monitor_system(interval=5):
    """Monitor system health in real-time with enhanced GPU monitoring."""
    print("🔍 Enhanced System Monitor Started")
    print("=" * 80)
    print("Monitoring CPU, GPU, RAM, and Temperature")
    print("Press Ctrl+C to stop\n")
    
    alert_count = 0
    last_alert_time = 0
    
    try:
        while True:
            # Get metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            cpu_temp = get_cpu_temp()
            gpu_temp = get_gpu_temp()
            
            # Get Ollama process info
            ollama_running = False
            ollama_mem = 0
            ollama_cpu = 0
            for proc in psutil.process_iter(['name', 'memory_info', 'cpu_percent']):
                try:
                    if 'ollama' in proc.info['name'].lower():
                        ollama_running = True
                        ollama_mem += proc.info['memory_info'].rss / (1024**3)  # GB
                        ollama_cpu += proc.info['cpu_percent']
                except:
                    pass
            
            # Display
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\r[{timestamp}] ", end="")
            
            # CPU
            cpu_color = "🟢" if cpu_percent < 70 else "🟡" if cpu_percent < 90 else "🔴"
            print(f"{cpu_color} CPU: {cpu_percent:5.1f}% | ", end="")
            
            # RAM
            ram_color = "🟢" if mem.percent < 65 else "🟡" if mem.percent < 75 else "🔴"
            print(f"{ram_color} RAM: {mem.percent:5.1f}% ({mem.used/(1024**3):.1f}/{mem.total/(1024**3):.1f} GB) | ", end="")
            
            # CPU Temperature
            if cpu_temp:
                temp_color = "🟢" if cpu_temp < 65 else "🟡" if cpu_temp < 70 else "🔴"
                print(f"{temp_color} CPU Temp: {cpu_temp:5.1f}°C | ", end="")
            
            # GPU Temperature (NEW)
            if gpu_temp:
                gpu_color = "🟢" if gpu_temp < 70 else "🟡" if gpu_temp < 75 else "🔴"
                print(f"{gpu_color} GPU Temp: {gpu_temp:5.1f}°C | ", end="")
            
            # Ollama
            if ollama_running:
                print(f"🤖 Ollama: {ollama_mem:.2f} GB ({ollama_cpu:.0f}% CPU)", end="")
            else:
                print("⚫ Ollama: OFF", end="")
            
            print(" " * 5, end="", flush=True)  # Clear rest of line
            
            # ALERT SYSTEM
            current_time = time.time()
            alerts = []
            
            if mem.percent >= 75:
                alerts.append(f"⚠️ HIGH RAM: {mem.percent:.1f}%")
            if cpu_temp and cpu_temp >= 70:
                alerts.append(f"🔥 HIGH CPU TEMP: {cpu_temp:.1f}°C")
            if gpu_temp and gpu_temp >= 75:
                alerts.append(f"🔥 HIGH GPU TEMP: {gpu_temp:.1f}°C")
            if cpu_percent >= 95:
                alerts.append(f"⚠️ CPU MAXED OUT: {cpu_percent:.1f}%")
            
            if alerts and (current_time - last_alert_time) > 30:  # Alert every 30s max
                print("\n")
                print("🚨 " + " | ".join(alerts))
                print("   → The script should auto-pause. If PC is getting hot, stop manually (Ctrl+C)")
                alert_count += 1
                last_alert_time = current_time
            
            time.sleep(interval)
            
    except KeyboardInterrupt:
        print("\n\n✓ Monitor stopped")
        if alert_count > 0:
            print(f"\n⚠️ Total alerts during session: {alert_count}")
            print("If you saw many alerts, consider:")
            print("  1. Improving case airflow/cooling")
            print("  2. Using Gemini-only mode (no local compute)")
            print("  3. Generating smaller batches with longer breaks")

if __name__ == "__main__":
    monitor_system()
