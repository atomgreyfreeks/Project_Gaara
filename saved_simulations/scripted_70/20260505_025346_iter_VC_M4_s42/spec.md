# Gaara Animism — scripted_70
_Run: 20260505_025346_iter_VC_M4_s42_

## TL;DR
Custom resonance run.

## Configuration
- Scenario: **scripted_70**
- Clusters: 20
- Duration: 70 steps
- Seed: 42
- Model: `qwen2.5:7b` (temp=0.7)

## Aggregate metrics
- Mean cluster distance from Mother (overall): 7.56
- Mean color temperature (overall): 0 K
- Mean agitation (overall): 0.000

## Files
- `config_snapshot.yaml`
- `cluster_positions.jsonl` — 3D positions + velocities per step
- `cluster_params.jsonl` — transducer outputs per step
- `mother_state.jsonl` — broadcast + interior per step
- `collective_metrics.json` — summary
