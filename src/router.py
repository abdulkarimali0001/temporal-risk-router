"""The router: combines both checks to decide how a question should be answered.

    Check 1 - does the answer change over time?   (src/time_check.py)
    Check 2 - does the AI actually know it?        (src/knowledge_check.py)

                      | AI knows it               | AI unsure
    ------------------+---------------------------+------------------------------
    LOW   (never)     | answer from memory        | SEARCH (incomplete knowledge)
    MAYBE (sometimes) | answer + recency warning  | SEARCH
    HIGH  (often)     | SEARCH (may be outdated)  | SEARCH

Why both? A knowledge check alone misses "confident but outdated" answers,
and a time check alone misses stable facts the AI never learned.

Try it:
    python -m src.router "Who wrote the Swahili novel Kufa Kuzikana?"
"""
from __future__ import annotations

from src import knowledge_check, time_check

ACTIONS = {"answer": "answer from memory",
           "warn": "answer + recency warning",
           "search": "search first"}
GROUP_NAMES = {"LOW": "LOW", "AMBIGUOUS": "MAYBE", "HIGH": "HIGH"}


def decide(group: str, knows: bool | None) -> tuple[str, str]:
    """Return (action, reason) from the two checks."""
    if group == "HIGH":
        return "search", "the answer changes often, so memory may be outdated"
    if not knows:
        return "search", "the AI is unsure, so its knowledge may be incomplete"
    if group == "AMBIGUOUS":
        return "warn", "the AI knows it, but the answer can change sometimes"
    return "answer", "stable fact and the AI knows it"


def route(question: str, model=None) -> dict:
    group = time_check.classify(question, model)
    if group == "HIGH":
        # No need to check the AI's knowledge: we search anyway.
        knowledge = {"knows": None, "agreement": None, "answers": []}
    else:
        knowledge = knowledge_check.check(question)
    action, reason = decide(group, knowledge["knows"])
    return {"question": question, "group": group, **knowledge, "action": action, "reason": reason}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Who wrote the Swahili novel Kufa Kuzikana?"
    r = route(q)
    print(f"Question: {q}")
    print(f"Check 1 (does the answer change?): {GROUP_NAMES[r['group']]}")
    if r["knows"] is None:
        print("Check 2 (does the AI know it?):    skipped - already HIGH")
    else:
        print(f"Check 2 (does the AI know it?):    "
              f"{'KNOWS IT' if r['knows'] else 'UNSURE'} (agreement {r['agreement']:.0%})")
        for i, a in enumerate(r["answers"], 1):
            print(f"    try {i}: {a}")
    print(f"Decision: {ACTIONS[r['action']].upper()} - {r['reason']}")
