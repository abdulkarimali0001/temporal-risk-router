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

from src import llm, router, search

WARNING = "(Note: this can change over time. Please check an official source.)"
NOT_FOUND = "I could not find this in the sources I searched, so I won't guess."

ANSWER_PROMPT = "Answer the question in one or two short sentences.\n\nQuestion: {q}"
QUERY_PROMPT = ("Write a short search query (2 to 6 words) for looking up this question "
                "on Wikipedia. Reply with the query only.\n\nQuestion: {q}")
SOURCE_PROMPT = """Answer the question using ONLY the sources below.
Write a full sentence and cite the source number like [1]. If the sources do not contain the answer,
reply exactly: NOT FOUND

Sources:
{sources}

Question: {q}
Answer:"""


def search_query(question: str) -> str:
    """Ask the AI for good search words; fall back to simple keywords."""
    try:
        q = llm.generate(QUERY_PROMPT.format(q=question)).splitlines()[0].strip(' "\'')
        if 1 <= len(q.split()) <= 8:
            return q
    except Exception:
        pass
    return search.keywords(question)


def answer_from_sources(question: str, pages: list[dict]) -> str:
    numbered = "\n\n".join(f"[{i}] {p['title']}: {p['text']}" for i, p in enumerate(pages, 1))
    for _ in range(2):  # retry once if the AI replies with only a citation like "[1]"
        answer = llm.generate(SOURCE_PROMPT.format(sources=numbered, q=question))
        if "NOT FOUND" in answer.upper():
            return NOT_FOUND
        if len(re.sub(r"\[\d+\]|\W", "", answer)) >= 3:
            return answer
    return NOT_FOUND


def ask(question: str, model=None) -> dict:
    route = router.route(question, model=model)
    out = {**route, "query": "", "sources": []}

    if route["action"] in ("answer", "warn"):
        answer = llm.generate(ANSWER_PROMPT.format(q=question))
        out["answer"] = answer + (" " + WARNING if route["action"] == "warn" else "")
        return out

    # search: try the AI's search words first, then simple keywords
    answer, pages = NOT_FOUND, []
    for query in dict.fromkeys([search_query(question), search.keywords(question)]):
        found = search.search(query, question=question)
        if not found:
            continue
        out["query"], pages = query, found
        answer = answer_from_sources(question, found)
        if answer != NOT_FOUND:
            break
    out["sources"], out["answer"] = pages, answer
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
