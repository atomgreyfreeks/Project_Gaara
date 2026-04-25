# saved_simulations — navigation guide

Each subfolder is a scenario. Each subfolder of a scenario is one simulation run.

> **For findings and which runs prove what, see `../FINDINGS.md` at the project root.**

---

## Folder layout

```
saved_simulations/
├── shield_test/                       ← the baseline scenario (most data here)
│   ├── *_4dir_baseline_v1/v2          ← yesterday's 4-direction menu runs
│   ├── *_8dir_stampede_fail/          ← the menu-bias collapse (original)
│   ├── *_targetpoint_success_v1/v2/v3 ← the architectural fix, replicated 3×
│   └── *_ablation_*/                  ← today's paired ablation (4dir, 8dir, target_point)
├── decoy_test/                        ← 1 real threat + 1 stationary decoy
├── dual_mothership_test/              ← 2 motherships, threat targets one
├── escape_test/                       ← wall of 4 threats
├── predator_prey_test/                ← adaptive threat (currently miscalibrated)
├── pulse_test/                        ← threat that appears, vanishes, reappears
├── scarcity_test/                     ← shield_test with only 5 particles
├── stealth_test/                      ← threat with small detection radius
├── _archive/                          ← incomplete runs kept for posterity
├── batch_*_summary.md                 ← per-batch overview tables
└── ablation_*_summary.md              ← architectural ablation summary
```

Folder names include a short suffix describing what happened in that run, so you can scan the directory and know the outcome without opening anything.

---

## What's inside each run

Every run folder contains:

| File | What it is | When you'd read it |
|---|---|---|
| **`spec.md`** | Plain-English TL;DR of what the run tested + key results | **Start here for any run** |
| **`REPORT.md`** (some runs only) | Deep walkthrough — only on the most important runs | When you want the full story |
| `config_snapshot.yaml` | Exact config used | To reproduce or check parameters |
| `collective_metrics.json` | Summary metrics (max coverage, breach step, intent distribution) | Quick numerical comparison |
| `particle_positions.jsonl` | Per-step particle positions | Plot trajectories, reanalyze |
| `particle_intents.jsonl` | Per-step LLM action + intent text | **Read this to understand what the particles were thinking** |
| `threat_positions.jsonl` | Per-step threat positions | Reconstruct geometry over time |
| `mothership_state.jsonl` | Per-step mothership state strings | See what the broadcast looked like |
| `shield_coverage.csv` | Coverage metric over time | Quick plot of swarm response |
| `angular_distribution.csv` | Particles per 45° sector around mothership | Check spatial spread |
| `frames/frame_XXXX.png` | Per-step visualization | Watch the run play out |
| `statistics.png` | Summary plot | Snapshot of run dynamics |

---

## Three good reading paths

**"I just want to understand the project's main finding"**
→ Read `../FINDINGS.md`, then `shield_test/*_targetpoint_success_v1/REPORT.md`.

**"I want to see the menu-bias failure"**
→ Open `shield_test/*_8dir_stampede_fail/spec.md` and look at any frame in the `frames/` folder. The 20 particles all charging up-right is unmistakable.

**"I want to look at how particles reasoned in a specific run"**
→ Open `<run>/particle_intents.jsonl`. Each line is one step. Look for the `"intent"` field on each particle — that's the LLM's natural-language explanation for what it's doing.

---

## Run naming convention

Format: `<YYYYMMDD>_<HHMMSS>_<descriptive_outcome_tag>`

The outcome tag is what the run *did*, not just what it tested. Examples:
- `4dir_baseline_v1` — first baseline using the 4-direction menu
- `8dir_stampede_fail` — the run where the 20-particle stampede happened
- `targetpoint_success_v1` — the run where the architectural fix first worked
- `ablation_menu_4dir` — part of today's paired ablation, 4-direction mode
- `partial_discrimination` — decoy test where particles half-discriminated
- `defensive_huddle` — stealth test where particles huddled near the mothership

This is intentional — you should be able to scan the folder list and know what happened without opening anything.
