#!/bin/bash
# run_batch.sh — runs a list of scenarios sequentially and writes a batch summary.
#
# Usage:
#   ./run_batch.sh                    # runs the full v1 portfolio (7 scenarios)
#   ./run_batch.sh shield_test pulse_test  # runs only these
#   LABEL=nightly ./run_batch.sh      # adds a label to each run directory

set -u  # no -e — we want to continue even if one scenario fails

LABEL="${LABEL:-batch}"

if [ $# -gt 0 ]; then
    SCENARIOS=("$@")
else
    SCENARIOS=(scarcity_test decoy_test pulse_test stealth_test dual_mothership_test escape_test predator_prey_test)
fi

echo "=============================================================="
echo "Swarm Shield batch run"
echo "Scenarios: ${SCENARIOS[@]}"
echo "Label: $LABEL"
echo "Start: $(date)"
echo "=============================================================="
echo

BATCH_ID="$(date +%Y%m%d_%H%M%S)"
BATCH_LOG="saved_simulations/batch_${BATCH_ID}.log"
BATCH_SUMMARY="saved_simulations/batch_${BATCH_ID}_summary.md"

mkdir -p saved_simulations
: > "$BATCH_LOG"

# Header for summary
{
    echo "# Batch run ${BATCH_ID}"
    echo ""
    echo "**Started:** $(date)"
    echo "**Scenarios:** ${SCENARIOS[*]}"
    echo "**Label:** $LABEL"
    echo ""
    echo "| # | Scenario | Status | Duration | Run dir |"
    echo "|---|---|---|---|---|"
} > "$BATCH_SUMMARY"

IDX=0
for s in "${SCENARIOS[@]}"; do
    IDX=$((IDX+1))
    echo "----- [$IDX/${#SCENARIOS[@]}] $s -----"
    START_TS=$(date +%s)

    # Capture the run directory by tailing the stderr/stdout for the "Run directory:" line
    LOG_FILE="$(mktemp)"
    python3 main.py --scenario "$s" --label "$LABEL" --notes "Part of batch ${BATCH_ID}." 2>&1 | tee -a "$BATCH_LOG" > "$LOG_FILE"
    RC=${PIPESTATUS[0]}
    END_TS=$(date +%s)
    DUR=$((END_TS - START_TS))

    RUN_DIR=$(grep -oE "saved_simulations/[^ ]+" "$LOG_FILE" | head -1)
    [ -z "$RUN_DIR" ] && RUN_DIR="(unknown)"

    if [ "$RC" -eq 0 ]; then
        STATUS="ok"
    else
        STATUS="FAIL(rc=$RC)"
    fi
    echo "| $IDX | $s | $STATUS | ${DUR}s | \`$RUN_DIR\` |" >> "$BATCH_SUMMARY"

    rm -f "$LOG_FILE"
    echo
done

{
    echo ""
    echo "**Finished:** $(date)"
} >> "$BATCH_SUMMARY"

echo "=============================================================="
echo "Batch complete. Summary: $BATCH_SUMMARY"
echo "Log:     $BATCH_LOG"
echo "=============================================================="
