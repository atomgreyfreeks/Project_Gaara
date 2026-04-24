# Iteration Report — The First Emergent Swarm Attack

**Run:** `20260424_150058_shield_test`
**Scenario:** `shield_test` · 20 particles · single threat from (20, 5), starting at step 4
**Model:** `qwen2.5:7b` · temperature 0.7 · max_tokens 100

---

## TL;DR

We found a prompt design where 20 LLM particles, given only a purpose ("protect the Mothership") and local sensory data, **spontaneously grouped up and swarmed the incoming threat.** No behavioral rules were given — no "cluster", no "intercept", no "attack". Max shield coverage reached **1.00** (versus 0.45 in prior baselines), the swarm physically enveloped the threat, and intent language such as *"intercept"*, *"neutralize"*, *"engage"* emerged unprompted.

The change that unlocked this was small but conceptually sharp: **we stopped asking the LLM to pick an action from a menu, and started asking it to name a point in space it wanted to move toward.** A deterministic server-side translator then converted that point into a grid-compatible direction.

In one sentence: **we separated cognition from motor execution**, and the emergence followed.

---

## The underlying principle (stated first, because it matters more than the result)

Before this iteration, the LLM was doing two jobs at once:

1. **Interpreting the situation** — reading its position, the mothership state, nearby particles, and perceived threats, then forming a judgment about what to do.
2. **Expressing that judgment in the target system's vocabulary** — picking one of 4, then 8, discrete direction labels the simulation engine understood.

These look like one job, but they are two. The first is cognition. The second is motor translation. When we force an LLM to do both in the same breath, the constraints of the output format leak backward into the reasoning. The LLM isn't just reasoning about the world; it's reasoning about which of the items in the menu is the best match — and that is a different, lesser thing.

In the working version, we split those jobs:

| Layer | Failed design | Working design |
|---|---|---|
| Cognition / interpretation | LLM | LLM |
| Motor translation / execution | LLM (same prompt) | Deterministic code (9 lines of Python) |

The LLM now expresses intent in **its native modality** — spatial language, places, points. It says *"I want to reach (4.5, 1.1) because that is where the threat is."* The simulation doesn't care about prose or coordinates; it needs one of 8 discrete moves. A small translator subtracts current position from the named target, takes the sign of each axis, and looks up the result in a table. Nine lines of code. No biases introduced at that layer because the mapping is monotonic and symmetric.

The useful analogy is biological motor control: your brain does not compute *"activate quadriceps at 67% for 120 ms."* It forms an intent — *"reach for the cup"* — and lower motor systems translate that into muscle activations. Cognition and execution are distinct layers, connected by a clean interface.

Applied to LLM agents, the principle generalizes:

> **Do not force the LLM to reason in your implementation's vocabulary. Let it reason in its own, then translate.** If your system needs discrete actions, put the discretization *after* the reasoning, not *inside* it.

This is not a hack or a prompt trick. It is a basic separation-of-concerns that was being violated.

---

## What we tried before (the full iteration trail)

### Attempt 1 — 4-direction movement (baseline, runs `131550` and `134240`)

**Prompt excerpt:**
> Move one step: up, down, left, right, or stay.

**Metrics:**
- Max shield coverage: **0.45**
- Avg post-threat coverage: **0.24 – 0.28**
- Cohesion (mean nearest-neighbor distance): **1.81 – 2.01**
- Breach: step 41 (deterministic; see caveats)

**Behavior:** Particles distributed across directions sensibly — roughly 14 up / 6 right in the steps after threat appearance. A loose shield formed, held for about 15 steps, then slowly decayed as noise scattered the particles. Intent language was *correct and protective*: *"position myself between the Mothership and the detected threat"*, *"maintain surveillance"*, *"monitor the threat"*.

**Verdict:** Weak-to-strong emergence. Real but unimpressive. The staircase movement restriction felt awkward — particles wanting to go northeast had to alternate steps, and the swarm couldn't commit to a coordinated position.

### Attempt 2 — 8-direction movement (run `140633`)

