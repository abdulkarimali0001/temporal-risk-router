# Experiment: when should the AI search?

Model `llama3.1:8b` · 2026-10-09 · 496/500 questions from public benchmarks (FreshQA 2026-04-21, PopQA)

Search used by the methods below: **Wikipedia + live web**.

## Main result

| Method | Correct (95% interval) | Wrong | No guess | Searched |
|---|---|---|---|---|
| Never search | 42% (38%-46%) | 170 | 117 | 0% |
| Always search | 64% (60%-68%) | 129 | 48 | 100% |
| Time check only | 46% (41%-50%) | 159 | 111 | 15% |
| Self-consistency only | 62% (58%-66%) | 143 | 45 | 66% |
| Verbal confidence | 62% (58%-66%) | 142 | 46 | 74% |
| **Router (ours)** | 63% (58%-67%) | 140 | 45 | 68% |
| **Router + cutoff rule (ours)** | 64% (59%-68%) | 134 | 46 | 75% |
| Oracle (best possible) | 68% (64%-72%) | 116 | 41 | 58% |

![Accuracy vs. searches](experiment_chart.png)

## Correct answers by question type

| Question type | n | Never search | Always search | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) | Oracle (best possible) |
|---|---|---|---|---|---|---|---|---|---|
| Stable, famous (PopQA) | 130 | 67% | 78% | 67% | 78% | 76% | 78% | 78% | 82% |
| Stable, rare (PopQA) - incomplete | 129 | 22% | 60% | 22% | 59% | 57% | 59% | 59% | 60% |
| Never-changing (FreshQA) | 77 | 79% | 87% | 79% | 87% | 86% | 87% | 86% | 95% |
| Changing (FreshQA) - outdated | 160 | 21% | 46% | 31% | 40% | 43% | 42% | 46% | 51% |

## Share of questions searched, by type

| Question type | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) |
|---|---|---|---|---|---|
| Stable, famous (PopQA) | 0% | 45% | 64% | 45% | 45% |
| Stable, rare (PopQA) - incomplete | 0% | 83% | 82% | 83% | 83% |
| Never-changing (FreshQA) | 3% | 44% | 49% | 45% | 65% |
| Changing (FreshQA) - outdated | 44% | 79% | 89% | 86% | 97% |

## Search quality: each version of the search

Accuracy when ALWAYS searching (193 questions answered by every version).

| Question type | First search (Wikipedia text) | Improved Wikipedia search | Wikipedia + live web |
|---|---|---|---|
| Stable, famous (PopQA) | 75% | 68% | 75% |
| Stable, rare (PopQA) - incomplete | 37% | 39% | 68% |
| Never-changing (FreshQA) | 55% | 66% | 79% |
| Changing (FreshQA) - outdated | 27% | 35% | 47% |
| **All** | 45% | 49% | 63% |

## Check 1 on FreshQA (outside data, not used for training)

- Right group (never/slow/fast = LOW/MAYBE/HIGH): 143/237 (60%)
- Fast-changing questions caught as HIGH: 49/80

## Is the difference real? (paired McNemar test)

For each pair: questions only the router got right vs. only the other method got right. p < 0.05 means the difference is unlikely to be chance.

| Router vs. | Only router right | Only other right | p-value |
|---|---|---|---|
| Never search | 123 | 16 | 0.000 * |
| Always search | 4 | 7 | 0.549 |
| Time check only | 102 | 12 | 0.000 * |
| Self-consistency only | 11 | 3 | 0.057 |
| Verbal confidence | 14 | 6 | 0.115 |

(Compared using: Router + cutoff rule (ours).)

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
