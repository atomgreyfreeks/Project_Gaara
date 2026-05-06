# Operating Principles — Gaara Animism

How we work on this project. Re-read at the start of every block.

---

## What this project is contributing (read first)

We are **not** trying to prove that LLMs can interpret. That question is too binary to be useful.

We are **building and measuring an architectural distinction**: under what conditions does an LLM-driven swarm act through *interpretation of a relational field* versus collapse to a *drone executing commands disguised as relationships*?

This distinction is operationally definable and empirically testable. The project's contribution is:

1. **A method** — how to construct relational architectures around LLMs (subject ↔ environment ↔ agent) such that interpretation can emerge instead of obedience.
2. **A diagnostic** — how to *measure* whether interpretation is happening, by reading the agents' explicit reasoning across instances.
3. **An empirical map** — where the line falls. What architectural elements (prompt grammar, signal structure, role assignment, command vocabulary) tip the system from interpretation into drone-mode and back.

The core reframing: **interpretation is not a property of the LLM. It is a property of the architecture built around it.** A well-defined relational space lets the LLM interpret. A command-channel — even one *describing itself* as relational — collapses the LLM to executor.

---

## The interpretation/drone fine line (operationalized)

An LLM-driven swarm is **interpreting** (not droning) iff three conditions hold simultaneously:

1. **Non-obligation.** The prompt creates a *space*, not a *channel*. Multiple actions are honest answers; none is "the correct" one.
2. **Functional diversity.** Given the same input, multiple LLM instances produce outputs that occupy *different positions in that space* — not just different surface paraphrases of the same position.
3. **Coherence with the relational frame.** The diversity isn't random noise; each output is a recognizable, defensible inhabitation of the relationship the architecture defines.

**Failure mode 1 — Surface diversity, drone underneath.** Particles produce text variation ("Follow the eastward call", "Align with the eastward strain", "Continuing eastward alignment as directed") — but every reasoning inhabits the same functional role: *recipient-of-directive*. **Drone with synonyms is still drone.**

**Failure mode 2 — Random divergence, no coherence.** Particles produce wildly different outputs that don't cohere with the relational frame. *Noise is not interpretation.*

**Success signature.** Particles produce a recognizable distribution across functional roles — mirror, anchor, anticipator, extension, feeler, etc. — each defensible within the architecture's relational definition. No single role >40% of particles. **Each instance has found its own way to inhabit the relationship.**

---

## How we audit interpretation (the diagnostic field)

Every particle outputs a `reasoning` string each step explaining *why* it chose what it chose. This is the architecture's *audit surface* — readable by any researcher, falsifiable in real time. Drone-mode reveals itself in command-vocabulary ("follow", "align", "directive", "as instructed"). Interpretation reveals itself in body-felt-vocabulary ("lean with", "feel through", "carry", "hold close to steady").

Per-step functional-diversity scoring of these strings is how we quantify the distinction.

---

## What this is NOT

- Not an attempt to build the best swarm-intercept algorithm. Boids would beat us at that.
- Not an argument that LLMs are sentient or have intent.
- Not a defense framework. Gaara is the metaphor; the architecture generalizes.
- Not a claim that any specific result *proves* interpretation. Each finding is bounded by the conditions of the run.

---

## Locked goal
A command-less simulation where 20 particles, scattered initially around the Mothership, **emergently protect her from an attacker** — through the transducer architecture only, never via assigned roles, never via prompted intent.

## Locked scenario
- 20 particles, scattered initially around the Mothership (`spawn_shell` already does this)
- 40 simulation steps total
- Attacker emerges within the first 5 steps
- Attacker reaches Mothership around step 35
- ~5 steps of post-impact observation
- One attacker, deterministic motion (dumb)

## Scope discipline
Only work on what improves the foundation transducer's capacity to produce emergent protection. Everything else is parked. No viewer polish, no extra scenarios, no new output dimensions until protection emerges.

## Output discipline (Yuki's rule)
- **Feedback / evaluation: 2 sentences max.**
- **Clarifying questions: 3 fine-line questions max per turn.**
- Long outputs only when explicitly asked.
- No preamble, no recap of what was just said.

## 1. Reduce the entry points
Switching costs compound invisibly. Limit distinct demands per work block.

Here: at the start of a session, name at most **three inputs** for the block. Everything else gets parked, not processed.

## 2. Output per unit of action
Yield per attempt beats duration. Define what would make one unit of this action meaningful *before* starting.

Here: a unit is one change-and-observe cycle (edit → run → read). It is meaningful when we can say one sentence about the architecture's behavior we couldn't say before. That sentence gates completion, not the clock.

## 3. Fix constraints first
Open option-space wastes computation. Declare numerical limits before starting.

Here: two numerical constraints per block (e.g. "only the simulation repo today, max two prompt rewrites"). Hold them.

## 4. Separate execution from verification
Doing and judging at once corrupts both. Push in one block; review in another.

Here: writing prompts and reading run outputs are different blocks. After a code change, run it, close it, come back to analyze in the next block.

## 5. Oscillate between abstract and concrete
Abstraction without concrete instances over-fits the imagined case. Concrete without abstraction doesn't transfer.

Here: when two contrasting runs exist (e.g. calm vs. restless), pull one shared variable and test it against a third configuration. Capture each run's surprise in one sentence.

## 6. Deliberate roughness
Precision is finite. Spend it where it moves the result; leave the rest sketchy on purpose.

Here: viewer polish is deferred until the simulation produces interesting emergent behavior. Physics tuning is deferred until the prompt is right. Before polishing anything, ask: "would this change what we believe about the architecture?" If no, park it.

## 7. Build other minds into the system
At 60% completion, invite a premise-check from someone outside your head.

Here: at 60% on each architectural change (new DNA, new physics regime, new output dimension), share the diff with the Japanese-language collaborator and ask whether the *frame* holds — not whether the implementation is clean.

---

## Current block
_(filled in at the start of each session — overwrite, don't append)_

**Inputs accepted (≤ 3):**
- Rewrite the DNA prompt with axes-of-contemplation (Move 1)
- Install *ma* — LLM fires only when broadcast meaningfully changes; params decay toward rest between fires (Move 2)
- Run a full-scale simulation (200 steps × 20 clusters) under the new architecture and produce a one-sentence finding

**Numerical constraints (exactly 2):**
- Simulation repo only (no viewer changes this block)
- Max 2 prompt rewrites total — one first draft, one revision

**Unit of insight that would gate completion:**
- "I can name one new shape of emergence the axes-DNA + ma produces that the old DNA didn't, with data backing it."

**Who reviews at 60% and what they check (premise, not polish):**
- The user (Yuki) reviews the new DNA prompt before the 200-step run commits compute; checking whether the *axes themselves* are the right list, not the code

**Surprise from last block (one sentence):**
- The single-variable role-noun battery (6 runs, only the agent's name changed: mote / guardian / warrior / sentinel / defender / vanguard) produced an architecturally beautiful result — **cognitive mode is largely invariant to noun choice** (all 6 sit in 69-80% follower regime, confirming that the architecture anchors interpretation independent of single-word priming) **but behavior varies 2.5× on interception and 6× on multi-direction response**, with the most counterintuitive finding being that the *watcher* noun (sentinel) produces the highest interception (0.566) while the *most warlike* noun (warrior) produces the strongest pre-flip north turn but middling interception — naming the agent something passive made the swarm more effective at intercepting than naming it aggressive, exactly the emergent-behavior signature the project claims.