**What we changed:** Added four diagonal actions so particles could move northeast, northwest, southeast, southwest in a single step.

**Prompt excerpt:**
> Move one step in any of these 8 directions, or stay: up, down, left, right, up-right, up-left, down-right, down-left.

**Metrics:**
- Max shield coverage: **0.35** (↓)
- Avg post-threat coverage: **0.07** (3× regression)
- Cohesion: **1.27** (tighter clumping, in a bad way)
- Breach: step 41

**Behavior:** The result was unexpectedly bad. Reading the per-step direction distribution made the problem immediate:

- Step 5: **19 of 20 particles chose `up-right`**
- Step 10: 19 of 20 `up-right`
- Step 20: 19 `up-right`, 1 `up-left`
- Step 30: 17 `up-right`, 2 `up`, 1 `stay`

Nearly every particle, every step, picked the same direction. The swarm degenerated into a conga line marching northeast. Intent language degraded too — from *"position myself between the Mothership and the threat"* (shielding) to *"head towards the threat"* and *"move toward particle #N"* (chasing and flocking).

**Why it failed — two compounding biases:**

1. **Positional bias.** LLMs over-select items that appear earlier in a list of options, a well-documented artifact of training data and attention mechanics. `up-right` was the first compound listed, and it punched above its weight for no reason related to the world.

2. **Semantic superset.** This is the larger effect. When the threat is in the NE quadrant (as in `shield_test` — threat at (20, 5), mothership at origin), `up-right` is semantically a *strict superset* of `up` and `right`. A particle reasoning *"I want to go up AND I want to go right"* finds one option that satisfies both goals in a single token. Every such particle collapses onto the same answer. The compound option does not just compete with its components — it dominates them whenever the target is diagonal. Different particles with different nuanced reasoning all converge on the one option that is never wrong in the compound sense.

Both effects exist because the LLM is being forced to match its continuous, nuanced reasoning onto a discrete menu. The menu is the failure surface.

### Attempt 3 — Target-point movement (run `150058`, this report)

**What we changed:** Removed the direction menu from the prompt entirely. We replaced *"pick one of 8 directions"* with *"name a point you want to move toward."* Everything else stayed the same — still 1 cell per step, still 8-direction movement under the hood, still identical sensory input and identity framing.

**Prompt excerpt:**
> Pick a point (x, y) you want to move toward this step. It can be any location — a threat, the Mothership, a spot between them, the void. You will move one step toward that point. Or choose to stay.
>
> Respond in JSON:
> `{"action": "move", "target": [x, y], "intent": "brief reason"}`
> or
> `{"action": "stay", "intent": "brief reason"}`

**Server-side translation:** given current position and the LLM's named target, compute `dx = tx − x`, `dy = ty − y`, take the sign of each axis (with a 0.25-unit deadband so near-zero deltas count as "stay"), and look up the matching direction in the 8-direction table. No heuristics. No ranking. No inherent preference.

**Metrics:**
- Max shield coverage: **1.00** (first time any run has hit this)
- Avg post-threat coverage: **0.28** (matches 4-direction baseline, but with dramatically higher peaks)
- Response time: **2 steps** after threat appearance
- Final intent distribution: **15 protect / 5 other**
- Direction spread at step 1: **all 8 directions used**
- Unique targets: 17–19 of 20 particles in early steps, settling to 13/20 at mid-run as the swarm converged

---

## What actually happened in the run

### Phase 1 — Calm orbit (steps 1–3)
Coverage: 0.00. Particles drift in different directions based on their local starting position. 19 unique targets across 20 particles. This is baseline noise — the swarm is doing nothing coordinated yet because there is nothing to coordinate around.

### Phase 2 — Threat appears (steps 4–10)
Coverage climbs from 0.00 to 0.30. Mothership state changes to *"alert — threat detected at (20.0, 5.0), distance 20.6"*. Particles within perception radius of the threat begin to see it. Intent strings immediately reference the threat — *"monitor the threat"*, *"approach to assess"*. The swarm starts loosening from orbit.

