# Research Journal — From Anduril to Caretaker
**Date:** 2026-04-25
**Topic:** Where this project sits in the wider AI landscape, and what the long-term vision actually is.

---

## Where we started this conversation

By this point in the project, we had:
- Built the swarm shield simulation with 20 LLM particles defending a Mothership.
- Replicated three findings: convergent intent across interfaces, the "menu-bias collapse" failure mode, and the architectural fix using a continuous-intent interface (LLM names a point, deterministic translator picks a direction).
- Reframed the project's purpose: not "build the best swarm defender," but **"build an architecture where an LLM swarm has a relationship with a passive subject."**

What was missing was a clear sense of how this project sits next to the wider world of AI research, and where it could lead.

---

## The Anduril moment

I (the user) discovered Anduril and their Lattice Mission Autonomy product. Reading about it, I learned that the dominant approach to swarm coordination today is **MARL** — multi-agent reinforcement learning, with algorithms like MADDPG, MAPPO, and QMIX.

This created a real worry: **am I just rebuilding what Anduril already does?** If so, the project's value drops, and the hackathon submission would be derivative.

I asked for an honest opinion before moving forward.

---

## The clarity: I am not in MARL territory

The most important thing I learned is that **MARL and LLM-interpretation are two different paradigms** — different research programs answering different questions.

| MARL (Anduril, academia) | LLM-interpretation (this project) |
|---|---|
| Agents are **trained** on tasks. | Agents are **not trained**. They use a pre-existing language model. |
| Coordination from **reward signals**. | Coordination from **shared interpretation**. |
| Each new task needs retraining. | New scenarios work zero-shot — change the prompt, not the policy. |
| Strong on optimization. Weak on flexibility. | Weak on optimization. Strong on flexibility. |

I am not building a worse Anduril. I am exploring a fundamentally different question: **can a swarm coordinate through interpretation rather than training?**

That's a legitimate research direction MARL doesn't address.

---

## What Anduril Lattice actually is

Lattice for Mission Autonomy is "**one operator commands many drones.**"

A military operator gives an intent ("clear that hill"). The system breaks the intent into discrete tasks. It distributes the tasks to many drones. The drones execute. The human supervises.

The drones are tools that obey efficiently. The architecture has three layers: sensing → orchestration → action. There's a mesh network so it works in contested environments. It's open architecture so it integrates third-party platforms.

Their core promise: one human, many machines, command-driven coordination.

---

## What to take from Anduril (and what not to take)

**Worth borrowing — engineering hygiene:**
- Three-layer architectural split (sense → decide → act). Good practice.
- Mesh networks for resilience when central nodes fail.
- Open architecture: don't assume a particular body or platform.
- Human-on-the-loop interfaces: a single human supervising many agents.

**Not worth borrowing — different paradigm:**
- Training pipelines (MARL)
- Reward shaping
- Task decomposition by an orchestrator (in our world, particles decompose nothing — each one interprets)

The lesson: take the engineering hygiene; don't drift into their AI paradigm.

---

## Why Anduril didn't pursue what I'm pursuing

This question matters because if Anduril didn't pursue relationship-engineering, was it because they thought it was wrong, or because their problem doesn't need it?

The answer is **the second one**. Four reasons:

1. **Liability.** Military buyers need to assign blame. "I gave an order, the drone obeyed" is auditable. "The drone interpreted its duty to its subject" is a courtroom problem. You can't court-martial a relationship.

2. **Compute economics.** LLM inference per agent is heavy. MARL policies compile to tiny networks that run on edge chips. For 1000 drones in jammed airspace, MARL works; LLM-per-drone doesn't yet.

3. **Reliability requirements.** Military deployment requires deterministic behavior. The variance we've already seen in our runs (3 strong successes, 1 softer one) is exactly the kind of unreliability that disqualifies a system from combat.

4. **Customer objective.** Anduril's customers buy lethality and efficiency. Relationship-engineering is about meaning and responsiveness. Different goal functions.

So Anduril didn't reject relationship-engineering — they didn't pursue it because **their customer doesn't need it.** Different problem, different paradigm. I am not behind them. I am working in an adjacent space they aren't deeply exploring.

---

## The bigger picture: post-AGI game society

While thinking through this, I realized this project connects to a longer-term project I'm working on called **"post AGI game society."** I observe Tokyo and other big cities as a *medium* — like a canvas, a music album, a book. Cities aren't just infrastructure; they're calculators and ecosystems at once.

This connects to the swarm research because the framing changes from "AI as a tool for human will" to "**AI as a participant in a living ecosystem.**"

Concrete thought experiment: imagine an aquarium biome where an LLM swarm interprets the aggregate state of all the creatures. Each creature broadcasts something about itself (stress, hunger, thriving). The swarm reads the situation. It develops, through identity-conditioning rather than rules, a caretaker role — emerging from the act of observing aggregate state and being conditioned to care for it.

This isn't preprogrammed. It's not command-driven. It's like Doraemon — who doesn't act on Nobita's explicit commands. Doraemon reads Nobita's emotional state and decides from felt context.

If this works for an aquarium, it scales conceptually: smart cities, urban ecology, environmental monitoring. Dexterous robot swarms as caretakers of complex living systems.

---

