# Accuracy at every search budget

Each method ranks the questions by how much they need a search; searching the top k% gives accuracy at that budget. **Area** = mean accuracy over all budgets from 0% to 100% (higher is better), with a 95% bootstrap interval. The learned router uses out-of-fold probabilities (never tested on a question it trained on).

![Curves](curves_chart.png)

## llama3.1:8b (499 questions)

Never search 42% · always search 68%

| Method | Area (95% interval) | at 25% searched | at 50% | at 75% |
|---|---|---|---|---|
| Time check | 55.6% (52.5%-59.2%) | 50% | 56% | 63% |
| Self-consistency | 58.2% (54.4%-62.1%) | 51% | 60% | 66% |
| Verbal confidence | 57.6% (53.9%-61.3%) | 51% | 59% | 65% |
| **Router (ours)** | 58.3% (54.6%-62.2%) | 51% | 60% | 67% |
| **Learned router (ours)** | 58.9% (55.2%-63.2%) | 53% | 60% | 67% |
| Random | 55.0% | 49% | 55% | 61% |
| Oracle | 67.2% | 68% | 72% | 72% |

Paired comparison of areas (same questions resampled; an interval above zero means the router is reliably better):

| Router (ours) vs. | Difference in area | 95% interval |
|---|---|---|
| Time check | +2.7 points | +1.0 to +4.3 * |
| Self-consistency | +0.2 points | -0.1 to +0.5 |
| Verbal confidence | +0.8 points | -0.2 to +1.9 |
| Random | +3.3 points | |

**Cost model.** Total cost per question = share searched + R x share not correct, where R = how many searches one wrong or missing answer is worth. Each method searches the budget that is cheapest for that R (its best point on the curve). Cost relative to always searching (lower is better); in brackets the share of questions searched.

| Method | R = 1 | R = 2 | R = 3 | R = 5 | R = 10 |
|---|---|---|---|---|---|
| Never search | 0.43 (0%) | 0.70 (0%) | 0.87 (0%) | 1.10 (0%) | 1.35 (0%) |
| Always search | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) |
| Time check | 0.43 (0%) | 0.70 (2%) | 0.87 (3%) | 0.97 (87%) | 0.99 (92%) |
| Self-consistency | 0.43 (0%) | 0.70 (0%) | 0.87 (63%) | 0.92 (67%) | 0.97 (70%) |
| Verbal confidence | 0.43 (0%) | 0.70 (0%) | 0.87 (10%) | 0.93 (71%) | 0.98 (86%) |
| **Router (ours)** | 0.43 (0%) | 0.70 (0%) | 0.86 (64%) | 0.91 (68%) | 0.95 (78%) |
| **Learned router (ours)** | 0.43 (0%) | 0.70 (0%) | 0.83 (34%) | 0.90 (70%) | 0.94 (73%) |
| Random | 0.43 (0%) | 0.70 (0%) | 0.87 (0%) | 1.00 (100%) | 1.00 (100%) |

## qwen2.5:7b (499 questions)

Never search 35% · always search 68%

| Method | Area (95% interval) | at 25% searched | at 50% | at 75% |
|---|---|---|---|---|
| Time check | 53.3% (49.5%-57.0%) | 46% | 53% | 62% |
| Self-consistency | 54.0% (50.3%-58.2%) | 45% | 55% | 65% |
| Verbal confidence | 53.3% (50.0%-57.4%) | 45% | 54% | 62% |
| **Router (ours)** | 54.3% (50.7%-58.5%) | 45% | 55% | 66% |
| **Learned router (ours)** | 54.7% (50.9%-58.8%) | 46% | 55% | 65% |
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
| **Learned router (ours)** | 0.49 (0%) | 0.78 (0%) | 0.91 (79%) | 0.94 (84%) | 0.96 (87%) |
| Random | 0.49 (0%) | 0.78 (0%) | 0.98 (0%) | 1.00 (100%) | 1.00 (100%) |

## qwen2.5:14b (497 questions)

Never search 40% · always search 70%

| Method | Area (95% interval) | at 25% searched | at 50% | at 75% |
|---|---|---|---|---|
| Time check | 57.4% (53.7%-61.6%) | 50% | 58% | 66% |
| Self-consistency | 57.9% (54.5%-62.2%) | 49% | 59% | 68% |
| Verbal confidence | 57.4% (54.1%-61.4%) | 48% | 59% | 67% |
| **Router (ours)** | 58.2% (54.7%-62.5%) | 49% | 59% | 69% |
| **Learned router (ours)** | 59.0% (55.3%-63.2%) | 51% | 60% | 69% |
| Random | 54.9% | 47% | 55% | 63% |
| Oracle | 68.0% | 65% | 74% | 74% |

Paired comparison of areas (same questions resampled; an interval above zero means the router is reliably better):

| Router (ours) vs. | Difference in area | 95% interval |
|---|---|---|
| Time check | +0.8 points | -0.9 to +2.6 |
| Self-consistency | +0.3 points | +0.2 to +0.5 * |
| Verbal confidence | +0.8 points | -0.5 to +2.0 |
| Random | +3.3 points | |

**Cost model.** Total cost per question = share searched + R x share not correct, where R = how many searches one wrong or missing answer is worth. Each method searches the budget that is cheapest for that R (its best point on the curve). Cost relative to always searching (lower is better); in brackets the share of questions searched.

| Method | R = 1 | R = 2 | R = 3 | R = 5 | R = 10 |
|---|---|---|---|---|---|
| Never search | 0.47 (0%) | 0.76 (0%) | 0.96 (0%) | 1.21 (0%) | 1.52 (0%) |
| Always search | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) | 1.00 (100%) |
| Time check | 0.47 (0%) | 0.75 (1%) | 0.90 (36%) | 0.97 (80%) | 0.99 (100%) |
| Self-consistency | 0.47 (0%) | 0.76 (0%) | 0.89 (68%) | 0.94 (72%) | 1.00 (82%) |
| Verbal confidence | 0.47 (0%) | 0.76 (0%) | 0.90 (59%) | 0.96 (79%) | 1.00 (100%) |
| **Router (ours)** | 0.47 (0%) | 0.76 (0%) | 0.89 (69%) | 0.92 (79%) | 0.95 (79%) |
| **Learned router (ours)** | 0.47 (0%) | 0.75 (12%) | 0.87 (64%) | 0.92 (77%) | 0.95 (81%) |
| Random | 0.47 (0%) | 0.76 (0%) | 0.96 (0%) | 1.00 (100%) | 1.00 (100%) |

