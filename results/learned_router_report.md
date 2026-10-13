# Learned router

A logistic-regression model predicts whether the memory answer will be wrong, from signals available before answering: p_low, p_maybe, p_high, agreement, dont_know, confidence, abstained. It decides to search when that is likely. Results are **out-of-fold** (5-fold cross-validation, repeated 5 times): every question is decided by a model that never saw it.

## Accuracy and searches

| Method | llama3.1:8b correct | wrong | searched | qwen2.5:7b correct | wrong | searched | qwen2.5:14b correct | wrong | searched |
|---|---|---|---|---|---|---|---|---|---|
| Never search | 42% | 170 | 0% | 35% | 281 | 0% | 40% | 240 | 0% |
| Always search | 68% | 115 | 100% | 68% | 108 | 100% | 70% | 108 | 100% |
| Self-consistency only | 65% | 131 | 66% | 65% | 126 | 73% | 67% | 123 | 72% |
| Verbal confidence | 65% | 129 | 74% | 54% | 189 | 49% | 68% | 122 | 79% |
| Router (ours) | 66% | 128 | 68% | 66% | 120 | 76% | 68% | 123 | 73% |
| Router + cutoff rule (ours) | 67% | 121 | 75% | 66% | 118 | 80% | 70% | 113 | 78% |
| **Learned router (ours)** | 67% | 116 | 91% | 68% | 110 | 90% | 70% | 108 | 92% |
| Oracle (best possible) | 72% | 102 | 58% | 71% | 100 | 65% | 74% | 98 | 60% |

## Is the learned router better? (paired McNemar test)

| Model | Learned vs. | Only learned right | Only other right | p-value |
|---|---|---|---|---|
| llama3.1:8b | Always search | 1 | 2 | 1.000 |
| llama3.1:8b | Self-consistency only | 18 | 6 | 0.023 * |
| llama3.1:8b | Router (ours) | 13 | 4 | 0.049 * |
| qwen2.5:7b | Always search | 2 | 2 | 1.000 |
| qwen2.5:7b | Self-consistency only | 21 | 6 | 0.006 * |
| qwen2.5:7b | Router (ours) | 14 | 6 | 0.115 |
| qwen2.5:14b | Always search | 0 | 0 | 1.000 |
| qwen2.5:14b | Self-consistency only | 20 | 6 | 0.009 * |
| qwen2.5:14b | Router (ours) | 19 | 6 | 0.015 * |

## Does it transfer to another AI model?

Trained on one model's questions, tested on another model (no retraining).

| Trained on | Tested on | Correct | Searched |
|---|---|---|---|
| llama3.1:8b | qwen2.5:7b | 68% | 91% |
| llama3.1:8b | qwen2.5:14b | 70% | 91% |
| qwen2.5:7b | llama3.1:8b | 68% | 94% |
| qwen2.5:7b | qwen2.5:14b | 70% | 94% |
| qwen2.5:14b | llama3.1:8b | 67% | 78% |
| qwen2.5:14b | qwen2.5:7b | 66% | 81% |

## What the model learned

Weights of the final model (standardised signals; positive = more likely to search):

| Signal | Weight |
|---|---|
| dont_know | +0.92 |
| abstained | +0.74 |
| agreement | -0.43 |
| p_high | +0.24 |
| confidence | -0.22 |
| p_low | -0.22 |
| p_maybe | +0.08 |

![Learned router](learned_router_chart.png)
