# Measured time per question

Every step timed without any cache on this computer, on a sample of benchmark questions. Seconds per method are worked out from these times and the decisions each method made in the main experiment. Steps run one after another (in the demo app the checks run at the same time as the answer, so users wait less).

## llama3.1:8b (28 questions timed)

| Step | Mean seconds | Median |
|---|---|---|
| memory | 2.36 | 2.24 |
| sample x1 | 0.66 | 0.63 |
| samples x3 | 1.76 | 1.64 |
| confidence | 0.37 | 0.30 |
| time check | 0.02 | 0.02 |
| ai time check | 0.36 | 0.30 |
| search | 24.45 | 23.07 |

| Method | Correct | Seconds / question | vs. always search |
|---|---|---|---|
| Never search | 42% | 2.4 | -90% |
| Always search | 68% | 24.5 | +0% |
| Time check only | 46% | 5.7 | -77% |
| Self-consistency only | 65% | 18.7 | -24% |
| Verbal confidence | 65% | 19.2 | -22% |
| **Router (ours)** | 66% | 19.0 | -22% |
| **Router + cutoff rule (ours)** | 67% | 20.4 | -17% |
| **Router, AI time check (ours)** | 66% | 19.1 | -22% |
| **Router, dated AI time check (ours)** | 66% | 19.4 | -21% |
| **Router, cheap check (ours)** | 66% | 20.8 | -15% |
| **Router, strict check (ours)** | 68% | 22.7 | -7% |

## qwen2.5:7b (28 questions timed)

| Step | Mean seconds | Median |
|---|---|---|
| memory | 2.38 | 1.87 |
| sample x1 | 0.67 | 0.53 |
| samples x3 | 1.45 | 1.08 |
| confidence | 0.71 | 0.62 |
| time check | 0.01 | 0.01 |
| ai time check | 0.36 | 0.31 |
| search | 23.16 | 22.57 |

| Method | Correct | Seconds / question | vs. always search |
|---|---|---|---|
| Never search | 35% | 2.4 | -90% |
| Always search | 68% | 23.2 | +0% |
| Time check only | 42% | 5.5 | -76% |
| Self-consistency only | 65% | 18.9 | -18% |
| Verbal confidence | 54% | 13.3 | -42% |
| **Router (ours)** | 66% | 19.3 | -17% |
| **Router + cutoff rule (ours)** | 66% | 20.3 | -12% |
| **Router, AI time check (ours)** | 66% | 19.7 | -15% |
| **Router, dated AI time check (ours)** | 65% | 19.4 | -16% |
| **Router, cheap check (ours)** | 65% | 20.7 | -10% |
| **Router, strict check (ours)** | 67% | 22.3 | -4% |

