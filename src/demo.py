"""Demo of the full pipeline.

    python -m src.demo            # run the demo questions -> results/demo_output.txt
    python -m src.demo --ask      # type your own questions (q to quit)
"""
from __future__ import annotations

import sys
from pathlib import Path

from src import llm, pipeline, time_check

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "results" / "demo_output.txt"

DEMO_QUESTIONS = [
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


def run_demo(model):
    header = f"DEMO - AI backend: {llm.backend()}, model: {llm.model_name()}"
    blocks = [header, "=" * len(header)]
    OUTPUT.parent.mkdir(exist_ok=True)
    for i, q in enumerate(DEMO_QUESTIONS, 1):
        print(f"[{i}/{len(DEMO_QUESTIONS)}] {q}", flush=True)
        try:
            block = pipeline.show(pipeline.ask(q, model))
        except Exception as e:  # one failing question should not stop the demo
            block = f"Q: {q}\n   ERROR: {type(e).__name__}: {e}"
        print(block + "\n", flush=True)
        blocks.append(block)
        OUTPUT.write_text("\n\n".join(blocks) + "\n", encoding="utf-8")  # save as we go
    print(f"Saved: {OUTPUT.relative_to(ROOT)}")


def interactive(model):
    print("Type a question and press Enter (q to quit).\n")
    while True:
        q = input("Question: ").strip()
        if q.lower() in {"q", "quit", "exit"}:
            break
        if q:
            print(pipeline.show(pipeline.ask(q, model)) + "\n")


if __name__ == "__main__":
    model = time_check.load()
    interactive(model) if "--ask" in sys.argv else run_demo(model)
