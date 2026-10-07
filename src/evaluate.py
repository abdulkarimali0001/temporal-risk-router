"""Evaluate Router v1 (rules) and Router v2 (ML).

Two tests:
  1. 5-fold cross-validation on data/questions.csv (v2 never sees the test fold)
  2. A held-out set, data/unseen_test.csv, that neither router was built on

Metrics:
  - accuracy        : share of questions put in the right band
  - HIGH recall     : share of truly HIGH-risk questions sent to search
                      (the most important number: a miss = an outdated answer)
  - searches        : share of all questions that trigger a web search (cost)

Run:   python -m src.evaluate
Output: printed tables + results/report.md + results/predictions_unseen.csv
"""
from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from src import router_rules
from src.router_ml import build_pipeline

ROOT = Path(__file__).resolve().parent.parent
LABELS = ["LOW", "AMBIGUOUS", "HIGH"]


def metrics(y_true, y_pred) -> dict:
    y_true, y_pred = list(y_true), list(y_pred)
    n = len(y_true)
    high = [p for t, p in zip(y_true, y_pred) if t == "HIGH"]
    return {
        "accuracy": sum(t == p for t, p in zip(y_true, y_pred)) / n,
        "high_recall": sum(p == "HIGH" for p in high) / len(high),
        "high_caught": f"{sum(p == 'HIGH' for p in high)}/{len(high)}",
        "searches": sum(p == "HIGH" for p in y_pred) / n,
    }


def confusion_md(y_true, y_pred) -> str:
    cm = confusion_matrix(y_true, y_pred, labels=LABELS)
    lines = ["| true \\ predicted | " + " | ".join(LABELS) + " |",
             "|---|" + "---|" * len(LABELS)]
    for label, row in zip(LABELS, cm):
        lines.append(f"| {label} | " + " | ".join(str(x) for x in row) + " |")
    return "\n".join(lines)


def row(name, m) -> str:
    return (f"| {name} | {m['accuracy']:.0%} | {m['high_caught']} ({m['high_recall']:.0%}) "
            f"| {m['searches']:.0%} |")


def main():
    train = pd.read_csv(ROOT / "data" / "questions.csv")
    unseen = pd.read_csv(ROOT / "data" / "unseen_test.csv")

    # --- Test 1: cross-validation on the main set ---
    v1_cv = train["question"].map(router_rules.route)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    v2_cv = cross_val_predict(build_pipeline(), train["question"], train["label"], cv=cv)

    # --- Test 2: held-out unseen questions ---
    v1_un = unseen["question"].map(router_rules.route)
    v2_model = build_pipeline().fit(train["question"], train["label"])
    v2_un = v2_model.predict(unseen["question"])

    baselines_un = {
        "Never search": ["LOW"] * len(unseen),
        "Always search": ["HIGH"] * len(unseen),
    }

    header = "| Router | Accuracy | HIGH caught (recall) | Searches |\n|---|---|---|---|"
    report = [
        "# Temporal-Risk Router — evaluation report", "",
        f"Main set: {len(train)} questions · Unseen set: {len(unseen)} questions", "",
        "## Test 1 — 5-fold cross-validation (main set)", "", header,
        row("v1 rules*", metrics(train["label"], v1_cv)),
        row("v2 ML", metrics(train["label"], v2_cv)), "",
        "*v1's keywords were written while looking at these questions, so this score is optimistic.", "",
        "## Test 2 — unseen questions", "", header,
    ]
    for name, preds in baselines_un.items():
        report.append(row(name, metrics(unseen["label"], preds)))
    report += [row("v1 rules", metrics(unseen["label"], v1_un)),
               row("v2 ML", metrics(unseen["label"], v2_un)), "",
               "### v1 confusion matrix (unseen)", "", confusion_md(unseen["label"], v1_un), "",
               "### v2 confusion matrix (unseen)", "", confusion_md(unseen["label"], v2_un), "",
               "## Misses on unseen questions", "",
               "| Question | True | v1 | v2 |", "|---|---|---|---|"]
    for q, t, a, b in zip(unseen["question"], unseen["label"], v1_un, v2_un):
        if a != t or b != t:
            report.append(f"| {q} | {t} | {a} | {b} |")

    text = "\n".join(report)
    print(text)
    out = ROOT / "results"
    out.mkdir(exist_ok=True)
    (out / "report.md").write_text(text + "\n", encoding="utf-8")
    pd.DataFrame({"question": unseen["question"], "true": unseen["label"],
                  "v1": v1_un, "v2": v2_un}).to_csv(out / "predictions_unseen.csv", index=False)
    print(f"\nSaved results/report.md and results/predictions_unseen.csv")


if __name__ == "__main__":
    main()
