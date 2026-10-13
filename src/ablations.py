"""Ablations: which parts of the router matter? (from saved answers, no AI needed)

  1. Number of samples in the knowledge check (1-5), with the old similarity rule and
     with the strict no-contradiction rule (which also includes the memory answer).
  2. Removing one part at a time: no time check, no memory answer in the check,
     similarity instead of strict comparison.
  3. The agreement threshold of the similarity rule (0.4 - 1.0).

    python -m src.ablations            (TRR_SET=heldout for the held-out set)
Output: results/ablation_report.md
"""
from __future__ import annotations

import csv

from src import benchmarks, knowledge_check as kc, router
from src.experiment import MODELS, answers_file
from src.llm import ROOT

REPORT = ROOT / "results" / "ablation_report.md"


def rows_for(model: str) -> list[dict]:
    path = ROOT / "results" / answers_file(model)
    if not path.exists():
        return []
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    for r in rows:
        r["_samples"] = kc.cached(r["question"], model)
    return [r for r in rows if r["_samples"] or r["group"] == "HIGH"]


def evaluate(rows: list[dict], knows_fn, use_time: bool = True) -> tuple[float, float]:
    ok = searched = 0
    for r in rows:
        group = r["group"] if use_time else "LOW"
        if group == "HIGH":
            s = True
        else:
            s = router.decide(group, knows_fn(r))[0] == "search"
        searched += s
        ok += (r["search_score"] if s else r["memory_score"]) == "correct"
    return ok / len(rows), searched / len(rows)


def similarity(n: int, threshold: float = kc.AGREEMENT_NEEDED, memory: bool = False):
    def f(r):
        a = ([r["memory"]] if memory else []) + r["_samples"][:n]
        if len(a) < 2:                       # one sample alone: only "I don't know" counts
            return not kc.IDK.search(a[0]) if a else False
        j = kc.judge(a)
        return j["said_dont_know"] == 0 and j["agreement"] >= threshold
    return f


def strict(n: int, memory: bool = True):
    def f(r):
        a = ([r["memory"]] if memory else []) + r["_samples"][:n]
        if len(a) < 2:
            return not kc.IDK.search(a[0]) if a else False
        return kc.judge_strict(a, r["question"])["knows"]
    return f


def main():
    L = ["# Ablations\n",
         f"Question set: **{benchmarks.current_set()}**. Accuracy / share of questions searched, "
         "from the saved answers (the same memory and search answers for every variant).\n"]
    for model in MODELS:
        rows = rows_for(model)
        if len(rows) < 100:
            continue
        most = max(len(r["_samples"]) for r in rows)
        always = sum(r["search_score"] == "correct" for r in rows) / len(rows)
        L += [f"## {model} ({len(rows)} questions; always search {always:.1%})\n",
              "### Number of samples in the knowledge check\n",
              "| Samples | Similarity rule | Strict rule (+ memory answer) |", "|---|---|---|"]
        for n in range(1, most + 1):
            if all(len(r["_samples"]) >= n for r in rows if r["group"] != "HIGH"):
                a1, s1 = evaluate(rows, similarity(n))
                a2, s2 = evaluate(rows, strict(n))
                L.append(f"| {n} | {a1:.1%} ({s1:.0%}) | {a2:.1%} ({s2:.0%}) |")
        L += ["", "### Removing one part at a time (3 samples)\n",
              "| Variant | Correct | Searched |", "|---|---|---|"]
        variants = [("Full router, strict check", strict(3), True),
                    ("- without the time check", strict(3), False),
                    ("- without the memory answer in the check", strict(3, memory=False), True),
                    ("- similarity instead of strict comparison (= original router)", similarity(3), True),
                    ("Original router without the time check (= self-consistency only)", similarity(3), False)]
        for name, fn, use_time in variants:
            a, s = evaluate(rows, fn, use_time)
            L.append(f"| {name} | {a:.1%} | {s:.0%} |")
        L += ["", "### Agreement threshold of the similarity rule (3 samples)\n",
              "| Threshold | Correct | Searched |", "|---|---|---|"]
        for t in [0.34, 0.5, 0.6, 0.67, 0.8, 1.0]:
            a, s = evaluate(rows, similarity(3, t))
            L.append(f"| {t:.2f} | {a:.1%} | {s:.0%} |")
        L.append("")
    benchmarks.suffixed(REPORT).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
