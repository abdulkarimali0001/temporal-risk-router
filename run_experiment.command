#!/bin/zsh
# Double-click in Finder: runs every experiment, for both AI models.
#   - 500 benchmark questions (FreshQA + PopQA), all methods     -> results/experiment_report*.md
#   - 31 hand-checked questions                                    -> results/answer_evaluation.md
#   - 34 Korean questions                                          -> results/korean_evaluation*.md
#   - learned router (trained on the saved results)                -> results/learned_router_report.md
#   - accuracy at every search budget, and cost per question       -> results/curves_report.md, results/cost_report.md
# Search: Wikipedia + live web (Tavily) when keys.txt has a key.
# Takes many hours the first time; leave the Mac plugged in. Everything is cached:
# if it stops, double-click again and it continues.     Log: results/experiment.log
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
mkdir -p results
exec > >(tee -a results/experiment.log) 2>&1
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
python -c "from src import search; print('Live web search:', 'ON' if search.web_enabled() else 'OFF (no key in keys.txt)')"

# 500-question benchmark (the first 200 stay the same)
if [ "$(python -c 'import csv;print(sum(1 for _ in csv.DictReader(open("data/benchmark.csv"))))' 2>/dev/null)" != "500" ]; then
  python -m src.benchmarks --large || { read "?Download failed. Press Enter to close"; exit 1; }
fi

for MODEL in llama3.1:8b qwen2.5:7b; do
  echo "=== Model: $MODEL ==="
  ollama list | grep -q "^$MODEL" || ollama pull "$MODEL"
  export OLLAMA_MODEL=$MODEL
  caffeinate -i python -m src.experiment
  caffeinate -i python -m src.evaluate_korean
  [ "$MODEL" = "llama3.1:8b" ] && caffeinate -i python -m src.evaluate_answers > /dev/null
done

echo "=== Learned router, curves, cost ==="
python -m src.rescore
python -m src.learned_router
python -m src.curves
python -m src.cost
echo; read "?DONE. Press Enter to close"
