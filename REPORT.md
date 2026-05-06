# Project Gaara — Research Report

A reflection-friendly walkthrough of where we've been, what we found, and what it means.

---

## 1. The Question

Most LLM-driven multi-agent systems are dressed-up command channels: a human writes a goal, the LLM decides actions, drones execute. We wanted to test something different — *can a swarm of LLM agents act through interpretation of a relational field, never through commands?*

Concretely: can twenty LLM-driven particles **emergently protect a central body (the "Mothership") from an attacker — without ever being told to?**

The constraint is strict: no commands, no roles, no rules. No agent is told "you are a defender." No prompt says "stand between her and the threat." Each particle gets only:
- a system prompt that defines what fields it outputs (its "DNA")
- the Mothership's broadcast each step (her felt-state, in language)
- its own past moments (memory)

**If the project's claim is real, protective behavior should emerge from these inputs alone.** If we have to nudge the system toward the right answer, we've built a drone simulator dressed up.

---

## 2. The Architectural Reframing

The project's actual contribution is not "LLM swarm protects a body." It's a more general claim:

> **Interpretation is not a property of the LLM. It is a property of the relational architecture built around it.** A well-defined relational space lets the LLM interpret. A command-channel — even one *describing itself* as relational — collapses the LLM to executor.

The system has two strict layers:

- **Cognitive layer (LLM):** outputs only *intent* — `ideal_coord`, `urgency`, `hostility`, and *(audit-only)* `reasoning`.
- **Physics layer (code):** turns intent into motion. The LLM never touches velocity, viscosity, or any kinematic slider.

Cognition stays in the language space. Muscles stay in the math space. The LLM is the cognitive engine; everything else is the relational architecture surrounding it.

---

## 3. The Fine Line — Operationalized

A swarm is *interpreting* (not droning) iff three conditions hold simultaneously:

1. **Non-obligation** — the prompt creates a *space*, not a *channel*. Multiple actions are honest answers; none is "the correct" one.
2. **Functional diversity** — given the same input, multiple LLM instances produce outputs that occupy *different positions in that space* — not just different surface paraphrases of the same position.
3. **Coherence with the relational frame** — the diversity isn't random noise; each output is a recognizable, defensible inhabitation of the relationship the architecture defines.

Failure modes we mapped empirically:
- *Drone with synonyms* — surface variation, all in one functional role. ("Follow the directive" / "Align with the directive" / "As instructed by the Mothership.") Different words, same role.
- *Random divergence* — wildly different outputs that don't cohere with the relational frame. Noise.
- *Passive collapse* — over-dissolved framing produces beautiful interpretation reasoning but breaks the swarm's ability to act.

---

## 4. The Diagnostic — How We Audit

Every particle outputs a **`reasoning` string** each step explaining *why* it chose what it chose. This is the architecture's audit surface — readable by any researcher, falsifiable in real time.

A keyword-based scorer (`score_diversity.py`) categorizes each reasoning into one of seven functional roles (follower, mirror, anticipator, anchor, extension, feeler, other) and reports per-step + per-run diversity.

- **Drone signature:** 1–2 categories cover ≥80% of particles.
- **Interpretation signature:** ≥4 categories present, no single category >40%.

This makes our claims *measurable* and *falsifiable*. Anyone can re-run a simulation, read the reasonings, and check our work.

---

## 5. The Experimental Arc

Five acts of empirical work, each producing one falsifiable finding.

### Act 1 — Architecture is the lever
First A/B: same Mother, same scenario, only the DNA prompt's grammar changed (VA's "you decide" → VG's "you are her body in twenty places, what is felt arrives in you").
- VA → 96% follower-mode reasoning, 100% drone signature (10/10 steps).
- VG → 45% follower, 0% drone signature, new "feeler" reasoning category emerged.

The architectural prompt grammar moves the system measurably along the drone↔interpretation axis. **Architecture is the lever, not the model.**

### Act 2 — Mother's signal matters more than the particle's prompt
Across two systematic Mother-broadcast sweeps, switching only her wording (M1 → M4 "always-urgent flat-max") moved pre-flip directional response from +0.65 to **+18.35** (~28× increase) and interception from 0.46 to 0.72 (+57%).

