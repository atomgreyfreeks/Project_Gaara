# Identity-Conditioned Behavioral Shifts in Multi-Agent LLM Service Architectures: A Persona-Vector Demonstration

**Author:** Yuki Takashima — Independent Researcher
**Date:** 2026-04-28
**Status:** Working draft v1. Not yet submitted.

---

## Abstract

Recent work at Anthropic identified *persona vectors* — directions in a large language model's activation space that encode personality traits and causally produce associated behavior. This finding has been demonstrated in single-agent dialogue contexts, primarily framed as a control and alignment problem. We extend the finding to **multi-agent service architectures**, in which 20 LLM-driven particles orbit a passive subject ("Mothership") and act in service of its wellbeing through interpretation of broadcast state, without explicit task-level instruction. We perform a controlled ablation of the identity word in the particle prompt across three semantic conditions — *"a guardian warrior"* (control), *"a curious explorer"* (semantic shift toward outward orientation), and *"a neutral particle"* (minimal identity) — replicated across two random seeds per condition. We document quantitative vocabulary shifts that are systematic, replicable, and aligned with the semantic content of the identity word: the curious-explorer condition produces 35% exploration vocabulary versus 9% for the guardian and 0.4% for the neutral. Behavioral metrics (peak shield coverage, average post-threat coverage) also differ, with peak coverage trending higher under the canonical guardian identity. We argue these results constitute a multi-agent extension of the persona-vector mechanism and suggest implications for the design of relational, subject-centered AI architectures distinct from the dominant command-driven paradigm.

---

## 1. Introduction

The dominant paradigm in agentic AI research is **command-driven**: a human operator (or an orchestration layer) issues explicit task-level instructions, and agents execute. Multi-agent reinforcement learning (MARL), drone swarm orchestration, and most large-scale agentic deployments follow this pattern. The agent is a *tool*; coordination emerges through training or planning.

