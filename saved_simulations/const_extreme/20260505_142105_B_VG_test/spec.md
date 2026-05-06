# Gaara Animism — const_extreme
_Run: 20260505_142105_B_VG_test_

## TL;DR
Custom resonance run.

## Configuration
- Scenario: **const_extreme**
- Clusters: 20
- Duration: 10 steps
- Seed: 42
- Model: `qwen2.5:7b` (temp=0.7)

## Aggregate metrics
- Mean cluster distance from Mother (overall): 7.89
- Mean color temperature (overall): 0 K
- Mean agitation (overall): 0.000

## Files
- `config_snapshot.yaml`
- `cluster_positions.jsonl` — 3D positions + velocities per step
- `cluster_params.jsonl` — transducer outputs per step
- `mother_state.jsonl` — broadcast + interior per step
- `collective_metrics.json` — summary
