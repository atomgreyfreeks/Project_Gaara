# Swarm Shield — gaara_test
_Run: 20260429_043122_gaara_v2c_

## TL;DR
Custom swarm shield experiment.

## Research question
Can a swarm of LLM particles that interpret local situations spontaneously produce collective shielding behaviors never explicitly programmed?

## What was tested
- Scenario: **gaara_test**
- Action mode: **target_point**
- Particles: 20
- Duration: 35 steps
- First threat appears at step: 4
- Model: `qwen2.5:7b` (temp=0.7)

## Key results
- Breach: **YES** (at step 29)
- Response time: never reached 0.3 coverage
- Max shield coverage: 0.10
- Avg shield coverage (post-threat): 0.01
- Avg cohesion (mean nearest-neighbor distance): 0.42
- Final intent distribution: {'protect': 6, 'explore': 0, 'retreat': 0, 'other': 14}

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
Gaara v2 compact: 35 steps, threat at (14,4) speed 0.55 commit_radius 7. Felt-state broadcast with 8-cardinal direction. Goal: observe approach, terminal commit, breach, and immediate post-breach response in ~12 min.
