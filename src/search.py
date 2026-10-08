"""Search step: look a question up on Wikipedia (free, no API key).

Used when the router decides to search first.
    python -m src.search "first Kenyan woman PhD"

Note: Wikipedia is good for facts the AI never learned (incomplete knowledge)
and for things that change slowly (who leads a company). It does NOT have
real-time data such as prices or weather; those need a live web search
(e.g. Claude's web search tool, see src/claude_answer.py).

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
HEADERS = {"User-Agent": "TemporalRiskRouter/1.0 (Kyungdong University research project; https://github.com/abdulkarimali0001) python-urllib"}

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
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == tries - 1:
                raise
            wait = int(e.headers.get("Retry-After") or 0) or 10 * (attempt + 1)
            print(f"   (Wikipedia asked us to slow down - waiting {wait}s)", flush=True)
            time.sleep(min(wait, 60))
        except (urllib.error.URLError, TimeoutError, OSError) as e:  # network hiccup: retry
            if attempt == tries - 1:
                raise
            print(f"   (network problem: {e} - retrying)", flush=True)
            time.sleep(5 * (attempt + 1))


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
    overlap = lambda t: len(q & set(re.findall(r"[\w'-]+", t.lower())))
    # small bonus for paragraphs that mention recent years, so newer information is kept
    recent = {str(y) for y in range(date.today().year - 2, date.today().year + 1)}
    bonus = lambda t: 1 if recent & set(re.findall(r"\b\d{4}\b", t)) else 0
    scored = sorted(enumerate(paras), key=lambda ip: (-(overlap(ip[1]) + bonus(ip[1])), ip[0]))
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


# ---------------------------------------------------------------------------
# Improved retrieval (used by the pipeline)
#
# The first version read only the plain text of each page ("extracts"), which
# drops infoboxes and tables - exactly where current facts live
# ("CEO: ...", "Population: ...", lists of records). It also kept only a few
# paragraphs per page. This version:
#   1. searches with several queries and merges the pages found,
#   2. reads each FULL page including infobox and tables,
#   3. splits pages into short passages and ranks them with BM25
#      (+ a small bonus for recent years and for the top of the page),
#   4. gives the model the best passages from all pages together.
# ---------------------------------------------------------------------------
import math
from collections import Counter
from html.parser import HTMLParser

PAGE_CACHE_PATH = ROOT / "results" / "page_cache.json"
SKIP_SECTIONS = {"references", "see also", "external links", "notes", "further reading",
                 "bibliography", "sources", "citations", "footnotes"}
MAX_PAGE_CHARS = 80000
PASSAGE_CHARS = 450
CONTEXT_CHARS = 5000


class _WikiText(HTMLParser):
    """Wikipedia HTML -> plain text lines; table rows become 'cell | cell'."""
    SKIP_TAGS = {"script", "style", "sup", "math", "figure"}
    SKIP_CLASSES = ("navbox", "reflist", "references", "mw-editsection", "hatnote", "metadata",
                    "noprint", "shortdescription", "sidebar", "toc", "mw-empty-elt", "reference")
    BLOCKS = {"p", "li", "dd", "dt", "h1", "h2", "h3", "h4", "h5", "caption", "div", "blockquote"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.buf, self.row, self.cell = [], [], None, None
        self.skip_depth, self.stack, self.heading, self.in_heading = 0, [], "", False
        self.skip_section = False

    def handle_starttag(self, tag, attrs):
        if tag in ("br", "hr", "img", "meta", "link", "input", "wbr"):
            if tag == "br" and self.skip_depth == 0:
                if self.cell is not None:
                    self.cell.append("; ")
                else:
                    self._flush()
            return
        cls = dict(attrs).get("class") or ""
        skip = self.skip_depth > 0 or tag in self.SKIP_TAGS or any(c in cls for c in self.SKIP_CLASSES)
        self.stack.append((tag, skip))
        if skip:
            self.skip_depth += 1
            return
        if tag in ("h2", "h3"):
            self._flush()
            self.in_heading = True
        elif tag == "tr":
            self._flush()
            self.row = []
        elif tag in ("td", "th") and self.row is not None:
            self.cell = []
        elif tag in self.BLOCKS:
            self._flush()

    def handle_endtag(self, tag):
        if tag in ("br", "hr", "img", "meta", "link", "input", "wbr"):
            return
        # pop to the matching tag (HTML can be sloppy)
        while self.stack:
            t, skip = self.stack.pop()
            if skip:
                self.skip_depth -= 1
            if t == tag:
                break
        if self.skip_depth > 0:
            return
        if tag in ("h2", "h3") and self.in_heading:
            self.in_heading = False
            title = " ".join("".join(self.buf).split())
            self.buf = []
            if tag == "h2":
                self.skip_section = title.lower() in SKIP_SECTIONS
            if not self.skip_section and title:
                self.heading = title
                self.lines.append(f"## {title}")
        elif tag in ("td", "th") and self.cell is not None:
            self.row.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.row is not None:
            cells = [c for c in self.row if c]
            if cells and not self.skip_section:
                self.lines.append(" | ".join(cells))
            self.row = None
        elif tag in self.BLOCKS:
            self._flush()

    def handle_data(self, data):
        if self.skip_depth > 0:
            return
        (self.cell if self.cell is not None else self.buf).append(data)

    def _flush(self):
        text = " ".join("".join(self.buf).split())
        self.buf = []
        if text and not self.skip_section:
            self.lines.append(text)


def html_to_text(html: str) -> str:
    parser = _WikiText()
    parser.feed(html)
    parser._flush()
    return "\n".join(parser.lines)


def _load(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def find_titles(query: str, k: int = 3, lang: str = "en") -> list[str]:
    cache = _load_cache()
    key = f"titles::{lang}::{k}::{query}"
    if key not in cache:
        params = {"action": "query", "list": "search", "srsearch": query, "srlimit": k,
                  "format": "json", "formatversion": 2}
        data = _get(API.format(lang=lang) + "?" + urllib.parse.urlencode(params))
        cache[key] = [h["title"] for h in data.get("query", {}).get("search", [])]
        _save_cache(cache)
    return cache[key]


def fetch_page(title: str, lang: str = "en") -> dict | None:
    """Full page text, including infobox and tables. Cached in results/page_cache.json."""
    cache = _load(PAGE_CACHE_PATH)
    key = f"{lang}::{title}"
    if key not in cache:
        params = {"action": "parse", "page": title, "prop": "text", "redirects": 1,
                  "disableeditsection": 1, "format": "json", "formatversion": 2}
        try:
            data = _get(API.format(lang=lang) + "?" + urllib.parse.urlencode(params))
        except Exception as e:
            print(f"   (could not read page {title}: {e})", flush=True)
            return None
        parsed = data.get("parse") or {}
        real = parsed.get("title", title)
        cache[key] = {"title": real,
                      "url": f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(real.replace(' ', '_'))}",
                      "text": html_to_text(parsed.get("text", ""))[:MAX_PAGE_CHARS],
                      "retrieved": date.today().isoformat()}
        PAGE_CACHE_PATH.parent.mkdir(exist_ok=True)
        PAGE_CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    return cache[key]


def _tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[\w'-]+", text.lower()) if w not in STOPWORDS]


def passages(page: dict) -> list[dict]:
    """Split a page into short passages; each remembers its section heading."""
    out, buf, heading = [], [], ""
    for line in page["text"].split("\n"):
        if line.startswith("## "):
            if buf:
                out.append({"heading": heading, "text": "\n".join(buf)})
                buf = []
            heading = line[3:]
            continue
        if buf and len("\n".join(buf)) + len(line) > PASSAGE_CHARS:
            out.append({"heading": heading, "text": "\n".join(buf)})
            buf = []
        buf.append(line[:PASSAGE_CHARS * 2])
    if buf:
        out.append({"heading": heading, "text": "\n".join(buf)})
    for i, p in enumerate(out):
        p.update(title=page["title"], url=page["url"], retrieved=page["retrieved"], position=i)
    return out


def rank(question: str, cands: list[dict], k1: float = 1.5, b: float = 0.75) -> list[dict]:
    """BM25 score of every passage against the question (+ small bonuses)."""
    if not cands:
        return []
    docs = [_tokens(f"{c['title']} {c['heading']} {c['text']}") for c in cands]
    avg = sum(map(len, docs)) / len(docs) or 1
    df = Counter(w for d in docs for w in set(d))
    q = set(_tokens(question))
    recent = {str(y) for y in range(date.today().year - 2, date.today().year + 1)}
    for c, d in zip(cands, docs):
        tf = Counter(d)
        score = sum(math.log(1 + (len(docs) - df[w] + 0.5) / (df[w] + 0.5)) *
                    tf[w] * (k1 + 1) / (tf[w] + k1 * (1 - b + b * len(d) / avg)) for w in q if tf[w])
        if recent & set(re.findall(r"\b\d{4}\b", c["text"])):
            score += 0.5                      # newer information
        if c["position"] < 2:
            score += 0.5                      # infobox / opening of the page
        c["score"] = score
    return sorted(cands, key=lambda c: -c["score"])


def retrieve(question: str, queries: list[str], k: int = 3, lang: str = "en",
             budget: int = CONTEXT_CHARS) -> list[dict]:
    """Best passages from all pages found by all queries, grouped per page:
    [{title, url, text, retrieved}] (same shape as search())."""
    titles = []
    for q in queries:
        try:
            titles += find_titles(q, k, lang)
        except Exception as e:
            print(f"   (search failed for '{q}': {e})", flush=True)
    pages = [p for p in (fetch_page(t, lang) for t in dict.fromkeys(titles)) if p and p["text"]]
    chosen, used = [], 0
    for c in rank(question, [x for p in pages for x in passages(p)]):
        if used + len(c["text"]) > budget:
            continue
        chosen.append(c)
        used += len(c["text"])
        if used > budget - 150:
            break
    grouped = {}
    for c in chosen:                       # keep page order by best passage
        g = grouped.setdefault(c["title"], {"title": c["title"], "url": c["url"],
                                             "retrieved": c["retrieved"], "parts": []})
        g["parts"].append(c)
    out = []
    for g in grouped.values():
        parts = sorted(g.pop("parts"), key=lambda c: c["position"])
        g["text"] = "\n...\n".join((f"({c['heading']}) " if c["heading"] else "") + c["text"] for c in parts)
        out.append(g)
    return out


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "first Kenyan woman PhD"
    for i, p in enumerate(search(q), 1):
        print(f"[{i}] {p['title']}  {p['url']}\n    {p['text'][:200]}...\n")
