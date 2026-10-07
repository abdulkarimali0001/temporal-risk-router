"""Version 3: the Two-Signal Router.

Signal 1 - Does the answer change over time?   (Version 2, machine learning)
Signal 2 - Does the AI actually know it?        (self-consistency, src/confidence.py)

                    | AI confident            | AI unsure
--------------------+-------------------------+---------------------------
LOW   (never changes)| answer from memory      | SEARCH (incomplete knowledge)
MAYBE (sometimes)    | answer + warning        | SEARCH
HIGH  (often)        | SEARCH (may be outdated)| SEARCH

Why both? A confidence check alone misses "confident but outdated" answers,
and a time check alone misses stable facts the AI never learned.

Try it:
    python -m src.two_signal "Who founded Kyungdong University?"
"""
from __future__ import annotations

from src import confidence, router_ml

ACTIONS = {"answer": "answer from memory",
           "warn": "answer + recency warning",
           "search": "search the web first"}


def decide(band: str, confident: bool) -> tuple[str, str]:
    """Return (action, reason) from the two signals."""
    if band == "HIGH":
        return "search", "the answer changes often, so memory may be outdated"
    if not confident:
        return "search", "the AI is unsure, so its knowledge may be incomplete"
    if band == "AMBIGUOUS":
        return "warn", "the AI knows it, but it can change sometimes"
    return "answer", "stable fact and the AI is confident"


def route(question: str, model=None, backend: str | None = None) -> dict:
    model = model or router_ml.load()
    band = model.predict([question])[0]
    if band == "HIGH":
        # No need to spend API calls checking confidence: we search anyway.
        conf = {"confident": None, "agreement": None, "answers": []}
    else:
        conf = confidence.check(question, backend)
    action, reason = decide(band, conf["confident"])
    return {"question": question, "band": band, **conf, "action": action, "reason": reason}


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Who founded Kyungdong University?"
    r = route(q)
    names = {"LOW": "LOW", "AMBIGUOUS": "MAYBE", "HIGH": "HIGH"}
    print(f"Question:  {q}")
    print(f"Signal 1 (changes over time?): {names[r['band']]}")
    if r["confident"] is None:
        print("Signal 2 (does the AI know?):  skipped - already HIGH")
    else:
        print(f"Signal 2 (does the AI know?):  "
              f"{'CONFIDENT' if r['confident'] else 'UNSURE'} (agreement {r['agreement']:.0%})")
        for i, a in enumerate(r["answers"], 1):
            print(f"    try {i}: {a}")
    print(f"Decision:  {ACTIONS[r['action']].upper()}  - {r['reason']}")
