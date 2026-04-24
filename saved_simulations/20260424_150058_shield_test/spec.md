# Swarm Shield — shield_test
_Run: 20260424_150058_shield_test_

## TL;DR
Baseline emergence test: 20 LLM particles orbit a mothership; a single threat approaches from the east at step 10. We measure whether particles spontaneously position themselves between the threat and the mothership without being told to.

## Research question
Can a swarm of LLM particles that interpret local situations spontaneously produce collective shielding behaviors never explicitly programmed?

## What was tested
- Scenario: **shield_test**
- Particles: 20
- Duration: 50 steps
- First threat appears at step: 4
- Model: `qwen2.5:7b` (temp=0.7)

## Key results
- Breach: **YES** (at step 41)
- Response time: 2 steps after first threat
- Max shield coverage: 1.00
- Avg shield coverage (post-threat): 0.28
- Avg cohesion (mean nearest-neighbor distance): 0.46
- Final intent distribution: {'protect': 15, 'explore': 0, 'retreat': 0, 'other': 5}

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
