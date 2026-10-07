"""Router v2: machine-learning Temporal-Risk Router.

A TF-IDF + logistic regression classifier trained on our labelled questions.
Unlike v1 it learns from examples, so it can pick up phrases such as
"Who runs ..." or "Is ... hiring" that have no explicit time keyword.

Train:   python -m src.router_ml
"""
from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "questions.csv"
MODEL_PATH = ROOT / "results" / "router_v2.joblib"


def build_pipeline() -> Pipeline:
    features = FeatureUnion([
        # word 1-2 grams catch phrases like "who runs", "is hiring"
        ("words", TfidfVectorizer(ngram_range=(1, 2), lowercase=True, sublinear_tf=True)),
        # character n-grams help with unseen word forms (hire / hiring)
        ("chars", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), sublinear_tf=True)),
    ])
    clf = LogisticRegression(max_iter=2000, C=5.0, class_weight="balanced")
    return Pipeline([("features", features), ("clf", clf)])


def train(data_path: Path = DATA) -> Pipeline:
    df = pd.read_csv(data_path)
    model = build_pipeline()
    model.fit(df["question"], df["label"])
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load() -> Pipeline:
    if not MODEL_PATH.exists():
        return train()
    return joblib.load(MODEL_PATH)


def route(question: str, model: Pipeline | None = None) -> str:
    model = model or load()
    return model.predict([question])[0]


if __name__ == "__main__":
    m = train()
    print(f"Trained on {DATA.name}, saved to {MODEL_PATH.relative_to(ROOT)}")
    for q in ["Who runs Samsung Electronics?", "What is photosynthesis?",
              "Is Naver hiring?", "What is the dorm fee?"]:
        print(f"{route(q, m):<10} {q}")
