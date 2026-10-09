# Experiment: when should the AI search?

Model `llama3.1:8b` · 2026-10-09 · 495/499 questions from public benchmarks (FreshQA 2026-04-21, PopQA)

Search used by the methods below: **Wikipedia + live web**.

## Main result

| Method | Correct (95% interval) | Wrong | No guess | Searched |
|---|---|---|---|---|
| Never search | 43% (38%-47%) | 166 | 117 | 0% |
| Always search | 67% (63%-71%) | 114 | 47 | 100% |
| Time check only | 47% (42%-51%) | 152 | 111 | 15% |
| Self-consistency only | 65% (61%-69%) | 130 | 44 | 66% |
| Verbal confidence | 65% (61%-69%) | 127 | 45 | 74% |
| **Router (ours)** | 65% (61%-69%) | 127 | 44 | 68% |
| **Router + cutoff rule (ours)** | 67% (62%-71%) | 120 | 45 | 75% |
| Oracle (best possible) | 72% (67%-75%) | 101 | 40 | 57% |

![Accuracy vs. searches](experiment_chart.png)

## Correct answers by question type

| Question type | n | Never search | Always search | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) | Oracle (best possible) |
|---|---|---|---|---|---|---|---|---|---|
| Stable, famous (PopQA) | 129 | 67% | 78% | 67% | 78% | 77% | 78% | 78% | 83% |
| Stable, rare (PopQA) - incomplete | 129 | 22% | 60% | 22% | 59% | 57% | 59% | 59% | 60% |
| Never-changing (FreshQA) | 77 | 79% | 87% | 79% | 87% | 86% | 87% | 86% | 95% |
| Changing (FreshQA) - outdated | 160 | 22% | 56% | 35% | 48% | 52% | 50% | 54% | 60% |

## Share of questions searched, by type

| Question type | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) |
|---|---|---|---|---|---|
| Stable, famous (PopQA) | 0% | 44% | 64% | 44% | 44% |
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
| Never search | 134 | 16 | 0.000 * |
| Always search | 4 | 8 | 0.388 |
| Time check only | 110 | 12 | 0.000 * |
| Self-consistency only | 12 | 3 | 0.035 * |
| Verbal confidence | 14 | 7 | 0.189 |

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
- FreshQA answers are as of 2026-04-21. Answers that changed since then were re-checked with sources (`data/gold_updates.csv`); broken questions are left out (`data/excluded_questions.csv`).
- Questions with a false premise were left out.
