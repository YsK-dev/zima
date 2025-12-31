import os
import json
import time
import psutil
import gc
from pathlib import Path
import pandas as pd
from google import genai
from google.genai import types

# --- GEMINI-PRIMARY Configuration ---
GEMINI_MODEL = 'gemini-3-flash-preview'  # Latest and fastest Gemini model
QWEN_MODEL = 'qwen2.5:3b'  # Ultra-lightweight Qwen (3B instead of 4B)
OUTPUT_FILE = 'synthetic_geriatric_data.jsonl'

# EXTREME SAFETY LIMITS
MAX_MEMORY_PERCENT = 60  # Very conservative
MAX_CPU_TEMP = 65  # Very low threshold
MAX_GPU_TEMP = 70  # Very low threshold
COOLDOWN_AFTER_QWEN = 120  # 2 minutes rest after EACH Qwen call
COOLDOWN_AFTER_GEMINI_BATCH = 5  # 5 seconds after each Gemini batch

# Hybrid mode: Use Gemini as primary, Qwen sparingly
GEMINI_RATIO = 0.95  # 95% Gemini, 5% Qwen
MAX_QWEN_CALLS_PER_HOUR = 10  # Limit Qwen to 10 calls per hour

# Resolve seed files
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
SEARCH_DIRS = [Path("."), BASE_DIR, Path.cwd()]

def check_system_health():
    """Monitor system resources and return warnings if limits are exceeded."""
    warnings = []
    
    # Check RAM
    mem = psutil.virtual_memory()
    if mem.percent > MAX_MEMORY_PERCENT:
        warnings.append(f"⚠️ RAM usage at {mem.percent:.1f}% (limit: {MAX_MEMORY_PERCENT}%)")
    
    # Check CPU temperature
    try:
        temps = psutil.sensors_temperatures()
        if 'k10temp' in temps:
            cpu_temp = max([t.current for t in temps['k10temp']])
            if cpu_temp > MAX_CPU_TEMP:
                warnings.append(f"🔥 CPU temp at {cpu_temp}°C (limit: {MAX_CPU_TEMP}°C)")
        
        # Check GPU temperature
        if 'amdgpu' in temps:
            gpu_temp = max([t.current for t in temps['amdgpu']])
            if gpu_temp > MAX_GPU_TEMP:
                warnings.append(f"🔥 GPU temp at {gpu_temp}°C (limit: {MAX_GPU_TEMP}°C)")
    except Exception:
        pass
    
    # Check CPU usage
    cpu_percent = psutil.cpu_percent(interval=0.5)
    if cpu_percent > 85:
        warnings.append(f"⚠️ CPU usage at {cpu_percent:.1f}%")
    
    return warnings

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

try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
    print("✓ Gemini client initialized")
except Exception as e:
    print(f"ERROR: Failed to initialize Gemini: {e}")
    gemini_client = None

# For Qwen (optional, only if safe)
from openai import OpenAI
qwen_client = None
try:
    qwen_client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_API_BASE,
        timeout=15.0,
        max_retries=0  # No retries for Qwen
    )
    print("✓ Qwen client initialized (will use sparingly)")
except Exception as e:
    print(f"⚠️ Qwen client failed to initialize: {e}")
    print("   Will use Gemini-only mode")

