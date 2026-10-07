# Evaluation report

## Part 1 - Check 1: does the answer change?

30 questions not used for training.

| Method | Right group | HIGH caught | Searches |
|---|---|---|---|
| Keyword baseline | 15/30 (50%) | 3/10 | 4 |
| Time check (ML) | 25/30 (83%) | 8/10 | 9 |

Confusion matrix (time check):

| true \ predicted | LOW | AMBIGUOUS | HIGH |
|---|---|---|---|
| LOW | 7 | 2 | 1 |
| AMBIGUOUS | 0 | 10 | 0 |
| HIGH | 0 | 2 | 8 |

## Part 2 - Router: when should the AI search?

45 questions, 15 of each type. AI backend: ollama, model: llama3.1:8b.

Questions sent to search, by type:

| Question type | Should search? | Time check only | Knowledge check only | Router (both checks) |
|---|---|---|---|---|
| Stable, well known | no | 1/15 | 0/15 | 1/15 |
| Stable, rare (incomplete) | yes | 4/15 | 11/15 | 15/15 |
| Changes over time (outdated) | yes | 15/15 | 0/15 | 15/15 |
| **Right decisions** | | **33/45 (73%)** | **26/45 (58%)** | **44/45 (98%)** |
| Total searches | | 20 | 11 | 31 |
