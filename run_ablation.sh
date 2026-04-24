#!/bin/bash
# run_ablation.sh — Action-interface ablation for shield_test.
#
# Runs shield_test three times under identical conditions with different
# LLM action interfaces: menu_4dir, menu_8dir, target_point.
#
# Purpose: confirm the cognition/execution split (target_point) is causally
# responsible for the emergent attack-swarm behavior. If menu modes fail
# under today's conditions and target_point succeeds, the architectural
# claim is validated as a paired experiment, not just a before/after story.
#
# Usage:
#   ./run_ablation.sh              # runs all 3 modes
#   ./run_ablation.sh menu_4dir    # runs a single mode

set -u

MODES_ALL=(menu_4dir menu_8dir target_point)
if [ $# -gt 0 ]; then
    MODES=("$@")
else
    MODES=("${MODES_ALL[@]}")
fi

BATCH_ID="ablation_$(date +%Y%m%d_%H%M%S)"
SUMMARY="saved_simulations/${BATCH_ID}_summary.md"
LOG="saved_simulations/${BATCH_ID}.log"

mkdir -p saved_simulations
: > "$LOG"

{
    echo "# Action-interface ablation — $BATCH_ID"
    echo ""
    echo "**Question:** Under identical conditions today, does the interpreter/executor split"
    echo "(target_point) still produce emergent attack-swarm behavior that menu interfaces fail to?"
    echo ""
    echo "**Design:** shield_test, 20 particles, threat at (20,5) start step 4, 50 steps."
    echo "Only the LLM's action interface varies."
    echo ""
    echo "**Modes tested:** ${MODES[*]}"
    echo ""
    echo "| # | Mode | Status | Duration | Max cov | Avg cov (post) | Breach | Run dir |"
    echo "|---|---|---|---|---|---|---|---|"
} > "$SUMMARY"

echo "=============================================================="
echo "Architectural ablation — $BATCH_ID"
echo "Modes: ${MODES[*]}"
echo "Started: $(date)"
echo "=============================================================="

IDX=0
for mode in "${MODES[@]}"; do
    IDX=$((IDX+1))
    echo
    echo "----- [$IDX/${#MODES[@]}] action_mode=$mode -----"
    START_TS=$(date +%s)

    LABEL="ablation_${mode}"
    NOTES="Architectural ablation: action_mode=${mode} under shield_test. Batch ${BATCH_ID}."

    LOG_FILE="$(mktemp)"
    python3 main.py --scenario shield_test \
                    --action-mode "$mode" \
                    --label "$LABEL" \
                    --notes "$NOTES" 2>&1 | tee -a "$LOG" > "$LOG_FILE"
    RC=${PIPESTATUS[0]}
    END_TS=$(date +%s)
    DUR=$((END_TS - START_TS))

    RUN_DIR=$(grep -oE "saved_simulations/[A-Za-z_]+/[0-9_a-z]+" "$LOG_FILE" | head -1)
    [ -z "$RUN_DIR" ] && RUN_DIR="(unknown)"

    # Pull metrics from the run's collective_metrics.json
    if [ -f "$RUN_DIR/collective_metrics.json" ]; then
        MAX_COV=$(python3 -c "import json; d=json.load(open('$RUN_DIR/collective_metrics.json')); print(f\"{d.get('max_shield_coverage',0):.2f}\")")
        AVG_COV=$(python3 -c "import json; d=json.load(open('$RUN_DIR/collective_metrics.json')); print(f\"{d.get('avg_shield_coverage_post_threat',0):.2f}\")")
        BREACH=$(python3 -c "import json; d=json.load(open('$RUN_DIR/collective_metrics.json')); v=d.get('breach_step'); print('-' if v is None else str(v))")
    else
        MAX_COV="-"; AVG_COV="-"; BREACH="-"
    fi

    if [ "$RC" -eq 0 ]; then STATUS="ok"; else STATUS="FAIL(rc=$RC)"; fi
    echo "| $IDX | \`$mode\` | $STATUS | ${DUR}s | $MAX_COV | $AVG_COV | $BREACH | \`$RUN_DIR\` |" >> "$SUMMARY"
    rm -f "$LOG_FILE"
done

{
    echo ""
    echo "**Finished:** $(date)"
    echo ""
    echo "## How to read the table"
    echo "- **Max cov** / **Avg cov (post)**: higher = more particles on the threat→mothership line."
    echo "- **Breach**: step when threat reached the mothership (or '-' if no breach)."
    echo ""
    echo "## Expected outcome if the architectural claim is correct"
    echo "- \`menu_8dir\`: low avg coverage, particles converge on 'up-right' (stampede / conga line)."
    echo "- \`menu_4dir\`: moderate coverage (~0.4 max, ~0.25 avg), loose shield."
    echo "- \`target_point\`: high peak coverage (~1.0), tight attack-swarm clustering, 'intercept/neutralize' intents."
    echo ""
    echo "If target_point shows clearly different behavior than the menus under identical conditions,"
    echo "the interpreter/executor split is causal — not a narrative artifact."
} >> "$SUMMARY"

echo
echo "=============================================================="
echo "Ablation complete."
echo "Summary: $SUMMARY"
echo "Log:     $LOG"
echo "=============================================================="