# --- Structured Output Schema (Alpaca Format) ---
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
            
            # Handle Alpaca format
            if isinstance(data, list) and len(data) > 0:
                if all(isinstance(item, dict) and 'instruction' in item for item in data):
                    df = pd.DataFrame(data)
                    return df.rename(columns={'instruction': 'text', 'output': 'label'})
            
            # Handle intents format
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
    
    # Fallback
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
    """Generate data primarily with Gemini, use Qwen VERY sparingly."""
    if not gemini_client:
        print("ERROR: Gemini client not available. Cannot proceed.")
        return []
    
    generated_count = 0
    synthetic_data = []
    batch_count = 0
    qwen_calls_this_hour = 0
    hour_start_time = time.time()
    
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
    
    while generated_count < target_size:
        # Reset hourly Qwen counter
        if time.time() - hour_start_time > 3600:
            qwen_calls_this_hour = 0
            hour_start_time = time.time()
            print(f"📊 Hourly reset: Qwen calls available again (max {MAX_QWEN_CALLS_PER_HOUR}/hour)")
        
        # === HEALTH CHECK ===
        health_warnings = check_system_health()
        if health_warnings:
            print("\n🚨 SYSTEM HEALTH WARNING 🚨")
            for warning in health_warnings:
                print(f"  {warning}")
            print("⏸️  Pausing for 2 minutes to cool down...")
            time.sleep(120)
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
        
        # Only use Qwen if:
        # 1. Qwen client available
        # 2. Under hourly limit
        # 3. System is healthy
        # 4. Random chance (5%)
        can_use_qwen = (
            qwen_client is not None and
            qwen_calls_this_hour < MAX_QWEN_CALLS_PER_HOUR and
            not health_warnings and
            random.random() < (1 - GEMINI_RATIO)
        )
        
        use_gemini = not can_use_qwen or random.random() < GEMINI_RATIO
        
        active_client = gemini_client if use_gemini else qwen_client
        model_name = GEMINI_MODEL if use_gemini else QWEN_MODEL
        
        print(f"[Batch {batch_count+1}] Using {model_name} | Topic: {current_topic[:50]}...")
        
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
            else:
                # Qwen call - very conservative
                print("  ⚠️  Using local Qwen (rare) - monitoring closely...")
                response = active_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                        {"role": "user", "content": generation_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8,
                    max_tokens=1000  # Very short to reduce compute
                )
                data = json.loads(response.choices[0].message.content)
                if isinstance(data, list):
                    new_triples = data
                elif isinstance(data, dict):
                    for key, val in data.items():
                        if isinstance(val, list):
                            new_triples = val
                            break
                
                qwen_calls_this_hour += 1
            
            if new_triples:
                valid_triples = [t for t in new_triples if all(k in t for k in ["instruction", "input", "output"])]
                synthetic_data.extend(valid_triples)
                generated_count += len(valid_triples)
                print(f"✓ Generated {len(valid_triples)} triples. Total: {generated_count}/{target_size}")
                
                # Save incrementally
                with open(OUTPUT_FILE, "a") as f:
                    for item in valid_triples:
                        f.write(json.dumps(item) + "\n")
                
                batch_count += 1
                
                # Cooldown logic
                if use_gemini:
                    print(f"💤 Short cooldown ({COOLDOWN_AFTER_GEMINI_BATCH}s)...")
                    time.sleep(COOLDOWN_AFTER_GEMINI_BATCH)
                else:
                    print(f"😴 LONG cooldown after Qwen ({COOLDOWN_AFTER_QWEN}s)...")
                    time.sleep(COOLDOWN_AFTER_QWEN)
                    gc.collect()
        
        except Exception as e:
            print(f"❌ Generation failed with {model_name}: {e}")
            print("Waiting 20 seconds before retry...")
            time.sleep(20)
            gc.collect()
    
    print(f"\n✅ Generation Complete! Data saved to {OUTPUT_FILE}")
    return synthetic_data

if __name__ == "__main__":
    print("=== GEMINI-PRIMARY MODE (95% Cloud, 5% Local) ===")
    print(f"Safety: RAM<{MAX_MEMORY_PERCENT}%, CPU<{MAX_CPU_TEMP}°C, GPU<{MAX_GPU_TEMP}°C")
    print(f"Ratio: {GEMINI_RATIO*100:.0f}% Gemini, {(1-GEMINI_RATIO)*100:.0f}% Qwen")
    print(f"Qwen limit: {MAX_QWEN_CALLS_PER_HOUR} calls/hour\n")
    
    seeds = prepare_seed_data(SEED_FILES, SEED_SAMPLE_SIZE)
    
    print(f"\nStarting generation: Target {TARGET_GENERATION_SIZE} samples")
    print(f"Models: {GEMINI_MODEL} (primary) + {QWEN_MODEL} (rare)\n")
    generate_synthetic_data(seeds, TARGET_GENERATION_SIZE, gemini_client, qwen_client)
