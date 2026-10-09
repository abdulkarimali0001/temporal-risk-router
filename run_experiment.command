#!/bin/zsh
# Double-click in Finder: runs every experiment, for both AI models.
#   - 500 benchmark questions (FreshQA + PopQA), all methods     -> results/experiment_report*.md
#     (incl. the AI-judged time check and the cheaper knowledge check)
#   - 31 hand-checked questions                                    -> results/answer_evaluation.md
#   - 49 Korean and 32 Swahili questions                           -> results/korean_evaluation*.md, results/swahili_evaluation*.md
#   - measured seconds per step, no caches (30 questions)          -> results/timing_report.md
#   - learned router, accuracy at every search budget, cost model  -> results/learned_router_report.md,
#                                                                     results/curves_report.md, results/cost_report.md
# Search: Wikipedia + live web (Tavily) when keys.txt has a key.
# Most answers are already saved, so this takes about 1-2 hours. Leave the Mac plugged in.
# If it stops, double-click again and it continues.     Log: results/experiment.log
# A bigger model (qwen2.5:14b) is a separate, overnight run: run_bigger_model.command
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
  caffeinate -i python -m src.evaluate_korean data/swahili_test.csv
  [ "$MODEL" = "llama3.1:8b" ] && caffeinate -i python -m src.evaluate_answers > /dev/null
  # timing: only once per model (delete results/timing.csv to measure again)
  python -c "import csv,os,sys;sys.exit(0 if os.path.exists('results/timing.csv') and any(r['model']=='$MODEL' for r in csv.DictReader(open('results/timing.csv'))) else 1)" \
    || caffeinate -i python -m src.timing
done

echo "=== Learned router, curves, cost, timing ==="
./run_reports.command
echo; read "?DONE. Press Enter to close"
