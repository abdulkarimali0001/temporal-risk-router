# Experiment: when should the AI search?

Model `qwen2.5:7b` · 2026-10-08 · 200/200 questions from public benchmarks (FreshQA 2026-04-21, PopQA)

## Main result

| Method | Correct (95% interval) | Wrong | No guess | Searched |
|---|---|---|---|---|
| Never search | 35% (29%-42%) | 108 | 22 | 0% |
| Always search | 42% (35%-48%) | 40 | 77 | 100% |
| Time check only | 36% (29%-42%) | 99 | 30 | 18% |
| Self-consistency only | 41% (34%-48%) | 49 | 69 | 69% |
| Verbal confidence | 36% (30%-43%) | 71 | 56 | 50% |
| **Router (ours)** | 41% (34%-48%) | 48 | 70 | 72% |
| **Router + cutoff rule (ours)** | 42% (34%-48%) | 45 | 72 | 80% |
| Oracle (best possible) | 49% (42%-56%) | 33 | 69 | 65% |

![Accuracy vs. searches](experiment_chart_qwen2.5-7b.png)

## Correct answers by question type

| Question type | n | Never search | Always search | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) | Oracle (best possible) |
|---|---|---|---|---|---|---|---|---|---|
| Stable, famous (PopQA) | 40 | 62% | 62% | 62% | 65% | 65% | 65% | 65% | 70% |
| Stable, rare (PopQA) - incomplete | 40 | 25% | 30% | 25% | 30% | 30% | 30% | 30% | 32% |
| Never-changing (FreshQA) | 40 | 57% | 65% | 55% | 65% | 55% | 62% | 62% | 78% |
| Changing (FreshQA) - outdated | 80 | 15% | 25% | 18% | 22% | 16% | 24% | 25% | 32% |

## Share of questions searched, by type

| Question type | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Router + cutoff rule (ours) |
|---|---|---|---|---|---|
| Stable, famous (PopQA) | 0% | 52% | 28% | 52% | 52% |
| Stable, rare (PopQA) - incomplete | 0% | 88% | 95% | 88% | 88% |
| Never-changing (FreshQA) | 2% | 48% | 40% | 50% | 68% |
| Changing (FreshQA) - outdated | 45% | 79% | 44% | 86% | 98% |

## Check 1 on FreshQA (outside data, not used for training)

- Right group (never/slow/fast = LOW/MAYBE/HIGH): 76/120 (63%)
- Fast-changing questions caught as HIGH: 25/40

## Is the difference real? (paired McNemar test)

For each pair: questions only the router got right vs. only the other method got right. p < 0.05 means the difference is unlikely to be chance.

| Router vs. | Only router right | Only other right | p-value |
|---|---|---|---|
| Never search | 25 | 12 | 0.047 * |
| Always search | 3 | 3 | 1.000 |
| Time check only | 21 | 9 | 0.043 * |
| Self-consistency only | 6 | 5 | 1.000 |
| Verbal confidence | 18 | 8 | 0.076 |

(Compared using: Router + cutoff rule (ours).)

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
