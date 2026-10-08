# Experiment: when should the AI search?

Model `llama3.1:8b` · 2026-10-08 · 197/200 questions from public benchmarks (FreshQA 2026-04-21, PopQA)

## Main result

| Method | Correct (95% interval) | Wrong | No guess | Searched |
|---|---|---|---|---|
| Never search | 41% (34%-47%) | 74 | 43 | 0% |
| Always search | 48% (42%-55%) | 39 | 63 | 100% |
| Time check only | 41% (34%-47%) | 65 | 52 | 18% |
| Self-consistency only | 48% (41%-55%) | 43 | 60 | 68% |
| Verbal confidence | 49% (42%-56%) | 43 | 57 | 76% |
| **Router (ours)** | 48% (41%-55%) | 43 | 59 | 70% |
| **Router + cutoff rule (ours)** | 48% (41%-55%) | 41 | 62 | 80% |
| Oracle (best possible) | 57% (51%-64%) | 31 | 53 | 59% |

![Accuracy vs. searches](experiment_chart.png)

## Correct answers by question type

| Question type | n | Never search | Always search | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) | Oracle (best possible) |
|---|---|---|---|---|---|---|---|---|---|
| Stable, famous (PopQA) | 40 | 65% | 68% | 65% | 68% | 70% | 68% | 68% | 75% |
| Stable, rare (PopQA) - incomplete | 40 | 20% | 38% | 20% | 35% | 38% | 35% | 35% | 38% |
| Never-changing (FreshQA) | 39 | 77% | 64% | 77% | 74% | 72% | 74% | 64% | 87% |
| Changing (FreshQA) - outdated | 78 | 21% | 36% | 21% | 31% | 33% | 32% | 36% | 44% |

## Share of questions searched, by type

| Question type | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) |
|---|---|---|---|---|---|
| Stable, famous (PopQA) | 0% | 50% | 68% | 50% | 50% |
| Stable, rare (PopQA) - incomplete | 0% | 88% | 90% | 88% | 88% |
| Never-changing (FreshQA) | 3% | 41% | 44% | 41% | 64% |
| Changing (FreshQA) - outdated | 45% | 81% | 90% | 86% | 99% |

## Search quality: first version vs. improved search

Accuracy when ALWAYS searching, by question type (improved = full pages with infoboxes and tables, merged queries, BM25 ranking).

| Question type | First search | Improved search |
|---|---|---|
| Stable, famous (PopQA) | 75% | 68% |
| Stable, rare (PopQA) - incomplete | 36% | 38% |
| Never-changing (FreshQA) | 55% | 66% |
| Changing (FreshQA) - outdated | 27% | 35% |
| **All** | **44%** | **48%** |

## Check 1 on FreshQA (outside data, not used for training)

- Right group (never/slow/fast = LOW/MAYBE/HIGH): 73/117 (62%)
- Fast-changing questions caught as HIGH: 24/39

## Is the difference real? (paired McNemar test)

For each pair: questions only the router got right vs. only the other method got right. p < 0.05 means the difference is unlikely to be chance.

| Router vs. | Only router right | Only other right | p-value |
|---|---|---|---|
| Never search | 27 | 12 | 0.024 * |
| Always search | 6 | 6 | 1.000 |
| Time check only | 22 | 7 | 0.008 * |
| Self-consistency only | 1 | 0 | 1.000 |
| Verbal confidence | 4 | 6 | 0.754 |

(Compared using: Router (ours).)

## Cutoff rule

Model training cutoff: 2023-12 (2.8 years before the test date). With the cutoff rule, questions whose answers change *sometimes* (MAYBE) are also searched when the model's knowledge is more than a year old.

## How to read this

- **Never search** shows what the AI gets wrong on its own (outdated + incomplete knowledge).
- **Always search** is the most expensive option; searching can also hurt when the source is poor.
- **Oracle** searches only when the memory answer is wrong: the best any method could do.
- A good method gets close to the best accuracy while searching far fewer questions.

## Notes

- Scoring: an answer is correct if it contains one of the benchmark's accepted answers (automatic matching; see `experiment_answers.csv` to check by hand).
- FreshQA answers are as of 2026-04-21; a few fast-changing answers may have changed since.
- Questions with a false premise were left out.
