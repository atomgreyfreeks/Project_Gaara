#!/bin/bash
# Overnight 16-run sweep + auto-analysis + bundle.
# Block A — Mother phrasing sweep (scripted_70):
#   M1@42, M1@101, M2@42, M3@42, M3@101, M4@42, M4@101  (7 runs)
# Block B — Constant-state diagnostic (40 steps, no attacker):
#   const_calm, const_faint, const_immediate, const_extreme  (4 runs, seed 42)
# Block C — Signaling architecture (scripted_70 with awareness range varied):
#   aware8 + M1@42, aware2 + M1@42, aware6 + M3@42  (3 runs)
# Block D — Premium combo + replication (scripted_70):
#   VC + winning Mother @42  ← decided after Block A finishes (placeholder M3)
#   VA + M1 @202 (extra seed for noise floor)  (2 runs)
# Total: 16 runs, ~8.5 hr expected.

set -u
cd "$(dirname "$0")"
REPO_DIR="$(pwd)"
VIEWER_DIR="${VIEWER_DIR:-../Gaara_Animism_Viewer}"
LOG_FILE="$REPO_DIR/RUNS_LOG.md"
ORCH_LOG="$REPO_DIR/orchestrator.log"

echo "" >> "$ORCH_LOG"
echo "=== overnight v3 sweep started $(date) ===" >> "$ORCH_LOG"

# Wait for any in-flight main.py to finish.
while pgrep -f "python3 main.py" > /dev/null; do
  echo "[$(date)] waiting for in-flight main.py..." >> "$ORCH_LOG"
  sleep 30
done

# spec format: SCENARIO|DNA|MOTHER|SEED|LABEL
RUNS=(
  # Block A — Mother phrasing sweep (scripted_70)
  "scripted_70|VA|M1|42|A_M1_s42"
  "scripted_70|VA|M1|101|A_M1_s101"
  "scripted_70|VA|M2|42|A_M2_s42"
  "scripted_70|VA|M3|42|A_M3_s42"
  "scripted_70|VA|M3|101|A_M3_s101"
  "scripted_70|VA|M4|42|A_M4_s42"
  "scripted_70|VA|M4|101|A_M4_s101"
  # Block B — Constant-state isolated diagnostic
  "const_calm|VA|M1|42|B_calm"
  "const_faint|VA|M1|42|B_faint"
  "const_immediate|VA|M1|42|B_immediate"
  "const_extreme|VA|M1|42|B_extreme"
  # Block C — Signaling architecture
  "scripted_70_aware8|VA|M1|42|C_aware8"
  "scripted_70_aware2|VA|M1|42|C_aware2"
  "scripted_70_aware6|VA|M3|42|C_aware6_M3"
  # Block D — Premium combo + replication
  "scripted_70|VC|M3|42|D_VC_M3"
  "scripted_70|VA|M1|202|D_VA_M1_s202"
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
    echo "[$(date)] !! $LABEL exited $RC, continuing" >> "$ORCH_LOG"
    continue
  fi

  RUN_DIR=$(ls -td "saved_simulations/$SCENARIO"/*"_${LABEL}" 2>/dev/null | head -1)
  if [ -z "$RUN_DIR" ]; then
    echo "[$(date)] !! could not locate run dir for $LABEL" >> "$ORCH_LOG"
    continue
  fi

  python3 analyze_run.py "$RUN_DIR" --log "$LOG_FILE" >> "$ORCH_LOG" 2>&1 || true
  python3 "$VIEWER_DIR/scripts/bundle_run.py" "$RUN_DIR" --out "$VIEWER_DIR/public/runs" >> "$ORCH_LOG" 2>&1 || true
done

echo "[$(date)] === main 16-run sweep complete ===" >> "$ORCH_LOG"

# Comparison summary appended to FINDINGS.md.
python3 - <<'PY' >> "$ORCH_LOG" 2>&1
import json, statistics
from pathlib import Path
def gather(scenarios):
    rows = []
    for sc in scenarios:
        d = Path("saved_simulations") / sc
        if not d.is_dir(): continue
        for run in sorted(d.iterdir()):
            a = run / "analysis.json"
            if a.exists():
                rows.append(json.loads(a.read_text()))
    return rows

block_A = gather(["scripted_70"])
block_B = gather(["const_calm","const_faint","const_immediate","const_extreme"])
block_C = gather(["scripted_70_aware8","scripted_70_aware2","scripted_70_aware6"])

lines = ["", "## scripted_70 v3 sweep — overnight summary", ""]
lines.append("### Block A · Mother phrasing (scripted_70, VA prompt)")
lines.append("| label | mother | seed | response_t | intercept | pre_flip_x | post_flip_x | host_σ | %close |")
lines.append("|---|---|---|---|---|---|---|---|---|")
for a in block_A:
    if "A_" in str(a["run_dir"]) or "D_" in str(a["run_dir"]):
        lines.append(f"| {Path(a['run_dir']).name.split('_',2)[-1]} | {a.get('mother_variant','-')} | {a['seed']} | {a['response_time_v1']} | {a['interception_score']} | **{a['pre_flip_mean_ideal_x']}** | {a['post_flip_mean_ideal_x']} | {a['hostility_stdev_mean']} | {a['final_within_5_units_pct']}% |")

lines.append("")
lines.append("### Block B · Constant-state diagnostic (40 steps, no attacker, VA prompt)")
lines.append("| label | mean_urg | mean_host | pre_flip_ideal_x | %close |")
lines.append("|---|---|---|---|---|")
for a in block_B:
    lines.append(f"| {Path(a['run_dir']).name.split('_',2)[-1]} | {a['mean_urgency_overall']} | {a['mean_hostility_overall']} | {a['pre_flip_mean_ideal_x']} | {a['final_within_5_units_pct']}% |")

lines.append("")
lines.append("### Block C · Signaling architecture")
lines.append("| label | response_t | intercept | pre_flip_x | post_flip_x |")
lines.append("|---|---|---|---|---|")
for a in block_C:
    lines.append(f"| {Path(a['run_dir']).name.split('_',2)[-1]} | {a['response_time_v1']} | {a['interception_score']} | {a['pre_flip_mean_ideal_x']} | {a['post_flip_mean_ideal_x']} |")

lines.append("")
lines.append("_Auto-evaluation pending (see follow-up runs)._")
with open("FINDINGS.md", "a") as f:
    f.write("\n".join(lines) + "\n")
print("FINDINGS.md updated.")
PY

echo "[$(date)] === all done ===" >> "$ORCH_LOG"
