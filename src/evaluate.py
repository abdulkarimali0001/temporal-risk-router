"""Evaluation.

Part 1 - Check 1 (does the answer change?) on questions it was not trained on
         (data/time_check_test.csv). Compared with a simple keyword baseline.
Part 2 - The router (both checks) on data/router_test.csv, 45 questions:
           stable_common  never changes, AI should know it   -> should NOT search
           stable_rare    never changes, AI may not know it   -> should search (incomplete)
           changing       answer changes over time            -> should search (outdated)
         Each check is also scored on its own, to show what each contributes.

    python -m src.evaluate

Writes results/evaluation_report.md and results/router_decisions.csv.
Part 2 needs the language model (AI_BACKEND in .env) unless its answers are cached.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import confusion_matrix

from src import keyword_baseline, llm, router, time_check

ROOT = Path(__file__).resolve().parent.parent
LABELS = ["LOW", "AMBIGUOUS", "HIGH"]
TYPE_NAMES = {"stable_common": "Stable, well known", "stable_rare": "Stable, rare (incomplete)",
              "changing": "Changes over time (outdated)"}


def check1_metrics(truth, pred) -> dict:
    truth, pred = list(truth), list(pred)
    high = [p for t, p in zip(truth, pred) if t == "HIGH"]
    return {"right": sum(t == p for t, p in zip(truth, pred)), "n": len(truth),
            "high_caught": sum(p == "HIGH" for p in high), "high_n": len(high),
            "searches": sum(p == "HIGH" for p in pred)}


def confusion_md(truth, pred) -> list[str]:
    cm = confusion_matrix(truth, pred, labels=LABELS)
    rows = ["| true \\ predicted | " + " | ".join(LABELS) + " |", "|---|" + "---|" * 3]
    rows += [f"| {lab} | " + " | ".join(map(str, r)) + " |" for lab, r in zip(LABELS, cm)]
    return rows


def part1(model) -> list[str]:
    test = pd.read_csv(ROOT / "data" / "time_check_test.csv")
    preds = {"Keyword baseline": [keyword_baseline.route(q) for q in test["question"]],
             "Time check (ML)": list(model.predict(test["question"]))}
    out = ["## Part 1 - Check 1: does the answer change?", "",
           f"{len(test)} questions not used for training.", "",
           "| Method | Right group | HIGH caught | Searches |", "|---|---|---|---|"]
    for name, p in preds.items():
        m = check1_metrics(test["label"], p)
        out.append(f"| {name} | {m['right']}/{m['n']} ({m['right'] / m['n']:.0%}) "
                   f"| {m['high_caught']}/{m['high_n']} | {m['searches']} |")
    out += ["", "Confusion matrix (time check):", ""] + confusion_md(test["label"], preds["Time check (ML)"])
    print("\n".join(out) + "\n")
    return out


def part2(model) -> list[str]:
    test = pd.read_csv(ROOT / "data" / "router_test.csv")
    rows = []
    for i, q in enumerate(test["question"], 1):
        print(f"\r  checking question {i}/{len(test)} ...", end="", flush=True)
        r = router.route(q, model=model)
        rows.append({"group": r["group"], "knows": r["knows"], "agreement": r["agreement"],
                     "answers": " | ".join(r["answers"]),
                     "search_time_check_only": r["group"] == "HIGH",
                     "search_knowledge_check_only": r["knows"] is False,
                     "search_router": r["action"] == "search"})
    print()
    res = pd.concat([test, pd.DataFrame(rows)], axis=1)
    res.to_csv(ROOT / "results" / "router_decisions.csv", index=False)

    cols = {"Time check only": "search_time_check_only",
            "Knowledge check only": "search_knowledge_check_only",
            "Router (both checks)": "search_router"}
    need = res["should_search"] == "yes"
    out = ["## Part 2 - Router: when should the AI search?", "",
           f"{len(res)} questions, {len(res) // 3} of each type. "
           f"AI backend: {llm.backend()}, model: {llm.model_name()}.", "",
           "Questions sent to search, by type:", "",
           "| Question type | Should search? | " + " | ".join(cols) + " |",
           "|---|---|" + "---|" * len(cols)]
    for t, name in TYPE_NAMES.items():
        part = res[res["type"] == t]
        should = "no" if t == "stable_common" else "yes"
        out.append(f"| {name} | {should} | " +
                   " | ".join(f"{int(part[c].sum())}/{len(part)}" for c in cols.values()) + " |")
    out.append("| **Right decisions** | | " + " | ".join(
        f"**{int((res[c] == need).sum())}/{len(res)} ({(res[c] == need).mean():.0%})**"
        for c in cols.values()) + " |")
    out.append("| Total searches | | " + " | ".join(str(int(res[c].sum())) for c in cols.values()) + " |")
    print("\n".join(out))
    return out


def main():
    model = time_check.load()
    report = ["# Evaluation report", ""] + part1(model) + [""] + part2(model)
    (ROOT / "results").mkdir(exist_ok=True)
    (ROOT / "results" / "evaluation_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\nSaved: results/evaluation_report.md and results/router_decisions.csv")


if __name__ == "__main__":
    main()
