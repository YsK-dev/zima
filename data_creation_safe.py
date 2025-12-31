import os
import json
import time
import psutil
import gc
from pathlib import Path
import pandas as pd
from google import genai
from google.genai import types

# --- Configuration Constants ---
GEMINI_MODEL = 'gemini-3-flash-preview'  # SOTA Teacher Model (Released Dec 17, 2025)
QWEN_MODEL = 'qwen3:4b'           # CPU-Optimized Local Teacher Model (Ryzen 9 5900X)
OUTPUT_FILE = 'synthetic_geriatric_data.jsonl'

# SAFETY LIMITS to prevent PC shutdown
MAX_MEMORY_PERCENT = 75  # Stop if RAM usage exceeds this
MAX_CPU_TEMP = 80  # Stop if CPU temp exceeds this (Celsius)
COOLDOWN_EVERY_N_BATCHES = 5  # Take a break every N generations
COOLDOWN_DURATION = 10  # Seconds to rest between batches

# Resolve seed files across common notebook locations (Colab/local/Drive/Windows path provided)
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
INTENTS_ENV = os.getenv("INTENTS_JSON_PATH")

# Base directories to search for seed files
SEARCH_DIRS = [
    Path("."),
    Path("aws;_colab/archive"),
    BASE_DIR,
    Path.cwd()
]

def check_system_health():
    """Monitor system resources and return warnings if limits are exceeded."""
    warnings = []
    
    # Check RAM
    mem = psutil.virtual_memory()
    if mem.percent > MAX_MEMORY_PERCENT:
        warnings.append(f"⚠️ RAM usage at {mem.percent:.1f}% (limit: {MAX_MEMORY_PERCENT}%)")
    
    # Check CPU temperature (if available)
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps or 'k10temp' in temps:
            temp_key = 'k10temp' if 'k10temp' in temps else 'coretemp'
            cpu_temp = max([t.current for t in temps[temp_key]])
            if cpu_temp > MAX_CPU_TEMP:
                warnings.append(f"🔥 CPU temp at {cpu_temp}°C (limit: {MAX_CPU_TEMP}°C)")
    except:
        pass  # Temperature monitoring not available
    
    return warnings

def resolve_all_seed_files():
    """Find and return paths to all available seed data files."""
    seed_files = {
        'intents': None,
        'claude': None,
        'gemini': None
    }
    
    # Check environment variable for intents.json first
    if INTENTS_ENV:
        p = Path(INTENTS_ENV)
        if p.exists():
            seed_files['intents'] = p
    
    # Search for each seed file in all directories
    for name in seed_files.keys():
        if seed_files[name] is not None:
            continue  # Already found via env var
        
        filename = f"{name}.json"
        for search_dir in SEARCH_DIRS:
            candidate = search_dir / filename
            if candidate.exists():
                seed_files[name] = candidate
                break
    
    # At least one seed file must exist
    found_files = {k: v for k, v in seed_files.items() if v is not None}
    if not found_files:
        checked = [str(d / "*.json") for d in SEARCH_DIRS[:5]]  # Show first 5 for brevity
        raise FileNotFoundError(
            f"No seed data files found. Looking for: intents.json, claude.json, gemini.json.\n"
            f"Searched in: {', '.join(checked)}..."
        )
    
    print(f"Found {len(found_files)} seed file(s):")
    for name, path in found_files.items():
        print(f"  - {name}.json: {path}")
    
    return found_files

SEED_FILES = resolve_all_seed_files()
SEED_SAMPLE_SIZE = 500  # Only use a small, diverse subset of the mental health data
TARGET_GENERATION_SIZE = 50000 # The number of high-quality examples we aim to generate

# API Client Initialization
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAF0jRW5m446-N6Gp8UO_vWo8HYQWaAyIk")  # Fallback from list_models.py
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "EMPTY") # Default for local vLLM/Ollama
QWEN_API_BASE = os.getenv("QWEN_API_BASE", "http://localhost:11434/v1")

try:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
    if not gemini_client:
        print("WARNING: GEMINI_API_KEY not set. Gemini generation will be skipped.")
