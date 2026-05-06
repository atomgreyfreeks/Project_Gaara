# Project Gaara — Animism

> Twenty LLM-driven particles emergently protect a central body — through interpretation of body-language, never through commands.

This repository is the **raw evidence layer** behind the demo video and the PDF specs. If you've already watched the video and read the spec, this is where you go to check that the work is empirically real.

---

## Where the proof lives

| Claim from the PDF | Evidence in this repo |
|---|---|
| The architecture is a *real* lever — same model, same scenario, prompt grammar moves the swarm from drone-mode to interpretation-mode. | `saved_simulations/scripted_100/` (VA/VB/VC/VD/VE sweep). Run `python3 score_diversity.py <run_dir>` to read the functional-diversity scoring. |
| Mother's wording is more load-bearing than the agent's prompt — switching her phrasing alone shifts pre-flip directional response 28×. | `saved_simulations/scripted_70/` (M1/M2/M3/M4 sweep). Compare `analysis.json` across `*_a_m1_*` vs `*_a_m4_*` runs. |
| Pure-interpretation existence proof: 20 particles drift +24 east with **no attacker in the field** — purely because Mother's body says east. | `saved_simulations/const_extreme/20260504_203124_b_extreme/` |
| The cognitive/behavior trade-off: VG produces the *richest* reasoning under calm Mother but breaks under urgent. | `saved_simulations/const_calm/20260505_162742_bonus_vg_const_calm_s42/` vs `saved_simulations/scripted_70/20260505_144749_big_vg_m5_s42/` |
| The headline noun-substitution result: same architecture, only the agent's name changes — **sentinel beats warrior 2× on interception** despite warrior being the more aggressive label. | `saved_simulations/scripted_70/20260505_*noun_*_VC_M5_s42/` (mote / guardian / warrior / sentinel / defender / vanguard) |
| **New (May 6):** heterogeneous noun assignment — 10 sentinel + 10 warrior — wins on both intercept *and* pre-flip directional pull simultaneously. The first new architectural lever in the project's recent campaign. | `saved_simulations/scripted_30/20260506_162835_exp_09_mixed_nouns/` — see `EXP_BATCH_REPORT.md` for the full exp_* batch. |

Every run directory contains `cluster_intents.jsonl` (per-particle reasoning + intent), `cluster_positions.jsonl` (position trace), `mother_state.jsonl` (her broadcast each step), and `analysis.json` (per-run summary metrics).

---

## How to verify any single claim

```bash
# Read the functional-diversity profile of a run (the audit surface)
python3 score_diversity.py saved_simulations/scripted_70/20260505_200135_noun_sentinel_VC_M5_s42

# Reproduce the per-run analysis (interception, pre-flip x, awareness flips)
python3 analyze_run.py saved_simulations/scripted_70/20260505_200135_noun_sentinel_VC_M5_s42

# Re-run any experiment yourself (requires Ollama + qwen2.5:7b locally)
python3 main.py --scenario scripted_70 --duration 70 --seed 42 \
  --dna-variant VC --mother-variant M5 --role-noun sentinel --label replication
```

For the May 6 architectural-exploration batch (10 pilots, four axes):

```bash
./run_exp_batch.sh                # re-run the entire batch
python3 summarize_exp_batch.py    # ranked table of completed exp_* runs
```

---

## What's in this folder

```
REPORT.md                — full hackathon-ready research report (10 sections).
FINDINGS.md              — dated empirical log, every run's surprise.
EXP_BATCH_REPORT.md      — May 6 architectural-exploration batch summary.
GLOSSARY.md              — decoder for every code (DNA / Mother / scenario / metric).
OPERATING_PRINCIPLES.md  — the discipline we worked under.

main.py                  — CLI entry point. Switch-style: every architectural axis
                           is a flag, defaults reproduce the original baseline.
cluster.py               — the LLM particle. DNA prompt variants live here.
mothership.py            — the central body and her interior states.
scenarios.py             — Mother-broadcast scripts and phase boundaries.
simulation.py            — orchestrator (per-step LLM transduce + physics integrate).
physics.py               — intent-to-motion translator. The LLM never touches
                           velocity; cognition stays in language space.
analyze_run.py           — per-run analysis (interception, pre-flip x, etc.).
score_diversity.py       — functional-diversity scorer for the reasoning audit.
summarize_exp_batch.py   — exp_* batch ranked-table generator.

saved_simulations/       — every run's full logs, organized by scenario.
config.yaml              — physics constants, scenario definitions, LLM settings.
```

A companion 3D viewer lives at `../Gaara_Animism_Viewer/` (clone separately).

---

## The one paragraph

The project's claim isn't that LLMs can interpret. The question is too binary to be useful. The claim is that **interpretation is a property of the relational architecture built around an LLM, not of the LLM itself.** A well-defined relational space — subject, environment, agent, body-language as protocol — lets the LLM interpret. A command-channel disguised as a relationship collapses it back into an executor. We built the architecture, instrumented it with a per-particle reasoning audit field, and ran enough single-variable experiments to map where the line falls.

The Japanese-animist framing is not decoration. It's the sensibility that produced the architecture — *every thing has presence, including the LLM* — and it suggests where the work goes next: subject substitution beyond Gaara (gut microbiome, soil network, aquarium ecosystem), brain–machine interface as relationship interface, and information-life ontology bottom-up.

---

## Reproducibility

- Model: `qwen2.5:7b` via Ollama, temperature 0.7.
- Seeds: 42, 101, 202 used across the sweeps.
- All experiments are command-line reproducible. Every saved run carries its `config_snapshot.yaml`.
- Primary reasoning audit: each particle outputs a `reasoning` field per step. Categorized by `score_diversity.py` keyword rules. Any run, any reasoning, any researcher can re-classify.

The codebase is self-contained. If you can run Ollama with qwen2.5:7b, you can re-run any experiment in this folder.
