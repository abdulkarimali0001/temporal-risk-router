"""Ask a question through the Temporal-Risk Router.

    python -m src.answer "Who is the current CEO of Anthropic?"
    python -m src.answer "What is photosynthesis?" --router v1
    python -m src.answer "Who runs Samsung?" --dry-run     (no API key needed)

LOW        -> Claude answers from memory
AMBIGUOUS  -> Claude answers from memory + a recency warning
HIGH       -> Claude must use the web search tool and cite sources

Needs ANTHROPIC_API_KEY in your environment (or in a .env file) unless --dry-run.
"""
import argparse
import os
from pathlib import Path

from src import router_rules

MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5-5")
WEB_SEARCH_TOOL = os.getenv("WEB_SEARCH_TOOL", "web_search_20260318")

CAVEAT = ("\n\n⚠ This kind of information can change. "
          "Please check an official, up-to-date source before relying on it.")


def load_env():
    env = Path(__file__).resolve().parent.parent / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def classify(question: str, router: str) -> str:
    if router == "v1":
        return router_rules.route(question)
    from src import router_ml
    return router_ml.route(question)


def ask_claude(question: str, band: str):
    import anthropic
    client = anthropic.Anthropic()
    kwargs = dict(model=MODEL, max_tokens=1024,
                  messages=[{"role": "user", "content": question}])
    if band == "HIGH":
        kwargs["tools"] = [{"type": WEB_SEARCH_TOOL, "name": "web_search", "max_uses": 3}]
        kwargs["tool_choice"] = {"type": "any"}  # force a search for HIGH-risk questions
    response = client.messages.create(**kwargs)

    text, sources = [], {}
    for block in response.content:
        if block.type == "text":
            text.append(block.text)
            for c in getattr(block, "citations", None) or []:
                if getattr(c, "url", None):
                    sources[c.url] = c.title
    answer = "".join(text).strip()
    if band == "AMBIGUOUS":
        answer += CAVEAT
    return answer, sources


def main():
    p = argparse.ArgumentParser(description="Temporal-Risk Router demo")
    p.add_argument("question")
    p.add_argument("--router", choices=["v1", "v2"], default="v2")
    p.add_argument("--dry-run", action="store_true", help="only show the risk band")
    args = p.parse_args()

    band = classify(args.question, args.router)
    action = {"LOW": "answer from memory",
              "AMBIGUOUS": "answer + recency warning",
              "HIGH": "web search first"}[band]
    print(f"Router {args.router}: {band}  ->  {action}\n")
    if args.dry_run:
        return

    load_env()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("ANTHROPIC_API_KEY is not set. Add it to .env or use --dry-run.")
    answer, sources = ask_claude(args.question, band)
    print(answer)
    if sources:
        print("\nSources:")
        for url, title in sources.items():
            print(f"  - {title}: {url}")


if __name__ == "__main__":
    main()
