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

IDK = re.compile(r"\b(i don'?t know|not sure|unknown|cannot (determine|answer)|no information)\b"
                 r"|모르|알 수 없|정보가 없|확실하지 않"
                 r"|\bsijui\b|sina uhakika|sina taarifa|haijulikani", re.I)

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


# ---------- strict version: no contradictions allowed ----------
# The similarity rule above says "located in Gangneung, Gangwon-do" and "located in Yangyang,
# Gangwon-do" are the same answer, because most words match. The strict rule compares only
# the specific words of each answer (not filler, not words from the question): two answers
# CONTRADICT when each names something the other does not (Gangneung vs Yangyang). A less
# specific answer ("in Gangwon-do") does not contradict a more specific one.
FILLER = set("""yes no not the a an is was are were be been it its this that these those of in on at
to for by with from and or but as also actually located situated called known named which who what
where when i think believe am sure answer correct currently current now still there here has have had
he she they his her their s based found lies part""".split())


def _key(text: str, question: str = "") -> set[str]:
    q = set(_normalise(question).split())
    return {w for w in _normalise(text).split() if w not in FILLER and w not in q}


def _tok_eq(a: str, b: str) -> bool:
    return a == b or (len(a) >= 4 and len(b) >= 4 and SequenceMatcher(None, a, b).ratio() >= 0.85)


def contradicts(a: str, b: str, question: str = "") -> bool:
    ka, kb = _key(a, question), _key(b, question)
    if not ka or not kb:
        return not _same(a, b)
    extra_a = {w for w in ka if not any(_tok_eq(w, x) for x in kb)}
    extra_b = {w for w in kb if not any(_tok_eq(w, x) for x in ka)}
    return bool(extra_a and extra_b)


def judge_strict(answers: list[str], question: str = "") -> dict:
    """KNOWS only if no answer says "I don't know" and no two answers contradict.
    Used with the memory answer + the samples, so the answer the user would get is
    itself checked against the samples."""
    said_idk = sum(bool(IDK.search(a)) for a in answers)
    pairs = list(combinations(answers, 2))
    clashes = [(a, b) for a, b in pairs if contradicts(a, b, question)]
    return {"answers": answers, "agreement": round(1 - len(clashes) / len(pairs), 2),
            "said_dont_know": said_idk, "contradictions": len(clashes),
            "knows": said_idk == 0 and not clashes}


def _load_cache() -> dict:
    return json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}


def _save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def cached(question: str, model: str | None = None) -> list[str]:
    """Saved samples only (no AI call); [] if none."""
    backend, model = llm.backend(), model or llm.model_name()
    cache = _load_cache()
    for key in (f"{backend}::{model}::{question}",
                f"{backend}::{question}" if model == "llama3.1:8b" else None):
        if key and key in cache:
            return cache[key]
    return []


def samples(question: str, n: int = SAMPLES) -> list[str]:
    """At least n sampled answers to the question (cached; only missing ones are generated)."""
    backend, model = llm.backend(), llm.model_name()
    cache = _load_cache()
    key = f"{backend}::{model}::{question}"
    old_key = f"{backend}::{question}"   # older cache entries (all made with llama3.1:8b)
    if key not in cache and old_key in cache and model == "llama3.1:8b":
        key = old_key
    have = cache.get(key, [])
    if len(have) < n:
        from concurrent.futures import ThreadPoolExecutor
        missing = n - len(have)
        with ThreadPoolExecutor(missing) as pool:   # Ollama answers them in parallel
            new = list(pool.map(lambda _: llm.generate(PROMPT.format(q=question),
                                                       temperature=1.0, max_tokens=40),
                                range(missing)))
        cache = _load_cache()
        cache[key] = cache.get(key, have)[:len(have)] + new
        _save_cache(cache)
        have = cache[key]
    return have[:n]


def check(question: str) -> dict:
    """Ask the model SAMPLES times and decide whether it knows the answer."""
    return judge(samples(question, SAMPLES))


def check_strict(question: str, memory_answer: str) -> dict:
    """The memory answer + SAMPLES samples, no contradictions allowed."""
    return judge_strict([memory_answer] + samples(question, SAMPLES), question)


def check_cheap(question: str, memory_answer: str) -> dict:
    """Cheaper Check 2: compare the memory answer (which is needed anyway) with ONE sample.
    2 answers instead of 3 samples + the memory answer: one AI call instead of three."""
    return judge([memory_answer] + samples(question, 1))


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "Who wrote the Swahili novel Kufa Kuzikana?"
    r = check(q)
    print(f"Question: {q}")
    for i, a in enumerate(r["answers"], 1):
        print(f"  try {i}: {a}")
    print(f"Agreement: {r['agreement']:.0%}  ->  {'KNOWS IT' if r['knows'] else 'UNSURE'}")
