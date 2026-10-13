# Experiment: when should the AI search?

Model `llama3.1:8b` · 2026-10-12 · 499/499 questions from public benchmarks (FreshQA 2026-04-21, PopQA)

Search used by the methods below: **Wikipedia + live web**.

## Main result

| Method | Correct (95% interval) | Wrong | No guess | Searched |
|---|---|---|---|---|
| Never search | 42% (38%-47%) | 170 | 117 | 0% |
| Always search | 68% (63%-72%) | 115 | 47 | 100% |
| Time check only | 46% (42%-51%) | 156 | 111 | 15% |
| Self-consistency only | 65% (61%-69%) | 131 | 44 | 66% |
| Verbal confidence | 65% (61%-69%) | 129 | 45 | 74% |
| **Router (ours)** | 66% (62%-70%) | 128 | 44 | 68% |
| **Router + cutoff rule (ours)** | 67% (63%-71%) | 121 | 45 | 75% |
| **Router, AI time check (ours)** | 66% (62%-70%) | 124 | 45 | 68% |
| **Router, dated AI time check (ours)** | 66% (62%-70%) | 127 | 44 | 69% |
| **Router, cheap check (ours)** | 66% (62%-70%) | 127 | 44 | 75% |
| **Router, strict check (ours)** | 68% (63%-71%) | 119 | 43 | 79% |
| Oracle (best possible) | 72% (67%-75%) | 102 | 40 | 58% |

![Accuracy vs. searches](experiment_chart.png)

## Correct answers by question type

| Question type | n | Never search | Always search | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) | Router, AI time check (ours) | Router, dated AI time check (ours) | Router, cheap check (ours) | Router, strict check (ours) | Oracle (best possible) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Stable, famous (PopQA) | 129 | 67% | 78% | 67% | 78% | 77% | 78% | 78% | 78% | 78% | 79% | 79% | 83% |
| Stable, rare (PopQA) - incomplete | 130 | 22% | 60% | 22% | 59% | 58% | 59% | 59% | 59% | 59% | 57% | 60% | 61% |
| Never-changing (FreshQA) | 80 | 76% | 86% | 76% | 86% | 84% | 86% | 85% | 86% | 86% | 86% | 86% | 94% |
| Changing (FreshQA) - outdated | 160 | 22% | 56% | 35% | 48% | 52% | 50% | 54% | 52% | 51% | 52% | 55% | 60% |

## Share of questions searched, by type

| Question type | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) |
|---|---|---|---|---|---|
| Stable, famous (PopQA) | 0% | 44% | 64% | 44% | 44% |
| Stable, rare (PopQA) - incomplete | 0% | 83% | 82% | 83% | 83% |
| Never-changing (FreshQA) | 4% | 46% | 50% | 48% | 66% |
| Changing (FreshQA) - outdated | 44% | 79% | 89% | 86% | 97% |

## Search quality: each version of the search

Accuracy when ALWAYS searching (194 questions answered by every version).

| Question type | First search (Wikipedia text) | Improved Wikipedia search | Wikipedia + live web |
|---|---|---|---|
| Stable, famous (PopQA) | 75% | 68% | 75% |
| Stable, rare (PopQA) - incomplete | 36% | 38% | 69% |
| Never-changing (FreshQA) | 55% | 66% | 79% |
| Changing (FreshQA) - outdated | 29% | 38% | 52% |
| **All** | 45% | 49% | 65% |

## Check 1 on FreshQA (outside data, not used for training)

- Right group (never/slow/fast = LOW/MAYBE/HIGH): 145/240 (60%)
- Fast-changing questions caught as HIGH: 49/80
- Check 1 asked to the AI instead: right group 143/240 (60%), fast-changing caught as HIGH 64/80
- Check 1 asked to the AI, told its cutoff and today's date: right group 124/240 (52%), fast-changing caught as HIGH 62/80

## Is the difference real? (paired McNemar test)

For each pair: questions only the router got right vs. only the other method got right. p < 0.05 means the difference is unlikely to be chance.

| Router vs. | Only router right | Only other right | p-value |
|---|---|---|---|
| Never search | 142 | 17 | 0.000 * |
| Always search | 3 | 3 | 1.000 |
| Time check only | 118 | 13 | 0.000 * |
| Self-consistency only | 17 | 4 | 0.007 * |
| Verbal confidence | 16 | 4 | 0.012 * |

(Compared using: Router, strict check (ours).)

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