except Exception as e:
    print(f"ERROR: Failed to initialize Google GenAI Client: {e}")
    gemini_client = None

# For Qwen 3 (OpenAI compatible API)
from openai import OpenAI
try:
    qwen_client = OpenAI(
        api_key=QWEN_API_KEY, 
        base_url=QWEN_API_BASE,
        timeout=30.0,  # Add timeout to prevent hanging
        max_retries=2   # Limit retries
    )
except Exception as e:
    print(f"ERROR: Failed to initialize OpenAI client for Qwen: {e}")
    qwen_client = None

# --- 1. Define the Structured Output Schema (Alpaca Format) ---
ALPAC_SCHEMA = types.Schema(
    type=types.Type.ARRAY,
    description="A list of high-quality Alpaca-style instruction tuning examples.",
    items=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "instruction": types.Schema(type=types.Type.STRING, description="The user's question or symptom."),
            "input": types.Schema(type=types.Type.STRING, description="Mandatory medical or contextual data for elderly focus (e.g., 'Patient is 78, takes blood thinner')."),
            "output": types.Schema(type=types.Type.STRING, description="The safe, simple, and actionable medical/wellness advice from the AI.")
        },
        required=["instruction", "input", "output"]
    )
)

# --- 2. Master System Prompt (Safety Critical) ---
MASTER_SYSTEM_PROMPT = """
You are an AI Geriatric Health Assistant. Your mission is to provide safe, simple, non-diagnostic, and proactive daily wellness and common medical advice tailored for an ELDERLY POPULATION (70+ years old).

STRICT SAFETY RULES:
1. CRITICAL: For severe symptoms (e.g., chest pain, stroke signs, sudden severe headache, profuse bleeding), the output MUST immediately advise contacting emergency services (e.g., "Call 911 or your local emergency number immediately").
2. NEVER diagnose a condition, suggest stopping prescribed medication, or recommend specific drug dosages.
3. The tone must be simple, encouraging, and easy for a non-technical senior citizen to understand.
4. Your output must be a JSON array of objects, strictly following the provided schema. Generate 10 unique, high-quality instruction-response triples per prompt.
"""

def load_seed_dataframe(path: Path) -> pd.DataFrame:
    """Load seed data flexibly from csv/json/jsonl and validate required columns."""
    suffix = path.suffix.lower()
    
    # 1. Try parsing as JSON first
    if suffix == '.json':
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle array of {instruction, input, output} objects (Alpaca/Claude/Gemini format)
            if isinstance(data, list) and len(data) > 0:
                if all(isinstance(item, dict) and 'instruction' in item for item in data):
                    # Direct Alpaca format - map to text/label
                    df = pd.DataFrame(data)
                    # Combine instruction as text, output as label
                    # Keep input for context but use instruction as the primary text
                    print(f"Detected Alpaca format. Loaded {len(df)} instruction-output pairs.")
                    return df.rename(columns={'instruction': 'text', 'output': 'label'})
            
            # Handle {"intents": [...]} format (mental health chatbot)
            if isinstance(data, dict) and "intents" in data and isinstance(data["intents"], list):
                rows = []
                for item in data["intents"]:
                    patterns = item.get("patterns", [])
                    responses = item.get("responses", [])
                    
                    # Ensure lists
                    if isinstance(patterns, str): patterns = [patterns]
                    if isinstance(responses, str): responses = [responses]
                    
                    # Create pairs
                    for p in patterns:
                        for r in responses:
                            rows.append({"text": p, "label": r})
                
                if rows:
                    print(f"Detected 'intents' format. Parsed {len(rows)} text-label pairs.")
                    return pd.DataFrame(rows)
                    
        except Exception as e:
            print(f"JSON parsing failed: {e}. Falling back to pandas.")

    # 2. Fallback to Pandas loaders
    if suffix in {'.jsonl', '.jsonl.gz'}:
        df = pd.read_json(path, lines=True)
    elif suffix == '.json':
        df = pd.read_json(path)
    else:
        # Allow automatic delimiter detection; fallback to python engine for robustness
        df = pd.read_csv(path, encoding='utf-8', sep=None, engine='python')

    # 3. Identify text/label columns
    text_candidates = ['text', 'question', 'prompt', 'input', 'instruction', 'pattern', 'patterns']
    label_candidates = ['label', 'answer', 'response', 'output', 'responses']
    
    text_col = next((c for c in text_candidates if c in df.columns), None)
    label_col = next((c for c in label_candidates if c in df.columns), None)
    
    if not text_col or not label_col:
        raise ValueError(
            f"Seed file must contain text and label columns. Found columns: {df.columns.tolist()}. "
            "Tried candidates: " + ",".join(text_candidates) + " / " + ",".join(label_candidates)
        )
        
    # If columns contain lists (e.g. from raw json), explode them or take first
    # This is a simple heuristic
    if not df.empty:
        if isinstance(df[text_col].iloc[0], list):
            df = df.explode(text_col)
        if isinstance(df[label_col].iloc[0], list):
            df = df.explode(label_col)
        
    return df.rename(columns={text_col: 'text', label_col: 'label'})

