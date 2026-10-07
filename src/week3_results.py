"""Week 3: does the Two-Signal Router catch BOTH problems?

Test set: data/two_signal_test.csv  (45 questions, 3 types)
  stable_common - never changes, AI should know it      -> should NOT search
  stable_rare   - never changes, but AI may never have learned it
                  (INCOMPLETE knowledge)                 -> should search
  changing      - answer changes over time (OUTDATED)    -> should search

We compare:
  Version 2      - time signal only (searches only when HIGH)
  Version 3      - Two-Signal Router (time signal + confidence signal)

Run (needs the Claude API key in .env, or CONFIDENCE_BACKEND=ollama):
    python -m src.week3_results
Results are also saved to results/week3_results.csv
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src import router_ml, two_signal

ROOT = Path(__file__).resolve().parent.parent
LABEL = {"stable_common": "Stable, well known", "stable_rare": "Stable, rare (incomplete)",
         "changing": "Changes (outdated)"}


def main():
    test = pd.read_csv(ROOT / "data" / "two_signal_test.csv")
    model = router_ml.train()

    rows = []
    for i, q in enumerate(test["question"], 1):
        print(f"\r Checking question {i}/{len(test)} ...", end="", flush=True)
        r = two_signal.route(q, model=model)
        rows.append({"question": q,
                     "v2_search": r["band"] == "HIGH",
                     "v3_search": r["action"] == "search",
                     "band": r["band"], "confident": r["confident"],
                     "agreement": r["agreement"], "answers": " | ".join(r["answers"])})
    print()
    res = pd.concat([test, pd.DataFrame(rows).drop(columns="question")], axis=1)
    (ROOT / "results").mkdir(exist_ok=True)
    res.to_csv(ROOT / "results" / "week3_results.csv", index=False)

    print("=" * 74)
    print(" WEEK 3 RESULTS - Two-Signal Router (Group 4)")
    print("=" * 74)
    print(f" {'Question type':<28}{'Should search?':<16}{'Version 2':<17}{'Version 3'}")
    print(" " + "-" * 72)
    for t in ["stable_common", "stable_rare", "changing"]:
        part = res[res["type"] == t]
        n = len(part)
        should = "no" if t == "stable_common" else "yes"
        v2, v3 = int(part["v2_search"].sum()), int(part["v3_search"].sum())
        print(f" {LABEL[t]:<28}{should:<16}{f'{v2}/{n} searched':<17}{v3}/{n} searched")
    print(" " + "-" * 72)
    print(f" {'Total searches':<44}{int(res['v2_search'].sum()):<17}{int(res['v3_search'].sum())}")

    need = res["should_search"] == "yes"
    for name, col in [("Version 2", "v2_search"), ("Version 3", "v3_search")]:
        right = int((res[col] == need).sum())
        print(f" {name}: right decision for {right}/{len(res)} questions ({right / len(res):.0%})")

    print("\n Rare facts the AI was UNSURE about (caught by Signal 2):")
    caught = res[(res["type"] == "stable_rare") & (res["v3_search"]) & (~res["v2_search"])]
    for _, r in caught.head(5).iterrows():
        print(f"   - {r['question']}\n       tries: {r['answers']}")
    print("=" * 74)
    print(" Saved: results/week3_results.csv")


if __name__ == "__main__":
    main()
