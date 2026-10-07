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
MODEL_PATH = ROOT / "results" / "time_check_model.joblib"
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


def train(data_path: Path = TRAIN_DATA) -> Pipeline:
    df = pd.read_csv(data_path)
    model = build_pipeline().fit(df["question"], df["label"])
    MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    return model


def load() -> Pipeline:
    if MODEL_PATH.exists():
        try:
            return joblib.load(MODEL_PATH)
        except Exception:  # saved with another scikit-learn version: retrain
            pass
    return train()


def classify(question: str, model: Pipeline | None = None) -> str:
    model = model or load()
    return model.predict([question])[0]


if __name__ == "__main__":
    m = train()
    print(f"Trained on {TRAIN_DATA.name}, saved to {MODEL_PATH.relative_to(ROOT)}")
    for q in ["Who runs Samsung Electronics?", "What is photosynthesis?",
              "Is Naver hiring?", "What is the dorm fee?"]:
        print(f"{classify(q, m):<10} {q}")
