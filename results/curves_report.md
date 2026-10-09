# Accuracy at every search budget

Each method ranks the questions by how much they need a search; searching the top k% gives accuracy at that budget. **Area** = mean accuracy over all budgets from 0% to 100% (higher is better), with a 95% bootstrap interval. The learned router uses out-of-fold probabilities (never tested on a question it trained on).

![Curves](curves_chart.png)

## llama3.1:8b (495 questions)

Never search 43% · always search 67%

| Method | Area (95% interval) | at 25% searched | at 50% | at 75% |
|---|---|---|---|---|
| Time check | 55.8% (52.0%-59.6%) | 50% | 56% | 63% |
| Self-consistency | 58.2% (54.5%-62.0%) | 51% | 60% | 66% |
| Verbal confidence | 57.6% (53.6%-61.5%) | 51% | 59% | 65% |
| **Router (ours)** | 58.4% (54.7%-62.4%) | 51% | 60% | 67% |
| **Learned router (ours)** | 59.0% (55.2%-63.0%) | 53% | 60% | 67% |
| Random | 55.2% | 49% | 55% | 61% |
| Oracle | 67.3% | 68% | 72% | 72% |

Paired comparison of areas (same questions resampled; an interval above zero means the router is reliably better):

| Router (ours) vs. | Difference in area | 95% interval |
|---|---|---|
| Time check | +2.6 points | +1.1 to +4.4 * |
| Self-consistency | +0.2 points | -0.1 to +0.6 |
| Verbal confidence | +0.9 points | -0.2 to +1.9 |
| Random | +3.3 points | |

**Cost model.** Total cost per question = share searched + R x share not correct, where R = how many searches one wrong or missing answer is worth. Each method searches the budget that is cheapest for that R (its best point on the curve). Cost relative to always searching (lower is better); in brackets the share of questions searched.

| Method | R = 1 | R = 2 | R = 3 | R = 5 | R = 10 |
|---|---|---|---|---|---|
| Never search | 0.43 (0%) | 0.69 (0%) | 0.87 (0%) | 1.09 (0%) | 1.34 (0%) |
| Always search | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) |
| Time check | 0.43 (0%) | 0.69 (2%) | 0.86 (3%) | 0.97 (87%) | 0.99 (92%) |
| Self-consistency | 0.43 (0%) | 0.69 (0%) | 0.86 (50%) | 0.92 (69%) | 0.97 (70%) |
| Verbal confidence | 0.43 (0%) | 0.69 (0%) | 0.87 (0%) | 0.93 (71%) | 0.98 (71%) |
| **Router (ours)** | 0.43 (0%) | 0.69 (0%) | 0.85 (56%) | 0.91 (67%) | 0.95 (78%) |
| **Learned router (ours)** | 0.43 (0%) | 0.69 (0%) | 0.83 (35%) | 0.89 (62%) | 0.95 (71%) |
| Random | 0.43 (0%) | 0.69 (0%) | 0.87 (0%) | 1.00 (100%) | 1.00 (100%) |

## qwen2.5:7b (499 questions)

Never search 35% · always search 68%

| Method | Area (95% interval) | at 25% searched | at 50% | at 75% |
|---|---|---|---|---|
| Time check | 53.3% (49.5%-57.0%) | 46% | 53% | 62% |
| Self-consistency | 54.0% (50.3%-58.2%) | 45% | 55% | 65% |
| Verbal confidence | 53.3% (50.0%-57.4%) | 45% | 54% | 62% |
| **Router (ours)** | 54.3% (50.7%-58.5%) | 45% | 55% | 66% |
| **Learned router (ours)** | 54.6% (50.8%-58.7%) | 46% | 55% | 65% |
| Random | 51.6% | 44% | 52% | 60% |
| Oracle | 64.8% | 61% | 71% | 71% |

Paired comparison of areas (same questions resampled; an interval above zero means the router is reliably better):

| Router (ours) vs. | Difference in area | 95% interval |
|---|---|---|
| Time check | +1.0 points | -0.6 to +3.0 |
| Self-consistency | +0.3 points | +0.1 to +0.6 * |
| Verbal confidence | +1.0 points | -0.3 to +2.2 |
| Random | +2.7 points | |

**Cost model.** Total cost per question = share searched + R x share not correct, where R = how many searches one wrong or missing answer is worth. Each method searches the budget that is cheapest for that R (its best point on the curve). Cost relative to always searching (lower is better); in brackets the share of questions searched.

| Method | R = 1 | R = 2 | R = 3 | R = 5 | R = 10 |
|---|---|---|---|---|---|
| Never search | 0.49 (0%) | 0.78 (0%) | 0.98 (0%) | 1.23 (0%) | 1.53 (0%) |
| Always search | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) |
| Time check | 0.49 (0%) | 0.78 (1%) | 0.95 (24%) | 0.99 (90%) | 1.00 (100%) |
| Self-consistency | 0.49 (0%) | 0.78 (0%) | 0.91 (73%) | 0.95 (73%) | 1.00 (98%) |
| Verbal confidence | 0.49 (0%) | 0.78 (0%) | 0.95 (43%) | 0.98 (90%) | 1.00 (90%) |
| **Router (ours)** | 0.49 (0%) | 0.78 (0%) | 0.90 (74%) | 0.94 (75%) | 0.97 (82%) |
| **Learned router (ours)** | 0.49 (0%) | 0.78 (0%) | 0.91 (73%) | 0.94 (85%) | 0.96 (88%) |
| Random | 0.49 (0%) | 0.78 (0%) | 0.98 (0%) | 1.00 (100%) | 1.00 (100%) |

