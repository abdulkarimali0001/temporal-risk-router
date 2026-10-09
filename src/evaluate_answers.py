"""Answer correctness: are the final answers actually right?

Compares three ways of answering the questions in data/answer_test.csv,
each checked against verified correct answers:

  1. Memory only    - the AI answers alone, never searches
  2. Always search  - search Wikipedia first for every question
  3. Router         - our two checks decide: answer from memory, warn, or search

Each answer is scored as:
  correct    - contains one of the accepted answers
  no guess   - the system said it could not find / does not know
  wrong      - anything else (a confident wrong or outdated answer)

    python -m src.evaluate_answers
Output: results/answer_evaluation.md, results/answer_evaluation.csv
"""
from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import date

from src import llm, pipeline, router, search, time_check
from src.llm import ROOT

DATA = ROOT / "data" / "answer_test.csv"
RESULTS = ROOT / "results"
CACHE = RESULTS / "answer_cache.json"
CSV_OUT = RESULTS / "answer_evaluation.csv"
REPORT = RESULTS / "answer_evaluation.md"

METHODS = {"memory": "Memory only", "search": "Always search", "router": "Router (both checks)"}
TYPES = {"stable_common": "Stable, well known",
         "stable_rare": "Stable, rare (incomplete)",
         "changing": "Changes over time (outdated)"}
NO_GUESS = ["i don't know", "i do not know", "not sure", "could not find", "couldn't find",
            "no information", "not able to", "unable to", "don't have", "do not have",
            "not aware", "unknown", "i cannot", "i can't",
            "모르", "알 수 없", "찾을 수 없", "정보가 없", "확인할 수 없",
            "sijui", "sina uhakika", "sikuweza kupata", "hakuna taarifa", "sina taarifa"]


# ---------- scoring ----------
MONTHS = {m: m[:3] for m in ["january", "february", "march", "april", "june", "july", "august",
                               "september", "october", "november", "december"]}
MONTHS["sept"] = "sep"


def _spaced(text: str) -> str:
    words = re.sub(r"[^\w]+", " ", text.lower()).split()
    return " ".join(MONTHS.get(w, w) for w in words)       # "November 27" = "Nov. 27"


def _compact(text: str) -> str:
    return re.sub(r"[^\w]+", "", _spaced(text))


GENERIC = set("""city county state states river university united kingdom republic island islands
province party team club records music film group company north south east west new saint
national international association federation league church""".split())


def _is_name(alias: str) -> bool:
    """Looks like a person's name: 2-3 capitalised words, e.g. "Sanae Takaichi"."""
    words = alias.split()
    return 2 <= len(words) <= 3 and all(w[:1].isupper() for w in words)


def is_correct(answer: str, aliases: list[str]) -> bool:
    a_sp, a_cp = f" {_spaced(answer)} ", _compact(answer)
    for alias in aliases:
        alias = alias.strip()
        if not alias:
            continue
        if re.fullmatch(r"[\d,.]+", alias):              # numbers: "1,708" = "1708m" = "1708미터"
            num = alias.replace(",", "")
            if re.search(rf"(?<![\d.]){re.escape(num)}(?![\d])", answer.replace(",", "")):
                return True
            continue
        if f" {_spaced(alias)} " in a_sp:          # whole-word match ("8", "Fe", "LG")
            return True
        if len(_compact(alias)) >= 5 and _compact(alias) in a_cp:  # "Noh-jung" = "Nohjung"
            return True
        if re.search(r"[\uac00-\ud7a3]", alias) and len(_compact(alias)) >= 2 \
                and _compact(alias) in a_cp:                 # Korean: "서울" in "서울입니다"
            return True
        last = _spaced(alias).split()[-1] if _spaced(alias) else ""
        if (_is_name(alias) and len(last) >= 4 and last not in GENERIC
                and f" {last} " in a_sp):          # surname only: "Takaichi" for "Sanae Takaichi"
            return True
    return False


def score(answer: str, aliases: list[str]) -> str:
    if is_correct(answer, aliases):
        return "correct"
    low = answer.lower()
    if answer.strip() == pipeline.NOT_FOUND or any(p in low for p in NO_GUESS):
        return "no guess"
    return "wrong"


# ---------- cached answering ----------
def _load_cache() -> dict:
    try:
        return json.loads(CACHE.read_text())
    except Exception:
        return {}


