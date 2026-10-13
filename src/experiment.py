"""Main experiment: the router against the methods used in other research,
on public benchmarks (FreshQA + PopQA, see src/benchmarks.py).

For every question we compute once (and cache):
  - memory answer        the AI answers alone
  - search answer        Wikipedia search, answer only from the sources
  - Check 1              time check group (LOW / MAYBE / HIGH)
  - Check 2              self-consistency (3 samples) -> knows / unsure
  - verbal confidence    the AI's own 0-100 confidence (a common baseline)
Each method then only decides WHICH answer to use, so all methods are compared
on exactly the same answers:

  Never search          always the memory answer
  Always search         always the search answer
  Time check only       search if HIGH
  Self-consistency only search if unsure                (Moskvoretskii et al. 2025)
  Verbal confidence     search if confidence < 70        (asking the model)
  Router (ours)         both checks
  Oracle                search only when the memory answer is wrong (best possible)

Measures: accuracy, wrong answers (confidently wrong/outdated), no-guess answers,
share of questions searched. 95% intervals by bootstrap.

    python -m src.experiment
Output: results/experiment_report.md, results/experiment_answers.csv, results/experiment_chart.png
"""
from __future__ import annotations

import csv
import json
import random
import re
import time
from collections import Counter
from datetime import date

from src import benchmarks, knowledge_check, llm, pipeline, router, time_check
from src.evaluate_answers import score
from src.llm import ROOT

RESULTS = ROOT / "results"
CACHE = RESULTS / "experiment_cache.json"
CSV_OUT = RESULTS / "experiment_answers.csv"
REPORT = RESULTS / "experiment_report.md"
CHART = RESULTS / "experiment_chart.png"
MAIN_MODEL = "llama3.1:8b"   # other models get their own files, e.g. experiment_report_qwen2.5-7b.md
MODELS = ["llama3.1:8b", "qwen2.5:7b", "qwen2.5:14b"]   # every model that may have a run


def answers_file(model: str) -> str:
    """results/ file with one model's answers to the benchmark."""
    if model == MAIN_MODEL:
        return CSV_OUT.name
    slug = re.sub(r"[^\w.-]+", "-", model)
    return f"{CSV_OUT.stem}_{slug}{CSV_OUT.suffix}"



# Training-data cutoff of each model (from the model cards). Used by the cutoff-aware router:
# if the model's knowledge is more than a year old, "changes sometimes" (MAYBE) is treated
# as risky too, because a slowly changing answer has probably changed since then.
MODEL_CUTOFFS = {"llama3.1:8b": "2023-12",
                 # Qwen does not publish a data cutoff; its release month is an upper bound
                 "qwen2.5:7b": "2024-09", "qwen2.5:14b": "2024-09"}
STALE_AFTER_YEARS = 1.0

CONFIDENCE_THRESHOLD = 70
# "search" = first version (plain page text, a few paragraphs);
# "search_v2" = full pages with infoboxes and tables, merged queries, BM25 passage ranking
# "search_v3" = search_v2 + live web search (Tavily), used when a Tavily key is set
SEARCH_LABELS = {"search": "First search (Wikipedia text)",
                 "search_v2": "Improved Wikipedia search",
                 "search_v3": "Wikipedia + live web"}


def search_version() -> str:
    from src import search as _s
    return "search_v3" if _s.web_enabled() else "search_v2"


SEARCH_VERSION = search_version()
CONF_PROMPT = ("Today's date is {today}. How confident are you that you know the correct, "
               "up-to-date answer to this question, without looking anything up? "
               "Reply with one number from 0 to 100 only.\n\nQuestion: {q}")

METHODS = ["Never search", "Always search", "Time check only", "Self-consistency only",
           "Verbal confidence", "Router (ours)", "Router + cutoff rule (ours)",
           "Router, AI time check (ours)", "Router, dated AI time check (ours)",
           "Router, cheap check (ours)", "Router, strict check (ours)", "Oracle (best possible)"]
OURS = ("Router (ours)", "Router + cutoff rule (ours)", "Router, AI time check (ours)",
        "Router, dated AI time check (ours)", "Router, cheap check (ours)", "Router, strict check (ours)")
