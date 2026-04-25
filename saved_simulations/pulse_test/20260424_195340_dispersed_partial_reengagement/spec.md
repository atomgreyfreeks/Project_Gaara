# Swarm Shield — pulse_test
_Run: 20260424_195340_batch_

## TL;DR
Temporal interpretation: threat appears at step 4, disappears at step 15, reappears at step 25. No particle memory. Does the swarm disperse when the threat vanishes? Does it respond faster the second time?

## Research question
Can a swarm of LLM particles that interpret local situations spontaneously produce collective shielding behaviors never explicitly programmed?

## What was tested
- Scenario: **pulse_test**
- Particles: 20
- Duration: 45 steps
- First threat appears at step: 4
- Model: `qwen2.5:7b` (temp=0.7)

## Key results
- Breach: **NO**
- Response time: 1 steps after first threat
- Max shield coverage: 0.60
- Avg shield coverage (post-threat): 0.10
- Avg cohesion (mean nearest-neighbor distance): 0.48
- Final intent distribution: {'protect': 12, 'explore': 0, 'retreat': 0, 'other': 8}

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
