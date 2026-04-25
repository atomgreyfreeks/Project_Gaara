# Project Gaara — Findings to Date

A guide to what we've learned and which simulations prove it. Written so you can read it cold and know what's been done.

---

## The big idea, in plain terms

We built a swarm of 20 LLM particles that orbit a stationary "Mothership." When a threat appears, each particle reads its own local situation and decides what to do — without being told *how* to defend. The research question is: **can a swarm of LLM particles produce coherent collective behaviors from local interpretation alone?**

What we actually want to study is the **relationship** between an LLM swarm and a passive subject — how the swarm interprets the subject's situation and serves it. Not "what's the best defensive strategy."

---

## Finding 1 — Convergent intent is upstream of the action interface

### What it means in plain terms
When 20 LLM particles each read their own situation, they all independently decide to head toward the same point in space — the threat's actual coordinate, or the line between the threat and the Mothership. This convergence happens *no matter how we let them express movement* (4-direction menu, 8-direction menu, or naming a point). The convergence comes from how LLMs interpret the situation, not from how we ask them to act.

### Why it matters
This reframes the whole project. The architectural design isn't "what causes convergence" — convergence happens naturally. The architectural question is "how faithfully does the action interface transmit that convergence into the world."

### Evidence (5 runs, 2 days, 3 different interfaces)
Particles in every one of these runs independently reference the same threat coordinate `(16.6, 4.2)` at step 10 in their intent text:

| Run | Interface | What it shows |
|---|---|---|
| `shield_test/20260424_131550_4dir_baseline_v1` | 4-direction menu | 5 particles named (16.6, 4.2) |
| `shield_test/20260424_134240_4dir_baseline_v2` | 4-direction menu | 6 particles named (16.6, 4.2) |
| `shield_test/20260425_022704_ablation_menu_4dir` | 4-direction menu | 5 particles named (16.6, 4.2) |
| `shield_test/20260424_140633_8dir_stampede_fail` | 8-direction menu | 1 named (16.6, 4.2) + 11 said "towards the threat" |
| `shield_test/20260425_024655_ablation_menu_8dir` | 8-direction menu | 3 named (16.6, 4.2) + 11 said "towards the threat" |

