#!/bin/zsh
# Rebuilds every report from the saved answers (no AI needed, a few minutes),
# for the development set and, if it has been run, the held-out test set.
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
source .venv/bin/activate 2>/dev/null || source ./setup.sh
for SET in dev heldout; do
  [ "$SET" = "heldout" ] && [ ! -f results/experiment_answers_heldout.csv ] && continue
  echo "=== Reports: $SET set ==="
  export TRR_SET=$SET
  python -m src.rescore
  python -m src.learned_router
  python -m src.curves
  python -m src.cost
  python -m src.ablations
done
unset TRR_SET
[ -f results/timing.csv ] && python -m src.timing --report
