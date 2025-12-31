"""
Lightning.ai Data Generation - 100% Local GPU Generation
=========================================================

Pure local generation using:
- GPU-accelerated Qwen 14B model (NVIDIA L40 - 48GB VRAM)
- No external API dependencies
- Optimized for 4-hour Lightning.ai free tier

Target: 50,000 samples in ~3-4 hours
"""

import os
import json
import time
from pathlib import Path
import pandas as pd

# --- LIGHTNING.AI GPU-OPTIMIZED Configuration ---
QWEN_MODEL = 'qwen2.5:14b'  # Optimized for L40 GPU (48GB VRAM)
OUTPUT_FILE = 'synthetic_geriatric_data.jsonl'

# GPU OPTIMIZATION
BATCH_SIZE = 20  # Generate 20 samples per call
COOLDOWN_SECONDS = 1  # Minimal cooldown

# Time tracking (4-hour limit)
import datetime
START_TIME = datetime.datetime.now()
MAX_RUNTIME_HOURS = 3.5  # Stop at 3.5 hours to save checkpoint

def time_remaining():
    """Check remaining time in 4-hour window."""
    elapsed = (datetime.datetime.now() - START_TIME).total_seconds() / 3600
    remaining = MAX_RUNTIME_HOURS - elapsed
    return max(0, remaining)

# Resolve seed files
BASE_DIR = Path.cwd()
SEARCH_DIRS = [Path("."), BASE_DIR]

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
        # Create dummy seed if none found
        print("⚠️  No seed files found - will use minimal seed data")
        return {}
    
    print(f"Found {len(found_files)} seed file(s):")
    for name, path in found_files.items():
        print(f"  - {name}.json: {path}")
    
    return found_files

SEED_FILES = resolve_all_seed_files()
SEED_SAMPLE_SIZE = 500
TARGET_GENERATION_SIZE = 50000

# Initialize Qwen client (100% local, GPU-accelerated)
QWEN_API_KEY = "EMPTY"
QWEN_API_BASE = "http://localhost:11434/v1"

from openai import OpenAI
qwen_client = None
try:
    qwen_client = OpenAI(
        api_key=QWEN_API_KEY,
        base_url=QWEN_API_BASE,
        timeout=60.0,  # Longer timeout for larger model
        max_retries=1
    )
    print("✓ Qwen client initialized (GPU-ACCELERATED)")
except Exception as e:
    print(f"⚠️ Qwen client initialization deferred: {e}")

