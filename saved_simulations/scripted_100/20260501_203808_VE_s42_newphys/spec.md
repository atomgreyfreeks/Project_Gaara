# Gaara Animism — scripted_100
_Run: 20260501_203808_VE_s42_newphys_

## TL;DR
Custom resonance run.

## Configuration
- Scenario: **scripted_100**
- Clusters: 20
- Duration: 100 steps
- Seed: 42
- Model: `qwen2.5:7b` (temp=0.7)

## Aggregate metrics
- Mean cluster distance from Mother (overall): 4.11
- Mean color temperature (overall): 0 K
- Mean agitation (overall): 0.000

## Files
- `config_snapshot.yaml`
- `cluster_positions.jsonl` — 3D positions + velocities per step
- `cluster_params.jsonl` — transducer outputs per step
- `mother_state.jsonl` — broadcast + interior per step
- `collective_metrics.json` — summary
