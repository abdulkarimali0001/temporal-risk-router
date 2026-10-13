"""Measured time per question: how many seconds each method really takes.

AI calls are not all the same size: a knowledge-check sample is a short 8-word answer,
while answering from sources means reading about 5,000 characters of pages. So this
script times every step on a sample of benchmark questions, WITHOUT any cache (all
caches point to a temporary folder), on this computer:

  memory          the AI answers alone
  sample x1       one knowledge-check sample (the cheap check)
  samples x3      three samples, asked in parallel (the full check)
  confidence      the AI's stated confidence
  time check      the classifier (no AI) and the AI-judged version
  search          web + Wikipedia search, page reading, and the answer from sources

Seconds per question for each method are then worked out from these times and the
decisions each method made in the main experiment (results/experiment_answers*.csv).

    python -m src.timing            (needs Ollama running; uses ~30 web searches)
Output: results/timing.csv, results/timing_report.md
"""
from __future__ import annotations

import csv
import os
import random
import statistics
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from src import benchmarks, experiment, knowledge_check, language, llm, pipeline, search, time_check
from src.llm import ROOT

N = int(os.environ.get("TRR_TIMING_N", "30"))
OUT = ROOT / "results" / "timing.csv"
REPORT = ROOT / "results" / "timing_report.md"
STEPS = ["memory", "sample_x1", "samples_x3", "confidence", "time_check", "ai_time_check", "search"]


def no_caches():
    """Point every cache at an empty temporary folder, so nothing is reused."""
    tmp = Path(tempfile.mkdtemp(prefix="trr-timing-"))
    search.CACHE_PATH = tmp / "search_cache.json"
    search.PAGE_CACHE_PATH = tmp / "page_cache.json"
    search.WEB_CACHE_PATH = tmp / "web_cache.json"
    knowledge_check.CACHE_PATH = tmp / "kc.json"
    language.CACHE = tmp / "translate.json"
    time_check.LLM_CACHE = tmp / "llm_time.json"


def timed(fn) -> float:
    t0 = time.perf_counter()
    fn()
    return round(time.perf_counter() - t0, 3)


def sample_questions() -> list[dict]:
    items = benchmarks.load()
    rng = random.Random(7)
    by_type = {}
    for it in items:
        by_type.setdefault(it["type"], []).append(it)
    per = max(1, N // len(by_type))
    return [it for t in sorted(by_type) for it in rng.sample(by_type[t], min(per, len(by_type[t])))]


def measure() -> list[dict]:
    no_caches()
    model = time_check.load()
    llm.warm_up()
    one = lambda q: llm.generate(knowledge_check.PROMPT.format(q=q), temperature=1.0, max_tokens=40)
    rows = []
    for i, it in enumerate(sample_questions(), 1):
        q = it["question"]
        print(f"[{i}] {q}", flush=True)
        try:
            r = {"id": it["id"], "type": it["type"], "model": llm.model_name(),
                 "memory": timed(lambda: pipeline.answer_from_memory(q)),
                 "sample_x1": timed(lambda: one(q)),
                 "samples_x3": timed(lambda: list(ThreadPoolExecutor(3).map(one, [q] * 3))),
                 "confidence": timed(lambda: experiment.confidence(q)),
                 "time_check": timed(lambda: time_check.classify(q, model)),
                 "ai_time_check": timed(lambda: time_check.classify_llm(q)),
                 "search": timed(lambda: pipeline.answer_with_search(q))}
        except Exception as e:
            print(f"   ERROR: {e}", flush=True)
            continue
        print("   " + "  ".join(f"{k} {r[k]:.1f}s" for k in STEPS), flush=True)
        rows.append(r)
    with OUT.open("a" if OUT.exists() else "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id", "type", "model"] + STEPS)
        if f.tell() == 0:
            w.writeheader()
        w.writerows(rows)
    return rows


def seconds(method: str, r: dict, t: dict) -> float:
    """Sequential seconds for one question under one method (t = mean time per step)."""
    searched = r[f"{method}::searched"] in ("True", "true", "1")
    answer = t["search"] if searched else t["memory"]
    high = r["group"] == "HIGH"
    if method in ("Never search", "Always search"):
        return answer
    if method == "Time check only":
        return t["time_check"] + answer
    if method == "Self-consistency only":
        return t["samples_x3"] + answer
    if method == "Verbal confidence":
        return t["confidence"] + answer
    if method == "Router, strict check (ours)":
        return t["time_check"] + (answer if high else t["memory"] + t["samples_x3"]
                                  + (t["search"] if searched else 0))
    if method == "Router, cheap check (ours)":   # memory answer is made anyway, + 1 sample
        return t["time_check"] + (answer if high else t["memory"] + t["sample_x1"]
                                  + (t["search"] if searched else 0))
    if method == "Router, AI time check (ours)":
        return t["ai_time_check"] + (0 if r.get("llm_group") == "HIGH" else t["samples_x3"]) + answer
    if method == "Router, dated AI time check (ours)":
        return t["ai_time_check"] + (0 if r.get("dated_group") == "HIGH" else t["samples_x3"]) + answer
    if method.startswith("Router"):
        return t["time_check"] + (0 if high else t["samples_x3"]) + answer
    return answer


def report():
    rows = list(csv.DictReader(OUT.open(encoding="utf-8")))
    L = ["# Measured time per question\n",
         "Every step timed without any cache on this computer, on a sample of benchmark "
         "questions. Seconds per method are worked out from these times and the decisions "
         "each method made in the main experiment. Steps run one after another (in the demo "
         "app the checks run at the same time as the answer, so users wait less).\n"]
    for model, name in ((m, experiment.answers_file(m)) for m in experiment.MODELS):
        mine = [r for r in rows if r["model"] == model]
        path = ROOT / "results" / name
        if not mine or not path.exists():
            continue
        t = {k: statistics.mean(float(r[k]) for r in mine) for k in STEPS}
        L += [f"## {model} ({len(mine)} questions timed)\n",
              "| Step | Mean seconds | Median |", "|---|---|---|"]
        for k in STEPS:
            L.append(f"| {k.replace('_', ' ')} | {t[k]:.2f} | "
                     f"{statistics.median(float(r[k]) for r in mine):.2f} |")
        exp = list(csv.DictReader(path.open(encoding="utf-8")))
        L += ["", "| Method | Correct | Seconds / question | vs. always search |", "|---|---|---|---|"]
        always = statistics.mean(seconds("Always search", r, t) for r in exp)
        for m in experiment.METHODS:
            if m.startswith("Oracle") or f"{m}::searched" not in exp[0]:
                continue
            acc = sum(r[f"{m}::score"] == "correct" for r in exp) / len(exp)
            s = statistics.mean(seconds(m, r, t) for r in exp)
            L.append(f"| {'**' + m + '**' if 'ours' in m else m} | {acc:.0%} | {s:.1f} | "
                     f"{(s / always - 1) * 100:+.0f}% |")
        L.append("")
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    import sys
    llm.load_env()
    if "--report" not in sys.argv:
        measure()
    report()