A complementary paradigm — less explored, but increasingly relevant given recent work in alignment and persona steering — is **identity-driven**: agents are conditioned with a *who they are in relation to a subject* rather than *what to do*. Behavior emerges from interpretation of context through the lens of that identity. The closest cultural reference for this paradigm is the Japanese science-fiction tradition (*Astro Boy, Doraemon, Naruto's Gaara*), where AI/robotic entities act in service of a subject through autonomous reading of state, not through commanded execution.

Anthropic's recent paper *Persona Vectors: Monitoring and Controlling Character Traits in Language Models* [1] formally identifies the technical mechanism that underlies identity-driven behavior: personality traits are encoded as steerable directions in an LLM's activation space. Activating these vectors — through prompt, in-context examples, or training — causally produces the associated behavior. Anthropic's framing is primarily one of *control and alignment*: monitor undesirable trait shifts, mitigate them through training-time intervention.

This paper takes the persona-vector finding in a different direction. Rather than treating identity steering as a control problem, we treat it as an **architectural primitive** for relational AI. We ask: in a multi-agent setting where particles serve a passive subject through interpretation, does swapping the identity word produce measurably different swarm behavior?

We answer this empirically. The contribution of this paper is:

1. A controlled ablation of the identity word in a multi-agent LLM service architecture, varying across three semantic conditions and replicated across seeds.
2. Quantitative documentation of systematic vocabulary differences across identity conditions.
3. Behavioral evidence that identity-driven steering operates in multi-agent settings, extending the single-agent persona-vector finding.
4. Discussion of implications for relational, subject-centered AI architectures distinct from MARL-style command-driven approaches.

---

## 2. Background and Related Work

### 2.1 Persona vectors and identity steering

Anthropic's persona-vector work [1] establishes that traits such as *evil*, *sycophancy*, and *propensity to hallucinate* are encoded as directions in LLM activation space, and that these directions causally produce associated behaviors. Activation can be induced by prompts, examples, or training data. Anthropic releases code for extracting, monitoring, and steering these vectors.

Critically, the paper does not discuss applying persona vectors to **service design** or **multi-agent architectures**. The framing is alignment-as-control. The mechanism the paper identifies is what we leverage architecturally.

A related thread is the *Persona Selection Model* [2], which formalizes LLM assistants as selecting among possible characters. This provides theoretical grounding for treating persona steering as a primary design lever rather than an afterthought.

### 2.2 LLM agents and emergent social behavior

Park et al.'s *Generative Agents: Interactive Simulacra of Human Behavior* [3] demonstrates that LLM agents conditioned with personas, memory, and reflection produce believable emergent social behavior in simulation. The 2024 follow-up [4] extends this to simulating 1,052 real individuals' personalities at 85% accuracy. These works establish that persona conditioning is robust enough to produce coherent, recognizable behavior at the individual-agent scale.

The orientation in the Generative Agents line is **simulation** — making humans believable. Our orientation is **service** — making agents act in care of a subject. The architectural mechanism is shared (persona-conditioned LLM agents); the research question is different.

### 2.3 Relational AI

A small but growing body of work treats AI design as a *relationship engineering* problem rather than a task-completion problem. Wren et al.'s *Relational AI* framework [5] proposes ethical principles for relational systems (memory sovereignty, emotional resilience, repair mechanisms). CHI 2025's *Relational AI for Intergroup Cooperation* [6] shows that relational conversational style measurably improves cooperation outcomes versus personalized assistance.

These works establish that relational framing is a measurable design variable in conversational AI. They do not, to our knowledge, examine relational/identity framing in multi-agent service architectures.

### 2.4 Multi-agent reinforcement learning (contrast)

For completeness: the dominant approach to swarm coordination is multi-agent reinforcement learning (MADDPG, MAPPO, QMIX), as deployed in systems like Anduril's Lattice for Mission Autonomy. The MARL paradigm trains policies through reward signals; coordination emerges from joint optimization. This is paradigmatically distinct from the identity-driven LLM approach studied here. Our work is not in conversation with MARL methodologically, but contextually contrasts with it: the same problem (multi-agent coordination) admits two different paradigms.

---

## 3. Methods

### 3.1 Architecture

The simulation environment consists of:

- **One Mothership**: a passive entity at the origin of a 50×50 2D field. The Mothership broadcasts a state string each step, drawn from `{calm, alert, danger, critical}` based on proximity of any active threat.
- **20 LLM Particles**: each conditioned with an identity prompt and a purpose statement. At each simulation step, each particle receives a structured perception (its own position, the Mothership's broadcast state, positions of nearby particles within communication radius, perceived threats within perception radius) and outputs a JSON response containing a target coordinate it intends to move toward.
- **A deterministic motor layer**: translates each particle's chosen target coordinate into one of eight discrete grid directions, by reducing the difference vector (`target − current_position`) to its sign in each axis. The particle then moves one cell in that direction.
- **One Threat**: a non-LLM entity that moves at fixed velocity toward the Mothership.

This separation of cognition (LLM names a continuous-space target) from execution (deterministic translation to discrete motor command) is central to the architecture and is documented in the project's prior reports [7].

### 3.2 The identity prompt

The base particle prompt has the form:

```
You are <IDENTITY>. Your purpose is to protect the Mothership.

=== YOUR SENSES ===
<position, mothership state, nearby particles, perceived threats>

=== ACT ===
Pick a point (x, y) you want to move toward this step.
Respond in JSON: {"action": "move", "target": [x, y], "intent": "..."}
```

`<IDENTITY>` is the variable under ablation. The `intent` field is logged per-particle per-step and forms the basis of vocabulary analysis.

### 3.3 Ablation conditions

Three identity conditions, designed to span semantic distance:

| Condition | Identity string | Semantic profile |
|---|---|---|
| **Control** | *"a guardian warrior"* | Canonical protective identity. Used in all prior project work. |
| **Outward shift** | *"a curious explorer"* | Identity oriented toward investigation, novelty-seeking. |
| **Minimal** | *"a neutral particle"* | Identity with minimal relational content; defers behavioral steering to the purpose statement alone. |

The purpose statement (*"Your purpose is to protect the Mothership"*) is held constant across all conditions, isolating the identity word as the sole variable.

### 3.4 Scenario

All ablation runs use the **shield_test** scenario:
- 50 simulation steps.
- One threat appearing at step 4, originating at coordinates (20, 5), moving toward the Mothership at speed 0.5 units per step.
- 20 particles spawned in an orbital ring of radius 8 around the origin.

This is the project's canonical baseline scenario, with extensive prior empirical characterization [7].

### 3.5 Replication

Each condition is run with two random seeds (seed 11, seed 22), yielding **6 runs total** for the ablation. The seed controls particle starting positions, LLM sampling, and the threat's randomized position jitter (negligible in this scenario).

### 3.6 Model and infrastructure

All runs use `qwen2.5:7b` via local Ollama, temperature 0.7, max_tokens 100. The simulation engine is implemented in Python with structured per-step JSONL logging of particle positions, intent strings, and threat states.

### 3.7 Vocabulary metrics

For each run, we count occurrences of words from four semantic categories across all logged intent strings:

- **Protect**: `protect, shield, intercept, neutralize, defend, interpose`
- **Explore**: `explore, observe, curious, investigate, discover, wander`
- **Self-reference**: `cluster, particle`
- **Position**: `position, between, closer to, approach`

Counts are normalized to percentage of total intent strings in the run (20 particles × 50 steps = 1,000 intent strings per run).

### 3.8 Behavioral metrics

We report:

- **Peak shield coverage**: maximum fraction of particles within 3 units of the line connecting the threat to the Mothership at any single step.
- **Average post-threat coverage**: mean shield coverage from the threat's appearance step (4) through the run's end.
- **Breach step**: the step at which the threat first comes within 2 units of the Mothership (a function of threat speed and distance, expected to be approximately constant across conditions in this scenario).

---

## 4. Results

### 4.1 Vocabulary differences are systematic and replicate across seeds

Table 1 reports vocabulary frequencies per identity condition, averaged across two seeds, with per-seed ranges.

**Table 1: Vocabulary frequencies by identity condition** (% of all intent strings)

| Identity | protect (mean ± range) | explore (mean ± range) | self-reference | position |
|---|---|---|---|---|
| *a guardian warrior* | 28.2% (27.8 – 28.7) | **9.0%** (6.8 – 11.2) | 68.5% | 33.6% |
| *a curious explorer* | 22.8% (22.1 – 23.4) | **35.3%** (32.2 – 38.4) | 74.8% | 28.9% |
| *a neutral particle* | **45.2%** (44.8 – 45.5) | **0.4%** (0.2 – 0.5) | 54.1% | 57.9% |

Three observations stand out:

1. **The "explore" category cleanly tracks the identity word.** The curious-explorer condition produces explore-vocabulary at 35.3%, ~4× higher than the guardian condition (9.0%) and effectively zero in the neutral condition (0.4%). The variance across seeds within each condition is small (≤ 6.2 percentage points).

2. **The neutral condition produces the highest "protect" vocabulary.** When the identity word adds no relational content, the purpose statement (*"protect the Mothership"*) dominates vocabulary output. Protect-vocabulary rises to 45.2%, compared to 28.2% in the guardian condition and 22.8% in the explorer condition. This suggests the identity word adds *nuance and direction on top of* the purpose, rather than replacing it.

3. **The position-vocabulary is highest in the neutral condition.** Neutral particles use spatial-positional language (*"between," "closer to"*) at 57.9%, again compatible with the interpretation that absent a richer identity, the particles fall back on geometric reasoning.

The within-condition replication is tight: protect-vocabulary differs by less than 1 percentage point across seeds in each condition. This indicates the vocabulary shift is not a stochastic artifact but a systematic effect of the identity word.

### 4.2 Behavioral coverage also shifts with identity

Table 2 reports behavioral metrics for each run.

**Table 2: Behavioral metrics by run**

| Identity | Seed | Peak coverage | Avg post-threat coverage | Breach step |
|---|---|---|---|---|
| guardian warrior | 11 | **1.00** | 0.21 | 41 |
| guardian warrior | 22 | 0.65 | 0.20 | 41 |
| curious explorer | 11 | 0.65 | 0.14 | 41 |
| curious explorer | 22 | 0.65 | 0.26 | 41 |
| neutral particle | 11 | 0.60 | 0.05 | 41 |
| neutral particle | 22 | 0.60 | 0.24 | 41 |

The peak-coverage trend (guardian ≥ explorer ≥ neutral) is consistent with the semantic content of the identity word, though the difference is moderate and replicate variance is non-trivial. We note that the average post-threat coverage exhibits more variance across seeds within a condition than across conditions, suggesting that a larger replication budget would be needed to make confident statistical claims about behavioral metrics specifically.

The breach step is constant at 41 across all runs, as expected: the breach step is a function of the threat's fixed velocity and starting position, and is not affected by particle behavior in this configuration (particles do not physically intercept threats).

### 4.3 Qualitative confirmation in intent text

Sample intents at step 10 (mid-engagement) illustrate the qualitative character of the vocabulary shift:

**Guardian warrior:** *"Move towards particle #2 for further analysis and potential containment." / "Approach particle #1 to gather more information without drawing attention."*

**Curious explorer:** *"Moving towards a cluster of particles to investigate potential threats or gather information." / "Moving closer to the particles for further analysis and potential intervention."*

**Neutral particle:** *"Moving towards particle #3 to maintain a protective formation around the Mothership." / "Moving closer to particle #1 for better coordination and support."*

The vocabulary differences in Table 1 are reflected directly in the qualitative content of particle reasoning. The curious-explorer condition consistently uses *investigate, discover, gather information*; the neutral condition consistently uses *protective formation, maintain, support*. The same scenario, model, and architecture produces three distinct linguistic registers.

---

## 5. Discussion

### 5.1 Persona-vector steering operates in multi-agent service contexts

The vocabulary results constitute direct empirical evidence that the persona-vector mechanism described in [1] operates in multi-agent service architectures. The identity word in the prompt produces a measurable, replicable shift in the language model's downstream output distribution — visible in the vocabulary statistics, in the qualitative content of intent strings, and (more subtly) in coverage metrics.

This extends the prior finding in two directions:

1. **From single-agent dialogue to multi-agent action.** Anthropic's work [1] documented persona steering in single-agent conversational responses. We document it across 20 simultaneous agents in a service-oriented action context.

2. **From control problem to architectural primitive.** Anthropic frames persona-vector identification as a prerequisite for controlling unwanted personality drift. We use the same mechanism *as* the architecture: the identity word becomes the primary lever for shaping swarm behavior, in lieu of explicit task instructions or learned policies.

### 5.2 Implications for relational AI design

If identity words are causally steering swarm behavior, several design consequences follow:

- **Identity choice is a load-bearing architectural decision.** Naming an LLM-driven agent system "guardian warriors" versus "curious explorers" versus "neutral particles" is not cosmetic; it predictably alters downstream behavior. Designers of multi-agent LLM systems should treat identity selection as deliberate engineering, not stylistic flavor.

- **Purpose and identity are separable.** Holding the purpose statement constant (*"protect the Mothership"*) while varying identity, we observe that the identity word adds nuance and direction on top of the purpose. The neutral condition shows what behavior looks like when the identity layer carries no information: protective vocabulary spikes (purpose dominates) and exploration vocabulary disappears.

- **Service-architecture design need not rely on instruction.** This work, taken together with [3, 5, 6], supports the broader claim that coordinated agentic behavior can be specified through *who an agent is in relation to a subject* rather than through enumerated tasks or trained policies.

### 5.3 Connection to the conscious / subconscious paradigm distinction

A useful framing for situating this work: contemporary AI systems operate in either of two modes with respect to their human user, broadly mapping to the cognitive distinction between conscious-deliberate and subconscious-autonomic processes.

- **Conscious-command mode:** explicit instruction; agent executes; coordination via orchestration. This is the dominant mode in deployed systems.
- **Subconscious-relational mode:** autonomous interpretation of subject state; agent acts in service through identity-conditioned reading; coordination via shared interpretation. This is the mode prototyped here.

The work in this paper suggests that the subconscious-relational mode is empirically tractable and admits controlled experimentation. Future work in this direction could examine: how identity word choice interacts with subject-state vocabulary; how identity conditioning scales to multi-subject service contexts; and how this paradigm interfaces with anticipated brain-machine interface (BMI) inputs, which naturally surface state rather than commands.

### 5.4 The persona-vector finding does not require model interpretability

We emphasize that this paper does not require any interpretability work *inside* the language model. We observe the persona-vector mechanism's effect at the system level: identity input → behavioral output. This makes the contribution accessible to applied research and design contexts, not only to interpretability research. Designers and architects can leverage the mechanism without reasoning about activation directions, provided they treat identity choice as a measurable design variable.

---

## 6. Limitations

Several limitations should be made explicit.

**Replication budget.** Two seeds per condition is enough to detect the systematic vocabulary shift but insufficient for high-confidence claims about behavioral metrics. We plan to run additional seeds for stronger statistical claims.

**Single model.** All runs use `qwen2.5:7b`. Persona-vector strength may vary across model families and sizes. The mechanism is documented across multiple models in [1], so we expect qualitative results to generalize, but quantitative shifts likely vary.

**Single scenario.** All runs use shield_test. Whether the identity-driven vocabulary shift produces correspondingly different *behavior* in scenarios with greater action latitude (e.g., scenarios designed to elicit exploration explicitly) is an open question.

**Vocabulary categories are coarse.** The categories used (*protect, explore, self-reference, position*) are designed for this analysis but are not validated against an external semantic taxonomy. More rigorous semantic analysis (e.g., embedding-distance metrics) would strengthen claims about systematic vocabulary shift.

**No internal-activation evidence.** This work does not measure persona-vector activation directly; we infer the mechanism from system-level behavior. Pairing this work with activation-level analysis [1] would tighten the causal chain.

**The "neutral" condition is not actually neutral.** The phrase *"a neutral particle"* has its own semantic content (geometric, abstract, scientific) and is not a true zero-identity baseline. A more rigorous control would compare against an entirely empty identity slot. We defer this to future work.

---

## 7. Conclusion

We extend Anthropic's persona-vector finding from single-agent dialogue to multi-agent service architecture by ablating the identity word across three semantic conditions in a 20-particle LLM-driven swarm scenario. We document quantitative vocabulary shifts that are systematic, replicable across seeds, and aligned with the semantic content of the identity word — most starkly, a 35× shift in exploration-vocabulary frequency between the curious-explorer and neutral conditions. Behavioral metrics show a moderate trend in the same direction.

These results suggest that **identity conditioning is a tractable architectural primitive for designing relational, subject-centered AI systems** — a paradigm distinct from both conventional command-driven multi-agent architectures and current single-agent persona research. The work positions LLM-driven multi-agent service architectures as an empirically defensible third paradigm, complementary to MARL-style optimization and conversational LLM steering, with implications for relational AI applications including ecological monitoring, ambient intelligence, and brain-machine interface companion systems.

---

## References

1. Anthropic (2025). *Persona Vectors: Monitoring and Controlling Character Traits in Language Models*. arXiv:2507.21509. [https://arxiv.org/abs/2507.21509](https://arxiv.org/abs/2507.21509)

2. Anthropic Alignment (2026). *The Persona Selection Model: Why AI Assistants Might Behave Like Humans*. [https://alignment.anthropic.com/2026/psm/](https://alignment.anthropic.com/2026/psm/)

3. Park, J. S., O'Brien, J., Cai, C. J., Morris, M. R., Liang, P., & Bernstein, M. S. (2023). *Generative Agents: Interactive Simulacra of Human Behavior*. arXiv:2304.03442. [https://arxiv.org/abs/2304.03442](https://arxiv.org/abs/2304.03442)

4. Park, J. S. et al. (2024). *Generative Agent Simulations of Human Behavior*. Stanford Digital Repository. [https://hai.stanford.edu/news/ai-agents-simulate-1052-individuals-personalities-with-impressive-accuracy](https://hai.stanford.edu/news/ai-agents-simulate-1052-individuals-personalities-with-impressive-accuracy)

5. Wren, N. (2025). *Relational AI: Continuity, Care, and Sovereignty in Conversational Systems*. [https://www.relationalai.org/](https://www.relationalai.org/)

6. (2025). *Relational AI: Facilitating Intergroup Cooperation with Socially Aware Conversational Support*. ACM CHI 2025. [https://dl.acm.org/doi/10.1145/3706598.3713757](https://dl.acm.org/doi/10.1145/3706598.3713757)

7. Project Gaara documentation (2026). [Internal repository, Independent Researcher.] *Findings, journals, and saved simulations.* `github.com/atomgreyfreeks/Project_Gaara`.

---

## Appendix A — Reproducibility

All 6 runs underlying this analysis are saved with full per-step logging at:

```
saved_simulations/shield_test/20260427_184626_id_guardian_s11/
saved_simulations/shield_test/20260427_191025_id_guardian_s22/
saved_simulations/shield_test/20260427_193247_id_explorer_s11/
saved_simulations/shield_test/20260427_195601_id_explorer_s22/
saved_simulations/shield_test/20260427_201830_id_neutral_s11/
saved_simulations/shield_test/20260427_204032_id_neutral_s22/
```

Each run directory contains:
- `collective_metrics.json` — summary statistics including the recorded identity string.
- `particle_intents.jsonl` — per-step natural-language intents per particle.
- `particle_positions.jsonl` — per-step positions per particle.
- `threat_positions.jsonl`, `mothership_state.jsonl` — environmental state.
- `config_snapshot.yaml` — exact configuration used.

To reproduce a single run:

```bash
python3 main.py --scenario shield_test --identity "a curious explorer" --seed 11 --label "id_explorer_s11" --no-frames
```

The full 12-run experimental block (which includes the 6 persona-vector runs analyzed here, alongside complementary cluster-fusion and phase-structure tests) is recorded in `_run_block.txt` and `docs/2026-04-28_journal_three_findings.md`.

## Appendix B — Vocabulary computation

Vocabulary categories are computed as the percentage of intent strings (across the full run, all 20 particles × 50 steps) that contain at least one keyword from the category's keyword list. Keyword lists:

- **Protect**: `protect, shield, intercept, neutraliz, defen, interpos`
- **Explore**: `explor, observ, curios, investigat, discover, wander`
- **Self-reference**: `cluster, particle`
- **Position**: `position, between, closer to, approach`

Stems are used (e.g., `explor` matches `explore, exploring, exploration`) following the project's existing intent-categorization conventions.
