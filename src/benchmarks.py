"""Public benchmarks: test the router on questions we did NOT write ourselves.

  FreshQA (Vu et al. 2023, Google; updated weekly, here the April 21, 2026 version)
      Questions whose answers never change, change slowly or change fast.
      -> tests OUTDATED knowledge. Its DEV split also gives extra training
         data for the time check (fast = HIGH, slow = AMBIGUOUS, never = LOW).
  PopQA (Mallen et al. 2023, ACL)
      Simple facts about famous and very obscure entities (Wikipedia page views).
      -> tests INCOMPLETE knowledge (models miss rare, "long-tail" facts).

    python -m src.benchmarks          # download once and sample -> data/benchmark.csv

Output files:
  data/benchmark.csv            questions used by src/experiment.py
  data/freshqa_dev_labels.csv   FreshQA DEV questions (kept for reference)
  data/time_check_extra.csv     all FreshQA + some PopQA questions NOT in the benchmark,
                                extra training data for the time check
The sample is fixed (random seed) so every run and every model sees the same questions.
"""
from __future__ import annotations

import csv
import io
import json
import random
import time
import urllib.parse
import urllib.request

from src.llm import ROOT

FRESHQA_VERSION = "2026-04-21"
FRESHQA_URL = ("https://docs.google.com/spreadsheets/d/"
               "1_8mi-yuK30mvoDJu1KQXD6ODem7MKMcIgVAwDSzJkjM/export?format=csv")
POPQA_URL = "https://datasets-server.huggingface.co/rows?dataset=akariasai/PopQA&config=default&split=test"

RAW = ROOT / "data" / "raw"
BENCHMARK = ROOT / "data" / "benchmark.csv"
DEV_LABELS = ROOT / "data" / "freshqa_dev_labels.csv"
# all FreshQA questions NOT in the benchmark (DEV + unused TEST, with their change-speed labels)
# and unused PopQA questions (stable facts): extra training data for the time check
TIME_TRAIN = ROOT / "data" / "time_check_extra.csv"
EXTRA_POPQA = 150

SEED = 42
PER_FRESHQA_TYPE = 40      # never / slow / fast-changing
PER_POPQA_TYPE = 40        # famous / rare
POPQA_PAGES = 12           # 12 x 100 rows downloaded, then sampled
RARE_MAX_VIEWS = 100       # PopQA s_pop (monthly page views): rare entity
COMMON_MIN_VIEWS = 10000   #                                    famous entity
POPQA_PROPS = {"place of birth", "country", "capital", "capital of", "author", "director",
               "producer", "screenwriter", "composer", "sport", "father", "mother"}

TIME_GROUP = {"never-changing": "LOW", "slow-changing": "AMBIGUOUS", "fast-changing": "HIGH"}
FIELDS = ["id", "source", "question", "type", "fact_type", "popularity", "correct_answers", "version"]


def _fetch(url: str, tries: int = 4) -> bytes:
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "TemporalRiskRouter/1.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except Exception as e:
            if attempt == tries - 1:
                raise
            print(f"   download failed ({e}), retrying...", flush=True)
            time.sleep(5 * (attempt + 1))


# ---------- FreshQA ----------
def load_freshqa() -> list[dict]:
    path = RAW / f"freshqa_{FRESHQA_VERSION}.csv"
    if not path.exists():
        print("Downloading FreshQA ...", flush=True)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(_fetch(FRESHQA_URL))
    rows = list(csv.reader(io.StringIO(path.read_text(encoding="utf-8"))))
    # the sheet may start with note rows: find the real header
    h = next(i for i, r in enumerate(rows)
             if "question" in [c.strip().lower() for c in r] and
             "fact_type" in [c.strip().lower() for c in r])
    header = [c.strip().lower() for c in rows[h]]
    out = []
    for r in rows[h + 1:]:
        d = dict(zip(header, (c.strip() for c in r)))
        if not d.get("question"):
            continue
        d["answers"] = [d[k] for k in header if k.startswith("answer_") and d.get(k)]
        out.append(d)
    return out


