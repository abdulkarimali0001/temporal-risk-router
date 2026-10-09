"""Korean (and other non-English) questions.

The time check was trained on English questions, so a Korean question is first
translated to English for Check 1. Translations are cached in
results/translate_cache.json.
"""
from __future__ import annotations

import json
import re

from src import llm
from src.llm import ROOT

CACHE = ROOT / "results" / "translate_cache.json"
HANGUL = re.compile(r"[가-힣]")
PROMPT = ("Translate this question into English. Keep names of people, places and companies "
          "in their usual English spelling. Reply with the translation only.\n\nQuestion: {q}")


def is_korean(text: str) -> bool:
    return bool(HANGUL.search(text or ""))


def to_english(question: str) -> str:
    if not is_korean(question):
        return question
    try:
        cache = json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        cache = {}
    if question not in cache:
        text = llm.generate(PROMPT.format(q=question), max_tokens=100).strip().splitlines()[0]
        cache[question] = text.strip(' "\'')
        CACHE.parent.mkdir(exist_ok=True)
        CACHE.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    return cache[question]
