# Cost per question

AI calls and web searches each method needs per question, with its accuracy. Fewer calls and searches = faster and cheaper.

## llama3.1:8b (495 questions)

| Method | Correct | AI calls / question | Searches / question |
|---|---|---|---|
| Never search | 43% | 1.0 | 0.00 |
| Always search | 67% | 2.0 | 1.00 |
| Time check only | 47% | 1.1 | 0.15 |
| Self-consistency only | 65% | 4.7 | 0.66 |
| Verbal confidence | 65% | 2.7 | 0.74 |
| **Router (ours)** | 65% | 4.2 | 0.68 |
| **Router + cutoff rule (ours)** | 67% | 4.3 | 0.75 |

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

The router skips the knowledge check for fast-changing questions, which are searched anyway. Measured seconds per question are added to the experiment from the next run on (`results/experiment_answers*.csv`, columns `seconds_*`).