def freshqa_items(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    usable = [r for r in rows
              if r.get("fact_type") in TIME_GROUP and r["answers"]
              and r.get("false_premise", "").upper() != "TRUE"]
    dev = [{"question": r["question"], "label": TIME_GROUP[r["fact_type"]], "category": "freshqa_dev"}
           for r in usable if r.get("split", "").upper() == "DEV"]
    test = [r for r in usable if r.get("split", "").upper() == "TEST"]
    rng = random.Random(SEED)
    items = []
    for ft in TIME_GROUP:
        group = [r for r in test if r["fact_type"] == ft]
        for r in rng.sample(group, min(PER_FRESHQA_TYPE, len(group))):
            items.append({"id": f"fqa-{r.get('id', '')}", "source": "FreshQA", "question": r["question"],
                          "type": "stable_freshqa" if ft == "never-changing" else "changing",
                          "fact_type": ft, "popularity": "",
                          "correct_answers": "|".join(r["answers"]), "version": FRESHQA_VERSION})
    return items, dev


# ---------- PopQA ----------
def load_popqa() -> list[dict]:
    path = RAW / "popqa_sample.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    print("Downloading PopQA sample ...", flush=True)
    first = json.loads(_fetch(POPQA_URL + "&offset=0&length=1"))
    total = first.get("num_rows_total", 14267)
    rng = random.Random(SEED)
    rows = []
    for off in sorted(rng.sample(range(0, total - 100, 100), POPQA_PAGES)):
        data = json.loads(_fetch(POPQA_URL + f"&offset={off}&length=100"))
        rows += [x["row"] for x in data["rows"]]
        time.sleep(1)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows


def _answers(row: dict) -> list[str]:
    a = row.get("possible_answers") or "[]"
    if isinstance(a, str):
        try:
            a = json.loads(a)
        except json.JSONDecodeError:
            a = [a]
    return [x for x in a if x]


def popqa_items(rows: list[dict]) -> list[dict]:
    rows = [r for r in rows if r.get("prop") in POPQA_PROPS and _answers(r)]
    rng = random.Random(SEED)
    items = []
    for kind, keep in [("stable_common", lambda p: p >= COMMON_MIN_VIEWS),
                       ("stable_rare", lambda p: p <= RARE_MAX_VIEWS)]:
        group = [r for r in rows if keep(int(r.get("s_pop") or 0))]
        for r in rng.sample(group, min(PER_POPQA_TYPE, len(group))):
            items.append({"id": f"pop-{r.get('id', '')}", "source": "PopQA", "question": r["question"],
                          "type": kind, "fact_type": r["prop"], "popularity": r.get("s_pop", ""),
                          "correct_answers": "|".join(_answers(r)), "version": "PopQA test"})
    return items


def time_training(fresh_rows: list[dict], pop_rows: list[dict], used: set[str]) -> list[dict]:
    """Labelled questions for the time check that are NOT in the benchmark."""
    out = [{"question": r["question"], "label": TIME_GROUP[r["fact_type"]], "category": "freshqa"}
           for r in fresh_rows if r.get("fact_type") in TIME_GROUP and r["question"] not in used]
    pop = [r["question"] for r in pop_rows if r["question"] not in used]
    random.Random(SEED).shuffle(pop)
    out += [{"question": q, "label": "LOW", "category": "popqa"} for q in pop[:EXTRA_POPQA]]
    return out


def build() -> list[dict]:
    fresh_rows, pop_rows = load_freshqa(), load_popqa()
    fresh, dev = freshqa_items(fresh_rows)
    pop = popqa_items(pop_rows)
    items = fresh + pop
    with TIME_TRAIN.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["question", "label", "category"])
        w.writeheader()
        w.writerows(time_training(fresh_rows, pop_rows, {i["question"] for i in items}))
    with BENCHMARK.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(items)
    with DEV_LABELS.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["question", "label", "category"])
        w.writeheader()
        w.writerows(dev)
    return items


GOLD_UPDATES = ROOT / "data" / "gold_updates.csv"
EXCLUDED = ROOT / "data" / "excluded_questions.csv"


def apply_updates(items: list[dict]) -> list[dict]:
    """Answers re-checked on a later date (data/gold_updates.csv: add an accepted answer, or
    replace it when the benchmark's answer has changed since its release) and broken
    questions left out (data/excluded_questions.csv)."""
    if EXCLUDED.exists():
        skip = {r["id"] for r in csv.DictReader(EXCLUDED.open(encoding="utf-8"))}
        items = [i for i in items if i["id"] not in skip]
    if GOLD_UPDATES.exists():
        upd = {r["id"]: r for r in csv.DictReader(GOLD_UPDATES.open(encoding="utf-8"))}
        for i in items:
            u = upd.get(i["id"])
            if u:
                i["correct_answers"] = (u["answers"] if u["action"] == "replace"
                                        else i["correct_answers"] + "|" + u["answers"])
                i["answer_checked_on"] = u["checked_on"]
    return items


def load() -> list[dict]:
    if not BENCHMARK.exists():
        build()
    return apply_updates(list(csv.DictReader(BENCHMARK.open(encoding="utf-8"))))


