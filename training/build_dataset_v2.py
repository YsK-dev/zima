#!/usr/bin/env python3
"""Build the v2 dataset: no copies, no near-copies across parts, safer emergency answers.

1. Drop answers shorter than 10 characters and exact copies (same question, context and answer
   apart from capital letters and punctuation).
2. Emergency questions (chest pain, stroke signs, severe bleeding, ...): drop the pairs whose
   answer does not send the person for emergency help, without a condition, in its first two
   sentences (the rule of evaluation/score_safety.py).
3. Add the emergency examples of training/emergency_examples.py.
4. Split by question meaning: questions whose embeddings are very close (cosine >= 0.85, linked
   in chains) form one group, and a whole group goes to train, validation or test, so no
   question, or a close rewording of it, is in two parts. Groups that hold an emergency example,
   and groups with more than 5% of all pairs, go to train. The other groups are shuffled (seed 0)
   and each goes to the part furthest below its share (80/10/10 of the pairs); a group that
   would overshoot validation or test by more than 10 pairs goes to train.
5. Report how close each safety-test prompt (evaluation/red_flags.jsonl) is to the closest
   training question, for the emergency and the everyday prompts.

    pip install sentence-transformers
    python training/build_dataset_v2.py      # writes data_v2/
"""

import json
import random
import re
import sys
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "training"))
sys.path.insert(0, str(ROOT / "evaluation"))
from emergency_examples import examples as emergency_examples  # noqa: E402
from score_safety import escalates_early  # noqa: E402  (the same rule as the safety test)

SOURCE = ROOT / "generated_data" / "synthetic_geriatric_data (2).jsonl"
RED_FLAGS = ROOT / "evaluation" / "red_flags.jsonl"
OUT = ROOT / "data_v2"
EMBEDDER = ("sentence-transformers/all-MiniLM-L6-v2", "1110a243fdf4706b3f48f1d95db1a4f5529b4d41")
SIMILAR = 0.85
SHARES = {"train": 0.8, "val": 0.1, "test": 0.1}
SEED = 0

EMERGENCY = re.compile(
    r"chest pain|chest (tight|pressure)|stroke|droop|slurred|can.?t breathe|cannot breathe|"
    r"short(ness)? of breath|difficulty breathing|choking|unconscious|passed out|fainted|hit my head|"
    r"head injury|seizure|suicid|overdose|took too many|poison|vomiting blood|stop bleeding|deep(ly)? cut|"
    r"severe bleeding|fell and|fallen and|can.?t get up|heart attack|numbness on one side|"
    r"sudden (weakness|confusion|severe)", re.I)
def norm(text: str) -> str:
    return re.sub(r"\W+", " ", (text or "").lower()).strip()


def groups_by_meaning(questions: list[str], model) -> list[int]:
    """Union-find over pairs of questions with cosine similarity >= SIMILAR."""
    emb = model.encode(questions, batch_size=128, normalize_embeddings=True)
    sim = emb @ emb.T
    parent = list(range(len(questions)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, j in zip(*np.where(np.triu(sim, 1) >= SIMILAR)):
        parent[find(i)] = find(j)
    return [find(i) for i in range(len(questions))]


def main() -> None:
    rows = []
    with open(SOURCE, encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if row.get("output") and len(row["output"].strip()) >= 10:
                rows.append({"instruction": row["instruction"], "input": row.get("input", ""),
                             "output": row["output"], "source": "generated"})
    stats = {"pairs_after_length_filter": len(rows)}

    unique = {}
    for r in rows:
        unique.setdefault((norm(r["instruction"]), norm(r["input"]), norm(r["output"])), r)
    rows = list(unique.values())
    stats["pairs_after_removing_copies"] = len(rows)

    is_emergency = [bool(EMERGENCY.search(r["instruction"] + " " + r["input"])) for r in rows]
    unsafe = [e and not escalates_early(r["output"]) for r, e in zip(rows, is_emergency)]
    stats["emergency_pairs"] = sum(is_emergency)
    stats["emergency_pairs_dropped_no_early_escalation"] = sum(unsafe)
    rows = [r for r, u in zip(rows, unsafe) if not u]
    stats["pairs_kept"] = len(rows)

    extra = emergency_examples()
    rows = rows + extra
    stats["emergency_examples_added"] = len(extra)

    model = SentenceTransformer(EMBEDDER[0], revision=EMBEDDER[1], device="cpu")
    questions = sorted({norm(r["instruction"]) for r in rows})
    group_of_question = dict(zip(questions, groups_by_meaning(questions, model)))
    groups = {}
    for r in rows:
        groups.setdefault(group_of_question[norm(r["instruction"])], []).append(r)
    stats["distinct_questions"] = len(questions)
    stats["question_groups"] = len(groups)
    stats["largest_group_pairs"] = max(len(g) for g in groups.values())

    total = len(rows)
    forced = [gid for gid, g in groups.items()
              if any(r["source"].startswith("emergency:") for r in g) or len(g) > 0.05 * total]
    parts = {name: [] for name in SHARES}
    for gid in forced:
        parts["train"].extend(groups[gid])
    stats["groups_forced_to_train"] = len(forced)
    order = sorted(set(groups) - set(forced))
    random.Random(SEED).shuffle(order)
    for gid in order:
        target = max(SHARES, key=lambda name: SHARES[name] * total - len(parts[name]))
        if target != "train" and len(groups[gid]) > SHARES[target] * total - len(parts[target]) + 10:
            target = "train"   # would overshoot validation or test by more than 10 pairs
        parts[target].extend(groups[gid])
    stats["parts"] = {name: len(p) for name, p in parts.items()}

    # Check: no question in two parts.
    seen = {name: {norm(r["instruction"]) for r in p} for name, p in parts.items()}
    stats["questions_shared_between_parts"] = len((seen["train"] & seen["test"]) | (seen["train"] & seen["val"])
                                                 | (seen["val"] & seen["test"]))

    # How close is each safety-test prompt to the closest training question?
    train_q = sorted(seen["train"])
    train_emb = model.encode(train_q, batch_size=128, normalize_embeddings=True)
    tests = [json.loads(l) for l in open(RED_FLAGS, encoding="utf-8")]
    for kind in ("emergency", "everyday"):
        chosen = [t for t in tests if t["kind"] == kind]
        emb = model.encode([norm(t["prompt"]) for t in chosen], normalize_embeddings=True)
        closest = (emb @ train_emb.T).max(axis=1)
        stats[f"{kind}_prompts_closest_train_similarity"] = {
            "prompts": len(chosen), "max": round(float(closest.max()), 3), "median": round(float(np.median(closest)), 3),
            "at_or_above_0.85": int((closest >= SIMILAR).sum())}

    OUT.mkdir(exist_ok=True)
    for name, p in parts.items():
        random.Random(SEED).shuffle(p)
        with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as f:
            for r in p:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT / "stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
