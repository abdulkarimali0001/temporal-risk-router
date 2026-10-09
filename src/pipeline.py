"""The full pipeline: router -> (search) -> answer.

    question
       -> router: does the answer change? does the AI know it?
       -> answer from memory | answer + warning | search Wikipedia first
       -> final answer, with source links when it searched

If the sources do not contain the answer, the pipeline says so instead of guessing.

Ask one question:
    python -m src.pipeline "Who was the first Kenyan woman to earn a PhD?"
"""
from __future__ import annotations

import re
import sys
from datetime import date

from src import language, llm, router, search

WARNING = "(Note: this can change over time. Please check an official source.)"
NOT_FOUND = "I could not find this in the sources I searched, so I won't guess."

ANSWER_PROMPT = ("Today's date is {today}. Answer the question in one or two short sentences."
                 "{lang}\n\nQuestion: {q}")
KOREAN = " Answer in Korean."
QUERY_PROMPT = ("Write a short search query (2 to 6 words) for looking up this question "
                "on {wiki}. Reply with the query only.\n\nQuestion: {q}")
SOURCE_PROMPT = """Today's date is {today}. Answer the question using ONLY the sources below.
Write a full sentence and cite the source number like [1].
The answer should be correct as of today: if the sources mention several people, values or dates,
use the MOST RECENT one, and do not give an answer the sources describe as former or past.
Tables are written as "cell | cell". If the sources contain the answer, or enough to work it out,
answer. Only if they do not contain it at all, reply exactly: NOT FOUND
{lang}
Sources:
{sources}

Question: {q}
Answer:"""


def search_query(question: str, wiki: str = "Wikipedia") -> str:
    """Ask the AI for good search words; fall back to simple keywords."""
    try:
        q = llm.generate(QUERY_PROMPT.format(q=question, wiki=wiki)).splitlines()[0].strip(' "\'')
        if 1 <= len(q.split()) <= 8:
            return q
    except Exception:
        pass
    return search.keywords(question)


def answer_from_sources(question: str, pages: list[dict]) -> str:
    numbered = "\n\n".join(f"[{i}] {p['title']}: {p['text']}" for i, p in enumerate(pages, 1))
    for _ in range(2):  # retry once if the AI replies with only a citation like "[1]"
        answer = llm.generate(SOURCE_PROMPT.format(
            sources=numbered, q=question, today=date.today().isoformat(),
            lang="The question is in Korean: answer in Korean.\n" if language.is_korean(question) else ""))
        if "NOT FOUND" in answer.upper():
            return NOT_FOUND
        if len(re.sub(r"\[\d+\]|\W", "", answer)) >= 3:
            return answer
    return NOT_FOUND


def answer_from_memory(question: str) -> str:
    """The AI answers alone, with no search."""
    return llm.generate(ANSWER_PROMPT.format(q=question, today=date.today().isoformat(),
                                             lang=KOREAN if language.is_korean(question) else ""))


def gather_sources(question: str, web: bool | None = None) -> list[dict]:
    """Fast source search for the demo app: no AI calls, so it can run while the AI is
    busy answering. Keywords on Wikipedia (Korean Wikipedia too for Korean questions)
    plus the question itself on the live web."""
    from concurrent.futures import ThreadPoolExecutor
    web = search.web_enabled() if web is None else web
    queries = [(search.keywords(question), "ko" if language.is_korean(question) else "en")]
    with ThreadPoolExecutor(1) as pool:
        web_job = pool.submit(search.web_search, question) if web else None
        if language.is_korean(question):
            queries.append((search.keywords(language.to_english(question)), "en"))
        web_pages = web_job.result() if web_job else []
    return search.retrieve(question, queries, extra_pages=web_pages)


def source_prompt(question: str, pages: list[dict]) -> str:
    numbered = "\n\n".join(f"[{i}] {p['title']}: {p['text']}" for i, p in enumerate(pages, 1))
    return SOURCE_PROMPT.format(
        sources=numbered, q=question, today=date.today().isoformat(),
        lang="The question is in Korean: answer in Korean.\n" if language.is_korean(question) else "")


def memory_prompt(question: str) -> str:
    return ANSWER_PROMPT.format(q=question, today=date.today().isoformat(),
                                lang=KOREAN if language.is_korean(question) else "")


def answer_with_search(question: str, web: bool | None = None, korean_wiki: bool = True) -> dict:
    """Search, keep the best passages from all sources, and answer only from them.
      - English Wikipedia: the AI's search words + simple keywords
      - Korean question: also Korean Wikipedia, and the English translation on English Wikipedia
      - web=True (default when a Tavily key is set): live web results ranked together with Wikipedia"""
    from concurrent.futures import ThreadPoolExecutor
    web = search.web_enabled() if web is None else web
    with ThreadPoolExecutor(1) as pool:
        web_job = pool.submit(search.web_search, question) if web else None   # runs meanwhile
        queries = [(search_query(question), "en"), (search.keywords(question), "en")]
        if language.is_korean(question):
            english = language.to_english(question)
            queries = [(search.keywords(english), "en"), (search_query(english), "en")]
            if korean_wiki:
                queries += [(search_query(question, "Korean Wikipedia (in Korean)"), "ko"),
                            (search.keywords(question), "ko")]
        queries = list(dict.fromkeys(queries))
        web_pages = web_job.result() if web_job else []
    pages = search.retrieve(question, queries, extra_pages=web_pages)
    answer = answer_from_sources(question, pages) if pages else NOT_FOUND
    return {"answer": answer, "query": " / ".join(f"{q} ({l})" for q, l in queries)
            + (" + web" if web_pages else ""), "sources": pages}


def ask(question: str, model=None) -> dict:
    route = router.route(question, model=model)
    out = {**route, "query": "", "sources": []}

    if route["action"] in ("answer", "warn"):
        answer = answer_from_memory(question)
        out["answer"] = answer + (" " + WARNING if route["action"] == "warn" else "")
        return out

    out.update(answer_with_search(question))
    return out


def show(r: dict) -> str:
    knows = "skipped" if r["knows"] is None else ("knows it" if r["knows"] else "unsure")
    lines = [f"Q: {r['question']}",
             f"   Check 1 (changes?): {router.GROUP_NAMES[r['group']]}   Check 2 (AI knows?): {knows}",
             f"   Decision: {router.ACTIONS[r['action']]}"]
    if r["action"] == "search":
        lines.append(f"   Searched Wikipedia for: \"{r['query']}\"")
    lines.append(f"   Answer: {r['answer']}")
    if r["sources"]:
        lines.append("   Sources:" if r["answer"] != NOT_FOUND else "   Pages checked (answer not in them):")
    for i, p in enumerate(r["sources"], 1):
        lines.append(f"   [{i}] {p['title']} - {p['url']} (retrieved {p['retrieved']})")
    return "\n".join(lines)


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "Who was the first Kenyan woman to earn a PhD?"
    print(show(ask(q)))
