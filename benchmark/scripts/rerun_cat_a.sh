#!/bin/bash
# Category A re-run: 7 models, 21 v2 tasks, ~1068 cases
# Run in tmux for crash safety: tmux new-session -d -s benchmark './scripts/rerun_cat_a.sh'
set -e
cd "$(dirname "$0")/.."

LOG="results/rerun_cat_a_$(date +%Y%m%d_%H%M%S).log"
echo "=== Category A Re-run started at $(date) ===" | tee "$LOG"

CAT_A="gpt-5.5-pro,kimi-k2.6,deepseek/deepseek-v4-pro,o4-mini,nvidia/nemotron-3-super-120b-a12b,MiniMax-M2.7,o3"

TASKS=(
  code_explanation code_generation code_review_v2 data_to_text
  email_summary_v2 extraction_hard_v2 function_calling instruction_following
  intent_clinc150 json_transform_v2 long_summarization moderation_toxigen
  multistep_reasoning ner_extraction rag_qa reasoning_gsm8k
  sentiment_sst2 sql_spider structured_output test_generation_v2
  translation_enfr
)

for task in "${TASKS[@]}"; do
  echo "" | tee -a "$LOG"
  echo ">>> Task: $task at $(date)" | tee -a "$LOG"
  python3 scripts/run_batch.py --task "$task" --models "$CAT_A" --skip-azure 2>&1 | tee -a "$LOG"
  echo ">>> Done: $task at $(date)" | tee -a "$LOG"

  # Commit after each task
  git add results/raw/ results/spend_tracker.json results/benchmark_results.csv 2>/dev/null || true
  git commit -m "data(benchmark): re-run $task for Category A models" 2>/dev/null || true
done

echo "" | tee -a "$LOG"
echo "=== Category A Re-run COMPLETE at $(date) ===" | tee -a "$LOG"

# Rebuild CSV from raw files
echo "Rebuilding CSV..." | tee -a "$LOG"
python3 scripts/rebuild_csv.py 2>&1 | tee -a "$LOG"
git add results/benchmark_results.csv
git commit -m "data(benchmark): rebuild CSV after Category A re-run" 2>/dev/null || true

echo "DONE." | tee -a "$LOG"
