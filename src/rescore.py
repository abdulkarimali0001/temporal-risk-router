"""Re-score saved experiment answers without running the AI again.

Use after the scoring rules or the accepted answers change (data/gold_updates.csv,
data/excluded_questions.csv). Reads results/experiment_answers*.csv, scores every
memory and search answer again, recomputes every method, and rewrites the reports.

    python -m src.rescore
"""
from __future__ import annotations

import csv
import os

from src import benchmarks
from src.evaluate_answers import score
from src.llm import ROOT

RUNS = {"llama3.1:8b": "experiment_answers.csv", "qwen2.5:7b": "experiment_answers_qwen2.5-7b.csv"}


def rescore(model: str, filename: str) -> list[dict]:
    from src import experiment
    path = ROOT / "results" / filename
    if not path.exists():
        return []
    os.environ["OLLAMA_MODEL"] = model
    gold = {i["id"]: i for i in benchmarks.load()}            # with updates and exclusions
    with path.open(encoding="utf-8") as f:
        header = next(csv.reader(f))
    # the report names the search the saved answers came from, not this computer's setting
    experiment.SEARCH_VERSION = "search_v3" if "search_v3::score" in header else "search_v2"
    # leave out methods added after this run (they need a new run on the Mac)
    all_methods = list(experiment.METHODS)
    experiment.METHODS[:] = [m for m in all_methods
                             if m.startswith("Oracle") or f"{m}::searched" in header]
    experiment.OURS = tuple(m for m in experiment.OURS if m in experiment.METHODS)
    rows = []
    for r in csv.DictReader(path.open(encoding="utf-8")):
        if r["id"] not in gold:
            continue                                          # excluded question
        r["correct_answers"] = gold[r["id"]]["correct_answers"]
        aliases = r["correct_answers"].split("|")
        r["memory_score"], r["search_score"] = score(r["memory"], aliases), score(r["search"], aliases)
        for m in experiment.METHODS:
            searched = r[f"{m}::searched"] in ("True", "true", "1", True)
            if m.startswith("Oracle"):
                searched = r["memory_score"] != "correct"
            r[f"{m}::searched"] = searched
            r[f"{m}::score"] = r["search_score"] if searched else r["memory_score"]
        rows.append(r)
    with experiment.out_path(experiment.CSV_OUT).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), restval="")
        w.writeheader()
        w.writerows(rows)
    experiment.write_report(rows, len(gold))
    experiment.METHODS[:] = all_methods
    return rows


if __name__ == "__main__":
    for model, filename in RUNS.items():
        rows = rescore(model, filename)
        print(f"{model}: {len(rows)} answers re-scored")