TYPES = {"stable_common": "Stable, famous (PopQA)",
         "stable_rare": "Stable, rare (PopQA) - incomplete",
         "stable_freshqa": "Never-changing (FreshQA)",
         "changing": "Changing (FreshQA) - outdated"}


# ---------- per-question work (cached) ----------
def _load_cache() -> dict:
    try:
        return json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict):
    CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


def confidence(question: str) -> int:
    reply = llm.generate(CONF_PROMPT.format(q=question, today=date.today().isoformat()), max_tokens=10)
    m = re.search(r"\d{1,3}", reply)
    return min(int(m.group()), 100) if m else 0


def components(q: str, cache: dict, tag: str) -> dict:
    key = f"{tag}::{q}"
    c = cache.setdefault(key, {})
    t = c.setdefault("seconds", {})
    if "memory" not in c:
        t0 = time.time(); c["memory"] = pipeline.answer_from_memory(q)
        t["memory"] = round(time.time() - t0, 2); _save_cache(cache)
    if "confidence" not in c:
        t0 = time.time(); c["confidence"] = confidence(q)
        t["confidence"] = round(time.time() - t0, 2); _save_cache(cache)
    if "llm_group" not in c:
        t0 = time.time(); c["llm_group"] = time_check.classify_llm(q)
        t["llm_time_check"] = round(time.time() - t0, 2); _save_cache(cache)
    if "dated_group" not in c:
        cutoff = MODEL_CUTOFFS.get(llm.model_name(), "2024")
        c["dated_group"] = time_check.classify_llm_dated(q, cutoff); _save_cache(cache)
    if SEARCH_VERSION not in c:
        t0 = time.time()
        r = pipeline.answer_with_search(q)
        t["search"] = round(time.time() - t0, 2)
        c[SEARCH_VERSION] = {"answer": r["answer"], "query": r["query"],
                             "sources": [p["url"] for p in r["sources"]]}
        _save_cache(cache)
    return c


def out_path(path):
    """Main model -> results/experiment_report.md; other models get a suffix."""
    name = llm.model_name()
    if name == MAIN_MODEL:
        return path
    slug = re.sub(r"[^\w.-]+", "-", name)
    return path.with_name(f"{path.stem}_{slug}{path.suffix}")


def knowledge_age_years(model: str) -> float | None:
    cutoff = MODEL_CUTOFFS.get(model)
    if not cutoff:
        return None
    y, m = map(int, cutoff.split("-"))
    today = date.today()
    return (today.year - y) + (today.month - m) / 12


def knowledge_is_stale(model: str) -> bool:
    """Unknown cutoff: assume stale (every current open model is older than a year)."""
    age = knowledge_age_years(model)
    return age is None or age >= STALE_AFTER_YEARS


def decisions(group: str, knows: bool, conf: int, memory_correct: bool,
              stale: bool = True, llm_group: str | None = None,
              knows_cheap: bool | None = None, dated_group: str | None = None,
              knows_strict: bool | None = None) -> dict:
    """Which methods search (True) for this question."""
    return {"Never search": False,
            "Always search": True,
            "Time check only": group == "HIGH",
            "Self-consistency only": not knows,
            "Verbal confidence": conf < CONFIDENCE_THRESHOLD,
            "Router (ours)": router.decide(group, knows)[0] == "search",
            "Router + cutoff rule (ours)": (router.decide(group, knows)[0] == "search"
                                            or (stale and group == "AMBIGUOUS")),
            "Router, AI time check (ours)": router.decide(llm_group or group, knows)[0] == "search",
            # the AI is told its training cutoff and today's date
            "Router, dated AI time check (ours)": router.decide(dated_group or group, knows)[0] == "search",
            # Check 2 from the memory answer + ONE sample (1 AI call instead of 3)
            # memory answer + 3 samples, no two of them may contradict each other
            "Router, strict check (ours)": router.decide(
                group, knows if knows_strict is None else knows_strict)[0] == "search",
            "Router, cheap check (ours)": router.decide(
                group, knows if knows_cheap is None else knows_cheap)[0] == "search",
            "Oracle (best possible)": not memory_correct}


