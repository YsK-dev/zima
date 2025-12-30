import os
import json
import time
from pathlib import Path
import pandas as pd
from google import genai
from google.genai import types

# --- Configuration Constants ---
GEMINI_MODEL = 'gemini-3-flash-preview'  # SOTA Teacher Model (Released Dec 17, 2025)
QWEN_MODEL = 'qwen3:30b'          # Local Teacher Model (Ryzen 9 5900X)
OUTPUT_FILE = 'synthetic_geriatric_data.jsonl'

# Resolve seed file across common notebook locations (Colab/local/Drive/Windows path provided)
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
INTENTS_ENV = os.getenv("INTENTS_JSON_PATH")
CANDIDATE_SEED_PATHS = [
    Path("intents.json"),
    Path("archive/intents.json"),
    Path("aws;_colab/archive/intents.json"),
    BASE_DIR / "intents.json",
    BASE_DIR / "archive/intents.json",
    BASE_DIR / "aws;_colab/archive/intents.json",
    Path.cwd() / "intents.json",
    Path.cwd() / "archive/intents.json",
    Path.cwd() / "aws;_colab/archive/intents.json",
    Path("/content/drive/MyDrive/intents.json"),
    Path("/content/drive/MyDrive/archive/intents.json"),
    Path("/content/drive/MyDrive/aws;_colab/archive/intents.json"),
    Path("/content/drive/MyDrive/Colab Notebooks/intents.json"),
    Path("/content/drive/MyDrive/Colab Notebooks/archive/intents.json"),
    Path("/content/drive/MyDrive/Colab Notebooks/aws;_colab/archive/intents.json"),
    Path(r"C:\Users\Adnan Menderes Üni\Yusuf-sertkaya\intents.json"),
    Path(r"C:\Users\Adnan Menderes Üni\Yusuf-sertkaya\archive\intents.json"),
]

def resolve_seed_path():
    if INTENTS_ENV:
        p = Path(INTENTS_ENV)
        if p.exists():
            return p
    checked = []
    for p in CANDIDATE_SEED_PATHS:
        checked.append(str(p))
        if p.exists():
            return p
    raise FileNotFoundError(
        "intents.json not found. Place it next to the notebook, under archive/, aws;_colab/archive/, set INTENTS_JSON_PATH env var, or ensure your Drive/Windows path is mounted. Checked: " + ", ".join(checked)
    )

KAGGLE_SEED_PATH = resolve_seed_path()
SEED_SAMPLE_SIZE = 500  # Only use a small, diverse subset of the mental health data
TARGET_GENERATION_SIZE = 50000 # The number of high-quality examples we aim to generate

# API Client Initialization
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
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
    qwen_client = OpenAI(api_key=QWEN_API_KEY, base_url=QWEN_API_BASE)
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
    
    # 1. Try parsing as standard 'intents.json' structure first if .json
    if suffix == '.json':
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle {"intents": [...]} format
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
            print(f"JSON parsing as intents failed: {e}. Falling back to pandas.")

    # 2. Fallback to Pandas loaders
    if suffix in {'.jsonl', '.jsonl.gz'}:
        df = pd.read_json(path, lines=True)
    elif suffix == '.json':
        df = pd.read_json(path)
    else:
        # Allow automatic delimiter detection; fallback to python engine for robustness
        df = pd.read_csv(path, encoding='utf-8', sep=None, engine='python')

    # 3. Identify text/label columns
    text_candidates = ['text', 'question', 'prompt', 'input', 'pattern', 'patterns']
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

def prepare_seed_data(file_path, sample_size):
    """Loads and transforms the Kaggle mental health data into Alpaca format for use as seeds."""
    print(f"Preparing seed data from {file_path}...")
    df = load_seed_dataframe(Path(file_path))
    df_sampled = df.sample(min(len(df), sample_size), random_state=42)
    
    seed_data = []
    for index, row in df_sampled.iterrows():
        # Transforming the 'mental health' context to a 'general health' context for the model to learn structure
        instruction = row['text']
        # Use a placeholder input since the original data is simple conversational
        input_context = "Patient is generally well, seeking conversational advice." 
        output_advice = row['label'] # Using the label/response as the 'output'
        
        # Add a simple conversion logic to general health for the prompt
        if 'anxiety' in instruction.lower():
            instruction = instruction.replace('anxiety', 'feeling stressed')
        
        seed_data.append({
            "instruction": instruction,
            "input": input_context,
            "output": output_advice
        })
    print(f"Prepared {len(seed_data)} seed samples.")
    return seed_data

### B. Generation Script

def generate_synthetic_data(seed_data, target_size, gemini_client, qwen_client):
    """Iteratively calls Gemini and Qwen to generate structured data."""
    if not gemini_client and not qwen_client:
        print("ERROR: No AI clients available. Check your API keys and endpoints.")
        return []
    
    generated_count = 0
    synthetic_data = []
    
    # Topics for guided generation to ensure diversity and domain focus
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
        "Senior-safe exercise and mobility"
    ]
    
    while generated_count < target_size:
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
        
        print(f"Attempting generation with {model_name} for topic: {current_topic}")
        
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
                # Qwen 3 via OpenAI API
                response = active_client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                        {"role": "user", "content": generation_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8
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
                print(f"Generated {len(valid_triples)} new triples. Total: {generated_count}/{target_size}")
                
                # Append to file incrementally
                with open(OUTPUT_FILE, "a") as f:
                    for item in valid_triples:
                        f.write(json.dumps(item) + "\n")
            
        except Exception as e:
            print(f"Generation failed with {model_name}: {e}")
            time.sleep(5) # Cooldown
            
    print(f"\n--- Stage 1 Complete. Data saved to {OUTPUT_FILE} ---")
    return synthetic_data
if __name__ == "__main__":
    # 1. Prepare Seed Data
    seeds = prepare_seed_data(KAGGLE_SEED_PATH, SEED_SAMPLE_SIZE)
    
    # 2. Run Generation
    print(f"Starting generation pipeline with target size: {TARGET_GENERATION_SIZE}")
    generate_synthetic_data(seeds, TARGET_GENERATION_SIZE, gemini_client, qwen_client)
