"""Router v1: rule-based Temporal-Risk Router.

Scans a question for time-sensitivity signals and returns a risk band:
LOW, AMBIGUOUS or HIGH.
"""
import re

LABELS = ["LOW", "AMBIGUOUS", "HIGH"]

# Words that strongly suggest the answer changes quickly -> search first.
HIGH_PATTERNS = [
    r"\bcurrent(ly)?\b", r"\blatest\b", r"\btoday\b", r"\bnow\b", r"\bright now\b",
    r"\bthis (week|month|year|season|morning)\b", r"\btomorrow\b", r"\byesterday\b",
    r"\blast night\b", r"\bprice\b", r"\bexchange rate\b", r"\bweather\b",
    r"\bdeadline\b", r"\bCEO\b", r"\bpresident\b", r"\bprime minister\b",
    r"\bnewest\b", r"\brecent(ly)?\b", r"\b20(2[5-9])\b", r"\bscore\b", r"\bstill\b",
    r"\bnext\b",
]

# Words that suggest the answer may change from time to time -> add a caveat.
AMBIGUOUS_PATTERNS = [
    r"\bpolicy\b", r"\brequire(d|ments?)?\b", r"\bfees?\b", r"\btuition\b",
    r"\bversion\b", r"\brules?\b", r"\blaw\b", r"\bact\b", r"\bcurriculum\b",
    r"\bschedule\b", r"\bbest\b", r"\bcost\b", r"\bsalary\b", r"\bwage\b",
    r"\bvisa\b", r"\bscholarships?\b",
]


def route(question: str) -> str:
    """Return the risk band for one question."""
    if any(re.search(p, question, re.IGNORECASE) for p in HIGH_PATTERNS):
        return "HIGH"
    if any(re.search(p, question, re.IGNORECASE) for p in AMBIGUOUS_PATTERNS):
        return "AMBIGUOUS"
    return "LOW"


if __name__ == "__main__":
    for q in ["What is photosynthesis?",
              "What is the tuition fee for Smart Computing?",
              "Who is the current CEO of Anthropic?",
              "Who runs Samsung Electronics?"]:
        print(f"{route(q):<10} {q}")