### Phase 3 — Convergence march (steps 11–25)
Coverage drops to 0.00 for most of this window. This is misleading — the metric says "particles between threat and mothership", and the particles have started moving **past** the shield line toward the threat itself. They are not holding a defensive position; they are advancing. Unique target count drops as more particles converge on similar coordinates.

### Phase 4 — Contact (steps 26–40)
Coverage climbs 0.25 → 0.70 → 0.85 → **1.00**. By step 35, reading the intent log directly, ten of twenty particles all specified targets within a 0.1-unit radius of `(4.5, 1.1)` — essentially the threat's current position. Their intent strings: *"neutralize the threat before it reaches the Mothership"*, *"intercept it"*, *"engage"*. Cohesion score drops to **0.46**, meaning the mean nearest-neighbor distance is under half a cell — particles are physically piled on each other.

The two screenshot frames (step ~28 and ~36) show this clearly: first a dense cluster forming northeast of the mothership, directly between M and the threat; then, a few steps later, particles completely enveloping the threat triangle on all sides.

### Phase 5 — Pass-through (step 41)
Coverage collapses to 0.00 as the threat reaches the breach radius around the mothership. The swarm did not stop it (more on this in caveats).

---

## Why we think this worked (the mechanism)

Four interlocking reasons, in rough order of importance:

**1. No menu means no positional bias.** There is nothing to be listed first. The LLM cannot favor an option because no options are presented. The very structure that caused the `up-right` collapse no longer exists.

**2. No menu means no semantic-superset collapse.** Two particles that both want to go "northeast" can want to go to *different northeast points*. The old menu let them express "northeast" in the same token; the new interface forces them to name the specific spatial commitment. Particle A at (−3, 2) wanting to reach (6, 4) and particle B at (5, 0) wanting to reach (7, 3) both arguably "go up-right" — but the first moves almost due east and the second moves almost due north. The named target disambiguates what the menu flattened.

**3. The LLM is thinking in its native modality.** Spatial reasoning about places and points is closer to how language models have learned to describe the world than *"pick one of eight compass labels."* The cognitive load shifts from "match my reasoning to a category" to "state where I want to be" — and stating where you want to be is a more natural act of description for a language model.

**4. The output encodes more information.** A direction label is a function from 20 particles to 8 values — at most three bits per particle per step. A target point is ℝ². When we log these targets, we can see *spatial consensus* that a direction log would hide. At step 35 the log literally showed ten particles converging on a 0.1-unit patch of space. That is a coordination signal the discretized interface was destroying before it reached us.

A further observation worth stating explicitly: **the translator is a design artifact we own, and it is not neutral by accident.** We built it to be monotonic (closer target → same direction), symmetric (equal treatment of all 8 directions, no favored axis), and small enough that there is no room for it to do anything clever. If we had used a messier translator — say, a classifier trained on labeled data, or a weighted scheme that preferred cardinal directions — we would have smuggled the menu bias back in at the motor layer. The clean, symmetric, deterministic translator is what preserves the LLM's intent downstream. This is the lesson generalized: the translator must be as neutral as it is discrete, or you have just moved the problem.

---

## What emerged — and why it was not what we expected

We set out to study whether particles could form a **defensive shield**. What they actually did was **attack**.

Specifically: the swarm gathered, then rushed the threat. Intent fields never mentioned "shield" or "wall" once the threat appeared. Instead: *"intercept"*, *"neutralize"*, *"engage"*, *"assess and neutralize potential danger"*. The resulting spatial pattern did coincidentally produce a perfect "shield coverage" score (1.00) — because a dense cluster between the mothership and the threat technically sits on the threat-to-mothership line — but the *strategy* the particles verbalized and enacted was offensive, not defensive.

This is a genuine and somewhat unexpected finding. Nothing in the prompt told them to attack. The word "attack" does not appear; neither does "group", "swarm", "rush", "engage". The prompt says only *"You are a guardian warrior. Your purpose is to protect the Mothership."* and then provides sensory data. The collective tactic — gather, then charge the threat in formation — was assembled from twenty independent local decisions that each happened to be some version of *"move toward where the threat is."*

