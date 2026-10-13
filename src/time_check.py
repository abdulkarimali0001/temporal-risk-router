"""Check 1: does the answer to this question change over time?

A TF-IDF + logistic regression classifier (scikit-learn) trained on labelled
questions. It puts each question in one of three groups:

    LOW        the answer never changes          ("What is photosynthesis?")
    AMBIGUOUS  the answer changes sometimes      ("What is the tuition fee?")
    HIGH       the answer changes often          ("Who is the CEO of Naver?")

Because it learns from examples rather than a keyword list, it also catches
phrasings with no time word, such as "Who runs Samsung?".

Train and try it:
    python -m src.time_check
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parent.parent
TRAIN_DATA = ROOT / "data" / "time_check_train.csv"
# Extra outside training data, created by src/benchmarks.py: FreshQA questions labelled by how
# fast their answer changes, plus stable PopQA questions - none of them in the benchmark test set
EXTRA_DATA = ROOT / "data" / "time_check_extra.csv"
MODEL_PATH = ROOT / "results" / "time_check_model.joblib"


def _paths() -> tuple[Path, Path]:
    """(extra training data, saved model) for the question set being tested.
    TRR_SET=heldout: the held-out test set gets its own classifier, trained WITHOUT its
    questions (it may use the development questions instead) - so no test question is
    ever seen in training."""
    import os
    if os.getenv("TRR_SET") == "heldout":
        return (ROOT / "data" / "time_check_extra_heldout.csv",
                ROOT / "results" / "time_check_model_heldout.joblib")
    return EXTRA_DATA, MODEL_PATH
LABELS = ["LOW", "AMBIGUOUS", "HIGH"]


def build_pipeline() -> Pipeline:
    features = FeatureUnion([
        # word 1-2 grams catch phrases like "who runs", "is hiring"
        ("words", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True)),
        # character n-grams help with unseen word forms (hire / hiring)
        ("chars", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
    ])
    clf = LogisticRegression(max_iter=2000, C=5.0, class_weight="balanced")
    return Pipeline([("features", features), ("clf", clf)])


def training_files() -> list[Path]:
    return [p for p in (TRAIN_DATA, _paths()[0]) if p.exists()]


OWN_WEIGHT = 3   # our own hand-labelled questions count 3x the outside data


def train() -> Pipeline:
    frames = [pd.read_csv(p) for p in training_files()]
    df = pd.concat(frames, ignore_index=True)
    weights = [OWN_WEIGHT] * len(frames[0]) + [1] * (len(df) - len(frames[0]))
    model = build_pipeline().fit(df["question"], df["label"], clf__sample_weight=weights)
    path = _paths()[1]
    path.parent.mkdir(exist_ok=True)
    joblib.dump(model, path)
    return model


def load() -> Pipeline:
    newest_data = max(p.stat().st_mtime for p in training_files())
    path = _paths()[1]
    if path.exists() and path.stat().st_mtime >= newest_data:
        try:
            return joblib.load(path)
        except Exception:  # saved with another scikit-learn version: retrain
            pass
    return train()


def classify(question: str, model: Pipeline | None = None) -> str:
    model = model or load()
    return model.predict([question])[0]


if __name__ == "__main__":
    m = train()
    print(f"Trained on {', '.join(p.name for p in training_files())}, saved to {_paths()[1].relative_to(ROOT)}")
    for q in ["Who runs Samsung Electronics?", "What is photosynthesis?",
              "Is Naver hiring?", "What is the dorm fee?"]:
        print(f"{classify(q, m):<10} {q}")


# ---------------------------------------------------------------------------
# Check 1 by the AI itself (compared with the classifier above in src/experiment.py)
# The classifier only sees words; the AI knows what kind of fact is being asked
# ("Who runs Samsung?" = a role that changes hands). One short AI call, cached.
# ---------------------------------------------------------------------------
LLM_PROMPT = ("How often does the correct answer to this question change?\n"
              "never = a fixed fact (history, science, geography, a book's author)\n"
              "sometimes = changes every few years (a CEO, a leader, a record, a population)\n"
              "often = changes within months or weeks (prices, rankings, recent events, ages, 'latest')\n"
              "Reply with one word: never, sometimes or often.\n\nQuestion: {q}")
LLM_GROUPS = {"never": "LOW", "sometimes": "AMBIGUOUS", "often": "HIGH"}
LLM_CACHE = ROOT / "results" / "llm_time_cache.json"


def classify_llm(question: str) -> str:
    """Check 1 asked to the AI: LOW / AMBIGUOUS / HIGH."""
    import json
    from src import llm
    key = f"{llm.backend()}::{llm.model_name()}::{question}"
    try:
        cache = json.loads(LLM_CACHE.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
    if key not in cache:
        reply = llm.generate(LLM_PROMPT.format(q=question), max_tokens=5).lower()
        cache[key] = next((g for w, g in LLM_GROUPS.items() if w in reply), "AMBIGUOUS")
        LLM_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache[key]


# Date-aware version: the AI is told how old its knowledge is and today's date, and asked
# whether the answer has probably changed SINCE THEN (not just whether it can change).
DATED_PROMPT = ("Your knowledge comes from training data that ends around {cutoff}. Today is {today}.\n"
                "Could the correct answer to this question be different today from the answer "
                "in {cutoff}?\n"
                "no = it cannot have changed (a fixed fact)\n"
                "maybe = it may have changed (it changes every few years)\n"
                "yes = it has probably changed (it changes often, or it asks about recent events)\n"
                "Reply with one word: no, maybe or yes.\n\nQuestion: {q}")
DATED_GROUPS = {"no": "LOW", "maybe": "AMBIGUOUS", "yes": "HIGH"}


def classify_llm_dated(question: str, cutoff: str) -> str:
    """Check 1 asked to the AI, knowing its training cutoff and today's date."""
    import json
    import re
    from datetime import date
    from src import llm
    key = f"dated::{llm.backend()}::{llm.model_name()}::{cutoff}::{question}"
    try:
        cache = json.loads(LLM_CACHE.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
    if key not in cache:
        reply = llm.generate(DATED_PROMPT.format(q=question, cutoff=cutoff,
                                                 today=date.today().isoformat()), max_tokens=5).lower()
        word = re.search(r"\b(no|maybe|yes)\b", reply)
        cache[key] = DATED_GROUPS[word.group(1)] if word else "AMBIGUOUS"
        try:                                     # re-read: keep entries other runs added
            cache = {**json.loads(LLM_CACHE.read_text(encoding="utf-8")), key: cache[key]}
        except Exception:
            pass
        LLM_CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache[key]
