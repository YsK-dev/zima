import os
import json
import time
import psutil
import gc
from pathlib import Path
import pandas as pd
from google import genai
from google.genai import types

# --- QWEN-PRIMARY WITH EXTREME SAFETY Configuration ---
GEMINI_MODEL = 'gemini-3-flash-preview'
QWEN_MODEL = 'qwen2.5:3b'  # Ultra-lightweight 3B model
OUTPUT_FILE = 'synthetic_geriatric_data.jsonl'

# EXTREME SAFETY LIMITS - Even more conservative
MAX_MEMORY_PERCENT = 55  # Very strict
MAX_CPU_TEMP = 60  # Very cool
MAX_GPU_TEMP = 65  # Very cool
MANDATORY_COOLDOWN_EVERY_CALL = 30  # 30 seconds after EVERY Qwen call
LONG_COOLDOWN_EVERY_N = 5  # Every 5 batches, take a 3-minute break
LONG_COOLDOWN_DURATION = 180  # 3 minutes

# Balanced mode: Prefer Qwen but use Gemini when available
GEMINI_RATIO = 0.10  # Use Gemini 10% of the time (when quota allows)
GEMINI_DAILY_QUOTA = 20  # Gemini free tier daily limit
gemini_calls_today = 0  # Track usage

# Resolve seed files
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
SEARCH_DIRS = [Path("."), BASE_DIR, Path.cwd()]

def check_system_health():
    """Monitor system resources with STRICT limits."""
    warnings = []
    metrics = {}
    
    # Check RAM
    mem = psutil.virtual_memory()
    metrics['ram'] = mem.percent
    if mem.percent > MAX_MEMORY_PERCENT:
        warnings.append(f"⚠️ RAM usage at {mem.percent:.1f}% (limit: {MAX_MEMORY_PERCENT}%)")
    
    # Check temperatures
    try:
        temps = psutil.sensors_temperatures()
        
        # CPU temperature
        if 'k10temp' in temps:
            cpu_temp = max([t.current for t in temps['k10temp']])
            metrics['cpu_temp'] = cpu_temp
            if cpu_temp > MAX_CPU_TEMP:
                warnings.append(f"🔥 CPU temp at {cpu_temp:.1f}°C (limit: {MAX_CPU_TEMP}°C)")
        
        # GPU temperature
        if 'amdgpu' in temps:
            gpu_temp = max([t.current for t in temps['amdgpu']])
            metrics['gpu_temp'] = gpu_temp
            if gpu_temp > MAX_GPU_TEMP:
                warnings.append(f"🔥 GPU temp at {gpu_temp:.1f}°C (limit: {MAX_GPU_TEMP}°C)")
    except Exception:
        pass
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=0.5)
    metrics['cpu_usage'] = cpu_percent
    if cpu_percent > 80:
        warnings.append(f"⚠️ CPU usage at {cpu_percent:.1f}%")
    
    return warnings, metrics

def print_health_status(metrics):
    """Print current system health status."""
    status_parts = []
    if 'ram' in metrics:
        status_parts.append(f"RAM: {metrics['ram']:.1f}%")
    if 'cpu_temp' in metrics:
        status_parts.append(f"CPU: {metrics['cpu_temp']:.1f}°C")
    if 'gpu_temp' in metrics:
        status_parts.append(f"GPU: {metrics['gpu_temp']:.1f}°C")
    if 'cpu_usage' in metrics:
        status_parts.append(f"Load: {metrics['cpu_usage']:.1f}%")
    
    if status_parts:
        print(f"  📊 {' | '.join(status_parts)}")

def resolve_all_seed_files():
    """Find and return paths to all available seed data files."""
    seed_files = {'intents': None, 'claude': None, 'gemini': None}
    
    for name in seed_files.keys():
        filename = f"{name}.json"
        for search_dir in SEARCH_DIRS:
            candidate = search_dir / filename
            if candidate.exists():
                seed_files[name] = candidate
                break
    
    found_files = {k: v for k, v in seed_files.items() if v is not None}
    if not found_files:
        raise FileNotFoundError("No seed data files found.")
    
    print(f"Found {len(found_files)} seed file(s):")
    for name, path in found_files.items():
        print(f"  - {name}.json: {path}")
    
    return found_files

SEED_FILES = resolve_all_seed_files()
SEED_SAMPLE_SIZE = 500
TARGET_GENERATION_SIZE = 50000