# --- Master System Prompt for Local Generation ---
MASTER_SYSTEM_PROMPT = f"""You are an AI Geriatric Health Assistant providing PRACTICAL, ACTIONABLE wellness and first-aid advice for elderly patients (70+ years).

CRITICAL FORMATTING RULES:
1. Your response MUST be a JSON array (list) containing exactly {BATCH_SIZE} objects
2. Each object must have: "instruction", "input", "output"
3. ALWAYS return an array, NEVER a single object

QUALITY RULES - VERY IMPORTANT:
1. Provide SPECIFIC, ACTIONABLE advice that seniors can do at home
2. Include practical steps: "Apply ice for 15 minutes", "Drink 8 glasses of water", "Use a heating pad"
3. Only suggest "see a doctor" for: severe emergencies, symptoms lasting weeks, or concerning changes
4. For common issues (mild pain, colds, fatigue, constipation): Give home remedies FIRST
5. Make advice IMMEDIATELY HELPFUL, not just "consult your doctor"

MEDICAL SAFETY:
- For EMERGENCIES (chest pain, stroke signs, severe bleeding, difficulty breathing): IMMEDIATELY advise calling 911
- For chronic/worsening symptoms: Recommend doctor visit AFTER providing immediate relief steps
- Never diagnose conditions or suggest stopping prescribed medications
- Use simple, encouraging language

EXAMPLES OF GOOD vs BAD OUTPUTS:

❌ BAD: "You should see your doctor about that headache"
✅ GOOD: "Rest in a quiet, dark room. Apply a cool cloth to your forehead. Take acetaminophen as directed. If headache lasts more than 2 days or is severe, contact your doctor."

❌ BAD: "Consult a doctor for constipation advice"
✅ GOOD: "Drink more water and eat high-fiber foods like prunes, oatmeal, and vegetables. Walk for 15-20 minutes daily. If no improvement after 3 days, contact your doctor."

❌ BAD: "See a doctor for your cold"
✅ GOOD: "Rest and drink warm fluids like tea with honey. Use saline nasal spray to clear congestion. Gargle with warm salt water for sore throat. Take over-the-counter cold medicine as directed on the package."

REQUIRED OUTPUT FORMAT (JSON array with {BATCH_SIZE} objects):
[
  {{
    "instruction": "What can I do about constipation?",
    "input": "Patient is 73 years old, reports infrequent bowel movements.",
    "output": "Drink 8-10 glasses of water daily. Eat more fiber: prunes, whole grains, vegetables. Walk for 20 minutes after meals. Try sitting on toilet same time each day. If no improvement in 3 days, contact your doctor."
  }},
  {{
    "instruction": "My ankle is swollen",
    "input": "Patient is 76, twisted ankle yesterday.",
    "output": "Rest and elevate your ankle above heart level. Apply ice wrapped in a towel for 15-20 minutes every 2 hours. Take ibuprofen if not contraindicated. If swelling doesn't improve in 24 hours or you can't bear weight, see a doctor."
  }}
  ... ({BATCH_SIZE} total)
]

REMEMBER: Be HELPFUL and SPECIFIC! Give actionable steps seniors can take RIGHT NOW!
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
    if not seed_files_dict:
        # Minimal fallback seed data
        return [{
            "instruction": "What should I do if I feel dizzy?",
            "input": "Patient is 75 years old, takes blood pressure medication.",
            "output": "Sit down immediately to prevent falls. Drink water slowly. If dizziness persists or worsens, contact your doctor."
        }]
    
    print(f"Preparing seed data from {len(seed_files_dict)} file(s)...")
    all_seed_data = []
    
    for name, file_path in seed_files_dict.items():
        if file_path is None:
            continue
        
        print(f"  Loading {name}.json...")
        df = load_seed_dataframe(Path(file_path))
        samples_from_this_file = min(len(df), sample_size // len(seed_files_dict))
        df_sampled = df.sample(min(samples_from_this_file, len(df)), random_state=42)
        
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

def generate_synthetic_data(seed_data, target_size, qwen_client):
    """Generate data with 100% local GPU acceleration - Lightning.ai optimized."""
    if not qwen_client:
        print("ERROR: Qwen client not available!")
        return []
    
    generated_count = 0
    batch_count = 0
    
    topics = [
        "Hydration and dietary advice", "Chronic pain management",
        "Fall prevention", "Medication management", "Common illnesses",
        "Sleep and fatigue", "Memory and cognition", "Diabetes management",
        "Heart health", "Exercise safety", "Treating minor injuries",
        "Headache management", "Nosebleeds", "Sore throat relief",
        "Digestive issues", "Vision comfort", "Emotional well-being",
        "Stress and anxiety", "Insomnia", "Grief and loss"
    ]
    
    print(f"\n🚀 LIGHTNING.AI 100% LOCAL GPU MODE - NVIDIA L40")
    print(f"   Target: {target_size} samples")
    print(f"   Batch size: {BATCH_SIZE} samples/call")
    print(f"   Time limit: {MAX_RUNTIME_HOURS:.1f} hours")
    print(f"   Model: {QWEN_MODEL} (GPU-accelerated)")
    print(f"   Mode: 100% Local (No external APIs)\n")
    
    import random
    random.seed(42)
    
    while generated_count < target_size:
        # Check time limit
        remaining = time_remaining()
        if remaining <= 0:
            print(f"\n⏰ Time limit reached! Stopping at {generated_count} samples.")
            break
        
        # Progress update every 100 batches
        if batch_count % 100 == 0 and batch_count > 0:
            elapsed = (datetime.datetime.now() - START_TIME).total_seconds() / 3600
            rate = generated_count / elapsed if elapsed > 0 else 0
            eta = (target_size - generated_count) / rate if rate > 0 else 0
            print(f"\n📊 Checkpoint {batch_count}")
            print(f"   Progress: {generated_count}/{target_size} ({100*generated_count/target_size:.1f}%)")
            print(f"   Speed: {rate:.0f} samples/hour")
            print(f"   ETA: {eta:.1f} hours")
            print(f"   Time remaining: {remaining:.1f} hours\n")
        
        topic = topics[generated_count % len(topics)]
        seed_sample = json.dumps(seed_data[:5], indent=2)
        
        generation_prompt = f"""
        Generate {BATCH_SIZE} NEW unique instruction/input/output JSON triples about: {topic}
        
        Examples:
        {seed_sample}
        """
        
        if batch_count % 50 == 0:  # Print every 50 batches
            print(f"[Batch {batch_count+1}] {QWEN_MODEL} | {generated_count}/{target_size}")
        
        try:
            # Pure local Qwen generation - GPU accelerated
            response = qwen_client.chat.completions.create(
                model=QWEN_MODEL,
                messages=[
                    {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                    {"role": "user", "content": generation_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8,
                max_tokens=3000  # Larger for batch of 20
            )
            
            # DEBUG: Show raw response
            raw_content = response.choices[0].message.content
            if batch_count < 3:  # Only print first 3 for debugging
                print(f"  🔍 DEBUG - Raw response preview: {raw_content[:200]}...")
            
            data = json.loads(raw_content)
            
            # DEBUG: Show parsed structure
            if batch_count < 3:
                print(f"  🔍 DEBUG - Parsed type: {type(data)}")
                if isinstance(data, dict):
                    print(f"  🔍 DEBUG - Dict keys: {list(data.keys())}")
            
            # Handle different response formats
            if isinstance(data, list):
                triples = data
            elif isinstance(data, dict):
                # Check if it's a single example with the right keys
                if all(k in data for k in ["instruction", "input", "output"]):
                    # Model returned single example instead of array - wrap it
                    triples = [data]
                    if batch_count < 3:
                        print(f"  ⚠️  Model returned single example instead of array - wrapping...")
                else:
                    # Try to find the list of examples in the dict
                    triples = next((v for v in data.values() if isinstance(v, list)), [])
                    if not triples:
                        # Might be a single-level dict with keys like "examples", "data", "results"
                        for key in ['examples', 'data', 'results', 'samples', 'triples']:
                            if key in data and isinstance(data[key], list):
                                triples = data[key]
                                break
            else:
                triples = []
            
            if batch_count < 3:
                print(f"  🔍 DEBUG - Found {len(triples)} triples")
            
            # Validate and save
            valid = [t for t in triples if isinstance(t, dict) and all(k in t for k in ["instruction", "input", "output"])]
            
            if batch_count < 3:
                print(f"  🔍 DEBUG - Valid triples: {len(valid)}")
                if len(valid) == 0 and len(triples) > 0:
                    print(f"  🔍 DEBUG - Sample triple: {triples[0]}")
            
            if valid:
                with open(OUTPUT_FILE, "a") as f:
                    for item in valid:
                        f.write(json.dumps(item) + "\n")
                
                generated_count += len(valid)
                batch_count += 1
                print(f"  ✓ Generated {len(valid)} valid samples | Total: {generated_count}/{target_size}")
                
                # Minimal cooldown
                time.sleep(COOLDOWN_SECONDS)
            else:
                # No valid triples found - show why
                print(f"  ⚠️  No valid triples found (got {len(triples)} triples total)")
                if len(triples) > 0:
                    print(f"  📝 Sample: {json.dumps(triples[0], indent=2)[:300]}")
                time.sleep(2)
        
        except Exception as e:
            error_str = str(e)
            print(f"  ❌ Error: {error_str}")
            import traceback
            print(f"  📍 Traceback: {traceback.format_exc()[:500]}")
            time.sleep(5)
    
    print(f"\n✅ GENERATION COMPLETE!")
    print(f"   Generated: {generated_count} samples")
    print(f"   Runtime: {(datetime.datetime.now() - START_TIME).total_seconds() / 3600:.2f} hours")
    print(f"   File: {OUTPUT_FILE}")
    return generated_count

if __name__ == "__main__":
    print("=" * 70)
    print("LIGHTNING.AI 100% LOCAL GPU-ACCELERATED DATA GENERATION")
    print("=" * 70)
    print(f"Hardware: NVIDIA L40 GPU (48GB VRAM)")
    print(f"Model: {QWEN_MODEL}")
    print(f"Batch Size: {BATCH_SIZE} samples/call")
    print(f"Target: {TARGET_GENERATION_SIZE} samples")
    print(f"Time Limit: {MAX_RUNTIME_HOURS} hours")
    print(f"Mode: 100% Local (No external APIs)")
    print("=" * 70)
    
    seeds = prepare_seed_data(SEED_FILES, SEED_SAMPLE_SIZE)
    
    final_count = generate_synthetic_data(seeds, TARGET_GENERATION_SIZE, qwen_client)
    
    print(f"\n📥 Download {OUTPUT_FILE} from Lightning.ai now!")
    print(f"   Total samples: {final_count}")