def prepare_seed_data(seed_files_dict, sample_size):
    """Loads and transforms seed data from multiple sources into Alpaca format.
    
    Args:
        seed_files_dict: Dictionary mapping seed names to file paths
        sample_size: Total number of samples to use across all seed files
    
    Returns:
        List of seed data dictionaries in Alpaca format
    """
    print(f"Preparing seed data from {len(seed_files_dict)} file(s)...")
    
    all_seed_data = []
    
    # Load data from each seed file
    for name, file_path in seed_files_dict.items():
        if file_path is None:
            continue
            
        print(f"  Loading {name}.json...")
        df = load_seed_dataframe(Path(file_path))
        
        # Sample proportionally from each source
        samples_from_this_file = min(len(df), sample_size // len(seed_files_dict))
        df_sampled = df.sample(samples_from_this_file, random_state=42)
        
        for index, row in df_sampled.iterrows():
            instruction = row['text']
            output_advice = row['label']
            
            # Context varies by source
            if name == 'intents':
                # Mental health conversational context
                input_context = "Patient is generally well, seeking conversational advice."
            else:
                # First aid / medical advice context (claude/gemini)
                input_context = "Patient is elderly (70+), seeking immediate first aid guidance."
            
            all_seed_data.append({
                "instruction": instruction,
                "input": input_context,
                "output": output_advice,
                "source": name  # Track which seed file this came from
            })
    
    # Shuffle to mix different sources
    import random
    random.seed(42)
    random.shuffle(all_seed_data)
    
    # Limit to target sample size
    all_seed_data = all_seed_data[:sample_size]
    
    print(f"Prepared {len(all_seed_data)} seed samples from {len(seed_files_dict)} source(s).")
    
    # Print distribution by source
    from collections import Counter
    source_counts = Counter([s['source'] for s in all_seed_data])
    for source, count in source_counts.items():
        print(f"    - {source}: {count} samples")
    
    return all_seed_data

### B. Generation Script

def generate_synthetic_data(seed_data, target_size, gemini_client, qwen_client):
    """Iteratively calls Gemini and Qwen to generate structured data with safety checks."""
    if not gemini_client and not qwen_client:
        print("ERROR: No AI clients available. Check your API keys and endpoints.")
        return []
    
    generated_count = 0
    synthetic_data = []
    batch_count = 0
    
    # Topics for guided generation to ensure diversity and domain focus
    topics = [
        # Geriatric-specific topics
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
        # First aid topics (from claude/gemini seed data)
        "Treating minor cuts, burns, and bruises in elderly patients",
        "Managing headaches and migraines safely for seniors",
        "Dealing with nosebleeds and hiccups in older adults",
        "Sore throat and cough relief for the elderly",
        "Handling digestive issues (heartburn, constipation, nausea)",
        "Eye strain, dry eyes, and vision comfort for seniors",
        # Mental health topics (from intents seed data)
        "Addressing loneliness and emotional well-being in seniors",
        "Managing stress and anxiety in elderly patients",
        "Sleep problems and insomnia in older adults",
        "Coping with grief and loss in senior years"
    ]
    
    while generated_count < target_size:
        # === SAFETY CHECK ===
        health_warnings = check_system_health()
        if health_warnings:
            print("\n🚨 SYSTEM HEALTH WARNING 🚨")
            for warning in health_warnings:
                print(f"  {warning}")
            print("Pausing for 60 seconds to let system cool down...")
            time.sleep(60)
            gc.collect()  # Force garbage collection
            continue
        
        # Sample a topic and some seed examples
        current_topic = topics[generated_count % len(topics)]
        seed_sample = json.dumps(seed_data[:5], indent=2)

        generation_prompt = f"""
        Based on the following examples, generate 10 NEW and unique instruction/input/output JSON triples.
        The new examples must focus specifically on: **{current_topic}**.

        Example Seed Triples to follow (DO NOT REPLICATE THESE EXACTLY):
        {seed_sample}
        """
        
        # Decide which client to use (alternate or based on availability)
        use_gemini = (generated_count // 10) % 2 == 0 if (gemini_client and qwen_client) else bool(gemini_client)
        
        active_client = gemini_client if use_gemini else qwen_client
        model_name = GEMINI_MODEL if use_gemini else QWEN_MODEL
        
        print(f"[Batch {batch_count+1}] Generating with {model_name} | Topic: {current_topic[:50]}...")
        
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
                # Qwen 3 via OpenAI API with reduced context
                response = active_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                        {"role": "user", "content": generation_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8,
                    max_tokens=2000  # Limit output length
                )
                # Note: OpenAI response needs parsing based on ALPAC_SCHEMA manually if not supported natively
                data = json.loads(response.choices[0].message.content)
                # Handle different JSON structures from different models
                if isinstance(data, list):
                    new_triples = data
                elif isinstance(data, dict):
                    # Look for the list inside the dict (e.g. {"examples": [...]})
                    for key, val in data.items():
                        if isinstance(val, list):
                            new_triples = val
                            break
                
            if new_triples:
                # Basic validation
                valid_triples = [t for t in new_triples if all(k in t for k in ["instruction", "input", "output"])]
                synthetic_data.extend(valid_triples)
                generated_count += len(valid_triples)
                print(f"✓ Generated {len(valid_triples)} triples. Total: {generated_count}/{target_size}")
                
                # Append to file incrementally
                with open(OUTPUT_FILE, "a") as f:
                    for item in valid_triples:
                        f.write(json.dumps(item) + "\n")
                
                batch_count += 1
                
                # Periodic cooldown to prevent overheating
                if batch_count % COOLDOWN_EVERY_N_BATCHES == 0:
                    print(f"💤 Cooldown break ({COOLDOWN_DURATION}s) after {batch_count} batches...")
                    time.sleep(COOLDOWN_DURATION)
                    gc.collect()  # Clear memory
            
        except Exception as e:
            print(f"❌ Generation failed with {model_name}: {e}")
            print("Waiting 10 seconds before retry...")
            time.sleep(10)
            gc.collect()
            
    print(f"\n✅ Stage 1 Complete. Data saved to {OUTPUT_FILE}")
    return synthetic_data

if __name__ == "__main__":
    print("=== SAFE DATA GENERATION MODE ===")
    print(f"Safety limits: RAM<{MAX_MEMORY_PERCENT}%, CPU<{MAX_CPU_TEMP}°C")
    print(f"Cooldown: Every {COOLDOWN_EVERY_N_BATCHES} batches for {COOLDOWN_DURATION}s\n")
    
    # 1. Prepare Seed Data from all available sources
    seeds = prepare_seed_data(SEED_FILES, SEED_SAMPLE_SIZE)
    
    # 2. Run Generation
    print(f"\nStarting generation pipeline with target size: {TARGET_GENERATION_SIZE}")
    print(f"Using teacher models: {GEMINI_MODEL} and {QWEN_MODEL}")
    generate_synthetic_data(seeds, TARGET_GENERATION_SIZE, gemini_client, qwen_client)