# ---------- statistics ----------
def bootstrap_ci(values: list[int], n: int = 2000, seed: int = 0) -> tuple[float, float]:
    if not values:
        return 0.0, 0.0
    rng = random.Random(seed)
    means = sorted(sum(rng.choice(values) for _ in values) / len(values) for _ in range(n))
    return means[int(0.025 * n)], means[int(0.975 * n) - 1]


def mcnemar(rows: list[dict], a: str, b: str) -> tuple[int, int, float]:
    """Exact McNemar test on paired answers: (a right & b wrong, a wrong & b right, p-value)."""
    from math import comb
    x = sum(r[f"{a}::score"] == "correct" and r[f"{b}::score"] != "correct" for r in rows)
    y = sum(r[f"{a}::score"] != "correct" and r[f"{b}::score"] == "correct" for r in rows)
    n = x + y
    if n == 0:
        return x, y, 1.0
    p = 2 * sum(comb(n, i) for i in range(0, min(x, y) + 1)) / 2 ** n
    return x, y, min(p, 1.0)


def summary(rows: list[dict]) -> dict:
    out = {}
    for m in METHODS:
        scores = [r[f"{m}::score"] for r in rows]
        correct = [int(s == "correct") for s in scores]
        c = Counter(scores)
        out[m] = {"acc": sum(correct) / len(rows), "ci": bootstrap_ci(correct),
                  "correct": c["correct"], "wrong": c["wrong"], "no guess": c["no guess"],
                  "search_rate": sum(r[f"{m}::searched"] for r in rows) / len(rows)}
    return out


# ---------- report ----------
def chart(s: dict, n: int):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib not installed - skipping chart)")
        return
    ink, muted, grid, accent = "#111827", "#6B7280", "#E5E7EB", "#2563EB"
    fig, ax = plt.subplots(figsize=(8, 5), dpi=200)
    for m in METHODS:
        x, y = s[m]["search_rate"] * 100, s[m]["acc"] * 100
        ours, oracle = m in OURS, m.startswith("Oracle")
        hollow = oracle or m == "Router + cutoff rule (ours)"
        ax.scatter(x, y, s=110 if ours else 60, zorder=3,
                   color="white" if hollow else (accent if ours else muted),
                   edgecolors=accent if ours else muted, linewidths=1.8 if ours else 1.5)
        dy = {"Router (ours)": 8, "Router + cutoff rule (ours)": -14}.get(m, -4)
        ax.annotate(m, (x, y), xytext=(9, dy), textcoords="offset points",
                    fontsize=10, color=ink, fontweight="bold" if ours else "normal")
    ax.set_xlabel("Questions searched (%)  - cost", color=ink)
    ax.set_ylabel("Correct answers (%)", color=ink)
    ax.set_title(f"Accuracy vs. searches ({n} benchmark questions, {llm.model_name()})",
                 color=ink, loc="left", fontsize=12)
    ax.set_xlim(-5, 115)
    ax.grid(color=grid, linewidth=0.8)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(grid)
    ax.tick_params(colors=muted)
    fig.tight_layout()
    fig.savefig(out_path(CHART))
    plt.close(fig)


