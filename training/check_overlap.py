#!/usr/bin/env python3
"""Count copies in the dataset and how much of the held-out set also appears in training.

Rebuilds the split of prepare_data.py (same filter, seed 42, 90/10) without writing files.
Two pairs count as the same when they match apart from capital letters and punctuation.

    python training/check_overlap.py
"""

import json
import random
import re
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "generated_data" / "synthetic_geriatric_data (2).jsonl"


def norm(text: str) -> str:
    return re.sub(r"\W+", " ", (text or "").lower()).strip()


def key(row: dict) -> tuple:
    return norm(row["instruction"]), norm(row.get("input", "")), norm(row["output"])


def main() -> None:
    rows = []
    with open(DATA, encoding="utf-8") as f:
        for line in f:
            try:
                row = json.loads(line.strip())
            except json.JSONDecodeError:
                continue
            if row.get("output") and len(row["output"].strip()) >= 10:  # same filter as prepare_data.py
                rows.append(row)

    print(f"pairs kept: {len(rows)}")
    print(f"different pairs: {len({key(r) for r in rows})}")
    print(f"different questions: {len({norm(r['instruction']) for r in rows})}")

    random.seed(42)  # same split as prepare_data.py
    random.shuffle(rows)
    cut = int(len(rows) * 0.9)
    train, held_out = rows[:cut], rows[cut:]
    train_pairs = {key(r) for r in train}
    train_questions = {norm(r["instruction"]) for r in train}
    same_pair = sum(key(r) in train_pairs for r in held_out)
    same_question = sum(norm(r["instruction"]) in train_questions for r in held_out)
    print(f"train: {len(train)}, held out: {len(held_out)}")
    print(f"held-out pairs also in training: {same_pair} ({same_pair / len(held_out):.1%})")
    print(f"held-out questions also in training: {same_question} ({same_question / len(held_out):.1%})")
    first = held_out[:100]  # evaluate_model.py computes perplexity on these
    print(f"of the first 100 held-out pairs (used for perplexity), also in training: {sum(key(r) in train_pairs for r in first)}")


if __name__ == "__main__":
    main()