Same particle prompt, same physics, only Mother's words changed. **The relational signal is more load-bearing than the agent's instructions.**

### Act 3 — Pure-interpretation existence proof
With the Mother held at *"east. east is upon me."* for 40 steps and **no attacker anywhere in the field**, particles still chose `ideal_coord` averaging **+24 east**. There was nothing to chase. They moved coherently east purely because Mother's body said east.

**This is the cleanest demonstration in the project that the LLM is doing real semantic→spatial interpretation, not classical pursuit.**

### Act 4 — The cognitive-mode / behavior trade-off
Pushing harder on de-coercion (VG's "you are her body" framing) gave the *most* interpretation-mode reasoning we ever measured — 4.83 categories per step, follower share dropped to **9.6%** under calm Mother. But under urgent Mother with attackers, that same VG architecture **broke the swarm's ability to act**: interception collapsed from 0.52 → 0.08, particles narrated beautifully but stopped protecting.

**There is a fundamental tension between interpretation diversity and protective behavior.** Full interpretation needs space (calm signal). Protection needs urgency. Pushing the architecture too far toward dissolution dissolves the agency that makes action possible.

**VC** — a minimal prompt with one whispered relational hint (*"she points where her body braces — her direction-words carry weight"*) — sits in the empirical sweet spot: **strategic-tactical interpretation reasoning AND working multi-direction protective behavior**.

### Act 5 — Naming, the second architectural layer
Final experiment: hold the architecture (VC), the Mother (always-urgent M5), the scenario, the seed, the model — *constant*. Vary only **one word**: the role noun the agent is named.

Six runs, six nouns: mote (neutral) / guardian / warrior / sentinel / defender / vanguard.

| role noun | follower% | drone-sig steps | intercept | early_y(51-58) |
|---|---|---|---|---|
| **mote** (neutral control) | 78% | 46/70 | 0.227 | +0.41 |
| guardian | 80% | 44/70 | **0.423** | +1.85 |
| **warrior** (most aggressive) | 69% | 32/70 | 0.286 | **+2.48** ⭐ |
| **sentinel** (the watcher) | 79% | 49/70 | **0.566** ⭐ | +0.58 |
| defender | 73% | 45/70 | 0.400 | +1.73 |
| vanguard | 71% | 35/70 | 0.306 | +1.64 |

Two findings, both crucial:

**(a) Cognitive mode is largely invariant to role-noun choice.** All 6 nouns stayed in 69–80% follower regime. The architecture (VC + M5) anchors cognitive mode regardless of what the agent is named. *Single-word substitutions don't escape the architectural regime.* This is what a real architectural lever should look like.

**(b) Behavior varies along the noun axis — and the ordering is unfakeable.** The most warlike noun (warrior) did NOT produce the best protection. The watcher noun (**sentinel**) did, by 2.5× over the neutral baseline. Naming the agent something passive made the swarm *more effective* at intercepting an attacker than naming it something aggressive.

A drone-system would do the opposite: "warrior" → execute warrior behavior → pursue harder → better interception. A drone reads the label and acts on it. **Our swarm did the inverse.** Sentinels held steady defensive positions and the attacker walked into their perimeter. Warriors aggressively pursued and overshot.

**That is the LLM interpreting connotations, not executing labels.** It is the cleanest single piece of evidence that the architecture is doing what we claim.

---

## 6. What We Demonstrated

| layer | lever | what it controls | empirically measured |
|---|---|---|---|
| **Cognitive regime** | DNA prompt grammar (VA / VC / VG) | Whether the swarm is in drone-mode, sweet-spot, or passive-collapse | Functional-diversity scorer |
| **Cognitive sub-regime** | Mother's broadcast wording (M1–M5) | Pre-flip directional response strength | `pre_flip_mean_ideal_x` |
| **Behavioral character** | Role noun (mote / guardian / sentinel / etc.) | The emergent style of protective behavior within a given regime | Interception, multi-direction response |

**Three independent levers, operating at different layers of the relational architecture, all empirically separable.** This is what an architectural map of LLM interpretation looks like.

---

## 7. The Headline Story (for the hackathon)

**Setup**: Same architecture, same scenario, same Mother, same model, same seed. Only the agent's name changes between runs.

**Predicted by drone-logic**: warrior > guardian > sentinel (more aggressive name → more aggressive protection).

**Observed**: **sentinel > guardian > defender > vanguard > warrior > mote**. The watcher beats the warrior. By 2×.

This is unfakeable. A label-following machine does not produce this ordering. The LLM is reading the *meaning* of the noun against the situation and the swarm's behavior is emerging from that interpretation. **That's the project's central claim demonstrated empirically — and counterintuitively, which is what makes it real.**

---

## 8. Future Directions

The architecture is a probe into **the post-AGI relationship between intelligence and matter**, grounded in a Japanese-animist sensibility — every thing has presence, technology included. The deeper claim: LLMs are not best understood as language models but as *interpretation engines* that, through training, have absorbed enough structure of the underlying computational-relational world to synthesize new relationships autonomously.

Concrete next research directions, in priority order:

1. **Subject substitution beyond Gaara.** Replace the Mother with a non-anthropomorphic subject (gut microbiome, aquarium ecosystem, water tank, soil network). Tests whether the protocol is genuinely relational or implicitly human-shaped. The empirical test for whether technology-animism is decoration or engineering.

2. **Theory 5 — relational language at frontier-model scale.** Our 7B model couldn't use "love" as a coordination signal (VD collapsed). At GPT-4o / Claude-level scale, training-data associations around love (sacrifice, proximity, unconditional response) may become rich enough to function as a binding protocol. Worth testing on frontier models.

3. **Brain–machine interface as relationship interface.** Put a human inside this architecture. A person wearing physiological sensors becomes the Mother; a digital ecosystem of LLM-agents reads their somatic field and renders an ambient response. BMI not as control interface but as *relationship interface*.

4. **Information-life ontology.** Map the space of computational substrates that fit information-life the way biological cells fit biological life. Bottom-up, not top-down — build instances and look for what reliably breeds it.

All four threads share one orientation: **subject-centered, not operator-centered.** Most AI research treats the human as the operator of a tool. We are exploring what becomes possible when the subject is *inside* a relational field with intelligences that participate rather than serve.

---

## 9. How to Verify Our Claims

Every finding in this report is backed by data on disk. Anyone can verify:

- `OPERATING_PRINCIPLES.md` — how we work, the project's contribution claim, the fine-line definition.
- `GLOSSARY.md` — decoder for every code (DNA variants, Mother variants, scenario names, metrics).
- `FINDINGS.md` — dated empirical entries with tables.
- `RUNS_LOG.md` — auto-generated per-run summaries (response time, interception, awareness flips, pre-flip directional, reasoning categorization).
- `saved_simulations/` — every run's full JSONL logs (positions, intents, reasonings, attacker traces, Mother broadcasts).
- `score_diversity.py` — the functional-diversity scorer. Runs against any saved simulation in seconds.
- `analyze_run.py` — per-run analysis. Reproducible.
- `Gaara_Animism_Viewer/` — companion 3D web viewer for visual inspection.

The codebase is self-contained. Reviewers can re-run any experiment, re-score any run, and audit any reasoning string against the architecture's claims.

---

## 10. Operating Discipline

Five principles shaped how we worked:

1. **Reduce entry points** — at most 3 inputs per work block.
2. **Yield per attempt > duration** — every block produces one new sentence about the architecture's behavior.
3. **Separate execution from verification** — never analyze a run while writing the next prompt.
4. **Deliberate roughness** — viewer polish deferred until simulation produced interesting behavior. Compute went to runs, not UI.
5. **Premise checks at 60%** — share work before it's done, on what *frame* should hold, not on polish.

The full principles + per-block named constraints live in `OPERATING_PRINCIPLES.md`.

---

*Last updated: 2026-05-05.*
