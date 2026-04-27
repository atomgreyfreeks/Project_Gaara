# Swarm Shield — saga_test
_Run: 20260427_043743_overnight_saga_

## TL;DR
Custom swarm shield experiment.

## Research question
Can a swarm of LLM particles that interpret local situations spontaneously produce collective shielding behaviors never explicitly programmed?

## What was tested
- Scenario: **saga_test**
- Action mode: **target_point**
- Particles: 20
- Duration: 500 steps
- First threat appears at step: 10
- Model: `qwen2.5:7b` (temp=0.7)

## Key results
- Breach: **YES** (at step 47)
- Response time: 0 steps after first threat
- Max shield coverage: 1.00
- Avg shield coverage (post-threat): 0.23
- Avg cohesion (mean nearest-neighbor distance): 0.28
- Final intent distribution: {'protect': 10, 'explore': 0, 'retreat': 0, 'other': 10}

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
500-step saga: 7 waves with calm gaps.
