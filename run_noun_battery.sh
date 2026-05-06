#!/bin/bash
# Single-variable warrior-noun battery — 5 runs, each ~50 min.
# Holds VC × M5 × scripted_70 × seed 42 × reasoning constant.
# Only the role noun changes ("twenty motes" → "twenty <noun>s") in the DNA.
set -u
cd "$(dirname "$0")"
REPO_DIR="$(pwd)"
VIEWER_DIR="/Users/yukitakashima/Desktop/PUBLISH/Gaara_Animism_Viewer"
LOG_FILE="$REPO_DIR/RUNS_LOG.md"
ORCH_LOG="$REPO_DIR/orchestrator.log"

echo "" >> "$ORCH_LOG"
echo "=== noun battery started $(date) ===" >> "$ORCH_LOG"
while pgrep -f "python3 main.py" > /dev/null; do sleep 30; done

NOUNS=(guardian warrior sentinel defender vanguard)

for NOUN in "${NOUNS[@]}"; do
  LABEL="noun_${NOUN}_VC_M5_s42"
  echo "[$(date)] === starting $LABEL ===" >> "$ORCH_LOG"
  python3 main.py \
    --scenario scripted_70 \
    --seed 42 \
    --label "$LABEL" \
    --dna-variant VC \
    --mother-variant M5 \
    --role-noun "$NOUN" \
    >> "$ORCH_LOG" 2>&1
  RC=$?
  if [ "$RC" -ne 0 ]; then
    echo "[$(date)] !! $LABEL exited $RC" >> "$ORCH_LOG"; continue
  fi
  RUN_DIR=$(ls -td "saved_simulations/scripted_70"/*"_${LABEL}" 2>/dev/null | head -1)
  [ -z "$RUN_DIR" ] && { echo "[$(date)] !! cannot locate $LABEL" >> "$ORCH_LOG"; continue; }
  python3 analyze_run.py "$RUN_DIR" --log "$LOG_FILE" >> "$ORCH_LOG" 2>&1 || true
  python3 score_diversity.py "$RUN_DIR" >> "$ORCH_LOG" 2>&1 || true
  python3 "$VIEWER_DIR/scripts/bundle_run.py" "$RUN_DIR" --out "$VIEWER_DIR/public/runs" >> "$ORCH_LOG" 2>&1 || true
done

echo "[$(date)] === noun battery complete ===" >> "$ORCH_LOG"
