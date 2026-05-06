#!/usr/bin/env bash
# Project Gaara — exp_* batch runner.
#
# Ten 30-step pilots exploring four architectural axes:
#   A. Mother's signal modality (sensory / metaphor / pulse)
#   B. Subject identity        (garden / we / dissolved-DNA)
#   C. Awareness bracket       (zero / full)
#   D. Swarm composition       (mixed nouns / axes-of-contemplation DNA)
#
# Foundation held constant across all ten:
#   scenario = scripted_30   (east attacker arrives ~step 25)
#   duration = 30
#   seed     = 42
#   model    = qwen2.5:7b
#
# Each invocation produces saved_simulations/scripted_30/<stamp>_<label>/.
# Logs are appended to exp_batch.log.

set -u  # error on unset vars; keep going on individual run failures so the
# batch finishes even if one experiment crashes.

cd "$(dirname "$0")"

LOG=exp_batch.log
echo "=== exp_* batch start: $(date) ===" | tee -a "$LOG"

run() {
    local label="$1"; shift
    echo "" | tee -a "$LOG"
    echo "--- $label   $(date +%H:%M:%S) ---" | tee -a "$LOG"
    echo "args: $*" | tee -a "$LOG"
    python3 main.py --scenario scripted_30 --duration 30 --seed 42 \
        --label "$label" "$@" 2>&1 | tee -a "$LOG"
    echo "--- $label DONE   $(date +%H:%M:%S) ---" | tee -a "$LOG"
}

# Axis A — Mother's signal modality. VC + sentinel held constant.
run exp_01_mother_sensory   --dna-variant VC --mother-variant M_SENSORY  --role-noun sentinel
run exp_02_mother_metaphor  --dna-variant VC --mother-variant M_METAPHOR --role-noun sentinel
run exp_03_mother_pulse     --dna-variant VC --mother-variant M_PULSE    --role-noun sentinel

# Axis B — Subject identity.
run exp_04_subject_garden   --dna-variant V_GARDEN    --mother-variant M_GARDEN --role-noun seed --say-prefix "the garden"
run exp_05_subject_plural   --dna-variant V_WE        --mother-variant M_WE     --role-noun place --say-prefix we
run exp_06_dna_dissolved    --dna-variant V_DISSOLVED --mother-variant M5       --role-noun place

# Axis C — Awareness bracket.
run exp_07_awareness_zero   --dna-variant VC --mother-variant M5 --role-noun sentinel --awareness-range 0
run exp_08_awareness_full   --dna-variant VC --mother-variant M5 --role-noun sentinel --awareness-range 100

# Axis D — Swarm composition.
run exp_09_mixed_nouns      --dna-variant VC      --mother-variant M5 --role-nouns "sentinel,warrior"
run exp_10_dna_axes         --dna-variant V_AXES  --mother-variant M5 --role-noun sentinel

echo "" | tee -a "$LOG"
echo "=== exp_* batch end: $(date) ===" | tee -a "$LOG"
