#!/bin/bash
# Overnight prompt-variant sweep — 100-step scripted scenario.
# 7 runs interleaved so each variant has at least one seed early:
#   VA@42, VD@42, VB@42, VC@42, VA@101, VD@101, VD@202
# Auto-analyze + bundle each. Comparison summary written to FINDINGS.md.

set -u
cd "$(dirname "$0")"
REPO_DIR="$(pwd)"
VIEWER_DIR="${VIEWER_DIR:-../Gaara_Animism_Viewer}"
LOG_FILE="$REPO_DIR/RUNS_LOG.md"
ORCH_LOG="$REPO_DIR/orchestrator.log"

echo "=== orchestrator started $(date) ===" >> "$ORCH_LOG"

# Wait for any in-flight main.py to finish.
while pgrep -f "python3 main.py" > /dev/null; do
  echo "[$(date)] waiting for in-flight main.py..." >> "$ORCH_LOG"
  sleep 30
done

# Order: control + heavy variant first; weight VD with extra seeds.
RUNS=(
  "VA 42"
  "VD 42"
  "VB 42"
  "VC 42"
  "VA 101"
  "VD 101"
  "VD 202"
)

for spec in "${RUNS[@]}"; do
  VARIANT=$(echo "$spec" | cut -d' ' -f1)
  SEED=$(echo "$spec" | cut -d' ' -f2)
  LABEL="${VARIANT}_s${SEED}"
  echo "[$(date)] === starting $LABEL ===" >> "$ORCH_LOG"

  python3 main.py \
    --scenario scripted_100 \
    --seed "$SEED" \
    --label "$LABEL" \
    --dna-variant "$VARIANT" \
    >> "$ORCH_LOG" 2>&1
  RC=$?
  if [ "$RC" -ne 0 ]; then
    echo "[$(date)] !! $LABEL exited $RC, continuing" >> "$ORCH_LOG"
    continue
  fi

  RUN_DIR=$(ls -td "saved_simulations/scripted_100"/*"_${LABEL}" 2>/dev/null | head -1)
  if [ -z "$RUN_DIR" ]; then
    echo "[$(date)] !! could not locate run dir for $LABEL" >> "$ORCH_LOG"
    continue
  fi

  echo "[$(date)] analyzing $RUN_DIR" >> "$ORCH_LOG"
  python3 analyze_run.py "$RUN_DIR" --log "$LOG_FILE" >> "$ORCH_LOG" 2>&1 || true

  echo "[$(date)] bundling $RUN_DIR" >> "$ORCH_LOG"
  python3 "$VIEWER_DIR/scripts/bundle_run.py" "$RUN_DIR" --out "$VIEWER_DIR/public/runs" >> "$ORCH_LOG" 2>&1 || true
done

echo "[$(date)] === orchestrator complete ===" >> "$ORCH_LOG"

# Final comparison summary across all scripted_100 runs.
python3 - <<'PY' >> "$ORCH_LOG" 2>&1
import json, statistics
from pathlib import Path
runs = sorted(Path("saved_simulations/scripted_100").iterdir(), key=lambda p: p.name)
analyses = []
for r in runs:
    a = r / "analysis.json"
    if a.exists():
        analyses.append(json.loads(a.read_text()))

if not analyses:
    print("no analyses found"); raise SystemExit

by_variant = {}
for a in analyses:
    by_variant.setdefault(a["dna_variant"], []).append(a)

lines = ["", f"## scripted_100 sweep — variant comparison", ""]
lines.append("| variant | n | response_t | intercept | urg_σ | host_σ | %close | h̄ | ū |")
lines.append("|---|---|---|---|---|---|---|---|---|")
for v in ("VA","VB","VC","VD","V1","V2","V3","V4"):
    if v not in by_variant: continue
    rs = by_variant[v]
    rts = [a["response_time_v1"] for a in rs if a["response_time_v1"] is not None]
    rt_str = f"{statistics.mean(rts):.0f}" if rts else "—"
    intercept = statistics.mean(a["interception_score"] for a in rs)
    urg_sig = statistics.mean(a["urgency_stdev_mean"] for a in rs)
    host_sig = statistics.mean(a["hostility_stdev_mean"] for a in rs)
    close_pct = statistics.mean(a["final_within_5_units_pct"] for a in rs)
    h_bar = statistics.mean(a["mean_hostility_overall"] for a in rs)
    u_bar = statistics.mean(a["mean_urgency_overall"] for a in rs)
    lines.append(f"| {v} | {len(rs)} | {rt_str} | {intercept:.3f} | {urg_sig:.3f} | {host_sig:.3f} | {close_pct:.1f}% | {h_bar:+.2f} | {u_bar:.2f} |")

with open("FINDINGS.md", "a") as f:
    f.write("\n".join(lines) + "\n")
print("FINDINGS.md updated.")
PY

echo "[$(date)] === all done ===" >> "$ORCH_LOG"
