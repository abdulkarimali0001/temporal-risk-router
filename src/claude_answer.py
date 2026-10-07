"""Optional: answer with Claude and its live web search tool, instead of Wikipedia.

Same router, but when it decides to search, Claude searches the live web,
which also covers real-time questions (prices, weather, news) that Wikipedia cannot.

    python -m src.claude_answer "Who is the current CEO of Naver?"

Needs ANTHROPIC_API_KEY in .env (costs a small amount per question).
"""
from __future__ import annotations

import os
import sys

from src import llm, router

MODEL = os.getenv("CLAUDE_ANSWER_MODEL", "claude-sonnet-5-5")
WEB_SEARCH_TOOL = os.getenv("WEB_SEARCH_TOOL", "web_search_20260318")
WARNING = ("\n\n(Note: this can change over time. "
           "Please check an official, up-to-date source.)")


def ask_claude(question: str, action: str):
    import anthropic
    kwargs = dict(model=MODEL, max_tokens=1024,
                  messages=[{"role": "user", "content": question}])
    if action == "search":
        kwargs["tools"] = [{"type": WEB_SEARCH_TOOL, "name": "web_search", "max_uses": 3}]
        kwargs["tool_choice"] = {"type": "any"}  # make Claude search before answering
    response = anthropic.Anthropic().messages.create(**kwargs)

    text, sources = [], {}
    for block in response.content:
        if block.type == "text":
            text.append(block.text)
            for c in getattr(block, "citations", None) or []:
                if getattr(c, "url", None):
                    sources[c.url] = c.title
    answer = "".join(text).strip()
    if action == "warn":
        answer += WARNING
    return answer, sources


if __name__ == "__main__":
    llm.load_env()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set. Add it to .env.")
    q = " ".join(sys.argv[1:]) or "Who is the current CEO of Naver?"
    r = router.route(q)
    print(f"Decision: {router.ACTIONS[r['action']]} - {r['reason']}\n")
    answer, sources = ask_claude(q, r["action"])
    print(answer)
    if sources:
        print("\nSources:")
        for url, title in sources.items():
            print(f"  - {title}: {url}")
