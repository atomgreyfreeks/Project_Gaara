# Gaara Animism — const_immediate
_Run: 20260504_201211_B_immediate_

## TL;DR
Custom resonance run.

## Configuration
- Scenario: **const_immediate**
- Clusters: 20
- Duration: 40 steps
- Seed: 42
- Model: `qwen2.5:7b` (temp=0.7)

## Aggregate metrics
- Mean cluster distance from Mother (overall): 13.59
- Mean color temperature (overall): 0 K
- Mean agitation (overall): 0.000

## Files
- `config_snapshot.yaml`
- `cluster_positions.jsonl` — 3D positions + velocities per step
- `cluster_params.jsonl` — transducer outputs per step
- `mother_state.jsonl` — broadcast + interior per step
- `collective_metrics.json` — summary