def _cached(cache: dict, key: str, fn):
    if key not in cache:
        cache[key] = fn()
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1))
    return cache[key]


def run_one(q: str, model, cache: dict, tag: str) -> dict:
    memory = _cached(cache, f"{tag}::memory::{q}", lambda: pipeline.answer_from_memory(q))
    searched = _cached(cache, f"{tag}::{search.version()}::{q}", lambda: _search_record(q))
    route = router.route(q, model=model)
    if route["action"] == "search":
        routed = searched["answer"]
    else:
        routed = memory + (" " + pipeline.WARNING if route["action"] == "warn" else "")
    return {"memory": memory, "search": searched["answer"], "router": routed,
            "action": route["action"], "group": route["group"], "query": searched["query"],
            "sources": " ".join(searched["sources"])}


def _search_record(q: str) -> dict:
    r = pipeline.answer_with_search(q)
    return {"answer": r["answer"], "query": r["query"], "sources": [p["url"] for p in r["sources"]]}


# ---------- report ----------
def write_report(rows: list[dict], total: int, model_name: str):
    lines = [f"# Answer correctness evaluation\n",
             f"Model: `{model_name}`   Date: {date.today()}   Questions: {len(rows)}/{total}\n",
             "Correct answers were checked by hand against the sources in `data/answer_test.csv`.\n",
             "## Overall\n",
             "| Method | Correct | Wrong | No guess | Searches |",
             "|---|---|---|---|---|"]
    for m, name in METHODS.items():
        c = Counter(r[f"{m}_score"] for r in rows)
        searches = {"memory": 0, "search": len(rows),
                    "router": sum(r["action"] == "search" for r in rows)}[m]
        n = len(rows) or 1
        lines.append(f"| {name} | {c['correct']}/{len(rows)} ({c['correct']*100//n}%) "
                     f"| {c['wrong']} | {c['no guess']} | {searches} |")

    lines += ["\n## Correct answers by question type\n",
              "| Question type | " + " | ".join(METHODS.values()) + " |",
              "|---|" + "---|" * len(METHODS)]
    for t, tname in TYPES.items():
        sub = [r for r in rows if r["type"] == t]
        if sub:
            cells = [f"{sum(r[f'{m}_score'] == 'correct' for r in sub)}/{len(sub)}" for m in METHODS]
            lines.append(f"| {tname} | " + " | ".join(cells) + " |")

    lines += ["\n## Wrong answers (for manual review)\n"]
    for r in rows:
        for m, name in METHODS.items():
            if r[f"{m}_score"] == "wrong":
                ans = r[m].replace("\n", " ")[:200]
                lines.append(f"- **{name}**, Q{r['id']} *{r['question']}* "
                             f"(expected: {r['correct_answers'].split('|')[0]}): {ans}")
    lines += ["\n**Scoring:** *correct* = the answer contains an accepted answer; "
              "*no guess* = the system said it could not find or does not know; "
              "*wrong* = a confident answer that is wrong or outdated. "
              "Automatic matching can make mistakes - check `answer_evaluation.csv`."]
    REPORT.write_text("\n".join(lines) + "\n")


def main():
    RESULTS.mkdir(exist_ok=True)
    questions = list(csv.DictReader(DATA.open(encoding="utf-8")))
    model = time_check.load()
    model_name = llm.model_name()
    tag = f"{llm.backend()}::{model_name}"
    cache = _load_cache()
    rows = []
    fields = ["id", "question", "type", "correct_answers", "group", "action",
              "memory", "memory_score", "search", "search_score", "router", "router_score",
              "query", "sources"]

    for i, q in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {q['question']}", flush=True)
        try:
            res = run_one(q["question"], model, cache, tag)
        except Exception as e:  # keep going if one question fails
            print(f"   ERROR: {e}", flush=True)
            continue
        aliases = q["correct_answers"].split("|")
        row = {**{k: q[k] for k in ("id", "question", "type", "correct_answers")}, **res}
        for m in METHODS:
            row[f"{m}_score"] = score(res[m], aliases)
        rows.append(row)
        print("   " + "   ".join(f"{METHODS[m]}: {row[m + '_score']}" for m in METHODS), flush=True)

        with CSV_OUT.open("w", newline="", encoding="utf-8") as f:   # save after every question
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        write_report(rows, len(questions), model_name)

    print("\n" + REPORT.read_text())


if __name__ == "__main__":
    main()
