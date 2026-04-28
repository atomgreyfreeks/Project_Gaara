# Swarm Shield — gaara_test
_Run: 20260429_031432_gaara_v1_

## TL;DR
Custom swarm shield experiment.

## Research question
Can a swarm of LLM particles that interpret local situations spontaneously produce collective shielding behaviors never explicitly programmed?

## What was tested
- Scenario: **gaara_test**
- Action mode: **target_point**
- Particles: 20
- Duration: 60 steps
- First threat appears at step: 4
- Model: `qwen2.5:7b` (temp=0.7)

## Key results
- Breach: **NO**
- Response time: 2 steps after first threat
- Max shield coverage: 0.40
- Avg shield coverage (post-threat): 0.06
- Avg cohesion (mean nearest-neighbor distance): 0.37
- Final intent distribution: {'protect': 9, 'explore': 0, 'retreat': 0, 'other': 11}

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
First integrated test of the three Gaara upgrades: felt-state subject voice, constitutive identity (the grain IS part of the Mothership), and adaptive threat that probes around particle density. No purpose statement. No coordinates in the broadcast. Watching for whether the sand reads emotional resonance and whether forms emerge from interpretation.
