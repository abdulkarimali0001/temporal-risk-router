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
| **1. Time check** | Does the answer change over time? | TF-IDF + logistic regression classifier (LOW / MAYBE / HIGH); Korean questions are translated first | outdated knowledge |
| **2. Knowledge check** | Does the AI actually know it? | Self-consistency: ask 3 times; disagreement or "I don't know" = unsure | incomplete knowledge |

The router combines them:

| | AI knows it | AI unsure |
|---|---|---|
| **LOW** (never changes) | answer from memory | **search** (incomplete knowledge) |
| **MAYBE** (changes sometimes) | answer + recency warning | **search** |
| **HIGH** (changes often) | **search** (may be outdated) | **search** |

When it searches, it reads **Wikipedia** (full pages with infoboxes and tables; Korean Wikipedia
too for Korean questions) and, with a free [Tavily](https://tavily.com) key, the **live web**. All
passages are ranked together (BM25) and the model answers **only from the best ones**, citing them.
It is told today's date and to prefer the newest information. If the sources do not contain the
answer, it says so instead of guessing.

Why two checks? A knowledge check alone misses answers that are *confident but outdated*;
a time check alone misses *stable facts the model never learned*.

## Results

Free local models through Ollama: **llama3.1:8b** (main) and **qwen2.5:7b** (second model).

### Main experiment: 500 questions from public benchmarks

FreshQA (240 questions whose answers never, slowly or quickly change; version 2026-04-21, answers
that changed since re-checked with sources in [`data/gold_updates.csv`](data/gold_updates.csv)) and
PopQA (260 facts about famous and very obscure entities). Search: Wikipedia + live web.

| Method | llama correct | llama wrong | llama searched | qwen correct | qwen wrong | qwen searched |
|---|---|---|---|---|---|---|
| Never search | 43% | 166 | 0% | 35% | 281 | 0% |
| Always search | 67% | 114 | 100% | 68% | 108 | 100% |
| Time check only | 47% | 152 | 15% | 42% | 256 | 15% |
| Self-consistency only (Moskvoretskii et al. 2025) | 65% | 130 | 66% | 65% | 126 | 73% |
| Model's own stated confidence | 65% | 127 | 74% | 54% | 189 | 49% |
| **Router (ours)** | **65%** | **127** | **68%** | **66%** | **120** | **76%** |
| **Router + cutoff rule (ours)** | **67%** | **120** | **75%** | **66%** | **118** | **80%** |
| Router, cheap check (ours) | 66% | 125 | 75% | 65% | 126 | 78% |
| Learned router (ours, out-of-fold) | 67% | 114 | 91% | 68% | 109 | 91% |
| Oracle (best possible) | 72% | 101 | 57% | 71% | 100 | 65% |

![Accuracy at every search budget](results/curves_chart.png)

Findings:
- **Close to always searching, with 20-30% fewer searches.** The router reaches 65-67% where
  searching everything reaches 67-68%, and it cuts wrong answers by about a quarter (llama) to more
  than half (qwen) compared with the model alone.
- **Better than one signal alone at most search budgets.** Across all budgets (the curves above),
  the router's area is higher than the time check (+2.6 points on llama, interval above zero) and
  self-consistency (+0.3 points on qwen, interval above zero); other differences are within noise
  ([`results/curves_report.md`](results/curves_report.md)).
- **Stable across models:** the model's own confidence works for llama (65%) but fails for qwen
  (54%); the router gives 65-66% on both.
- **Search quality matters most.** On the 200 questions answered by every search version,
  searching every question went from 45% (first Wikipedia search) to 49% (full pages, tables, BM25)
  to 63% (plus live web) on llama. Rare facts rose from 37% to 68%.
- **What the router saves is searches, not AI calls.** Its knowledge check costs 3 extra AI calls,
  so it uses about 4 AI calls per question against 2 for always searching
  ([`results/cost_report.md`](results/cost_report.md)). It pays off when searches are expensive,
  slow, rate-limited or private. In the demo app the checks run while the answer is written, so they
  add no waiting. A **cheaper knowledge check** (the memory answer + one sample instead of three
  samples) keeps the accuracy (66% / 65%) with 3.2-3.3 AI calls.
- **When is it worth it? A cost model.** If one wrong or missing answer costs R searches, each
  method searches the cheapest share of questions for that R. From R = 3 on, the router is the
  cheapest rule-based method on both models, 5-15% cheaper than always searching; below R = 2,
  not searching at all is cheapest ([`results/curves_report.md`](results/curves_report.md)).

Full reports: [`results/experiment_report.md`](results/experiment_report.md) (llama),
[`results/experiment_report_qwen2.5-7b.md`](results/experiment_report_qwen2.5-7b.md),
[`results/learned_router_report.md`](results/learned_router_report.md).

### Korean questions (first 34, answers verified 2026-10-08)

General knowledge, local Gangwon / Sokcho facts, and facts that change (officeholders after the
June 2026 local elections, CEOs, sports champions).

| Method | llama | qwen |
|---|---|---|
| Model alone | 30% | 26% |
| Search: English Wikipedia only | 58% | 50% |
| **Search: Korean + English** | **94%** | **94%** |
| **Router** | **85%** | **82%** |

Searching Korean sources nearly doubles accuracy over English-only search
([`results/korean_evaluation.md`](results/korean_evaluation.md)). The set now has 49 questions,
and a **Swahili set** of 32 questions (Swahili literature, East African places and leaders,
answers verified 2026-10-09) is searched on Swahili Wikipedia in the same way
([`results/swahili_evaluation.md`](results/swahili_evaluation.md)).

### Our own test sets

- **Check 1 on 30 questions it was not trained on:** 24/30 right group (keyword baseline 15/30).
- **Router decisions on 45 questions:** 44/45 right (time check alone 33, knowledge check alone 26).
- **31 questions with verified answers:** router 80% correct with 15 searches; always searching 83%
  with 31; model alone 61%.

## Demo app

Double-click `run_app.command` (or `python -m src.app`) and open http://localhost:8765. The AI starts
answering at once, word by word; the two checks and the source search run at the same time. Easy
questions keep the quick answer; risky ones are replaced by an answer written only from the sources,
with links. `run_app_fast.command` uses a smaller model (llama3.2:3b) for faster answers.

## Project structure

```
temporal-risk-router/
├── app/index.html             the demo page
├── data/
│   ├── time_check_train.csv   150 hand-labelled questions (LOW / AMBIGUOUS / HIGH) for Check 1
│   ├── time_check_extra.csv   outside training data for Check 1 (FreshQA + PopQA, none in any test)
│   ├── time_check_test.csv    30 questions to test Check 1
│   ├── router_test.csv        45 questions to test the router's decisions
│   ├── answer_test.csv        31 questions with verified answers and sources
│   ├── benchmark.csv          500 questions from FreshQA and PopQA
│   ├── gold_updates.csv       benchmark answers re-checked in October 2026, with sources
│   ├── excluded_questions.csv broken benchmark questions left out
│   ├── korean_test.csv        49 Korean questions with verified answers and sources
│   ├── swahili_test.csv       32 Swahili questions with verified answers and sources
│   └── human_review_sample.json 120 answers for the group's hand check
├── src/
│   ├── time_check.py          Check 1 (classifier, and two AI-judged variants)
│   ├── knowledge_check.py     Check 2: self-consistency (full, and the cheaper check)
│   ├── router.py              combines both checks into a decision
│   ├── learned_router.py      the decision learned from all signals
│   ├── search.py              Wikipedia (EN/KO) + live web search, BM25 passage ranking
│   ├── pipeline.py            router -> search -> answer with sources
│   ├── language.py            Korean and Swahili questions
│   ├── llm.py                 the language model (Ollama, or Claude)
│   ├── benchmarks.py          downloads and samples FreshQA + PopQA
│   ├── experiment.py          main experiment: every method on the benchmark
│   ├── rescore.py             re-scores saved answers (no AI needed)
│   ├── curves.py              accuracy at every search budget
│   ├── cost.py                AI calls and searches per question
│   ├── timing.py              measured seconds per step and per method
│   ├── evaluate.py            Check 1 and router decisions on our own sets
│   ├── evaluate_answers.py    answer correctness on 31 verified questions; the scoring rules
│   ├── evaluate_korean.py     the Korean and Swahili questions
│   ├── human_review.py        agreement between the group's hand check and the scoring
│   ├── app.py                 the demo app server
│   ├── demo.py                command-line demo
│   ├── keyword_baseline.py    keyword method, used as a comparison
│   └── claude_answer.py       optional: answer with Claude's web search
├── results/                   reports, charts, answers, caches
├── run_experiment.command     double-click: every experiment, both models
├── run_bigger_model.command   double-click (overnight): the same with qwen2.5:14b
├── run_reports.command        double-click: rebuild every report from saved answers
├── run_app.command            double-click: the demo app
├── run_app_fast.command       double-click: the demo app with a smaller model
├── run_demo.command / run_evaluation.command
├── keys.txt                   your Tavily key (stays on your computer, not uploaded)
└── setup.sh                   shared setup for the .command files
```

## Setup

Requirements: Python 3.9+, and [Ollama](https://ollama.com).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
ollama pull llama3.1:8b
```

Optional: put `TAVILY_API_KEY=...` in `keys.txt` for live web search (free, 1,000 searches a month).
Everything is cached in `results/`, so re-runs are fast and do not search again.

## Usage

```bash
python -m src.pipeline "Who wrote the Swahili novel Kufa Kuzikana?"   # one question, full pipeline
python -m src.router   "Who is the CEO of Naver?"                     # only the routing decision
python -m src.app                                                      # demo app
python -m src.experiment                                               # main experiment
python -m src.rescore && python -m src.curves && python -m src.cost    # reports from saved answers
```

## Limitations

- Two small local models (8B and 7B); a 14B model can be added with `run_bigger_model.command`.
- 500 benchmark questions: differences of 1-2 points between the best methods are within noise.
- Automatic scoring by answer matching; a hand check of 120 answers by the group is in progress.
- Benchmark answers for fast-changing questions go out of date; we re-checked the ones our system
  disagreed with (October 2026), not all of them.
- The time check puts 60% of FreshQA questions in the right of three groups; it was trained partly on
  FreshQA-style questions (none from the test set).

## Research basis

- Moskvoretskii et al., *Adaptive Retrieval without Self-Knowledge? Bringing Uncertainty Back Home*, ACL 2025.
- *KBM: Delineating Knowledge Boundary for Adaptive Retrieval in Large Language Models*, Findings of EMNLP 2025.
- *When Facts Change: Probing LLMs on Evolving Knowledge with evolveQA*, 2025.
- *Adaptive Retrieval helps Reasoning in LLMs - but mostly if it's not used*, 2026.
- Vu et al., *FreshLLMs: Refreshing Large Language Models with Search Engine Augmentation*, 2023 (FreshQA).
- Mallen et al., *When Not to Trust Language Models: Investigating Effectiveness of Parametric and Non-Parametric Memories*, ACL 2023 (PopQA).
