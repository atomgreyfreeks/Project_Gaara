#!/bin/bash
# Follow-up runs from the v3 sweep findings.
# 1. iter_VC_M4_s42      — does VC's relational hint amplify M4's directional signal?
# 2. iter_VA_M4_s202     — third seed of M4 baseline for stability
# 3. iter_VC_const_extreme — VC at constant-extreme to test premium prompt's pure-interpretation amplification
set -u
cd "$(dirname "$0")"
REPO_DIR="$(pwd)"
VIEWER_DIR="${VIEWER_DIR:-../Gaara_Animism_Viewer}"
LOG_FILE="$REPO_DIR/RUNS_LOG.md"
ORCH_LOG="$REPO_DIR/orchestrator.log"

echo "" >> "$ORCH_LOG"
echo "=== iter_v3 (3 follow-ups) started $(date) ===" >> "$ORCH_LOG"

while pgrep -f "python3 main.py" > /dev/null; do
  sleep 30
done

RUNS=(
  "scripted_70|VC|M4|42|iter_VC_M4_s42"
  "scripted_70|VA|M4|202|iter_VA_M4_s202"
  "const_extreme|VC|M1|42|iter_VC_const_extreme"
)
for spec in "${RUNS[@]}"; do
  IFS='|' read -r SCENARIO DNA MOTHER SEED LABEL <<< "$spec"
  echo "[$(date)] === starting $LABEL  (scenario=$SCENARIO dna=$DNA mother=$MOTHER seed=$SEED) ===" >> "$ORCH_LOG"

  python3 main.py \
    --scenario "$SCENARIO" \
    --seed "$SEED" \
    --label "$LABEL" \
    --dna-variant "$DNA" \
    --mother-variant "$MOTHER" \
    >> "$ORCH_LOG" 2>&1
  RC=$?
  if [ "$RC" -ne 0 ]; then
    echo "[$(date)] !! $LABEL exited $RC" >> "$ORCH_LOG"; continue
  fi

  RUN_DIR=$(ls -td "saved_simulations/$SCENARIO"/*"_${LABEL}" 2>/dev/null | head -1)
  [ -z "$RUN_DIR" ] && { echo "[$(date)] !! cannot locate $LABEL" >> "$ORCH_LOG"; continue; }
  python3 analyze_run.py "$RUN_DIR" --log "$LOG_FILE" >> "$ORCH_LOG" 2>&1 || true
  python3 "$VIEWER_DIR/scripts/bundle_run.py" "$RUN_DIR" --out "$VIEWER_DIR/public/runs" >> "$ORCH_LOG" 2>&1 || true
done

echo "[$(date)] === iter_v3 complete ===" >> "$ORCH_LOG"
