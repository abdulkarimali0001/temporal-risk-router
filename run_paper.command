#!/bin/zsh
# Double-click in Finder: the experiments for the paper. Run it overnight, plugged in,
# with nothing else running (no other .command window, no app). About 12-15 hours.
#   1. builds the HELD-OUT test set (~510 FreshQA + PopQA questions never used before)
#   2. for llama3.1:8b, qwen2.5:7b and qwen2.5:14b:
#        - development set: adds the new baselines (ask-the-AI, token probability, 5 samples)
#        - held-out set: every method, with a time check trained without these questions
#   3. every report, for both sets
# Needs ~510 web searches (Tavily). If credits run out, questions are skipped and listed as
# ERROR; add credits and double-click again - finished questions are kept.
# Log: results/paper.log
source ~/.zprofile 2>/dev/null; source ~/.zshrc 2>/dev/null
cd "$(dirname "$0")"
mkdir -p results
exec > >(tee -a results/paper.log) 2>&1
source ./setup.sh || { read "?Setup failed. Press Enter to close"; exit 1; }
export TRR_REQUIRE_WEB=1 TAVILY_MAX_CALLS=${TAVILY_MAX_CALLS:-1500}
python -c "from src import search; print('Live web search:', 'ON' if search.web_enabled() else 'OFF')"
[ -f data/heldout.csv ] || TRR_SET=heldout python -m src.benchmarks --heldout || { read "?Download failed. Press Enter to close"; exit 1; }

MEM_GB=$(( $(sysctl -n hw.memsize) / 1073741824 ))
MODELS=(llama3.1:8b qwen2.5:7b)
[ "$MEM_GB" -ge 16 ] && MODELS+=(qwen2.5:14b)
for MODEL in $MODELS; do
  echo "=== Model: $MODEL ==="
  ollama list | grep -q "^$MODEL" || ollama pull "$MODEL"
  export OLLAMA_MODEL=$MODEL
  TRR_SET=dev caffeinate -i python -m src.experiment
  TRR_SET=heldout caffeinate -i python -m src.experiment
done
./run_reports.command
grep -c "ERROR" results/paper.log | xargs -I{} echo "Questions with errors in this log: {} (double-click again to redo them)"
echo; read "?DONE. Press Enter to close"
