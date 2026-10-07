# Temporal-Risk Router — evaluation report

Main set: 150 questions · Unseen set: 30 questions

## Test 1 — 5-fold cross-validation (main set)

| Router | Accuracy | HIGH caught (recall) | Searches |
|---|---|---|---|
| v1 rules* | 65% | 26/50 (52%) | 17% |
| v2 ML | 63% | 26/50 (52%) | 26% |

*v1's keywords were written while looking at these questions, so this score is optimistic.

## Test 2 — unseen questions

| Router | Accuracy | HIGH caught (recall) | Searches |
|---|---|---|---|
| Never search | 33% | 0/10 (0%) | 0% |
| Always search | 33% | 10/10 (100%) | 100% |
| v1 rules | 57% | 4/10 (40%) | 17% |
| v2 ML | 83% | 8/10 (80%) | 30% |

### v1 confusion matrix (unseen)

| true \ predicted | LOW | AMBIGUOUS | HIGH |
|---|---|---|---|
| LOW | 10 | 0 | 0 |
| AMBIGUOUS | 6 | 3 | 1 |
| HIGH | 6 | 0 | 4 |

### v2 confusion matrix (unseen)

| true \ predicted | LOW | AMBIGUOUS | HIGH |
|---|---|---|---|
| LOW | 7 | 2 | 1 |
| AMBIGUOUS | 0 | 10 | 0 |
| HIGH | 0 | 2 | 8 |

## Misses on unseen questions

| Question | True | v1 | v2 |
|---|---|---|---|
| What is the formula for kinetic energy? | LOW | LOW | AMBIGUOUS |
| Who discovered penicillin? | LOW | LOW | HIGH |
| How does a decision tree split data? | LOW | LOW | AMBIGUOUS |
| Which GPUs are good for training models? | AMBIGUOUS | LOW | AMBIGUOUS |
| What are the working hour limits for international students? | AMBIGUOUS | LOW | AMBIGUOUS |
| What does LG Energy Solution make? | AMBIGUOUS | LOW | AMBIGUOUS |
| What is the passing score for TOPIK level 4? | AMBIGUOUS | HIGH | AMBIGUOUS |
| Which banks let foreigners open accounts in Korea? | AMBIGUOUS | LOW | AMBIGUOUS |
| What benefits do Samsung engineers get? | AMBIGUOUS | LOW | AMBIGUOUS |
| What is the unemployment rate in Korea? | AMBIGUOUS | LOW | AMBIGUOUS |
| Who manages Kakao these days? | HIGH | LOW | HIGH |
| Is Kakao hiring AI engineers? | HIGH | LOW | AMBIGUOUS |
| What is the yen to won rate? | HIGH | LOW | HIGH |
| When is the Samsung GSAT this fall? | HIGH | LOW | HIGH |
| Has the Kyungdong University fall festival been cancelled? | HIGH | LOW | AMBIGUOUS |
| Which team tops the Premier League table? | HIGH | LOW | HIGH |
