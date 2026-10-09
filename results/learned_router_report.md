# Learned router

A logistic-regression model predicts whether the memory answer will be wrong, from signals available before answering: p_low, p_maybe, p_high, agreement, dont_know, confidence, abstained. It decides to search when that is likely. Results are **out-of-fold** (5-fold cross-validation, repeated 5 times): every question is decided by a model that never saw it.

## Accuracy and searches

| Method | llama3.1:8b correct | wrong | searched | qwen2.5:7b correct | wrong | searched |
|---|---|---|---|---|---|---|
| Never search | 43% | 166 | 0% | 35% | 281 | 0% |
| Always search | 67% | 114 | 100% | 68% | 108 | 100% |
| Self-consistency only | 65% | 130 | 66% | 65% | 126 | 73% |
| Verbal confidence | 65% | 127 | 74% | 54% | 189 | 49% |
| Router (ours) | 65% | 127 | 68% | 66% | 120 | 76% |
| Router + cutoff rule (ours) | 67% | 120 | 75% | 66% | 118 | 80% |
| **Learned router (ours)** | 67% | 114 | 91% | 68% | 109 | 91% |
| Oracle (best possible) | 72% | 101 | 57% | 71% | 100 | 65% |

## Is the learned router better? (paired McNemar test)

| Model | Learned vs. | Only learned right | Only other right | p-value |
|---|---|---|---|---|
| llama3.1:8b | Always search | 1 | 1 | 1.000 |
| llama3.1:8b | Self-consistency only | 19 | 6 | 0.015 * |
| llama3.1:8b | Router (ours) | 14 | 4 | 0.031 * |
| qwen2.5:7b | Always search | 0 | 1 | 1.000 |
| qwen2.5:7b | Self-consistency only | 22 | 8 | 0.016 * |
| qwen2.5:7b | Router (ours) | 15 | 8 | 0.210 |

## Does it transfer to another AI model?

Trained on one model's questions, tested on the other model (no retraining).

| Trained on | Tested on | Correct | Searched |
|---|---|---|---|
| llama3.1:8b | qwen2.5:7b | 68% | 90% |
| qwen2.5:7b | llama3.1:8b | 67% | 94% |

## What the model learned

Weights of the final model (standardised signals; positive = more likely to search):

| Signal | Weight |
|---|---|
| dont_know | +0.88 |
| abstained | +0.82 |
| agreement | -0.46 |
| confidence | -0.23 |
| p_high | +0.23 |
| p_low | -0.21 |
| p_maybe | +0.07 |

![Learned router](learned_router_chart.png)