def write_report(rows: list[dict], total: int):
    s = summary(rows)
    n = len(rows)
    L = [f"# Experiment: when should the AI search?\n",
         f"Model `{llm.model_name()}` · {date.today()} · {n}/{total} questions from public benchmarks "
         f"(FreshQA {benchmarks.FRESHQA_VERSION}, PopQA)\n",
         f"Search used by the methods below: **{SEARCH_LABELS[SEARCH_VERSION]}**.\n",
         "## Main result\n",
         "| Method | Correct (95% interval) | Wrong | No guess | Searched |",
         "|---|---|---|---|---|"]
    for m in METHODS:
        x = s[m]
        name = f"**{m}**" if m in OURS else m
        L.append(f"| {name} | {x['acc']:.0%} ({x['ci'][0]:.0%}-{x['ci'][1]:.0%}) | {x['wrong']} "
                 f"| {x['no guess']} | {x['search_rate']:.0%} |")
    L += ["", f"![Accuracy vs. searches]({out_path(CHART).name})", ""]

    L += ["## Correct answers by question type\n",
          "| Question type | n | " + " | ".join(METHODS) + " |",
          "|---|---|" + "---|" * len(METHODS)]
    for t, name in TYPES.items():
        sub = [r for r in rows if r["type"] == t]
        if sub:
            L.append(f"| {name} | {len(sub)} | " + " | ".join(
                f"{sum(r[f'{m}::score'] == 'correct' for r in sub) / len(sub):.0%}" for m in METHODS) + " |")
    L += ["", "## Share of questions searched, by type\n",
          "| Question type | " + " | ".join(METHODS[2:7]) + " |", "|---|" + "---|" * 5]
    for t, name in TYPES.items():
        sub = [r for r in rows if r["type"] == t]
        if sub:
            L.append(f"| {name} | " + " | ".join(
                f"{sum(r[f'{m}::searched'] for r in sub) / len(sub):.0%}" for m in METHODS[2:7]) + " |")

    versions = [v for v in SEARCH_LABELS if any(r.get(f"{v}::score") for r in rows)]
    if len(versions) > 1:
        both = [r for r in rows if all(r.get(f"{v}::score") for v in versions)]
        L += ["", "## Search quality: each version of the search\n",
              f"Accuracy when ALWAYS searching ({len(both)} questions answered by every version).\n",
              "| Question type | " + " | ".join(SEARCH_LABELS[v] for v in versions) + " |",
              "|---|" + "---|" * len(versions)]
        for t, name in list(TYPES.items()) + [("all", "**All**")]:
            sub = [r for r in both if t == "all" or r["type"] == t]
            if sub:
                L.append(f"| {name} | " + " | ".join(
                    f"{sum(r[f'{v}::score'] == 'correct' for r in sub) / len(sub):.0%}"
                    for v in versions) + " |")

    fresh = [r for r in rows if r["source"] == "FreshQA"]
    if fresh:
        right = sum(r["group"] == benchmarks.TIME_GROUP[r["fact_type"]] for r in fresh)
        fast = [r for r in fresh if r["fact_type"] == "fast-changing"]
        L += ["", "## Check 1 on FreshQA (outside data, not used for training)\n",
              f"- Right group (never/slow/fast = LOW/MAYBE/HIGH): {right}/{len(fresh)} ({right / len(fresh):.0%})",
              f"- Fast-changing questions caught as HIGH: "
              f"{sum(r['group'] == 'HIGH' for r in fast)}/{len(fast)}"]
        for col, label in [("llm_group", "Check 1 asked to the AI instead"),
                           ("dated_group", "Check 1 asked to the AI, told its cutoff and today's date")]:
            llm_rows = [r for r in fresh if r.get(col)]
            if llm_rows:
                right_llm = sum(r[col] == benchmarks.TIME_GROUP[r["fact_type"]] for r in llm_rows)
                L += [f"- {label}: right group {right_llm}/{len(llm_rows)} "
                      f"({right_llm / len(llm_rows):.0%}), fast-changing caught as HIGH "
                      f"{sum(r[col] == 'HIGH' for r in llm_rows if r['fact_type'] == 'fast-changing')}"
                      f"/{sum(r['fact_type'] == 'fast-changing' for r in llm_rows)}"]

    L += ["", "## Is the difference real? (paired McNemar test)\n",
          "For each pair: questions only the router got right vs. only the other method got right. "
          "p < 0.05 means the difference is unlikely to be chance.\n",
          "| Router vs. | Only router right | Only other right | p-value |", "|---|---|---|---|"]
    best = max(OURS, key=lambda m: s[m]["acc"])
    for m in METHODS:
        if m in OURS or m.startswith("Oracle"):
            continue
        x, y, p = mcnemar(rows, best, m)
        L.append(f"| {m} | {x} | {y} | {p:.3f}{' *' if p < 0.05 else ''} |")
    L.append(f"\n(Compared using: {best}.)")

    age = knowledge_age_years(llm.model_name())
    L += ["", "## Cutoff rule\n",
          f"Model training cutoff: {MODEL_CUTOFFS.get(llm.model_name(), 'unknown')}"
          + (f" ({age:.1f} years before the test date)." if age is not None else ".")
          + " With the cutoff rule, questions whose answers change *sometimes* (MAYBE) are also "
          "searched when the model's knowledge is more than a year old."]

    L += ["", "## How to read this\n",
          "- **Never search** shows what the AI gets wrong on its own (outdated + incomplete knowledge).",
          "- **Always search** is the most expensive option; searching can also hurt when the source is poor.",
          "- **Oracle** searches only when the memory answer is wrong: the best any method could do.",
          "- A good method gets close to the best accuracy while searching far fewer questions.",
          "", "## Notes\n",
          "- Scoring: an answer is correct if it contains one of the benchmark's accepted answers "
          "(automatic matching; see `experiment_answers.csv` to check by hand).",
          f"- FreshQA answers are as of {benchmarks.FRESHQA_VERSION}. Answers that changed since then were "
          "re-checked with sources (`data/gold_updates.csv`); broken questions are left out "
          "(`data/excluded_questions.csv`).",
          "- Questions with a false premise were left out."]
    out_path(REPORT).write_text("\n".join(L) + "\n", encoding="utf-8")
    chart(s, n)


