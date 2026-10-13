"""Cost of each method: AI calls and searches per question.

Counted from what each method has to do for every question:
  answer from memory = 1 AI call
  search             = 1 web + 2 Wikipedia searches, ~6 page reads, 2 AI calls
                       (search words + answer from sources)
  knowledge check    = 3 AI calls   (skipped by the router when the answer changes often)
  verbal confidence  = 1 AI call
A method that searches does not also need the memory answer.

    python -m src.cost
Output: results/cost_report.md
"""
from __future__ import annotations

import csv

from src import benchmarks
from src.llm import ROOT

REPORT = ROOT / "results" / "cost_report.md"
SEARCH_CALLS, MEMORY_CALLS, CHECK_CALLS, CONF_CALLS = 2, 1, 3, 1


def calls(method: str, r: dict) -> int:
    searched = r[f"{method}::searched"] in ("True", "true", "1")
    answer = SEARCH_CALLS if searched else MEMORY_CALLS
    if method in ("Never search", "Always search", "Time check only"):
        return answer
    if method == "Self-consistency only":
        return CHECK_CALLS + answer
    if method in ("Verbal confidence", "Ask the AI"):
        return CONF_CALLS + answer
    if method.startswith("Router, strict"):   # + the memory answer, also when it searches
        if r["group"] == "HIGH":
            return answer
        return CHECK_CALLS + MEMORY_CALLS + (SEARCH_CALLS if searched else 0)
    if method.startswith("Router, cheap"):   # memory answer (made anyway) + ONE sample
        if r["group"] == "HIGH":
            return answer
        return MEMORY_CALLS + 1 + (SEARCH_CALLS if searched else 0)
    if method.startswith("Router, AI"):
        return 1 + (0 if r.get("llm_group") == "HIGH" else CHECK_CALLS) + answer
    if method.startswith("Router, dated"):
        return 1 + (0 if r.get("dated_group") == "HIGH" else CHECK_CALLS) + answer
    if method.startswith("Router"):
        return (0 if r["group"] == "HIGH" else CHECK_CALLS) + answer
    return answer


def main():
    from src.experiment import METHODS
    L = ["# Cost per question\n",
         "AI calls and web searches each method needs per question, with its accuracy. "
         "Fewer calls and searches = faster and cheaper.\n"]
    from src.experiment import MODELS, answers_file
    for model, name in ((m, answers_file(m)) for m in MODELS):
        if not (ROOT / "results" / name).exists():
            continue
        rows = list(csv.DictReader((ROOT / "results" / name).open(encoding="utf-8")))
        if not rows:
            continue
        n = len(rows)
        L += [f"## {model} ({n} questions)\n",
              "| Method | Correct | AI calls / question | Searches / question |", "|---|---|---|---|"]
        for m in METHODS:
            if m.startswith("Oracle") or f"{m}::score" not in rows[0]:
                continue
            acc = sum(r[f"{m}::score"] == "correct" for r in rows) / n
            c = sum(calls(m, r) for r in rows) / n
            s = sum(r[f"{m}::searched"] in ("True", "true", "1") for r in rows) / n
            name_md = f"**{m}**" if "ours" in m else m
            L.append(f"| {name_md} | {acc:.0%} | {c:.1f} | {s:.2f} |")
        L.append("")
    L += ["The router skips the knowledge check for fast-changing questions, which are searched "
          "anyway. AI calls differ in size (a knowledge-check sample is 8 words; an answer from "
          "sources reads ~5,000 characters), so measured seconds are in `results/timing_report.md`, "
          "and the trade-off between a search and a wrong answer in `results/curves_report.md`."]
    benchmarks.suffixed(REPORT).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
