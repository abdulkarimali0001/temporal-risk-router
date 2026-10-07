# Temporal-Risk Router — Group 4

Seminar on AI Project · Incomplete & Outdated Knowledge in Generative AI (case study: Claude)

The router reads a question **before** Claude answers and puts it in a risk band:

| Band | Meaning | What happens |
|---|---|---|
| LOW | Stable fact (math, history) | Claude answers from memory |
| AMBIGUOUS | Can change from time to time (fees, rules) | Answer + recency warning |
| HIGH | Likely outdated (CEO, prices, deadlines) | Claude must web-search and cite sources |

## Project layout

```
temporal-risk-router/
├── data/
│   ├── questions.csv        150 labelled questions (training / cross-validation)
│   ├── unseen_test.csv      30 new questions neither router was built on
│   └── two_signal_test.csv  45 questions: stable-common, stable-rare, changing
├── src/
│   ├── router_rules.py      Router v1 — keyword rules
│   ├── router_ml.py         Router v2 — TF-IDF + logistic regression (scikit-learn)
│   ├── evaluate.py          Compares v1, v2, "never search", "always search"
│   ├── answer.py            Full pipeline: route → call Claude (+ web search for HIGH)
│   ├── week2_results.py     Prints the Week 2 slide table and lessons
│   ├── confidence.py        Signal 2: does the AI know? (asks 3 times, checks agreement)
│   ├── two_signal.py        Version 3: Two-Signal Router (time + confidence)
│   ├── week3_results.py     Week 3 test: one check vs two checks on 45 questions
│   ├── web_search.py        Search step: looks questions up on Wikipedia (free)
│   ├── full_system.py       Full system: router -> search -> answer with sources
│   └── demo.py              Live demo: type a question, see Version 1 vs Version 2
└── results/                 report.md, predictions, trained model (created by scripts)
```

## Setup (macOS, once)

Open this folder in VS Code (**File → Open Folder…**), then open the terminal (**Terminal → New Terminal**):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

When VS Code asks "select interpreter", choose `.venv`.

## Run it

In the VS Code terminal (with `.venv` active), run from the project folder:

```bash
python -m src.week2_results                              # Week 2 slide results (for class)
python -m src.demo                                       # live demo: type your own questions
python -m src.evaluate                                   # full comparison, writes results/report.md
python -m src.router_ml                                  # train router v2
python -m src.answer "Who runs Samsung?" --dry-run       # show the risk band only (no API key)
python -m src.answer "Who is the current CEO of Anthropic?"   # real answer from Claude
```

For real answers, copy `.env.example` to `.env` and paste your Anthropic API key
(from console.anthropic.com). The key costs money per call and must never be shared or uploaded.

## Current results (Week 2)

| Router (unseen questions) | Accuracy | HIGH-risk caught | Searches |
|---|---|---|---|
| Never search | 33% | 0/10 | 0% |
| Always search | 33% | 10/10 | 100% |
| v1 rules | 50% | 3/10 | 13% |
| v2 ML | 83% | 8/10 | 30% |

Run `python -m src.evaluate` to reproduce. Notes for the report:
- v1 (same rules as the Week 1 pilot) scored 87% on the 30-question pilot but only 50% on new questions: the pilot was too small.
- v2 learns phrases like "Who manages…" and "When is … this fall" without time keywords.
- The unseen set is only 30 questions, so treat the numbers as early indicators.

## Week 3: Two-Signal Router (Version 3)

Version 2 only asks **"does the answer change over time?"** Version 3 also asks
**"does the AI actually know it?"**: it asks the model the same question 3 times
(no web search). If the answers disagree or it says "I don't know", the AI is unsure.

| | AI confident | AI unsure |
|---|---|---|
| LOW (never changes) | answer from memory | **search** (incomplete knowledge) |
| MAYBE (sometimes) | answer + warning | **search** |
| HIGH (often) | **search** (maybe outdated) | **search** |

Setup: copy `.env.example` to `.env` and either add `ANTHROPIC_API_KEY` (uses the
cheap Haiku model, about 90 short calls for the full test) or set
`CONFIDENCE_BACKEND=ollama` with Ollama running (`ollama pull llama3.2`).

```bash
python -m src.two_signal "Who founded Kyungdong University?"   # one question, shows both signals
python -m src.week3_results                                      # full test, saves results/week3_results.csv
```

All model answers are cached in `results/confidence_cache.json`, so a re-run (or a class demo) is free and works offline.

Research basis: self-consistency / uncertainty for deciding when to retrieve
(Moskvoretskii et al., ACL 2025; KBM, EMNLP Findings 2025), and evidence that models
can be confidently outdated (evolveQA, 2025). Most work uses one signal; we combine both.

## Full system: router + search + answer

When the router says "search", the system looks the question up on Wikipedia
(free, no key), gives the pages to the AI, and the AI answers ONLY from them,
with the source link and the date it was retrieved. If the pages don't contain
the answer, it says so instead of guessing.

```bash
python -m src.full_system "Who was the first Kenyan woman to earn a PhD?"
python -m src.full_system --demo        # 9 demo questions -> results/full_system_demo.txt
```

Or double-click `run_full_system.command` in Finder (uses the free local model).

Limitation: Wikipedia has no real-time data (prices, weather, today's news).
For those the system answers "not found"; a live web search (Claude's web search
tool, `src/answer.py`) is needed.

## Team to-do

- [ ] Second member re-labels `questions.csv` independently → measure agreement
- [ ] Add more unseen test questions (aim for 100+)
- [ ] Add `verified_answer`, `source_url`, `checked_on` for HIGH questions (needed for the Week 4 answer-accuracy test)
- [ ] Week 3: run `answer.py` on the test set with and without the router; compare correctness