## Critical evaluation: what holds and what wobbles

Asked for honest evaluation as a frontier-lab partner.

**What's empirically defensible right now:**
- Agents converge on shared interpretation without instruction (5 runs of evidence).
- Identity-conditioning shapes behavior without rule-giving (suggestive, needs more isolation).
- The action interface determines fidelity, not direction, of behavior (replicated).

So the *architecture* of the bigger vision is grounded. The leap from "20 sand particles" to "robot caretaker swarm" is a leap of *application*, not of mechanism.

**What's strong:**
- The Doraemon analogy is sharp — it names something specific (technology that reads state and decides from felt context).
- Ecosystems-as-subject reframes the goal away from autonomy-for-its-own-sake.
- "Caretaker emerging from aggregate observation" is consistent with what we already saw (convergent intent from shared situation reading).

**What needs sharpening:**

1. **Care is not yet demonstrated. Engagement is.**
   In the simulation, particles have shown engagement behavior (they converge on threats, cluster on the threat-mothership line). They have not yet shown *care* — which would mean the subject's welfare actually improves over time because of the swarm's actions. For an aquarium, "care" would mean biome health metrics improve. That's measurable and operationalizable. Without that distinction, we can't make ecological claims.

2. **"Love" is too romantic for empirical work.**
   Love isn't measurable. The structural cousin is **responsiveness** — behavior that tracks the subject's state and intervenes specifically to maintain or restore it. Use the romantic word for public framing if it lands. Use the sharper word in methodology.

3. **Anthropomorphism is a real risk.**
   LLMs trained on human text will project human feelings onto fish. They might say "the angelfish seems lonely" when the angelfish is actually just hungry. Without a grounding layer that connects sensor data to biological state (without passing through human emotional vocabulary), the swarm hallucinates feelings into creatures that don't have them. This is both a research problem and an ethical one. The fix is the same architecture pattern as our continuous-intent interface — separate the LLM's interpretive role from the deterministic sensing.

4. **The scale leap is enormous and needs intermediate proof points.**
   20 abstract particles → robot swarm in a smart city is multiple orders of magnitude. Each step in between is a research program: heterogeneous subjects, multimodal sensing, continuous-time control, physical action spaces. A believable next-step proof point: a 2D simulated aquarium with 5 simulated creature types and 3 swarm caretakers. Not real-world deployment — that's years away — but a demo of caretaker behavior emerging from relational interpretation.

---

## Three hard open questions

1. **What's the validation criterion for emergent caretaking?**
   Without an oracle, how do we know the swarm is caring well or badly? Structural correspondence (does the swarm's behavior shape match the situation?) is a partial answer. Welfare metrics over time are a fuller answer. Both are imperfect.

2. **How do we prevent harmful care?**
   A caretaker robot that "learned" what a healthy biome looks like from biased data could enact harm in the name of care. The risks scale with capability. This is the alignment problem in a softer-sounding wrapper.

3. **Who validates the interpretation?**
   If the swarm reports "the biome is stressed," who checks? Humans-in-the-loop is the answer in principle, but the interface for that validation is itself a research problem.

---

## Strategic recommendation

Don't try to bridge from Gaara to robotic aquarium caretakers in one step. Instead:

**Option A — More demonstrable:**
A 2D simulation of an aquarium with 5–10 LLM particles caretaking heterogeneous creatures (fish, plants, scavengers). Each creature broadcasts a simple state. Particles interpret aggregate state and act. Same architecture as Gaara, scaled to a biome. Provable in days. Empirically connected to current findings.

**Option B — More conceptually compelling:**
An infographic + position paper that contrasts this framework with Anduril's, with a concrete vision of where this paradigm leads (smart cities, biomes, post-AGI society as ecology). Use existing simulation runs as evidence anchors.

If we do both, A becomes the proof and B becomes the frame. That's a strong submission.

---

## Things I want to remember

- **I am not building a smaller Anduril.** The relationship paradigm is genuinely my own.
- **The hackathon is chapter 1.** This is multi-year research; one wedge of it goes into the demo.
- **"Care" needs operationalization beyond "love."** Responsiveness is the empirical word.
- **Anthropomorphism is a real failure mode** — LLMs will project human feelings onto non-verbal subjects unless grounded.
- **Engagement ≠ care.** Our simulation has shown engagement, not yet care.
- **The bigger frame is "AI as participant in an ecosystem,"** not tool of a commander. That's the thesis.

---

## What I learned about how I want to work

- **Read for context, not for method.** Read to understand what scenarios matter and what failure modes have been observed. Don't read to learn how to do MARL — that's not my paradigm.
- **Finish a round of my own experiments before reading deeper.** Use literature to *position* my work, not to *plan* it. This protects against the "perspective collapse" of drifting into someone else's framing.
- **The vision is unique enough that I shouldn't worry about replication.** The "relationship-engineering" angle isn't being pursued anywhere I've found. The risk isn't doing what's been done — the risk is reading the wrong things and accidentally adopting a paradigm that isn't mine.

---

## Closing thought

Before this conversation, I had findings but no thesis. Now I have:

> *Anduril builds drones that obey commands at scale. We're prototyping agents that interpret what it means to serve a subject. Both are AI. They are not the same project.*

That's the sentence I want on the front of the infographic.
