#!/bin/bash
# VG (no subject-object grammar) battery — 3 runs:
#   1. big test: VG × scripted_70 × M5 × seed 42 (multi-attacker, full scenario)
#   2. sanity:   VG × const_extreme × seed 101 (replicates A/B at new seed)
#   3. bonus:    VG × const_calm × seed 42 (does softer Mother let VG reach full interpretation?)
set -u
cd "$(dirname "$0")"
REPO_DIR="$(pwd)"
VIEWER_DIR="${VIEWER_DIR:-../Gaara_Animism_Viewer}"
LOG_FILE="$REPO_DIR/RUNS_LOG.md"
ORCH_LOG="$REPO_DIR/orchestrator.log"

echo "" >> "$ORCH_LOG"
echo "=== VG battery started $(date) ===" >> "$ORCH_LOG"

while pgrep -f "python3 main.py" > /dev/null; do sleep 30; done

RUNS=(
  "scripted_70|VG|M5|42|big_VG_M5_s42"
  "const_extreme|VG|M1|101|sanity_VG_const_extreme_s101"
  "const_calm|VG|M1|42|bonus_VG_const_calm_s42"
)

for spec in "${RUNS[@]}"; do
  IFS='|' read -r SCENARIO DNA MOTHER SEED LABEL <<< "$spec"
  echo "[$(date)] === starting $LABEL ===" >> "$ORCH_LOG"
  python3 main.py --scenario "$SCENARIO" --seed "$SEED" --label "$LABEL" \
      --dna-variant "$DNA" --mother-variant "$MOTHER" >> "$ORCH_LOG" 2>&1
  RC=$?
  if [ "$RC" -ne 0 ]; then
    echo "[$(date)] !! $LABEL exited $RC" >> "$ORCH_LOG"; continue
  fi
  RUN_DIR=$(ls -td "saved_simulations/$SCENARIO"/*"_${LABEL}" 2>/dev/null | head -1)
  [ -z "$RUN_DIR" ] && { echo "[$(date)] !! cannot locate $LABEL" >> "$ORCH_LOG"; continue; }
  python3 analyze_run.py "$RUN_DIR" --log "$LOG_FILE" >> "$ORCH_LOG" 2>&1 || true
  python3 score_diversity.py "$RUN_DIR" >> "$ORCH_LOG" 2>&1 || true
  python3 "$VIEWER_DIR/scripts/bundle_run.py" "$RUN_DIR" --out "$VIEWER_DIR/public/runs" >> "$ORCH_LOG" 2>&1 || true
done

echo "[$(date)] === VG battery complete ===" >> "$ORCH_LOG"
