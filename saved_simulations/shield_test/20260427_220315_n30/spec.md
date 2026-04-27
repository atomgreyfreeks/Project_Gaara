# Swarm Shield — shield_test
_Run: 20260427_220315_n30_

## TL;DR
Baseline emergence test: 20 LLM particles orbit a mothership; a single threat approaches from the east. We measure whether particles spontaneously position between the threat and the mothership without being told to.

## Research question
Can a swarm of LLM particles that interpret local situations spontaneously produce collective shielding behaviors never explicitly programmed?

## What was tested
- Scenario: **shield_test**
- Action mode: **target_point**
- Particles: 30
- Duration: 50 steps
- First threat appears at step: 4
- Model: `qwen2.5:7b` (temp=0.7)

## Key results
- Breach: **YES** (at step 41)
- Response time: 33 steps after first threat
- Max shield coverage: 0.60
- Avg shield coverage (post-threat): 0.06
- Avg cohesion (mean nearest-neighbor distance): 0.40
- Final intent distribution: {'protect': 21, 'explore': 1, 'retreat': 0, 'other': 8}

## Success bands
- **Weak:** coverage rises to 0.2–0.3, particles drift toward threat side.
- **Strong:** coverage > 0.4, clear clustering between threat and mothership.
- **Failure:** coverage stays near baseline; particles ignore threat.

## Files
- `config_snapshot.yaml` — exact config used
- `particle_positions.jsonl` / `particle_intents.jsonl` — per-step raw
- `threat_positions.jsonl` / `mothership_state.jsonl`
- `shield_coverage.csv` / `angular_distribution.csv`
- `collective_metrics.json` — summary metrics
- `frames/frame_XXXX.png` — visualizations
- `statistics.png` — summary plots

## Notes
Q3 phase structure: 30-particle swarm cluster behavior
