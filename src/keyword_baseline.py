"""Keyword baseline for Check 1 (does the answer change over time?).

A simple rule-based method used only for comparison in src/evaluate.py:
it looks for time words such as "current", "latest" or "price".
Its weakness: questions with no time word, such as "Who runs Samsung?".
"""
import re

LABELS = ["LOW", "AMBIGUOUS", "HIGH"]

# Words that suggest the answer changes often -> HIGH
HIGH_PATTERNS = [
    r"\bcurrent(ly)?\b", r"\blatest\b", r"\btoday\b", r"\bnow\b", r"\bthis (week|month|year)\b",
    r"\bprice\b", r"\bexchange rate\b", r"\bweather\b", r"\bdeadline\b", r"\bCEO\b",
    r"\bpresident\b", r"\bnewest\b", r"\brecent(ly)?\b", r"\b20(2[5-9])\b", r"\bscore\b", r"\bstill\b",
]

# Words that suggest the answer changes sometimes -> AMBIGUOUS
AMBIGUOUS_PATTERNS = [
    r"\bpolicy\b", r"\brequire(d|ments?)?\b", r"\bfee\b", r"\btuition\b", r"\bversion\b",
    r"\brules?\b", r"\blaw\b", r"\bcurriculum\b", r"\bschedule\b", r"\bbest\b",
]


def route(question: str) -> str:
    """Return LOW, AMBIGUOUS or HIGH for one question."""
    if any(re.search(p, question, re.IGNORECASE) for p in HIGH_PATTERNS):
        return "HIGH"
    if any(re.search(p, question, re.IGNORECASE) for p in AMBIGUOUS_PATTERNS):
        return "AMBIGUOUS"
    return "LOW"
