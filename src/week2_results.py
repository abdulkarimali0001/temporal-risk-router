"""Week 2 progress report — the numbers on our slides, computed live.

Run from the project folder:
    python -m src.week2_results

What it does:
  1. Trains Version 2 (machine learning) on the 150 practice questions
  2. Tests Version 1 and Version 2 on the 30 brand-new questions
  3. Prints the same table and lessons as our Week 2 slides
"""
from pathlib import Path

import pandas as pd

from src import router_rules
from src.router_ml import build_pipeline

ROOT = Path(__file__).resolve().parent.parent
NAMES = {"LOW": "LOW", "AMBIGUOUS": "MAYBE", "HIGH": "HIGH"}  # slide wording


def score(true_labels, predicted):
    """Return (right group, HIGH caught, number of HIGH, searches)."""
    right = sum(t == p for t, p in zip(true_labels, predicted))
    high_total = sum(t == "HIGH" for t in true_labels)
    high_caught = sum(t == "HIGH" and p == "HIGH" for t, p in zip(true_labels, predicted))
    searches = sum(p == "HIGH" for p in predicted)
    return right, high_caught, high_total, searches


def main():
    practice = pd.read_csv(ROOT / "data" / "questions.csv")
    test = pd.read_csv(ROOT / "data" / "unseen_test.csv")
    n = len(test)

    # --- Step 1: Version 2 learns from the 150 practice questions ---
    model = build_pipeline().fit(practice["question"], practice["label"])

    # --- Step 2: both versions sort the 30 brand-new questions ---
    v1 = [router_rules.route(q) for q in test["question"]]
    v2 = list(model.predict(test["question"]))
    truth = list(test["label"])

    print("=" * 64)
    print(" WEEK 2 RESULTS - Temporal-Risk Router (Group 4)")
    print("=" * 64)
    print(f" Practice questions (Version 2 learns from these): {len(practice)}")
    print(f" Brand-new test questions: {n}  (HIGH: {truth.count('HIGH')})\n")

    # --- Step 3: the table from the "Test result" slide ---
    print(f" {'':<15}{'Right group':<15}{'HIGH caught':<15}{'Searches'}")
    print(" " + "-" * 53)
    for name, preds in [("Version 1", v1), ("Version 2", v2)]:
        right, caught, total, searches = score(truth, preds)
        print(f" {name:<15}{f'{right} of {n}':<15}{f'{caught} of {total}':<15}{searches}")
    high_total = truth.count("HIGH")
    always = f"{high_total} of {high_total}"
    print(f" {'Always search':<15}{'-':<15}{always:<15}{n}")

    r1, r2 = score(truth, v1)[0], score(truth, v2)[0]
    print(f"\n -> Version 1: {r1 / n:.0%} correct   Version 2: {r2 / n:.0%} correct")

    # --- The example from our slides ---
    q = "Who runs Samsung Electronics?"
    print(f'\n Example: "{q}"')
    print(f"   Version 1 -> {NAMES[router_rules.route(q)]}")
    print(f"   Version 2 -> {NAMES[model.predict([q])[0]]}")

    # --- "What we learned" slide: where did the missed HIGH questions go? ---
    print("\n Missed HIGH questions (answer changes often):")
    for name, preds in [("Version 1", v1), ("Version 2", v2)]:
        misses = [(qq, p) for qq, t, p in zip(test["question"], truth, preds)
                  if t == "HIGH" and p != "HIGH"]
        print(f"\n   {name}: {len(misses)} missed")
        for qq, p in misses:
            note = "warning still shown" if p == "AMBIGUOUS" else "NO warning -> old answer"
            print(f"     - {qq}  -> {NAMES[p]} ({note})")
    print("=" * 64)


if __name__ == "__main__":
    main()