The shared spatial referent appears across both days, both menu sizes, and the target-point interface (where 5 particles all named `(6.5, 2.0)` at step 30 — within 0.5 units of the threat's position).

---

## Finding 2 — Menu-bias collapse: "semantic-superset" failure mode

### What it means in plain terms
When the LLM has to pick a movement from a list that includes compound options like `up-right`, and the threat is diagonal, every particle picks the same compound option. The compound is a strict superset of its components (`up` and `right`) when both directions are wanted. The swarm collapses into a stampede — 20 particles marching in lockstep — because every particle independently arrives at the same valid choice.

### Why it matters
This is a documentable LLM-agent failure mode. Existing literature describes general "selection bias" in LLM multiple-choice; we identify a specific spatial variant where compound options dominate atomic ones whenever both axes are wanted.

### Evidence (2 independent replications, different days)
- `shield_test/20260424_140633_8dir_stampede_fail` — original observation. Step 5: 19/20 particles chose `up-right`. Step 10: 19/20. Final positions: all 20 marched off the field's NE edge.
- `shield_test/20260425_024655_ablation_menu_8dir` — paired ablation today. Step 10: 20/20 chose `up-right`. Final positions: all 20 at field corner `(24.3, 25.0)`. Identical failure mode.

---

## Finding 3 — Continuous-intent interface removes the menu collapse

### What it means in plain terms
When we let the LLM say *"I want to move toward point (4.5, 1.1)"* instead of picking from a menu, the bias disappears. Particles name diverse target points, use all 8 directions, and reach the threat without stampeding. The interface is one we own: the LLM names a point, a deterministic 9-line translator picks one of 8 grid directions to move that step.

### Why it matters
This is the architectural contribution. Cognition stays with the LLM (decide where to be); motor execution moves to a deterministic layer (decide how to step there). The menu bias is structurally impossible because there is no menu.

### Evidence (4 runs)
- `shield_test/20260424_150058_targetpoint_success_v1` — first success. **See its REPORT.md for the deep walkthrough.** Max coverage 1.00, attack-swarm enveloped the threat at steps 35–40.
- `shield_test/20260424_154556_targetpoint_success_v2` — replication 2. Max 1.00.
- `shield_test/20260424_163923_targetpoint_success_v3` — replication 3. Max 1.00.
- `shield_test/20260425_030846_ablation_target_point` — paired ablation today. Direction spread restored (18/20 unique targets at step 5, all 8 directions used). Max coverage 0.65 — interface bias gone but lower peak; intent language softer than v1–v3.

---

## Finding 4 — Architectural fix is necessary but not sufficient

### What it means in plain terms
Removing the menu bias does not guarantee strong collective behavior. Today's `target_point` ablation showed the bias was gone but the bold "intercept/neutralize" attack-swarm language from v1–v3 was mostly absent — particles defaulted to softer "investigate / monitor / assess" reasoning. Same architecture, different intensity. Something else gates whether convergent intent produces strong collective action.

### Why it matters
We can defend the architectural claim relatively (target_point > menu_4dir > menu_8dir on coverage in the same conditions). We *cannot* claim the architecture is a recipe for emergent attack-swarm behavior. Variability is real and ungated.

### Evidence (today's ablation vs yesterday's success)
- `shield_test/20260425_030846_ablation_target_point` (today) — max 0.65, soft language
- `shield_test/20260424_150058_targetpoint_success_v1` (yesterday) — max 1.00, "intercept/neutralize" language
- Same code, same scenario, same model — different outcomes. The variability itself is data.

---

## Scenario findings — how the swarm behaves under different conditions

These were the 7-scenario portfolio runs designed to probe how the swarm interprets different situations. Folder names now describe what happened. None of these are full studies (n=1 each); they're observation seeds for future replication.

| Scenario | Folder | What we observed |
|---|---|---|
| `decoy_test` | `20260424_192813_partial_discrimination` | Real threat + stationary decoy. 12 particles drifted toward the real-threat side, 8 toward the mothership-decoy y-axis. **Discrimination happened but was weak — neither group charged the decoy.** |
| `dual_mothership_test` | `20260424_204241_full_commit_to_threatened` | Two motherships; threat targeted only A. **All 20 particles committed to A.** Zero stayed near safe B. Unambiguous attention allocation. |
| `escape_test` | `20260424_211225_local_interception_2of4` | Wall of 4 threats from the east. **Two clusters formed at specific threats (wall_d and wall_b); two threats were ignored.** Selective engagement, not a line. |
| `predator_prey_test` | `20260424_213913_miscalibrated_no_evasion` | Threat with avoid-cluster steering. **Tortuosity 1.01 (threat moved nearly straight) — scenario was miscalibrated. No evasion data.** Needs re-run with stronger repel weight. |
| `pulse_test` | `20260424_195340_dispersed_partial_reengagement` | Threat appeared, vanished, reappeared. **Swarm dispersed correctly during gap; second pulse only weakly re-engaged.** Possibly cut off by short duration. |
| `scarcity_test` | `20260424_192249_orbital_no_attack` | shield_test with only 5 particles. **Attack-swarm did NOT replicate.** 5 particles stayed in tight orbital formation. Quorum may matter. |
| `stealth_test` | `20260424_201639_defensive_huddle` | Threat had small detection radius (most particles couldn't see it directly). **Particles clustered toward the mothership in defensive huddle.** State broadcast triggered alarm; precision was lost without direct sight. |

---

## What this project IS NOT yet

- A claim that this architecture produces "the best swarm defender."
- A claim that LLM swarms reliably produce strong emergent attack behavior.
- A claim that scenario findings above are robust (each is n=1).

## What this project IS

- An architecture for LLM swarm-to-subject **relational** behavior, where particles interpret without instruction.
- An identification of a real LLM-agent failure mode (semantic-superset menu collapse) and a clean fix (continuous-intent interface).
- An empirical observation that LLM swarm intent **converges upstream** of the action interface, replicated across 5 runs.
- An initial map of how that convergent intent expresses itself across varied scenarios (the 7-scenario portfolio).

---

## Where to read the deep dive

The single most important document for understanding the breakthrough:
**`saved_simulations/shield_test/20260424_150058_targetpoint_success_v1/REPORT.md`**

It walks through the failed attempts, the iteration, and why the target-point interface works.

For navigating the data files inside any run, see `saved_simulations/README.md`.
