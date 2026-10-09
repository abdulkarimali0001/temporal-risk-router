"""Non-English questions: Korean and Swahili.

The time check was trained on English questions, so a Korean or Swahili question is
first translated to English for Check 1. Search also uses that language's Wikipedia,
and the answer is written in the question's language. Translations are cached in
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


NAMES = {"en": "English", "ko": "Korean", "sw": "Swahili"}
# Swahili has no special letters, so it is recognised by its common words
SW_QUESTION = {"nani", "nini", "gani", "wapi", "lini", "ngapi", "je", "yupi", "ipi", "upi", "kipi", "lipi"}
SW_WORDS = SW_QUESTION | set("""ni ya wa za la cha kwa katika mji mkuu nchi rais aliandika
iliandikwa iko ilikuwa alikuwa kubwa zaidi sasa mwaka huu hii hiyo kitabu riwaya mwandishi
ziwa mlima mto sarafu lugha kiongozi waziri timu ligi mshindi""".split())


def is_korean(text: str) -> bool:
    return bool(HANGUL.search(text or ""))


def detect(text: str) -> str:
    """'ko', 'sw' or 'en'."""
    if is_korean(text):
        return "ko"
    words = re.findall(r"[a-z']+", (text or "").lower())
    if sum(w in SW_WORDS for w in words) >= 2 and any(w in SW_QUESTION for w in words):
        return "sw"
    return "en"


def name(text: str) -> str:
    """Language name of a question, e.g. 'Korean'."""
    return NAMES[detect(text)]


def to_english(question: str) -> str:
    if detect(question) == "en":
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
