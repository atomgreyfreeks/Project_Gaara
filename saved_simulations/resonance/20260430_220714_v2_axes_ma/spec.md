# Gaara Animism — resonance
_Run: 20260430_220714_v2_axes_ma_

## TL;DR
20 swarm clusters orbit a Mothership with her own interior. Her felt-state drives a broadcast each step; clusters translate it into material parameters (attraction, viscosity, agitation, color). No threats. The only signal is the Mother. The only output is matter.

## Configuration
- Scenario: **resonance**
- Clusters: 20
- Duration: 200 steps
- Seed: 42
- Model: `qwen2.5:7b` (temp=0.7)

## Aggregate metrics
- Mean cluster distance from Mother (overall): 0.39
- Mean color temperature (overall): 6017 K
- Mean agitation (overall): 0.116

## Files
- `config_snapshot.yaml`
- `cluster_positions.jsonl` — 3D positions + velocities per step
- `cluster_params.jsonl` — transducer outputs per step
- `mother_state.jsonl` — broadcast + interior per step
- `collective_metrics.json` — summary
