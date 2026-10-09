"""Human check of the automatic scoring.

120 answers (both models, memory and search answers, stratified by automatic
score) are in data/human_review_sample.json. Group members mark them by hand on
the review page (blind: they don't see the automatic score, model or method).
Their marks are exported to data/human_review_marks.json as
    [{"reviewer": "...", "item": "r001", "verdict": "correct|wrong|no_answer|unsure", "note": ""}]

    python -m src.human_review
Output: results/human_review_report.md - agreement between people and the
automatic scoring (percent and Cohen's kappa), and between reviewers.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from itertools import combinations

from src.llm import ROOT

SAMPLE = ROOT / "data" / "human_review_sample.json"
MARKS = ROOT / "data" / "human_review_marks.json"
REPORT = ROOT / "results" / "human_review_report.md"
AUTO = {"correct": "correct", "wrong": "wrong", "no guess": "no_answer"}
LABELS = ["correct", "wrong", "no_answer"]


def kappa(pairs: list[tuple[str, str]]) -> float:
    n = len(pairs)
    if n == 0:
        return float("nan")
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / n ** 2
    return (po - pe) / (1 - pe) if pe < 1 else 1.0


def main():
    sample = {i["id"]: i for i in json.loads(SAMPLE.read_text(encoding="utf-8"))}
    marks = json.loads(MARKS.read_text(encoding="utf-8"))
    by_item = defaultdict(dict)
    for m in marks:
        if m["verdict"] in LABELS:
            by_item[m["item"]][m["reviewer"]] = m["verdict"]

    # majority human verdict per item (ties dropped)
    human = {}
    for item, votes in by_item.items():
        top = Counter(votes.values()).most_common()
        if len(top) == 1 or top[0][1] > top[1][1]:
            human[item] = top[0][0]
    pairs = [(AUTO[sample[i]["auto"]], v) for i, v in human.items()]
    agree = sum(a == b for a, b in pairs)

    L = ["# Human check of the automatic scoring\n",
         f"{len(by_item)} of {len(sample)} answers marked by "
         f"{len({m['reviewer'] for m in marks})} reviewers; {len(human)} have a clear majority verdict.\n",
         "## People vs. automatic scoring\n",
         f"- Agreement: {agree}/{len(pairs)} ({agree / max(len(pairs), 1):.0%})",
         f"- Cohen's kappa: {kappa(pairs):.2f} (above 0.8 = almost perfect, 0.6-0.8 = substantial)\n",
         "| Automatic \\ People | " + " | ".join(LABELS) + " |", "|---|" + "---|" * len(LABELS)]
    cm = Counter(pairs)
    for a in LABELS:
        L.append(f"| {a} | " + " | ".join(str(cm[(a, b)]) for b in LABELS) + " |")

    # where automatic "wrong" was actually right = scoring too strict
    strict = [i for i, v in human.items() if AUTO[sample[i]["auto"]] == "wrong" and v == "correct"]
    loose = [i for i, v in human.items() if AUTO[sample[i]["auto"]] == "correct" and v != "correct"]
    L += ["", f"- Automatic scoring too strict (marked wrong, people say correct): {len(strict)}",
          f"- Automatic scoring too lenient (marked correct, people disagree): {len(loose)}"]

    multi = [v for v in by_item.values() if len(v) >= 2]
    if multi:
        rp = [(a, b) for v in multi for a, b in combinations(list(v.values()), 2)]
        L += ["", "## Agreement between reviewers\n",
              f"- {len(multi)} answers marked by 2+ people; pairwise kappa {kappa(rp):.2f}"]

    L += ["", "## Disagreements (for discussion)\n"]
    for i in strict + loose:
        s = sample[i]
        L.append(f"- {i} *{s['question']}* - accepted: {', '.join(s['accepted'][:3])} - "
                 f"answer: {s['answer'][:160]} - automatic: {s['auto']}, people: {human[i]}")
    REPORT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
