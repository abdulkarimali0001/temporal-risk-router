# Experiment: when should the AI search?

Model `qwen2.5:7b` · 2026-10-09 · 500/500 questions from public benchmarks (FreshQA 2026-04-21, PopQA)

Search used by the methods below: **Wikipedia + live web**.

## Main result

| Method | Correct (95% interval) | Wrong | No guess | Searched |
|---|---|---|---|---|
| Never search | 35% (31%-40%) | 282 | 41 | 0% |
| Always search | 65% (60%-69%) | 123 | 54 | 100% |
| Time check only | 41% (36%-45%) | 262 | 35 | 15% |
| Self-consistency only | 62% (58%-66%) | 137 | 51 | 73% |
| Verbal confidence | 52% (47%-56%) | 196 | 44 | 49% |
| **Router (ours)** | 63% (59%-67%) | 133 | 50 | 76% |
| **Router + cutoff rule (ours)** | 63% (59%-67%) | 133 | 51 | 80% |
| Oracle (best possible) | 68% (64%-72%) | 114 | 44 | 65% |

![Accuracy vs. searches](experiment_chart_qwen2.5-7b.png)

## Correct answers by question type

| Question type | n | Never search | Always search | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) | Oracle (best possible) |
|---|---|---|---|---|---|---|---|---|---|
| Stable, famous (PopQA) | 130 | 56% | 76% | 56% | 78% | 68% | 78% | 78% | 79% |
| Stable, rare (PopQA) - incomplete | 130 | 25% | 60% | 25% | 58% | 54% | 58% | 58% | 62% |
| Never-changing (FreshQA) | 80 | 57% | 86% | 60% | 80% | 71% | 80% | 80% | 91% |
| Changing (FreshQA) - outdated | 160 | 16% | 48% | 31% | 44% | 28% | 48% | 47% | 53% |

## Share of questions searched, by type

| Question type | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) |
|---|---|---|---|---|---|
| Stable, famous (PopQA) | 0% | 59% | 40% | 59% | 59% |
| Stable, rare (PopQA) - incomplete | 0% | 88% | 75% | 88% | 88% |
| Never-changing (FreshQA) | 4% | 52% | 36% | 54% | 68% |
| Changing (FreshQA) - outdated | 44% | 81% | 42% | 89% | 98% |

## Search quality: each version of the search

Accuracy when ALWAYS searching (200 questions answered by every version).

| Question type | Improved Wikipedia search | Wikipedia + live web |
|---|---|---|
| Stable, famous (PopQA) | 62% | 72% |
| Stable, rare (PopQA) - incomplete | 30% | 62% |
| Never-changing (FreshQA) | 65% | 80% |
| Changing (FreshQA) - outdated | 25% | 49% |
| **All** | 42% | 62% |

## Check 1 on FreshQA (outside data, not used for training)

- Right group (never/slow/fast = LOW/MAYBE/HIGH): 145/240 (60%)
- Fast-changing questions caught as HIGH: 49/80

## Is the difference real? (paired McNemar test)

For each pair: questions only the router got right vs. only the other method got right. p < 0.05 means the difference is unlikely to be chance.

| Router vs. | Only router right | Only other right | p-value |
|---|---|---|---|
| Never search | 150 | 10 | 0.000 * |
| Always search | 9 | 15 | 0.307 |
| Time check only | 121 | 7 | 0.000 * |
| Self-consistency only | 5 | 0 | 0.062 |
| Verbal confidence | 66 | 9 | 0.000 * |

(Compared using: Router (ours).)

## Cutoff rule

Model training cutoff: unknown. With the cutoff rule, questions whose answers change *sometimes* (MAYBE) are also searched when the model's knowledge is more than a year old.

## How to read this

- **Never search** shows what the AI gets wrong on its own (outdated + incomplete knowledge).
- **Always search** is the most expensive option; searching can also hurt when the source is poor.
- **Oracle** searches only when the memory answer is wrong: the best any method could do.
- A good method gets close to the best accuracy while searching far fewer questions.

## Notes

- Scoring: an answer is correct if it contains one of the benchmark's accepted answers (automatic matching; see `experiment_answers.csv` to check by hand).
- FreshQA answers are as of 2026-04-21; a few fast-changing answers may have changed since.
- Questions with a false premise were left out.
