"""Search step: look a question up on Wikipedia (free, no API key).

Used when the router decides "search the web first".
    python -m src.web_search "first Kenyan woman PhD"

Note: Wikipedia is good for facts the AI never learned (incomplete knowledge)
and for things that change slowly (who leads a company). It does NOT have
real-time data such as prices or weather; those need a live web search
(e.g. Claude's web search tool, see src/answer.py).

Results are cached in results/search_cache.json so demos work offline.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE_PATH = ROOT / "results" / "search_cache.json"
API = "https://{lang}.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "Group4-TemporalRiskRouter/1.0 (Kyungdong University student project)"}

STOPWORDS = set("""a an the is was were are be been who what when where which why how
do does did of in on at to for by with from and or this that these those it its
first ever currently current now today latest new newest""".split()) - {"first", "current", "latest", "newest"}


def keywords(question: str) -> str:
    """Turn a question into a short search query (simple fallback)."""
    words = re.findall(r"[\w'-]+", question.lower())
    return " ".join(w for w in words if w not in STOPWORDS) or question


def _get(url: str, tries: int = 5) -> dict:
    """Polite request: short pause before each call, and wait-and-retry if
    Wikipedia says "429 Too Many Requests"."""
    import time
    import urllib.error
    for attempt in range(tries):
        time.sleep(1.0)
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 10 * (attempt + 1)
            print(f"   (Wikipedia asked us to slow down - waiting {wait}s)", flush=True)
            time.sleep(min(wait, 60))


def _load_cache() -> dict:
    return json.loads(CACHE_PATH.read_text()) if CACHE_PATH.exists() else {}


def _save_cache(cache: dict):
    CACHE_PATH.parent.mkdir(exist_ok=True)
    CACHE_PATH.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def best_passages(text: str, question: str, limit: int = 2500) -> str:
    """Keep the paragraphs that share the most words with the question.
    (Reading only the first paragraph missed answers further down the page.)"""
    paras = [p.strip() for p in text.split("\n") if len(p.strip()) > 40]
    if not paras:
        return text[:limit]
    q = set(keywords(question).split())
    scored = sorted(enumerate(paras),
                    key=lambda ip: (-len(q & set(re.findall(r"[\w'-]+", ip[1].lower()))), ip[0]))
    overlap = lambda t: len(q & set(re.findall(r"[\w'-]+", t.lower())))
    keep = [i for i, t in scored[:6] if overlap(t) > 0] if q else list(range(len(paras)))
    keep = sorted(set(keep) | {0})          # always keep the opening paragraph
    out = ""
    for i in keep:
        if len(out) + len(paras[i]) > limit:
            break
        out += paras[i] + "\n"
    return out.strip() or paras[0][:limit]


def search(query: str, k: int = 3, lang: str = "en", question: str = "") -> list[dict]:
    """Return up to k Wikipedia pages: [{title, url, text, retrieved}]."""
    cache = _load_cache()
    key = f"full2::{lang}::{k}::{query}::{question}"
    if key in cache:
        return cache[key]

    base = API.format(lang=lang)
    params = {"action": "query", "list": "search", "srsearch": query, "srlimit": k,
              "format": "json", "formatversion": 2}
    hits = _get(base + "?" + urllib.parse.urlencode(params))["query"]["search"]
    titles = [h["title"] for h in hits]
    pages = []
    for t in titles:  # one request per page: Wikipedia returns full text for only 1 page per request
        params = {"action": "query", "prop": "extracts|info", "inprop": "url",
                  "explaintext": 1, "redirects": 1, "titles": t,
                  "format": "json", "formatversion": 2}
        for p in _get(base + "?" + urllib.parse.urlencode(params))["query"]["pages"]:
            if p.get("extract"):
                pages.append({"title": p["title"], "url": p.get("fullurl", ""),
                              "text": best_passages(p["extract"], question or query),
                              "retrieved": date.today().isoformat()})
    cache[key] = pages
    _save_cache(cache)
    return pages


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "first Kenyan woman PhD"
    for i, p in enumerate(search(q), 1):
        print(f"[{i}] {p['title']}  {p['url']}\n    {p['text'][:200]}...\n")
