# Experiment: when should the AI search?

Model `llama3.1:8b` · 2026-10-07 · 197/200 questions from public benchmarks (FreshQA 2026-04-21, PopQA)

## Main result

| Method | Correct (95% interval) | Wrong | No guess | Searched |
|---|---|---|---|---|
| Never search | 41% (34%-47%) | 74 | 43 | 0% |
| Always search | 44% (37%-51%) | 35 | 75 | 100% |
| Time check only | 42% (35%-49%) | 58 | 56 | 27% |
| Self-consistency only | 46% (40%-53%) | 38 | 68 | 69% |
| Verbal confidence | 45% (38%-52%) | 38 | 70 | 76% |
| **Router (ours)** | 47% (40%-54%) | 35 | 70 | 74% |
| Oracle (best possible) | 56% (49%-62%) | 25 | 62 | 59% |

![Accuracy vs. searches](experiment_chart.png)

## Correct answers by question type

| Question type | n | Never search | Always search | Time check only | Self-consistency only | Verbal confidence | Router (ours) | Oracle (best possible) |
|---|---|---|---|---|---|---|---|---|
| Stable, famous (PopQA) | 40 | 65% | 75% | 70% | 78% | 75% | 78% | 80% |
| Stable, rare (PopQA) - incomplete | 39 | 21% | 36% | 21% | 33% | 36% | 33% | 36% |
| Never-changing (FreshQA) | 39 | 74% | 56% | 72% | 69% | 64% | 69% | 87% |
| Changing (FreshQA) - outdated | 79 | 22% | 27% | 24% | 25% | 25% | 27% | 38% |

## Share of questions searched, by type

| Question type | Time check only | Self-consistency only | Verbal confidence | Router (ours) |
|---|---|---|---|---|
| Stable, famous (PopQA) | 18% | 50% | 68% | 55% |
| Stable, rare (PopQA) - incomplete | 8% | 87% | 90% | 87% |
| Never-changing (FreshQA) | 5% | 44% | 44% | 46% |
| Changing (FreshQA) - outdated | 52% | 82% | 90% | 91% |

## Check 1 on FreshQA (outside data, not used for training)

- Right group (never/slow/fast = LOW/MAYBE/HIGH): 61/118 (52%)
- Fast-changing questions caught as HIGH: 24/40

## How to read this

- **Never search** shows what the AI gets wrong on its own (outdated + incomplete knowledge).
- **Always search** is the most expensive option; searching can also hurt when the source is poor.
- **Oracle** searches only when the memory answer is wrong: the best any method could do.
- A good method gets close to the best accuracy while searching far fewer questions.

## Notes

- Scoring: an answer is correct if it contains one of the benchmark's accepted answers (automatic matching; see `experiment_answers.csv` to check by hand).
- FreshQA answers are as of 2026-04-21; a few fast-changing answers may have changed since.
- Questions with a false premise were left out.
