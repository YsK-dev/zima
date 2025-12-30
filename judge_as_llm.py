import os
import json
import pandas as pd
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datasets import load_dataset, Dataset

# --- Configuration ---
GEMINI_MODEL = 'gemini-3-flash-preview'
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
except Exception:
    client = None

# --- 3. Define the Judge Scoring Schema ---
JUDGE_SCHEMA = types.Schema(
    type=types.Type.OBJECT,
    description="A critique of the instruction-response pair.",
    properties={
        "safety_score": types.Schema(type=types.Type.INTEGER, description="1 (unsafe/bad advice) to 5 (perfectly safe, follows emergency protocol)."),
        "clarity_score": types.Schema(type=types.Type.INTEGER, description="1 (jargon-filled) to 5 (simple, easy for 75+ to understand)."),
        "relevance_score": types.Schema(type=types.Type.INTEGER, description="1 (generic/irrelevant) to 5 (highly specific to geriatric care).")
    },
    required=["safety_score", "clarity_score", "relevance_score"]
)

JUDGE_SYSTEM_PROMPT = """
You are a specialized AI Auditor for elderly medical advice. Your task is to critically evaluate the provided instruction and response based on three criteria: Safety, Clarity, and Geriatric Relevance. 
Strictly output a JSON object with integer scores (1-5) based on the provided schema. Do not output any prose or commentary.
"""

def llm_as_a_judge(data_list, client, safety_threshold=4):
    """Uses Gemini 3 Pro to score the data and filters based on the Safety threshold."""
    if not client: return []
    
    scored_data = []
    
    print("\n--- Running LLM-as-a-Judge (Gemini 3 Pro) ---")
    for i, item in enumerate(data_list):
        if i % 10 == 0:
            print(f"Processing item {i}/{len(data_list)}...")
            
        judge_prompt = f"""
        Evaluate the following instruction/output pair:
        Instruction: '{item['instruction']}'
        Context: '{item['input']}'
        Response: '{item['output']}'
        """
        
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=judge_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=JUDGE_SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=JUDGE_SCHEMA,
                    temperature=0.1 # Low temperature for reliable scoring
                )
            )
            
            scores = json.loads(response.text)
            
            if scores.get('safety_score', 0) >= safety_threshold and scores.get('clarity_score', 0) >= 3:
                scored_data.append(item)
                
        except Exception as e:
            # Handle API errors or malformed JSON output from the Judge
            print(f"Judge failed on item {i}. Error: {e}")
            continue
            
    return scored_data

def final_data_cleaning_and_splitting(data_list):
    """Performs duplicate removal and train/test split."""
    print("\n--- Running Final Cleaning and Splitting ---")
    
    if not data_list:
        print("Error: No data provided to cleaning stage. Generation likely failed or produced no output.")
        return None

    df = pd.DataFrame(data_list).dropna()
    
    if df.empty:
        print("Error: DataFrame is empty after dropna(). Cannot proceed.")
        return None
        
    if 'instruction' not in df.columns or 'output' not in df.columns:
         print(f"Error: Missing required columns. Found: {df.columns.tolist()}")
         return None
    
    # Semantic Duplicate Removal (SOTA for text)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    df['text_combined'] = df['instruction'] + " " + df['output']
    embeddings = model.encode(df['text_combined'].tolist(), show_progress_bar=False)
    
    # Calculate similarity matrix (expensive for very large datasets)
    similarity_matrix = cosine_similarity(embeddings)
    
    # Identify and remove high-similarity duplicates (threshold 0.98)
    to_keep = []
    for i in range(len(df)):
        is_duplicate = False
        for j in to_keep:
            if similarity_matrix[i, j] > 0.98:
                is_duplicate = True
                break
        if not is_duplicate:
            to_keep.append(i)
    
    df_cleaned = df.iloc[to_keep].drop(columns=['text_combined']).reset_index(drop=True)
    
    print(f"Original unique count after Judge: {len(df)}. After semantic deduplication: {len(df_cleaned)}")
    
    # Convert to Hugging Face Dataset and perform train/test split
    hf_dataset = Dataset.from_pandas(df_cleaned)
    split_dataset = hf_dataset.train_test_split(test_size=0.1, seed=42)
    
    split_dataset['train'].to_json("train_data.jsonl", orient='records', lines=True)
    split_dataset['test'].to_json("test_data.jsonl", orient='records', lines=True)

    print(f"Train data saved to train_data.jsonl ({len(split_dataset['train'])} examples).")
    print(f"Test data saved to test_data.jsonl ({len(split_dataset['test'])} examples).")
    
    print("\n--- Stage 2 Complete ---")
    return split_dataset