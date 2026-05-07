#!/bin/bash
# 2-hour test: VA@42 and VE@42 with new simplified physics.
set -u
cd "$(dirname "$0")"
REPO_DIR="$(pwd)"
VIEWER_DIR="${VIEWER_DIR:-../Gaara_Animism_Viewer}"
LOG_FILE="$REPO_DIR/RUNS_LOG.md"
ORCH_LOG="$REPO_DIR/orchestrator.log"

echo "=== 2hr orchestrator started $(date) ===" >> "$ORCH_LOG"

RUNS=(
  "VA 42 newphys"
  "VE 42 newphys"
)

for spec in "${RUNS[@]}"; do
  VARIANT=$(echo "$spec" | cut -d' ' -f1)
  SEED=$(echo "$spec" | cut -d' ' -f2)
  TAG=$(echo "$spec" | cut -d' ' -f3)
  LABEL="${VARIANT}_s${SEED}_${TAG}"
  echo "[$(date)] === starting $LABEL ===" >> "$ORCH_LOG"

  python3 main.py \
    --scenario scripted_100 \
    --seed "$SEED" \
    --label "$LABEL" \
    --dna-variant "$VARIANT" \
    >> "$ORCH_LOG" 2>&1
  RC=$?
  if [ "$RC" -ne 0 ]; then
    echo "[$(date)] !! $LABEL exited $RC" >> "$ORCH_LOG"
    continue
  fi

  RUN_DIR=$(ls -td "saved_simulations/scripted_100"/*"_${LABEL}" 2>/dev/null | head -1)
  if [ -z "$RUN_DIR" ]; then
    echo "[$(date)] !! could not locate run dir for $LABEL" >> "$ORCH_LOG"
    continue
  fi
  python3 analyze_run.py "$RUN_DIR" --log "$LOG_FILE" >> "$ORCH_LOG" 2>&1 || true
  python3 "$VIEWER_DIR/scripts/bundle_run.py" "$RUN_DIR" --out "$VIEWER_DIR/public/runs" >> "$ORCH_LOG" 2>&1 || true
done

echo "[$(date)] === 2hr orchestrator complete ===" >> "$ORCH_LOG"
