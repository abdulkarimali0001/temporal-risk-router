"""Check 2: does the AI actually know the answer? (self-consistency)

Ask the model the SAME question several times, without any search:
  - the answers agree                     -> the model KNOWS it
  - the answers disagree, or it says
    "I don't know"                        -> the model is UNSURE
                                             (its knowledge is incomplete)

Based on the adaptive-retrieval literature (e.g. Moskvoretskii et al., ACL 2025),
which finds simple uncertainty checks like this competitive with complex methods.

Every answer is saved in results/knowledge_check_cache.json, so re-runs and
demos cost nothing and work offline.

Try it:
    python -m src.knowledge_check "Who wrote the Swahili novel Kufa Kuzikana?"
"""
from __future__ import annotations

import json
import re
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

from src import llm

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "results" / "knowledge_check_cache.json"

SAMPLES = 3                # how many times we ask the same question
AGREEMENT_NEEDED = 0.6     # share of answer pairs that must match to count as "knows it"

PROMPT = ("Answer the question in at most 8 words. No explanation. "
          "If you do not know, reply exactly: I don't know.\n\nQuestion: {q}")

IDK = re.compile(r"\b(i don'?t know|not sure|unknown|cannot (determine|answer)|no information)\b", re.I)

NUMBER_WORDS = {w: str(i) for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen "
    "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split())}


def _normalise(text: str) -> str:
    text = text.lower()
    # "Twelve" and "12" should count as the same answer
    text = " ".join(NUMBER_WORDS.get(w.strip(".,!?"), w) for w in text.split())
    text = re.sub(r"[^a-z0-9가-힣 ]", " ", text)
    return " ".join(w for w in text.split() if w not in {"the", "a", "an", "is", "was", "it"})


def _same(a: str, b: str) -> bool:
    a, b = _normalise(a), _normalise(b)
    if not a or not b:
        return False
    if a in b or b in a:
        return True
    return SequenceMatcher(None, a, b).ratio() >= 0.6


def agreement(answers: list[str]) -> float:
    """Share of answer pairs that say the same thing (0.0 - 1.0)."""
    pairs = list(combinations(answers, 2))
    return sum(_same(a, b) for a, b in pairs) / len(pairs)


def judge(answers: list[str]) -> dict:
    said_idk = sum(bool(IDK.search(a)) for a in answers)
    score = agreement(answers)
    return {"answers": answers, "agreement": round(score, 2), "said_dont_know": said_idk,
            "knows": said_idk == 0 and score >= AGREEMENT_NEEDED}


def _load_cache() -> dict:
    return json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}


def _save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def check(question: str) -> dict:
    """Ask the model SAMPLES times and decide whether it knows the answer."""
    backend = llm.backend()
    cache = _load_cache()
    key = f"{backend}::{question}"
    if key not in cache:
        cache[key] = [llm.generate(PROMPT.format(q=question), temperature=1.0, max_tokens=40)
                      for _ in range(SAMPLES)]
        _save_cache(cache)
    return judge(cache[key])


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Who wrote the Swahili novel Kufa Kuzikana?"
    r = check(q)
    print(f"Question: {q}")
    for i, a in enumerate(r["answers"], 1):
        print(f"  try {i}: {a}")
    print(f"Agreement: {r['agreement']:.0%}  ->  {'KNOWS IT' if r['knows'] else 'UNSURE'}")
