# Temporal-Risk Router

**Knowing when to search: a dual-signal router for incomplete and outdated knowledge in large language models.**

A language model only knows what it learned up to its training cutoff. Its answers can be
**outdated** (the world changed since) or **incomplete** (it never learned the fact), and it often
sounds confident either way. This project decides, *before* the model answers, whether it can
answer from memory or must look the answer up first.

## How it works

Every question goes through two checks:

| Check | Question it asks | Method | Catches |
|---|---|---|---|
| **1. Time check** | Does the answer change over time? | TF-IDF + logistic regression classifier (LOW / MAYBE / HIGH) | outdated knowledge |
| **2. Knowledge check** | Does the AI actually know it? | Self-consistency: ask 3 times; disagreement or "I don't know" = unsure | incomplete knowledge |

The router combines them:

| | AI knows it | AI unsure |
|---|---|---|
| **LOW** (never changes) | answer from memory | **search** (incomplete knowledge) |
| **MAYBE** (changes sometimes) | answer + recency warning | **search** |
| **HIGH** (changes often) | **search** (may be outdated) | **search** |

When it searches, the pipeline looks the question up on Wikipedia, gives the most relevant
passages to the model, and the model answers **only from those sources**, citing them with the
date they were retrieved. If the sources do not contain the answer, it says so instead of guessing.

Why two checks? A knowledge check alone misses answers that are *confident but outdated*;
a time check alone misses *stable facts the model never learned*. Most adaptive-retrieval work
uses only one of these signals.

## Project structure

```
temporal-risk-router/
├── data/
│   ├── time_check_train.csv   150 labelled questions (LOW / AMBIGUOUS / HIGH) to train Check 1
│   ├── time_check_test.csv    30 separate questions to test Check 1
│   └── router_test.csv        45 questions to test the router (15 stable-common, 15 stable-rare, 15 changing)
├── src/
│   ├── time_check.py          Check 1: does the answer change over time?
│   ├── knowledge_check.py     Check 2: does the AI actually know it?
│   ├── router.py              combines both checks into a decision
│   ├── search.py              Wikipedia search, keeps the most relevant passages
│   ├── pipeline.py            router -> search -> answer with sources
│   ├── llm.py                 access to the language model (Ollama or Claude)
│   ├── evaluate.py            evaluation of Check 1 and of the router
│   ├── demo.py                demo questions, or type your own (--ask)
│   ├── keyword_baseline.py    simple keyword method, used only as a comparison
│   └── claude_answer.py       optional: answer with Claude's live web search instead
├── results/                   evaluation report, router decisions, demo output, caches
├── run_demo.command           double-click (macOS): run the demo
├── run_evaluation.command     double-click (macOS): run the evaluation
└── setup.sh                   shared setup used by the .command files
```

## Setup

Requirements: Python 3.9+, and [Ollama](https://ollama.com) for the free local model.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.1:8b
```

Settings (optional): copy `.env.example` to `.env`. By default the project uses the local model
`llama3.1:8b` through Ollama; set `AI_BACKEND=claude` and `ANTHROPIC_API_KEY` to use Claude instead.

## Usage

```bash
python -m src.pipeline "Who wrote the Swahili novel Kufa Kuzikana?"   # one question, full pipeline
python -m src.router   "Who wrote the Swahili novel Kufa Kuzikana?"   # only the routing decision
python -m src.demo                                                     # demo questions -> results/demo_output.txt
python -m src.demo --ask                                               # type your own questions
python -m src.evaluate                                                 # -> results/evaluation_report.md
```

On macOS you can also double-click `run_demo.command` or `run_evaluation.command`.

Model answers and search results are cached in `results/`, so re-runs are fast and work offline.

## Results

Local model `llama3.1:8b`. Full numbers: [`results/evaluation_report.md`](results/evaluation_report.md).

**Check 1 on 30 questions it was not trained on**

| Method | Right group | HIGH questions caught |
|---|---|---|
| Keyword baseline | 15/30 (50%) | 3/10 |
| Time check (ML) | 25/30 (83%) | 8/10 |

**Router on 45 questions: was the search decision right?**

| Question type | Should search? | Time check only | Knowledge check only | Router (both) |
|---|---|---|---|---|
| Stable, well known | no | 1/15 searched | 0/15 | 1/15 |
| Stable, rare (incomplete) | yes | 4/15 | 11/15 | **15/15** |
| Changes over time (outdated) | yes | 15/15 | 0/15 | **15/15** |
| **Right decisions** | | 33/45 (73%) | 26/45 (58%) | **44/45 (98%)** |

Each check misses a different kind of problem; together they catch both.

**Pipeline examples** ([`results/demo_output.txt`](results/demo_output.txt)):
- *"Who wrote the Swahili novel Kufa Kuzikana?"*: the model alone said "I don't know" three times;
  the router searched and answered **Ken Walibora**, citing Wikipedia.
- *"What is the tuition fee for the Smart Computing department?"*: not found in the sources, so
  the system says so instead of guessing.
- *"Who is the CEO of Naver?"*: the source returned a CEO for **2017–2021**, showing that a search
  can also return outdated information.

## Limitations

- Small test sets (30 and 45 questions); the numbers are early indicators.
- Question labels were written by the authors and still need independent review.
- Wikipedia has no real-time data (prices, weather) and misses some Korean topics.
- All results so far use one small local model; larger models may know more rare facts.
- The correctness of final answers is not yet scored against verified answers.

## Research basis

- Moskvoretskii et al., *Adaptive Retrieval without Self-Knowledge? Bringing Uncertainty Back Home*, ACL 2025.
- *KBM: Delineating Knowledge Boundary for Adaptive Retrieval in Large Language Models*, Findings of EMNLP 2025.
- *When Facts Change: Probing LLMs on Evolving Knowledge with evolveQA*, 2025.
- *Adaptive Retrieval helps Reasoning in LLMs - but mostly if it's not used*, 2026.
- Vu et al., *FreshLLMs: Refreshing Large Language Models with Search Engine Augmentation*, 2023.