# API Client Initialization
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAF0jRW5m446-N6Gp8UO_vWo8HYQWaAyIk")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "EMPTY")
QWEN_API_BASE = os.getenv("QWEN_API_BASE", "http://localhost:11434/v1")

# Initialize Gemini (optional, for when quota available)
gemini_client = None
try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    print("✓ Gemini client initialized (will use when quota available)")
except Exception as e:
    print(f"⚠️ Gemini client failed: {e}")
    print("   Will use Qwen-only mode")

# Initialize Qwen (primary)
from openai import OpenAI
qwen_client = None
try:
    qwen_client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_API_BASE,
        timeout=15.0,
        max_retries=0
    )
    print("✓ Qwen client initialized (PRIMARY)")
except Exception as e:
    print(f"ERROR: Qwen client failed: {e}")
    raise RuntimeError("Cannot proceed without Qwen client")

# --- Structured Output Schema ---
ALPAC_SCHEMA = types.Schema(
    type=types.Type.ARRAY,
    description="A list of high-quality Alpaca-style instruction tuning examples.",
    items=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "instruction": types.Schema(type=types.Type.STRING, description="The user's question or symptom."),
            "input": types.Schema(type=types.Type.STRING, description="Mandatory medical or contextual data for elderly focus."),
            "output": types.Schema(type=types.Type.STRING, description="Safe, simple, actionable medical/wellness advice.")
        },
        required=["instruction", "input", "output"]
    )
)

# --- Master System Prompt ---
MASTER_SYSTEM_PROMPT = """
You are an AI Geriatric Health Assistant. Your mission is to provide safe, simple, non-diagnostic, and proactive daily wellness and common medical advice tailored for an ELDERLY POPULATION (70+ years old).

STRICT SAFETY RULES:
1. CRITICAL: For severe symptoms (e.g., chest pain, stroke signs, sudden severe headache, profuse bleeding), the output MUST immediately advise contacting emergency services (e.g., "Call 911 or your local emergency number immediately").
2. NEVER diagnose a condition, suggest stopping prescribed medication, or recommend specific drug dosages.
3. The tone must be simple, encouraging, and easy for a non-technical senior citizen to understand.
4. Your output must be a JSON array of objects, strictly following the provided schema. Generate 10 unique, high-quality instruction-response triples per prompt.
"""

def load_seed_dataframe(path: Path) -> pd.DataFrame:
    """Load seed data flexibly from csv/json/jsonl."""
    suffix = path.suffix.lower()
    
    if suffix == '.json':
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list) and len(data) > 0:
                if all(isinstance(item, dict) and 'instruction' in item for item in data):
                    df = pd.DataFrame(data)
                    return df.rename(columns={'instruction': 'text', 'output': 'label'})
            
            if isinstance(data, dict) and "intents" in data:
                rows = []
                for item in data["intents"]:
                    patterns = item.get("patterns", [])
                    responses = item.get("responses", [])
                    if isinstance(patterns, str): patterns = [patterns]
                    if isinstance(responses, str): responses = [responses]
                    for p in patterns:
                        for r in responses:
                            rows.append({"text": p, "label": r})
                if rows:
                    return pd.DataFrame(rows)
        except Exception as e:
            print(f"JSON parsing failed: {e}")
    
    if suffix in {'.jsonl', '.jsonl.gz'}:
        df = pd.read_json(path, lines=True)
    elif suffix == '.json':
        df = pd.read_json(path)
    else:
        df = pd.read_csv(path, encoding='utf-8', sep=None, engine='python')
    
    text_candidates = ['text', 'question', 'prompt', 'input', 'instruction']
    label_candidates = ['label', 'answer', 'response', 'output']
    
    text_col = next((c for c in text_candidates if c in df.columns), None)
    label_col = next((c for c in label_candidates if c in df.columns), None)
    
    if not text_col or not label_col:
        raise ValueError(f"Seed file must contain text and label columns. Found: {df.columns.tolist()}")
    
    return df.rename(columns={text_col: 'text', label_col: 'label'})

