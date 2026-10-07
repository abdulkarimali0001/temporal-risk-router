"""The full system: router + search + answer, all with a free local AI.

    question
       -> router (does the answer change? does the AI know it?)
       -> answer from memory / answer + warning / search Wikipedia first
       -> final answer (+ source link when searched)

Ask one question:
    python -m src.full_system "Who was the first Kenyan woman to earn a PhD?"
Run the class demo (9 questions, saved to results/full_system_demo.txt):
    python -m src.full_system --demo

Uses CONFIDENCE_BACKEND (ollama or claude) from .env for the AI.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from src import confidence, router_ml, two_signal, web_search

ROOT = Path(__file__).resolve().parent.parent

WARNING = "(Note: this can change over time. Please check an official source.)"
NOT_FOUND = "I could not find this in the sources I searched, so I won't guess."

ANSWER_PROMPT = "Answer the question in one or two short sentences.\n\nQuestion: {q}"
KEYWORD_PROMPT = ("Write a short search query (2 to 6 words) for looking up this question "
                  "on Wikipedia. Reply with the query only.\n\nQuestion: {q}")
SOURCE_PROMPT = """Answer the question using ONLY the sources below.
Write a full sentence and cite the source number like [1]. If the sources do not contain the answer,
reply exactly: NOT FOUND

Sources:
{sources}

Question: {q}
Answer:"""

DEMO = [
    "What is the capital of Australia?",
    "Who developed the theory of relativity?",
    "What is the tuition fee for the Smart Computing department?",
    "Who was the first Kenyan woman to earn a PhD?",
    "Who wrote the Swahili novel Kufa Kuzikana?",
    "Who designed the Sebeolsik Hangul keyboard layout?",
    "Who is the CEO of Naver?",
    "Who is the prime minister of Japan?",
    "What is the price of Bitcoin?",
]


def generate(prompt: str, temperature: float = 0.0) -> str:
    """One call to the AI (same backend as the confidence check)."""
    confidence.load_env()
    backend = os.getenv("CONFIDENCE_BACKEND", "claude")
    if backend == "ollama":
        import json
        import urllib.request
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        body = json.dumps({"model": confidence._ollama_model(host), "prompt": prompt,
                           "stream": False, "options": {"temperature": temperature}}).encode()
        req = urllib.request.Request(f"{host}/api/generate", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.load(r)["response"].strip()
    import anthropic
    msg = anthropic.Anthropic().messages.create(
        model=os.getenv("CONFIDENCE_MODEL", "claude-haiku-4-5-20251001"), max_tokens=300,
        temperature=temperature, messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in msg.content if b.type == "text").strip()


def search_query(question: str) -> str:
    try:
        q = generate(KEYWORD_PROMPT.format(q=question)).splitlines()[0].strip(' "\'')
        if 1 <= len(q.split()) <= 8:
            return q
    except Exception:
        pass
    return web_search.keywords(question)


def ask(question: str, model=None) -> dict:
    route = two_signal.route(question, model=model)
    out = {"question": question, "band": route["band"], "confident": route["confident"],
           "action": route["action"], "reason": route["reason"], "query": "", "sources": []}

    if route["action"] in ("answer", "warn"):
        answer = generate(ANSWER_PROMPT.format(q=question))
        if route["action"] == "warn":
            answer += " " + WARNING
        out["answer"] = answer
        return out

    # action == "search": try the AI's search words first, then simple keywords
    queries = [search_query(question), web_search.keywords(question)]
    answer, pages = NOT_FOUND, []
    for query in dict.fromkeys(queries):          # skip duplicates, keep order
        found = web_search.search(query, question=question)
        if not found:
            continue
        out["query"], pages = query, found
        answer = answer_from_sources(question, found)
        if answer != NOT_FOUND:
            break
    out["sources"] = pages
    out["answer"] = answer
    return out


def answer_from_sources(question: str, pages: list[dict]) -> str:
    numbered = "\n\n".join(f"[{i}] {p['title']}: {p['text']}" for i, p in enumerate(pages, 1))
    for _ in range(2):  # retry once if the AI replies with only a citation like "[1]"
        answer = generate(SOURCE_PROMPT.format(sources=numbered, q=question))
        if "NOT FOUND" in answer.upper():
            return NOT_FOUND
        if len(re.sub(r"\[\d+\]|\W", "", answer)) >= 3:
            return answer
    return NOT_FOUND


def show(r: dict) -> str:
    names = {"LOW": "LOW", "AMBIGUOUS": "MAYBE", "HIGH": "HIGH"}
    conf = "skipped" if r["confident"] is None else ("knows it" if r["confident"] else "unsure")
    lines = [f"Q: {r['question']}",
             f"   Check 1 (changes?): {names[r['band']]}   Check 2 (AI knows?): {conf}",
             f"   Decision: {two_signal.ACTIONS[r['action']]}"]
    if r["action"] == "search":
        lines.append(f"   Searched Wikipedia for: \"{r['query']}\"")
    lines.append(f"   Answer: {r['answer']}")
    if r["sources"]:
        lines.append("   Sources:" if r["answer"] != NOT_FOUND else "   Pages checked (answer not in them):")
    for i, p in enumerate(r["sources"], 1):
        lines.append(f"   [{i}] {p['title']} - {p['url']} (retrieved {p['retrieved']})")
    return "\n".join(lines)


def main():
    args = sys.argv[1:]
    model = router_ml.load()
    if args and args[0] == "--demo":
        confidence.load_env()
        backend = os.getenv("CONFIDENCE_BACKEND", "claude")
        header = f"FULL SYSTEM DEMO - Group 4 (AI backend: {backend})"
        if backend == "ollama":
            header += f", model: {confidence._ollama_model(os.getenv('OLLAMA_HOST', 'http://localhost:11434'))}"
        blocks = [header, "=" * len(header)]
        out = ROOT / "results" / "full_system_demo.txt"
        out.parent.mkdir(exist_ok=True)
        for i, q in enumerate(DEMO, 1):
            print(f"[{i}/{len(DEMO)}] Working on: {q}", flush=True)
            try:
                block = show(ask(q, model))
            except Exception as e:  # one failing question should not stop the demo
                block = f"Q: {q}\n   ERROR: {type(e).__name__}: {e}"
            print(block + "\n", flush=True)
            blocks.append(block)
            # save after every question, so progress is kept if the run stops
            out.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")
        print("Saved: results/full_system_demo.txt")
    else:
        q = " ".join(args) or "Who was the first Kenyan woman to earn a PhD?"
        print(show(ask(q, model)))


if __name__ == "__main__":
    main()
