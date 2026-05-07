#!/bin/bash
# Mote baseline — runs after the noun battery finishes, completes the
# 6-row comparison: 5 warrior nouns + mote (neutral control), all with
# reasoning field on, all VC × M5 × scripted_70 × seed 42.
set -u
cd "$(dirname "$0")"
REPO_DIR="$(pwd)"
VIEWER_DIR="${VIEWER_DIR:-../Gaara_Animism_Viewer}"
LOG_FILE="$REPO_DIR/RUNS_LOG.md"
ORCH_LOG="$REPO_DIR/orchestrator.log"

# Wait for the noun battery (and any other main.py) to finish first.
while pgrep -f "python3 main.py" > /dev/null; do sleep 30; done

LABEL="noun_mote_VC_M5_s42"
echo "[$(date)] === starting $LABEL (control) ===" >> "$ORCH_LOG"
python3 main.py \
  --scenario scripted_70 \
  --seed 42 \
  --label "$LABEL" \
  --dna-variant VC \
  --mother-variant M5 \
  --role-noun mote \
  >> "$ORCH_LOG" 2>&1
RC=$?
if [ "$RC" -ne 0 ]; then
  echo "[$(date)] !! $LABEL exited $RC" >> "$ORCH_LOG"; exit 0
fi
RUN_DIR=$(ls -td "saved_simulations/scripted_70"/*"_${LABEL}" 2>/dev/null | head -1)
[ -z "$RUN_DIR" ] && { echo "[$(date)] !! cannot locate $LABEL" >> "$ORCH_LOG"; exit 0; }
python3 analyze_run.py "$RUN_DIR" --log "$LOG_FILE" >> "$ORCH_LOG" 2>&1 || true
python3 score_diversity.py "$RUN_DIR" >> "$ORCH_LOG" 2>&1 || true
python3 "$VIEWER_DIR/scripts/bundle_run.py" "$RUN_DIR" --out "$VIEWER_DIR/public/runs" >> "$ORCH_LOG" 2>&1 || true
echo "[$(date)] === mote baseline complete (battery now full 6-row) ===" >> "$ORCH_LOG"
