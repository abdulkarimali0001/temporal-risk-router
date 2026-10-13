# Cost per question

AI calls and web searches each method needs per question, with its accuracy. Fewer calls and searches = faster and cheaper.

## llama3.1:8b (499 questions)

| Method | Correct | AI calls / question | Searches / question |
|---|---|---|---|
| Never search | 42% | 1.0 | 0.00 |
| Always search | 68% | 2.0 | 1.00 |
| Time check only | 46% | 1.1 | 0.15 |
| Self-consistency only | 65% | 4.7 | 0.66 |
| Verbal confidence | 65% | 2.7 | 0.74 |
| **Router (ours)** | 66% | 4.2 | 0.68 |
| **Router + cutoff rule (ours)** | 67% | 4.3 | 0.75 |
| **Router, AI time check (ours)** | 66% | 5.0 | 0.68 |
| **Router, dated AI time check (ours)** | 66% | 5.0 | 0.69 |
| **Router, cheap check (ours)** | 66% | 3.2 | 0.75 |
| **Router, strict check (ours)** | 68% | 5.0 | 0.79 |

## qwen2.5:7b (499 questions)

| Method | Correct | AI calls / question | Searches / question |
|---|---|---|---|
| Never search | 35% | 1.0 | 0.00 |
| Always search | 68% | 2.0 | 1.00 |
| Time check only | 42% | 1.1 | 0.15 |
| Self-consistency only | 65% | 4.7 | 0.73 |
| Verbal confidence | 54% | 2.5 | 0.49 |
| **Router (ours)** | 66% | 4.3 | 0.76 |
| **Router + cutoff rule (ours)** | 66% | 4.4 | 0.80 |
| **Router, AI time check (ours)** | 66% | 5.0 | 0.77 |
| **Router, dated AI time check (ours)** | 65% | 5.5 | 0.74 |
| **Router, cheap check (ours)** | 65% | 3.3 | 0.78 |
| **Router, strict check (ours)** | 67% | 5.1 | 0.82 |

## qwen2.5:14b (497 questions)

| Method | Correct | AI calls / question | Searches / question |
|---|---|---|---|
| Never search | 40% | 1.0 | 0.00 |
| Always search | 70% | 2.0 | 1.00 |
| Time check only | 45% | 1.1 | 0.15 |
| Self-consistency only | 67% | 4.7 | 0.72 |
| Verbal confidence | 68% | 2.8 | 0.79 |
| **Router (ours)** | 68% | 4.3 | 0.73 |
| **Router + cutoff rule (ours)** | 70% | 4.3 | 0.78 |
| **Router, AI time check (ours)** | 68% | 5.1 | 0.73 |
| **Router, dated AI time check (ours)** | 68% | 4.9 | 0.74 |
| **Router, cheap check (ours)** | 69% | 3.4 | 0.84 |
| **Router, strict check (ours)** | 70% | 5.0 | 0.81 |

The router skips the knowledge check for fast-changing questions, which are searched anyway. AI calls differ in size (a knowledge-check sample is 8 words; an answer from sources reads ~5,000 characters), so measured seconds are in `results/timing_report.md`, and the trade-off between a search and a wrong answer in `results/curves_report.md`.
