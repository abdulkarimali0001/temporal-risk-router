"""Non-English questions: does the router also work in Korean and Swahili?

data/korean_test.csv  - 49 Korean questions with verified answers: general knowledge,
                        local/rare facts (Gangwon, Sokcho, Seoraksan) and facts that change
                        (officeholders after the June 2026 local elections, CEOs, champions)
data/swahili_test.csv - 32 Swahili questions: general knowledge, Swahili literature and
                        East African places, and facts that change (East African leaders,
                        league champions)

Compared:
  Memory only                   the AI answers alone
  Search: English Wikipedia     the English translation searched on English Wikipedia
  Search: own language + English  also Korean / Swahili Wikipedia (and live web if a Tavily key is set)
  Router (both checks)          decides per question, using the own-language + English search

    python -m src.evaluate_korean                          (Korean)
    python -m src.evaluate_korean data/swahili_test.csv    (Swahili)
Output: results/korean_evaluation*.md / results/swahili_evaluation*.md, and .csv
"""
from __future__ import annotations

import csv
from collections import Counter
from datetime import date

from src import llm, pipeline, router, search, time_check
from src.evaluate_answers import _cached, _load_cache, score
from src.llm import ROOT

import sys

DATA = ROOT / (sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".csv") else "data/korean_test.csv")
RESULTS = ROOT / "results"
SET = DATA.stem.replace("_test", "")                  # "korean" or "swahili"
CSV_OUT = RESULTS / f"{SET}_evaluation.csv"
REPORT = RESULTS / f"{SET}_evaluation.md"


def out(path):
    """Main model -> korean_evaluation.md; other models get a suffix."""
    from src.experiment import out_path
    return out_path(path)
METHODS = {"memory": "Memory only", "search_en": "Search: English Wikipedia only",
           "search_ko": "Search: own language + English", "router": "Router (both checks)"}
TYPES = {"stable_common": "General knowledge", "stable_rare": "Local / rare facts",
         "changing": "Changes over time"}


def record(q: str, korean: bool) -> dict:
    r = pipeline.answer_with_search(q, korean_wiki=korean, web=None if korean else False)
    return {"answer": r["answer"], "query": r["query"], "sources": [p["url"] for p in r["sources"]]}


def main():
    RESULTS.mkdir(exist_ok=True)
    from src import evaluate_answers
    cache, tag = _load_cache(), f"{llm.backend()}::{llm.model_name()}"
    model = time_check.load()
    rows = []
    questions = list(csv.DictReader(DATA.open(encoding="utf-8")))
    for i, q in enumerate(questions, 1):
        text = q["question"]
        print(f"[{i}/{len(questions)}] {text}", flush=True)
        try:
            mem = _cached(cache, f"{tag}::ko-memory::{text}", lambda: pipeline.answer_from_memory(text))
            en = _cached(cache, f"{tag}::ko-search-en::{text}", lambda: record(text, False))
            ko = _cached(cache, f"{tag}::ko-{search.version()}::{text}", lambda: record(text, True))
            route = router.route(text, model=model)
        except Exception as e:
            print(f"   ERROR: {e}", flush=True)
            continue
        routed = ko["answer"] if route["action"] == "search" else \
            mem + (" " + pipeline.WARNING if route["action"] == "warn" else "")
        aliases = q["correct_answers"].split("|")
        row = {**q, "group": route["group"], "action": route["action"],
               "memory": mem, "search_en": en["answer"], "search_ko": ko["answer"], "router": routed,
               "sources": " ".join(ko["sources"])}
        for m in METHODS:
            row[f"{m}_score"] = score(row[m], aliases)
        rows.append(row)
        print("   " + "   ".join(f"{m}: {row[m + '_score']}" for m in METHODS), flush=True)
        with out(CSV_OUT).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), restval="")
            w.writeheader()
            w.writerows(rows)

    n = len(rows) or 1
    L = [f"# {SET.capitalize()} questions\n",
         f"Model `{llm.model_name()}` · {date.today()} · {len(rows)} {SET.capitalize()} questions "
         f"(answers verified {questions[0]['checked_on']}). Search: "
         f"{'Wikipedia + live web' if search.web_enabled() else 'Wikipedia'}.\n",
         "| Method | Correct | Wrong | No guess | Searched |", "|---|---|---|---|---|"]
    for m, name in METHODS.items():
        c = Counter(r[f"{m}_score"] for r in rows)
        searched = {"memory": 0, "search_en": len(rows), "search_ko": len(rows),
                    "router": sum(r["action"] == "search" for r in rows)}[m]
        L.append(f"| {name} | {c['correct']}/{len(rows)} ({c['correct'] / n:.0%}) | {c['wrong']} "
                 f"| {c['no guess']} | {searched} |")
    L += ["", "| Question type | n | " + " | ".join(METHODS.values()) + " |", "|---|---|" + "---|" * len(METHODS)]
    for t, name in TYPES.items():
        sub = [r for r in rows if r["type"] == t]
        if sub:
            L.append(f"| {name} | {len(sub)} | " + " | ".join(
                f"{sum(r[f'{m}_score'] == 'correct' for r in sub)}/{len(sub)}" for m in METHODS) + " |")
    L += ["", "## Wrong answers\n"]
    for r in rows:
        for m, name in METHODS.items():
            if r[f"{m}_score"] == "wrong":
                L.append(f"- **{name}**, {r['id']} {r['question']} (expected {r['correct_answers'].split('|')[0]}): "
                         f"{r[m][:160]}")
    out(REPORT).write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