def prepare_seed_data(seed_files_dict, sample_size):
    """Load and transform seed data from multiple sources."""
    print(f"Preparing seed data from {len(seed_files_dict)} file(s)...")
    all_seed_data = []
    
    for name, file_path in seed_files_dict.items():
        if file_path is None:
            continue
        
        print(f"  Loading {name}.json...")
        df = load_seed_dataframe(Path(file_path))
        samples_from_this_file = min(len(df), sample_size // len(seed_files_dict))
        df_sampled = df.sample(samples_from_this_file, random_state=42)
        
        for index, row in df_sampled.iterrows():
            instruction = row['text']
            output_advice = row['label']
            
            if name == 'intents':
                input_context = "Patient is generally well, seeking conversational advice."
            else:
                input_context = "Patient is elderly (70+), seeking immediate first aid guidance."
            
            all_seed_data.append({
                "instruction": instruction,
                "input": input_context,
                "output": output_advice,
                "source": name
            })
    
    import random
    random.seed(42)
    random.shuffle(all_seed_data)
    all_seed_data = all_seed_data[:sample_size]
    
    print(f"Prepared {len(all_seed_data)} seed samples.")
    return all_seed_data

def generate_synthetic_data(seed_data, target_size, gemini_client, qwen_client):
    """Generate data primarily with Qwen, with EXTREME safety measures."""
    global gemini_calls_today
    
    if not qwen_client:
        print("ERROR: Qwen client not available. Cannot proceed.")
        return []
    
    generated_count = 0
    synthetic_data = []
    batch_count = 0
    
    topics = [
        "Hydration and simple dietary advice for seniors",
        "Managing mild chronic pain (e.g., arthritis, backaches)",
        "Safety and fall prevention in the home",
        "Medication management and reminder tips",
        "Signs of common elderly illnesses (e.g., dehydration, flu)",
        "Tips for better sleep and managing fatigue",
        "Addressing mild memory concerns and cognitive engagement",
        "Diabetes management for seniors",
        "Hypertension and heart health for 70+",
        "Senior-safe exercise and mobility",
        "Treating minor cuts, burns, and bruises in elderly patients",
        "Managing headaches and migraines safely for seniors",
        "Dealing with nosebleeds and hiccups in older adults",
        "Sore throat and cough relief for the elderly",
        "Handling digestive issues (heartburn, constipation, nausea)",
        "Eye strain, dry eyes, and vision comfort for seniors",
        "Addressing loneliness and emotional well-being in seniors",
        "Managing stress and anxiety in elderly patients",
        "Sleep problems and insomnia in older adults",
        "Coping with grief and loss in senior years"
    ]
    
    print(f"\n🚀 Starting QWEN-PRIMARY generation mode")
    print(f"   Target: {target_size} samples")
    print(f"   Safety: CPU<{MAX_CPU_TEMP}°C, GPU<{MAX_GPU_TEMP}°C, RAM<{MAX_MEMORY_PERCENT}%\n")
    
    while generated_count < target_size:
        # === PRE-GENERATION HEALTH CHECK ===
        health_warnings, metrics = check_system_health()
        
        if health_warnings:
            print("\n🚨 SYSTEM HEALTH WARNING - PAUSING 🚨")
            for warning in health_warnings:
                print(f"  {warning}")
            print(f"  Cooling down for 3 minutes...")
            time.sleep(180)
            gc.collect()
            
            # Re-check after cooldown
            health_warnings, metrics = check_system_health()
            if health_warnings:
                print("  ⚠️ Still hot - extending cooldown to 5 minutes...")
                time.sleep(300)
                gc.collect()
            continue
        
        # Sample topic and seed examples
        current_topic = topics[generated_count % len(topics)]
        seed_sample = json.dumps(seed_data[:5], indent=2)
        
        generation_prompt = f"""
        Based on the following examples, generate 10 NEW and unique instruction/input/output JSON triples.
        The new examples must focus specifically on: **{current_topic}**.
        
        Example Seed Triples to follow (DO NOT REPLICATE THESE EXACTLY):
        {seed_sample}
        """
        
        # Decide which client to use
        import random
        
        # Use Gemini ONLY if:
        # 1. Gemini client available
        # 2. Under daily quota
        # 3. Random chance (10%)
        can_use_gemini = (
            gemini_client is not None and
            gemini_calls_today < GEMINI_DAILY_QUOTA and
            random.random() < GEMINI_RATIO
        )
        
        use_gemini = can_use_gemini
        active_client = gemini_client if use_gemini else qwen_client
        model_name = GEMINI_MODEL if use_gemini else QWEN_MODEL
        
        print(f"\n[Batch {batch_count+1}] Using {model_name}")
        print(f"  Topic: {current_topic[:60]}...")
        print_health_status(metrics)
        
        new_triples = []
        try:
            if use_gemini:
                response = active_client.models.generate_content(
                    model=model_name,
                    contents=generation_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=MASTER_SYSTEM_PROMPT,
                        response_mime_type="application/json",
                        response_schema=ALPAC_SCHEMA,
                        temperature=0.8
                    )
                )
                new_triples = json.loads(response.text)
                gemini_calls_today += 1
                print(f"  ✓ Gemini call successful (used {gemini_calls_today}/{GEMINI_DAILY_QUOTA} today)")
                
            else:
                # Qwen call - ULTRA conservative
                response = qwen_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                        {"role": "user", "content": generation_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8,
                    max_tokens=800  # Reduced from 1000 to minimize compute
                )
                data = json.loads(response.choices[0].message.content)
                if isinstance(data, list):
                    new_triples = data
                elif isinstance(data, dict):
                    for key, val in data.items():
                        if isinstance(val, list):
                            new_triples = val
                            break
            
            if new_triples:
                valid_triples = [t for t in new_triples if all(k in t for k in ["instruction", "input", "output"])]
                synthetic_data.extend(valid_triples)
                generated_count += len(valid_triples)
                print(f"  ✓ Generated {len(valid_triples)} triples")
                print(f"  📈 Progress: {generated_count}/{target_size} ({100*generated_count/target_size:.1f}%)")
                
                # Save incrementally
                with open(OUTPUT_FILE, "a") as f:
                    for item in valid_triples:
                        f.write(json.dumps(item) + "\n")
                
                batch_count += 1
                
                # Cooldown strategy
                if use_gemini:
                    print(f"  💤 Short cooldown (5s)...")
                    time.sleep(5)
                else:
                    # MANDATORY cooldown after Qwen
                    print(f"  😴 Mandatory cooldown after Qwen ({MANDATORY_COOLDOWN_EVERY_CALL}s)...")
                    time.sleep(MANDATORY_COOLDOWN_EVERY_CALL)
                    gc.collect()
                    
                    # Long cooldown every N batches
                    if batch_count % LONG_COOLDOWN_EVERY_N == 0:
                        print(f"  🛌 LONG cooldown ({LONG_COOLDOWN_DURATION}s) - batch {batch_count}")
                        time.sleep(LONG_COOLDOWN_DURATION)
                        gc.collect()
        
        except Exception as e:
            error_str = str(e)
            
            # Handle quota exhaustion
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                print(f"  ⚠️ Gemini quota exhausted ({gemini_calls_today}/{GEMINI_DAILY_QUOTA})")
                print(f"  ↪️  Switching to Qwen-only mode for remaining generations")
                gemini_calls_today = GEMINI_DAILY_QUOTA  # Block future Gemini calls
                time.sleep(5)
            else:
                print(f"  ❌ Generation failed with {model_name}: {error_str[:100]}")
                print(f"  Waiting 30 seconds before retry...")
                time.sleep(30)
                gc.collect()
    
    print(f"\n✅ GENERATION COMPLETE!")
    print(f"   Generated: {generated_count} samples")
    print(f"   File: {OUTPUT_FILE}")
    print(f"   Gemini calls used: {gemini_calls_today}/{GEMINI_DAILY_QUOTA}")
    return synthetic_data

if __name__ == "__main__":
    print("=" * 60)
    print("QWEN-PRIMARY MODE WITH EXTREME SAFETY")
    print("=" * 60)
    print(f"Safety Limits:")
    print(f"  - RAM: < {MAX_MEMORY_PERCENT}%")
    print(f"  - CPU Temp: < {MAX_CPU_TEMP}°C")
    print(f"  - GPU Temp: < {MAX_GPU_TEMP}°C")
    print(f"Cooldown Strategy:")
    print(f"  - After each Qwen call: {MANDATORY_COOLDOWN_EVERY_CALL}s")
    print(f"  - Every {LONG_COOLDOWN_EVERY_N} batches: {LONG_COOLDOWN_DURATION}s")
    print(f"Model Ratio:")
    print(f"  - Qwen (primary): ~90%")
    print(f"  - Gemini (when available): ~10%")
    print("=" * 60)
    
    seeds = prepare_seed_data(SEED_FILES, SEED_SAMPLE_SIZE)
    generate_synthetic_data(seeds, TARGET_GENERATION_SIZE, gemini_client, qwen_client)