# ---------- larger benchmark ----------
# The first 200 questions stay exactly as they are (so saved answers are reused);
# new questions are added on top until each group reaches its target.
LARGE_FRESHQA_PER_TYPE = 80     # never / slow / fast-changing  -> 240
LARGE_POPQA_PER_TYPE = 130      # famous / rare                  -> 260   (total 500)


def more_popqa(rows: list[dict], pages: int) -> list[dict]:
    """Download extra PopQA pages and add them to the saved sample."""
    print(f"Downloading {pages} more PopQA pages ...", flush=True)
    have = {r.get("id") for r in rows}
    total = json.loads(_fetch(POPQA_URL + "&offset=0&length=1")).get("num_rows_total", 14267)
    rng = random.Random(SEED + len(rows))
    for off in sorted(rng.sample(range(0, total - 100, 100), pages)):
        data = json.loads(_fetch(POPQA_URL + f"&offset={off}&length=100"))
        rows += [x["row"] for x in data["rows"] if x["row"].get("id") not in have]
        have |= {x["row"].get("id") for x in data["rows"]}
        time.sleep(1)
    (RAW / "popqa_sample.json").write_text(json.dumps(rows, ensure_ascii=False), encoding="utf-8")
    return rows


def extend(fresh_per_type: int = LARGE_FRESHQA_PER_TYPE,
           pop_per_type: int = LARGE_POPQA_PER_TYPE) -> list[dict]:
    items = load()                                   # existing questions first, unchanged
    used = {i["question"] for i in items}
    rng = random.Random(SEED + 1)
    fresh_rows = load_freshqa()
    test = [r for r in fresh_rows if r.get("fact_type") in TIME_GROUP and r["answers"]
            and r.get("false_premise", "").upper() != "TRUE" and r.get("split", "").upper() == "TEST"]
    for ft in TIME_GROUP:
        have = sum(i["fact_type"] == ft for i in items)
        pool = [r for r in test if r["fact_type"] == ft and r["question"] not in used]
        for r in rng.sample(pool, max(0, min(fresh_per_type - have, len(pool)))):
            items.append({"id": f"fqa-{r.get('id', '')}", "source": "FreshQA", "question": r["question"],
                          "type": "stable_freshqa" if ft == "never-changing" else "changing",
                          "fact_type": ft, "popularity": "",
                          "correct_answers": "|".join(r["answers"]), "version": FRESHQA_VERSION})
            used.add(r["question"])

    pop_rows = load_popqa()
    kinds = [("stable_common", lambda p: p >= COMMON_MIN_VIEWS),
             ("stable_rare", lambda p: p <= RARE_MAX_VIEWS)]

    def pool_for(keep):
        return [r for r in pop_rows if r.get("prop") in POPQA_PROPS and _answers(r)
                and r["question"] not in used and keep(int(r.get("s_pop") or 0))]
    # enough candidates for the test AND ~150 spare questions for time-check training
    while any(len(pool_for(k)) < pop_per_type - sum(i["type"] == t for i in items) + 80
              for t, k in kinds) and len(pop_rows) < 6000:
        pop_rows = more_popqa(pop_rows, 10)
    for t, keep in kinds:
        have = sum(i["type"] == t for i in items)
        pool = pool_for(keep)
        for r in rng.sample(pool, max(0, min(pop_per_type - have, len(pool)))):
            items.append({"id": f"pop-{r.get('id', '')}", "source": "PopQA", "question": r["question"],
                          "type": t, "fact_type": r["prop"], "popularity": r.get("s_pop", ""),
                          "correct_answers": "|".join(_answers(r)), "version": "PopQA test"})
            used.add(r["question"])

    with BENCHMARK.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(items)
    with TIME_TRAIN.open("w", newline="", encoding="utf-8") as f:   # never overlaps the test set
        w = csv.DictWriter(f, fieldnames=["question", "label", "category"])
        w.writeheader()
        w.writerows(time_training(fresh_rows, pop_rows, used))
    return items


if __name__ == "__main__":
    import sys
    items = extend() if "--large" in sys.argv else build()
    from collections import Counter
    print(f"Saved {len(items)} questions to {BENCHMARK.relative_to(ROOT)}")
    for (src, t), n in sorted(Counter((i["source"], i["type"]) for i in items).items()):
        print(f"  {src:8} {t:15} {n}")
    print(f"FreshQA DEV questions for time-check training: "
          f"{sum(1 for _ in open(DEV_LABELS)) - 1} -> {DEV_LABELS.relative_to(ROOT)}")
