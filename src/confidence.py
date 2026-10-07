"""Signal 2: does the AI actually know the answer? (self-consistency)

Idea (from the adaptive-retrieval research, e.g. Moskvoretskii et al., ACL 2025):
ask the model the SAME question several times WITHOUT web search.
  - If the answers agree      -> the model is CONFIDENT (it knows it)
  - If the answers disagree,
    or it says "I don't know" -> the model is UNSURE (knowledge is incomplete)

Two backends, choose with CONFIDENCE_BACKEND in .env:
  claude  - Claude API (needs ANTHROPIC_API_KEY, small cost per question)
  ollama  - free local model via Ollama (https://ollama.com, must be running)

Every answer is saved in results/confidence_cache.json, so re-running
(or demoing in class) costs nothing and works without internet.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request
from difflib import SequenceMatcher
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "results" / "confidence_cache.json"

SAMPLES = 3                # how many times we ask the same question
AGREEMENT_NEEDED = 0.6     # share of answer pairs that must match to be "confident"

PROMPT = ("Answer the question in at most 8 words. No explanation. "
          "If you do not know, reply exactly: I don't know.\n\nQuestion: {q}")

IDK = re.compile(r"\b(i don'?t know|not sure|unknown|cannot (determine|answer)|no information)\b", re.I)


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


# ---------------------------------------------------------------- backends
def ask_claude(question: str) -> str:
    import anthropic
    client = anthropic.Anthropic()
    msg = client.messages.create(
        model=os.getenv("CONFIDENCE_MODEL", "claude-haiku-4-5-20251001"),
        max_tokens=40,
        temperature=1.0,  # allow variation, so disagreement can show up
        messages=[{"role": "user", "content": PROMPT.format(q=question)}],
    )
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def _ollama_model(host: str) -> str:
    wanted = os.getenv("OLLAMA_MODEL")
    if wanted:
        return wanted
    with urllib.request.urlopen(f"{host}/api/tags", timeout=10) as r:
        models = [m["name"] for m in json.load(r).get("models", [])]
    if not models:
        raise SystemExit("Ollama has no models. Run e.g.:  ollama pull llama3.2")
    return models[0]


def ask_ollama(question: str) -> str:
    host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    body = json.dumps({"model": _ollama_model(host), "prompt": PROMPT.format(q=question),
                       "stream": False, "options": {"temperature": 1.0}}).encode()
    req = urllib.request.Request(f"{host}/api/generate", data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)["response"].strip()


BACKENDS = {"claude": ask_claude, "ollama": ask_ollama}


# ---------------------------------------------------------------- scoring
def _normalise(text: str) -> str:
    text = text.lower()
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
    confident = said_idk == 0 and score >= AGREEMENT_NEEDED
    return {"answers": answers, "agreement": round(score, 2),
            "said_dont_know": said_idk, "confident": confident}


# ---------------------------------------------------------------- main API
def _load_cache() -> dict:
    return json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}


def _save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def check(question: str, backend: str | None = None) -> dict:
    """Ask the model SAMPLES times and decide whether it is confident."""
    load_env()
    backend = backend or os.getenv("CONFIDENCE_BACKEND", "claude")
    cache = _load_cache()
    key = f"{backend}::{question}"
    if key not in cache:
        if backend == "claude" and not os.getenv("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY is not set (add it to .env), "
                             "or use CONFIDENCE_BACKEND=ollama")
        ask = BACKENDS[backend]
        cache[key] = [ask(question) for _ in range(SAMPLES)]
        _save_cache(cache)
    result = judge(cache[key])
    result["backend"] = backend
    return result


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "What is the capital of Kenya?"
    r = check(q)
    print(f"Question: {q}")
    for i, a in enumerate(r["answers"], 1):
        print(f"  answer {i}: {a}")
    print(f"Agreement: {r['agreement']:.0%}  ->  {'CONFIDENT' if r['confident'] else 'UNSURE'}")
