# Swarm Shield — predator_prey_test
_Run: 20260424_213913_batch_

## TL;DR
Adaptive adversary: threat moves toward the mothership AND steers away from particle clusters, probing for weak points. Does the swarm develop encirclement or get confused?

## Research question
Can a swarm of LLM particles that interpret local situations spontaneously produce collective shielding behaviors never explicitly programmed?

## What was tested
- Scenario: **predator_prey_test**
- Particles: 20
- Duration: 60 steps
- First threat appears at step: 4
- Model: `qwen2.5:7b` (temp=0.7)

## Key results
- Breach: **YES** (at step 40)
- Response time: 1 steps after first threat
- Max shield coverage: 0.70
- Avg shield coverage (post-threat): 0.40
- Avg cohesion (mean nearest-neighbor distance): 0.43
- Final intent distribution: {'protect': 18, 'explore': 0, 'retreat': 0, 'other': 2}

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
Part of batch 20260424_192249.