def main():
    RESULTS.mkdir(exist_ok=True)
    items = benchmarks.load()
    model = time_check.load()
    tag = f"{llm.backend()}::{llm.model_name()}"
    cache = _load_cache()
    rows = []
    stale = knowledge_is_stale(llm.model_name())
    print(f"{len(items)} questions, model {llm.model_name()}\n", flush=True)
    for i, it in enumerate(items, 1):
        q = it["question"]
        print(f"[{i}/{len(items)}] {q}", flush=True)
        try:
            c = components(q, cache, tag)
            t0 = time.time()
            kc = knowledge_check.check(q)
            c["seconds"].setdefault("knowledge_check", round(time.time() - t0, 2))
            kc_cheap = knowledge_check.check_cheap(q, c["memory"])
            kc_strict = knowledge_check.check_strict(q, c["memory"])
            group = time_check.classify(q, model)
        except Exception as e:  # keep going if one question fails
            print(f"   ERROR: {e}", flush=True)
            continue
        aliases = it["correct_answers"].split("|")
        srch = c[SEARCH_VERSION]
        mem_score, srch_score = score(c["memory"], aliases), score(srch["answer"], aliases)
        row = {**it, "group": group, "knows": kc["knows"], "agreement": kc["agreement"],
               "knows_cheap": kc_cheap["knows"], "knows_strict": kc_strict["knows"],
               "confidence": c["confidence"], "memory": c["memory"], "memory_score": mem_score,
               "search": srch["answer"], "search_score": srch_score, "query": srch["query"],
               "sources": " ".join(srch["sources"]),
               **{f"{v}::score": score(c[v] if v == "search" else c[v]["answer"], aliases)
                  for v in SEARCH_LABELS if v in c}}
        row["llm_group"] = c.get("llm_group", "")
        row["dated_group"] = c.get("dated_group", "")
        row.update({f"seconds_{k}": v for k, v in c.get("seconds", {}).items()})
        for m, searched in decisions(group, kc["knows"], c["confidence"], mem_score == "correct",
                                     stale, c.get("llm_group"), kc_cheap["knows"],
                                     c.get("dated_group"), kc_strict["knows"]).items():
            row[f"{m}::searched"] = searched
            row[f"{m}::score"] = srch_score if searched else mem_score
        rows.append(row)
        print(f"   memory: {mem_score}   search: {srch_score}   "
              f"router: {'search' if row['Router (ours)::searched'] else 'memory'}", flush=True)

        with out_path(CSV_OUT).open("w", newline="", encoding="utf-8") as f:   # save after every question
            w = csv.DictWriter(f, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), restval="")
            w.writeheader()
            w.writerows(rows)
        if i % 10 == 0 or i == len(items):
            write_report(rows, len(items))

    if rows:
        write_report(rows, len(items))
        print("\n" + out_path(REPORT).read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