It is worth asking which parts of the setup produced this. Two candidates:

1. **The identity framing.** An earlier edit changed "guardian particle" to "guardian warrior." A warrior naturally carries connotations of engagement, not avoidance. The behavior may be partly downstream of that single word choice. An ablation where we revert to a more neutral identity would tell us how load-bearing the word "warrior" is.

2. **The absence of any spacing or spreading pressure.** The prompt does not tell particles to stay apart, or to avoid overlap, or to hold formation. Without a spreading term, "move toward the threat" is a uniformly attractive gradient for all particles, and they stack up on it. Adding a *"fellow guardians stand with you"* framing without any explicit anti-clumping pressure may have amplified this further. A future experiment could add light repulsion language ("do not crowd your fellow guardians") and see whether a distributed shield emerges instead.

Either way, the emergence is real. The swarm did something collective and coordinated, from local information, without being told to.

---

## Honest caveats

**1. The threat was still breached.** Every shield_test run — including this perfect-coverage one — shows a breach at step 41. That is because the threat is a dumb programmed entity moving at 0.5 units/step on a straight line from (20, 5) to (0, 0), and particles currently have no physical effect on it. A particle at the threat's position does not block it, slow it, or push it. The "perfect shield" at steps 37–40 was visually complete but mechanically a ghost. If we want breach to be an honest metric, we need an interception mechanic — for example: the threat's speed drops by some factor for each particle within N units of it, or the threat stops entirely when surrounded.

**2. Avg post-threat coverage (0.28) understates the result.** The metric averages across the whole window after the threat appears, which includes the ~20 steps the swarm spent *traveling* toward the threat. Coverage was 0.00 during travel because the particles had moved past the defensive line toward the threat itself. Peak coverage (1.00 for four consecutive steps) tells a more accurate story of what happened at contact.

**3. n = 1.** This is a single run. We have not yet replicated it across seeds. Before treating this as robust, we should run 3–5 more shield_test seeds with the target-point interface and check that the attack-swarm pattern reproduces.

**4. The identity-framing confound.** As noted, we changed the identity string to "guardian warrior" before this run. We have not isolated how much of the attack behavior comes from that word versus from the target-point interface change. Without an ablation, we can't cleanly attribute the finding.

**5. The translator is a design choice that could be wrong in other settings.** Our translator works because it is symmetric across all 8 directions. In a setting with anisotropic geometry (e.g. long corridors), a symmetric round-to-8-direction mapping might discard meaningful information. The principle — separate cognition from execution — is general; the specific translator is specific.

---

## Implications beyond this simulation

The separation we stumbled into is a useful pattern for LLM agents in general. The failure mode we hit — LLM converges on one menu option because the option semantically dominates — will recur in any system that gives an LLM a fixed action list where some options are strict improvements over others in common contexts.

**Examples where this pattern probably applies:**

- Tool-use agents picking from a fixed tool menu. If one tool is a strict superset of two others, the LLM may over-select it even when a more specific tool would produce better results.
- Dialogue agents with fixed response categories. If one category subsumes others, it dominates.
- Multi-step planning agents picking from a discrete action vocabulary. Same principle.

**The generalizable advice:**
- Let the LLM express intent in the richest modality it can. Natural language, coordinates, counts, targets — not menu indices.
- Keep the translation layer between intent and execution as small, symmetric, and deterministic as you can make it.
- Log the intent, not just the executed action. Discretization discards information you will later wish you had kept.

---

## Takeaway

> Replacing a discrete action menu with a continuous spatial intent preserved the research purpose — LLM interprets a local situation and acts — while removing a confound: LLM picking the first or semantically strongest option from a fixed menu. The result was the first run where collective behavior was both unambiguous and clearly emergent.

The particles did not follow rules. They did not copy each other's syntax. They each looked at the world, named a point they cared about, and the points they cared about converged. The convergence was the shield. Or, in this case, the attack.

We changed one thing: we stopped asking them to pick a move and started asking them where they wanted to be. The cognition stayed with the model. The translation moved to a deterministic layer. The emergence appeared.
