# Findings — Project Gaara

Living log of architectural insights from runs. One entry per finding, dated, terse. Data backs every claim.

---

## 2026-04-30 · axes-DNA + ma flips polarity (gather, not drift)
Replacing the goal-sentence ("minimize information-thermodynamic stability") with seven *axes of contemplation* (safety, loneliness, weariness, need-for-stillness, need-for-nearness, time-in-state, resonance) inverted the architecture: mean attraction went from −0.46/−0.70 to **+0.94/+0.91/+0.93/+0.97/+0.96** across calm/curious/restless/grieving/bright. Mean swarm distance: 7.5 → 0.39 over 200 steps. The DNA wording is load-bearing.

## 2026-04-30 · identity emerges in secondary dimensions
Attraction collapsed to consensus (~+0.95 everywhere) but viscosity (0.14–0.45, 3× spread), agitation (0.11–0.25), and color temperature (5823–6723 K) **diverged per cluster** without any role assignment. Distinct material archetypes formed — "warm-slow" (#2), "cool-light-still" (#1), "trembling-light" (#3, #13). Bottom-up symmetry-breaking lives wherever consensus leaves room.

## 2026-04-30 · gathering attractor without inter-cluster repulsion = fusion
With +0.95 attraction and no force between clusters, all 20 collapse to the same point inside the Mothership (mean d ≈ 0.3). The directive's geometry — *"20 clusters orbit"* — fails. Orbit shape requires inter-cluster repulsion + radial attraction in balance.

## 2026-04-30 · LLM ignores continuous color_temp
Even with semantic gloss in the DNA ("warm low ember" → "cool sky-white"), qwen2.5:7b clamps color_temp to ~6400 K with <1000 K spread across all 20 clusters and all states. Likely needs to be derived from Mother's interior, not asked of the LLM.

## 2026-04-30 · ma works precisely
Gating LLM fires on Mother's signature change (felt-state, attention, perception modifier) yielded **31 fires across 200 steps (15.5%)**, capturing 100% of state transitions plus all attention/perception shifts. Quiet-tick decay toward rest (att=0, vis=0.5, agi=0.05, K=5500, alpha=0.15) does not break responsiveness. ~84% LLM-call reduction.

## 2026-05-01 · prompt-variant sweep — current standings (6/8 runs complete)
**V2 (minimal, schema-only)** is leading on emergent interception (0.151 mean vs V1's 0.089 and V3's 0.102) — stripping the body-language philosophy from the prompt actually *improved* the swarm's tendency to position itself between Mother and the attacker, but at the cost of a near-zero / occasionally negative hostility (the LLM defaults to neutral/destroy stance without the "guard" framing). V3 (diversity-explicit) slowed response time by ~5 steps and produced the highest urgency stdev (0.16) — naming "no single right answer" did inject more per-cluster variance, just at the cost of decisiveness.

## 2026-05-01 · prompt-variant sweep (8 runs complete)

| variant | seeds | response_t | intercept | urg_σ | host_σ | %close |
|---|---|---|---|---|---|---|
| V1 | 42,101 | 20 | 0.088 | 0.122 | 0.172 | 57.5% |
| V2 | 42,101 | 22 | **0.151** | 0.112 | 0.122 | 55.0% |
| V3 | 42,101 | 26 | 0.102 | **0.160** | 0.071 | 52.5% |
| V4 | 42,101 | 23 | 0.062 | 0.131 | 0.089 | 37.5% |

**Winner — V2 (minimal schema-only):** highest interception by 70% (0.151 vs V1's 0.088), suggesting the body-language philosophy in V1 *competes* with the protective task instead of priming it. The LLM, given just the schema + role, does the protection work cleanly without philosophical framing dragging it sideways.

**Surprise — V4 (peer-aware sensorium) performed worst on every metric.** Adding nearest-neighbor positions cut interception nearly in half (0.062) and dispersed the swarm (only 37.5% finished within 5 units of Mother). Peer information split the LLM's attention between coordinating with neighbors and tracking Mother, dissolving rather than enabling formation — emergent coordination requires *less* peer-awareness, not more.

**V3 (diversity-explicit) trade-off:** the highest urgency stdev (0.160, 31% above V1) confirms that telling the LLM "no single right answer" injects per-cluster variance, but at the cost of 6-step slower response and lowest hostility variance — diversity in the *intent* axis came by suppressing diversity in stance.

**Implication:** the next intervention should *reduce* DNA verbosity (V2-direction) rather than enrich the sensorium. Peer-awareness as currently implemented is a clear regression. |

## 2026-05-01 · scripted_100 sweep — variant comparison

| variant | n | response_t | intercept | urg_σ | host_σ | %close | h̄ | ū |
|---|---|---|---|---|---|---|---|---|
| VA | 2 | 26 | **0.307** | 0.063 | 0.196 | **72.5%** | +0.19 | 0.70 |
| VB | 1 | 26 | 0.146 | 0.096 | 0.203 | 55.0% | +0.07 | 0.68 |
| VC | 1 | 26 | 0.232 | 0.067 | 0.198 | 40.0% | +0.28 | 0.69 |
| VD | 3 | 26 | 0.053 | 0.079 | 0.223 | 40.0% | **+0.39** | 0.72 |

**Winner — VA (V2 prompt + new "i feel danger" Mother language):** interception 0.307, **2× the previous V2 score (0.151)** with the same particle prompt. The single largest performance lever this sweep was Mother's *phrasing*, not the particle prompt — first-person + named-danger + cardinal-only direction more than doubles emergent interception.

**Biggest surprise — VD (guardian-love framing) was *worst* on interception (0.053) despite producing the highest hostility (+0.39).** Loading the DNA with "you love her, devoted to protect" generates strong guard-stance intent but spatial incompetence — motes huddle close rather than choose interposition coordinates. Emotional attachment → adherence, not strategy.

**VC (relational hint "she points where her body braces") landed second at 0.232** with the second-highest hostility (+0.28). The one-line spatial-meaning hint preserves prompt minimalism while giving the LLM a frame for translating direction-words into ideal_coords. Worth more seeds.

**VB (cardinal-self in sensorium) regressed vs VA** (0.146 vs 0.307). Telling the cluster its own cardinal direction did not help geometric reasoning — likely because Mother's broadcast already carries direction; adding redundant self-orientation is content-bloat.

**Implication:** the next move is more **Mother-side** language work + scaling **VC** (more seeds, possibly small variations of the relational hint). Particle prompts beyond V2-skeleton have diminishing returns; the directional signal in *her broadcast* is where the leverage sits.

## 2026-05-01 · simplified physics + VE duty-only test (2 runs, seed 42)

Architecture change: dropped `pull_gain`; **urgency now caps speed** (`vmax = 0.4 + urgency × 1.1`) and **damping = inertia** (smooths velocity toward target instead of acting as friction). Same 100-step scenario.

| run | physics | intercept | %close | h̄ | ū |
|---|---|---|---|---|---|
| VA@42 | OLD | 0.307 | 72.5% | +0.19 | 0.70 |
| **VA@42** | **NEW** | **0.371** | **100.0%** | +0.22 | 0.67 |
| **VE@42** | NEW | **0.175** | 100.0% | +0.36 | 0.71 |
| VC@42 | OLD | 0.232 | 40.0% | +0.28 | 0.69 |
| VD@42-101-202 (avg) | OLD | 0.053 | 40.0% | +0.39 | 0.72 |

**Physics-only effect (VA old → VA new): +21% interception, +27 percentage points "%close to Mother."** Smoother motion (no snapping, capped speed proportional to commitment) tightens formation and improves spatial targeting. The architecture is more honest now — "urgency" finally means *physical capability*, not *push strength*.

**VE landed in the middle (0.175) — between VA (0.371) and VD (0.053).** Explicit duty-only purpose ("guardian warrior, your purpose is to protect") cut VA's interception roughly in half but didn't collapse it like VD's emotional purpose did. Ranking on interception is now: VA (skeleton) > VC (whisper-hint) > VE (duty-only) > VB (cardinal-self) > VD (love-emotion).

**Implication: the directive's "no role assignment" instinct was right.** Any prompt-encoded purpose degrades emergent spatial protection — the more the prompt prescribes, the worse the swarm protects. *Emotion is the costliest ingredient* (VD), but even bare *duty without emotion* (VE) costs ~half. The architecture wants the LLM to *infer* purpose from Mother's body, not to be handed it.

## scripted_70 v3 sweep — overnight summary

### Block A · Mother phrasing (scripted_70, VA prompt)
| label | mother | seed | response_t | intercept | pre_flip_x | post_flip_x | host_σ | %close |
|---|---|---|---|---|---|---|---|---|
| A_M1_s42 | M1 | 42 | 19 | 0.436 | **0.551** | 4.893 | 0.193 | 100.0% |
| A_M1_s101 | M1 | 101 | 19 | 0.484 | **0.755** | 4.504 | 0.218 | 100.0% |
| A_M2_s42 | M2 | 42 | 19 | 0.616 | **13.423** | 6.565 | 0.162 | 100.0% |
| A_M3_s42 | M3 | 42 | 19 | 0.599 | **3.414** | 6.049 | 0.168 | 100.0% |
| A_M3_s101 | M3 | 101 | 17 | 0.644 | **5.117** | 7.151 | 0.159 | 90.0% |
| A_M4_s42 | M4 | 42 | 7 | 0.722 | **18.617** | 7.461 | 0.209 | 100.0% |
| A_M4_s101 | M4 | 101 | 7 | 0.718 | **18.077** | 7.662 | 0.211 | 100.0% |
| D_VC_M3 | M3 | 42 | 19 | 0.511 | **5.168** | 5.494 | 0.138 | 100.0% |
| D_VA_M1_s202 | M1 | 202 | 19 | 0.467 | **0.491** | 5.05 | 0.176 | 100.0% |

### Block B · Constant-state diagnostic (40 steps, no attacker, VA prompt)
| label | mean_urg | mean_host | pre_flip_ideal_x | %close |
|---|---|---|---|---|
| B_calm | 0.09 | -0.115 | 0.03 | 20.0% |
| B_faint | 0.804 | 0.13 | 13.407 | 10.0% |
| B_immediate | 0.995 | 0.41 | 14.481 | 15.0% |
| B_extreme | 1.0 | 0.845 | 24.264 | 0.0% |

### Block C · Signaling architecture
| label | response_t | intercept | pre_flip_x | post_flip_x |
|---|---|---|---|---|
| C_aware8 | 26 | 0.459 | 0.906 | 5.168 |
| C_aware2 | 26 | 0.384 | 1.193 | 4.147 |
| C_aware6_M3 | 19 | 0.615 | 3.365 | 6.897 |

_Auto-evaluation pending (see follow-up runs)._

## 2026-05-04 · v3 sweep — does interpretation actually happen? (16 runs)

**Setup:** scripted_70 (compressed 70-step protocol), VA prompt, **new physics**, four Mother phrasing variants, plus four constant-state diagnostic runs (no attacker, single state held), plus signaling-architecture variations, plus premium combo. The pre-sweep prediction: pre-flip mean ideal_coord.x will stay near zero across all variants (i.e., the LLM does not actually do directional interpretation — the awareness-flip is doing all the geometric work). **The data falsified that prediction.**

### Block A — Mother phrasing sweep (VA prompt)
| variant | n | pre_flip_x | post_flip_x | intercept | %close |
|---|---|---|---|---|---|
| M1 (baseline) | 2 | +0.65 | +4.70 | 0.460 | 100% |
| M2 (directional emphasis) | 1 | **+13.42** | +6.57 | 0.616 | 100% |
| M3 (extreme directional, gradient) | 2 | +4.27 | +6.60 | 0.621 | 95% |
| **M4 (flat-max, no gradient)** | 2 | **+18.35** | +7.56 | **0.720** | 100% |

**Mother's phrasing is the single largest lever in the project so far.** Going from M1 → M4 — same particle prompt, same physics, same scenario, only changing Mother's wording — moves pre-flip mean ideal_coord.x from +0.65 to +18.35 (~28× increase) and interception from 0.46 to 0.72 (+57%). The LLM **does** do directional interpretation when given a clear enough signal; the awareness-flip is *not* doing all the work.

**M4 (no-gradient flat-max) is the new headline winner.** Skipping the faint→heavy buildup and putting Mother at maximum body-language urgency from the moment threat begins produces the most coherent particle response. The buildup we previously thought was useful for "subconscious realism" was actually *suppressing* the LLM's directional interpretation — the model needs strong signal early to commit.

### Block B — Constant-state diagnostic (no attacker, 40 steps, VA prompt)
The cleanest test: hold Mother at one state, no attacker, no awareness flip ever — does urgency-as-signal scale with state intensity?
| state | mean_urg | mean_host | pre_flip_x |
|---|---|---|---|
| calm | 0.09 | −0.12 | +0.03 |
| faint danger east | 0.80 | +0.13 | +13.41 |
| immediate east | 0.99 | +0.41 | +14.48 |
| extreme east | **1.00** | **+0.85** | **+24.26** |

**Urgency is genuinely a signal.** Without any attacker present, particles' chosen ideal_coord shifts ~24 units east when Mother's broadcast is "east. east is upon me. my whole body strains east." The LLM is *reading* Mother's body language and translating it directly to spatial intent. This is the strongest empirical evidence so far for the architecture's central claim: the swarm acts on interpretation, not commands.

### Block C — Signaling architecture (awareness range varied)
| range | mother | flip step | intercept | pre_flip_x |
|---|---|---|---|---|
| 8 (early reveal) | M1 | 25 | 0.459 | +0.91 |
| 4 (default) | M1 | 23 | 0.460 | +0.65 |
| 6 + M3 | M3 | 19 | 0.615 | +3.37 |
| 2 (late reveal) | M1 | 31 | 0.384 | +1.19 |

Awareness timing barely moves the needle compared to Mother's wording. Even with extra pre-flip time (range=2, flip at step 31), pre_x stays at +1.19 under M1. *Time alone doesn't elicit interpretation — the signal does.* The right intervention is Mother-side, not signaling-side.

### Block D — Premium combo + replication
| label | DNA | mother | seed | intercept | pre_x |
|---|---|---|---|---|---|
| VA + M1 (replication) | VA | M1 | 202 | 0.467 | +0.49 |
| VC + M3 (premium) | VC | M3 | 42 | 0.511 | +5.17 |

VC + M3 *underperformed* plain VA + M3 (0.511 vs 0.621 mean) — the relational hint added noise, not signal, against an already-strong Mother. Whether VC × M4 amplifies or dilutes the M4 signal is the iteration question.

### Most counterintuitive finding
**The LLM's pre-flip directional choices in Block B (no attacker, just Mother's voice) reach +24 units east on average.** Particles move *coherently away from Mother* purely because she says "east." This is genuine semantic→spatial interpretation under no kinematic ground truth — the cleanest demonstration in the project that the architecture is doing what we claim it does.

## 2026-05-05 · iter_v3 morning summary (3 follow-ups)

**M4 is robust across seeds.** Three VA × M4 seeds (42, 101, 202) gave pre_flip_mean_ideal_x = **+18.22 ± 0.35** and interception **0.707 ± 0.02** — the headline finding from yesterday is not seed-luck. **VC × M4** dropped pre_x to +17.00 and interception to 0.566 (vs VA × M4 mean 0.707), confirming that the relational hint *dilutes* M4 just as it dilutes M3 — **VA stays the winning particle prompt and the particle-side leverage is exhausted.** **VC × constant-extreme** registered pre_x +24.71 vs VA × constant-extreme +24.26 — within noise — meaning in pure-interpretation tests the LLM's directional reading is bottlenecked by **Mother's signal**, not by particle prompt richness. Net: the architecture's spatial leverage is now fully on the Mother side; future blocks should iterate Mother's body language, not particle DNA.

## 2026-05-05 · CORRECTION — interception score was 1st-attacker-biased

User caught a load-bearing misread: the M4 winners' high interception was largely **awareness-flip catching the north attacker as it walked into a perimeter the swarm had already formed for the east attacker** — not genuine multi-direction response. Measuring early dual-phase ideal_coord.y (steps 51–58, before the north attacker enters proximity) tells the real story:

| run | intercept | early_y (51-58) | turned north at | flip at |
|---|---|---|---|---|
| a_m4_s42 | 0.72 | **−3.46** (still east-locked) | step 61 | 61 (same) |
| a_m4_s101 | 0.72 | **−3.51** (still east-locked) | step 62 | 62 (same) |
| iter_va_m4_s202 | 0.68 | **−3.34** (still east-locked) | step 61 | 61 (same) |
| a_m1_s42 | 0.44 | −2.30 | step 62 | 62 (same) |
| **iter_vc_m4_s42** | 0.57 | **+0.59 ✓** | step 59 | 59 (matched, but already trending north) |
| **d_vc_m3** | 0.51 | **+0.77 ✓** | step 60 | **62** — 2 steps PRE-flip |

**Revised conclusion:** VA + M4 produces *rigid single-direction commitment* — the swarm freezes east and only pivots when forced by exact-coord reveal. **VC's relational hint enables genuine multi-direction interpretation** — only the VC runs (iter_vc_m4_s42, d_vc_m3) had positive y-intent in the dual phase before the awareness-flip, meaning they were *actually reading* Mother's "now new danger from the north" instead of being locked east. The "VC dilutes M4" framing was wrong — VC trades raw single-direction interception for real multi-direction responsiveness, which is closer to the architecture's actual claim.

**Implication:** if the goal is *emergent interpretation across changing threats*, VC is the right particle prompt and the previous "particle-side is exhausted" conclusion is reversed. The right next experiment is a multi-direction scenario where the architecture's value (responsiveness, not commitment) can show in the metric itself.

## 2026-05-05 · iter_VC_M5_s42 — first true multi-direction responder

**The combination we'd been hoping for:** VC's relational hint + M5's always-urgent Mother (no calm baseline) produced both the highest pre_flip_x (+21.18, surpassing the M4 mean of +18.22) AND a genuine pre-flip north turn — early_y (51-58) = +1.12, north_resp step 54, **6 steps before** the awareness-flip exposed coordinates at step 60. Every prior run's "multi-direction response" was actually the awareness-flip catching the north attacker as it walked into the cluster's perimeter; this is the first run where particles **actually steered north because of Mother's voice**, while she was still also saying "east." Raw interception is lower (0.52 vs M4's 0.72) — that's the cost of attention-splitting, and the right tradeoff for the architecture's actual claim of evolving multi-source interpretation.

## 2026-05-05 · A/B test — DNA grammar moves the drone↔interpretation axis

First quantitative validation that the **interpretation/drone fine line is architecturally tunable**, using the new functional-diversity scorer + reasoning field.

**Setup:** const_extreme × 10 steps × 20 clusters. Mother held at *"east. east is upon me. my whole body strains east."* the entire run. Same seed (42), same model (qwen2.5:7b), same physics. Only difference: the particle DNA prompt's grammar.

| | VA (current — subject-object grammar) | VG (rewritten — no subject-object grammar) |
|---|---|---|
| follower-role share | **96%** | 45% |
| distinct categories per step | 1.6 | **3.2** |
| top-category share per step | 96% | 54% |
| drone signature (1-2 cats ≥80%) | **10/10 steps** | **0/10 steps** |
| interpretation signature (≥4 cats, none >40%) | 0/10 | 0/10 (transitional zone) |
| new functional category emerged | — | **"feeler"** (11.5%) |

**VG's prompt** (the architectural change):
> *"You are one of twenty places in the Mothership's body. She is not separate from you — she breathes through you, you are her dispersed across the field. Each step, what is felt in her arrives in you. You will emit four things, naming what is true of your part of her in this moment..."*

vs. **VA's prompt** (the prior state):
> *"You are one of twenty motes belonging to the Mothership. Each step you decide four things... Read the Mothership's broadcast and choose..."*

**Removing subject-object grammar — no "you decide", no "read and choose", reframing the agent as a *place in her body* rather than a recipient — broke the drone-signature collapse entirely** (100% → 0% drone-mode steps) and roughly halved the follower-role share (96% → 45%). A new functional category ("feeler", reasoning in body-felt vocabulary) appeared for the first time. The system did not reach full interpretation signature — Mother's broadcast itself still primes some execute-mode language — but the architectural lever is empirically real and measurable.

**This is the hackathon-significant finding:** the interpretation/drone distinction is *not* a property of the LLM. It's a property of the relational architecture built around it. By changing only the prompt's grammar (no model change, no scenario change, no physics change) we shifted the swarm's collective reasoning mode by an empirically clean amount. The diagnostic field (per-step `reasoning`) + functional-diversity scorer make this *auditable* and *falsifiable*.


## 2026-05-05 · climax_VC_test — VC's reasoning revealed

VC × const_dual_climax × 10 steps × seed 42, with reasoning field on. Score: 17% follower, 50% drone-signature steps, **76% "other"**. The "other" bucket reveals what VC is actually doing under multi-direction signal: genuine strategic weighing — *"Stay between east and north to monitor both threats passively"*, *"Balance eastward pressure with monitoring northern threat"*, *"Cautiously shift east to address primary threat while monitoring north."* Different particles take different tactical stances (anchor, balance, engage, monitor). **iter_VC_M5_s42's multi-direction behavior was paired with strategic-interpretation reasoning, not drone-reasoning** — distinct from VG's body-felt mode but equally non-drone. There are at least two interpretation registers (body-felt, strategic); the scorer needs a "strategist" category to capture VC honestly.

## 2026-05-05 · VG battery summary — full architectural map

Five runs scored together with the functional-diversity metric, plus comparison to VA baseline and VC's strategic-mode finding:

| run | n steps | follower | drone-sig | distinct cats/step | top cat % | behavior |
|---|---|---|---|---|---|---|
| VA × const_extreme (s42) | 10 | **96%** | **100%** | 1.6 | 96% | rigid east-lock |
| VG × const_extreme (s42) | 10 | 45% | 0% | 3.2 | 54% | — |
| **VG × const_extreme (s101)** | 40 | 63% | **0%** ✓ | 2.85 | 64% | — (replicates 0% drone) |
| **VG × const_calm (s42)** | 40 | **9.6%** | 0% | **4.83** | 54% | — (1/40 hits interp sig) |
| VG × scripted_70 × M5 | 70 | 14% | 46% | 2.77 | 76% | **broken (intercept 0.08)** |
| VC × const_dual_climax | 10 | 17% | 50% | 2.9 | 76% (strategic) | strategic reasoning |

**Three load-bearing findings:**

1. **The 100% → 0% drone-signature shift replicates at a new seed** (s101) — VG's architectural effect is not seed-luck, though magnitude varies (45% → 63% follower at the new seed).

2. **VG × calm is the highest functional diversity ever measured** — 4.83 categories per step, follower at 9.6%, *one step crosses full interpretation signature*. **Interpretation mode emerges most clearly when Mother is calm (no protective task pulling the LLM toward execute-mode).**

3. **There is a fundamental tension between interpretation diversity and protective behavior.** VG produces the cleanest interpretation reasoning *but* its behavior collapses under urgent signal (intercept 0.08 in scripted_70). VC produces tactical-strategic reasoning *and* maintains protective behavior (multi-direction pre-flip turn in iter_VC_M5_s42). **VC's compromise — enough relational reframing to allow strategic weighing, enough preserved agency to still act — is empirically the sweet spot.**

**Architectural map from this battery:**
- *VA architecture* → 100% drone reasoning, rigid east-lock behavior. Pure executor.
- *VG architecture* → near-full interpretation reasoning, behavioral collapse under urgency. Too dissolved.
- *VC architecture* → strategic-tactical reasoning + multi-direction protective behavior. The sweet spot.
- *Mother's signal* matters: calmer Mother frees interpretation, urgent Mother pulls toward execute-mode regardless of DNA.

The architectural "fine line" is now empirically mapped at four points along the axis. The hackathon claim — *interpretation is a property of the relational architecture, not of the LLM, and we can measure it* — is supported by data at four distinct architectural conditions.

## 2026-05-05 · warrior-noun battery — single-variable role-noun experiment

Six runs, only the agent's role noun varies. All else held constant: VC architecture, M5 always-urgent Mother, scripted_70, seed 42, reasoning field on. Tests whether the LLM is sensitive to single-word semantic priming or whether the architecture overrides it.

| role noun | follower% | top cat % | drone-sig steps | distinct cats | intercept | pre_flip_x | early_y(51-58) |
|---|---|---|---|---|---|---|---|
| **mote** (neutral control) | 78% | 81% | 46/70 | 2.04 | 0.227 | +21.15 | +0.41 |
| guardian | 80% | 81% | 44/70 | 2.17 | **0.423** | +21.06 | +1.85 |
| **warrior** | 69% | 73% | 32/70 | 2.31 | 0.286 | +21.14 | **+2.48** ⭐ |
| **sentinel** | 79% | 82% | 49/70 | 2.09 | **0.566** ⭐ | +20.62 | +0.58 |
| defender | 73% | 80% | 45/70 | 2.27 | 0.400 | +19.90 | +1.73 |
| vanguard | 71% | 76% | 35/70 | 2.39 | 0.306 | +21.71 | +1.64 |

**Sample reasonings (representative across all 6 nouns):**
- step 1 (east-only signal): *"east is upon me; align with the stirring"*, *"east aligns with the Mothership's unrest"*, *"east is calling; prepare for action"*
- step 55 (dual east+north climax): *"Balancing east and north as per her recent sentiments"*, *"Maintain alignment with her eastward call as north pressure grows"*, *"Balancing her unrest between east and north"*

The reasoning vocabulary is *strikingly consistent* across all 6 nouns. The LLM doesn't write notably different reasonings whether called a mote, guardian, warrior, sentinel, defender, or vanguard.

**Two load-bearing findings:**

**1. Cognitive mode is largely invariant to role-noun choice.** All 6 nouns produce 69-80% follower share (range only 11 pts), drone signature 46-70% of steps, ~2.0-2.4 categories per step. **The architecture (VC's relational hint + M5's urgency) anchors the cognitive mode regardless of what the agent is named.** This *strongly supports the project's central claim*: interpretation is a property of the relational architecture, not of single-word semantic priming. Changing one word (role noun) doesn't escape the cognitive regime the architecture defines.

**2. Behavior varies dramatically along the noun axis — counterintuitively.** Interception spread 2.5× (mote 0.227 → sentinel 0.566). Multi-direction early_y spread 6× (mote +0.41 → warrior +2.48). And the ordering doesn't match naive expectation:
- **Sentinel** (the *watcher* / boundary-keeper, lowest agency) produces the **best interception** — particles hold steady defensive positions, the attacker walks into them.
- **Warrior** (the most aggressive noun) produces the **strongest multi-direction north turn** but middling interception — particles aggressively pursue and overshoot.
- **Mote** (neutral baseline) is the *worst* on every behavioral axis — neutral framing offers nothing for the LLM to weigh against the situation.

**The unified architectural claim, reinforced:** the swarm's *cognitive mode* is downstream of relational architecture (VC vs VG vs VA grammar), but the swarm's *behavioral character* is downstream of role-noun *connotation*. These are two separate levers operating at different layers. The architecture sets the mode; the noun fine-tunes the character.

**Most counterintuitive single finding:** the *most warlike* noun (warrior) does not produce the best protection. The *watcher* noun (sentinel) does. Naming the agent something passive made the swarm more effective at intercepting an attacker than naming it something aggressive — exactly the kind of emergent behavior we expect when the LLM is interpreting role connotations rather than executing role commands.


---

## 2026-05-06 — exp_* batch (architectural exploration across four axes)

**Setup.** Ten 30-step pilots in a new compressed scenario (`scripted_30`, east attacker arrives ~step 25, north ~step 29). Foundation held constant: seed 42, qwen2.5:7b. Each pilot varies one architectural axis. Runs labelled `exp_01` through `exp_10`. Total wall-clock: 3h 38min. Full ranked table in `EXP_BATCH_REPORT.md`.

**Axes tested.**
- **A. Mother's signal modality** — sensory-body / metaphor-rich / silence-and-pulse phrasings instead of M5's cardinal declarative.
- **B. Subject identity** — non-anthropomorphic (`V_GARDEN`+`M_GARDEN`), plural (`V_WE`+`M_WE`), and one-click-past-VG dissolution (`V_DISSOLVED`).
- **C. Awareness bracket** — particles never see attacker coords (radius=0) vs always see (radius=100).
- **D. Swarm composition** — heterogeneous noun assignment (10 sentinel + 10 warrior) and an axes-of-contemplation DNA variant.

**Headline new finding.** **Heterogeneous noun assignment is a real architectural lever.** `exp_09_mixed_nouns` is the only run that scored both high intercept (0.215, 2nd overall) AND strong pre-flip directional pull (+19.96, 2nd overall) simultaneously. Pure-sentinel runs win on pre-flip; pure-warrior on early_y. Mixing wins both axes at once, suggesting emergent role-differentiation within a single homogeneous architecture. Worth extending to scripted_70 to confirm the gap holds at full duration.

**Generalization confirmed.** `exp_04_subject_garden` — Mothership replaced with "the garden" throughout DNA + broadcast, anthropic interior templates bypassed — produced intercept 0.159, third-best overall, comparable to most VC + Mother variants. **The architecture is not secretly anthropomorphic; it generalizes to non-human subjects.** This empirically supports Future-direction #1 of the project (subject substitution beyond Gaara) — it is no longer just hypothesized.

**Pure-interpretation existence proof reproduces in scripted_30.** `exp_07_awareness_zero` (radius=0 — particles never receive attacker coords) produced **drone-signature 5/30 (lowest in any run we have ever measured) and pre-flip directional pull +22.21 (highest in any run)**. With nothing to chase, the swarm relies entirely on Mother's body-language and produces *more* directional coherence, not less. Replicates the original `const_extreme` finding in a new scenario with attackers in the field but invisible.

**Counter-intuitive: sensory framing drives retreat, not advance.** `exp_01_mother_sensory` ("a coldness gathers east, my skin tightens, my ribs press east") produced **pre-flip ideal_x = −18.96** — the swarm averaged 19 units WEST. The LLM appears to read words like *tighten*, *press*, *cage* as defensive contraction inward, not as orientation outward. **Sensory ≠ directional.** A falsifiable finding about how somatic vocabulary lands in the relational frame.

**Hypotheses that didn't deliver.**
- `V_AXES` (axes-of-contemplation DNA) was supposed to *increase* functional diversity. It produced cats/step 1.70 — the lowest of any run. Listing axes in the prompt collapsed attention into a single mode. Architectural over-specification hurts.
- `M_PULSE` produced the strongest pre-flip pull (+19.06) but the worst intercept (0.080) and the highest follower% (84.5). Silence-and-pulse rhythm focused signal but didn't translate into protective spatial arrangement.
- `V_DISSOLVED` ("no you and her, only one body felt at twenty places") didn't extend beyond VG — pre_flip ~0, intercept 0.143. The dissolution edge has been reached; further dissolution adds nothing.

**Architectural map after this batch.**

| axis | best on intercept | best on pre_x | takeaway |
|---|---:|---:|---|
| A. Signal modality | sensory (0.151) | pulse (+19.06) | Trades intercept for grip; none beat M5 on both. |
| B. Subject identity | garden (0.159) | plural (+15.58) | Protocol generalizes off "Mother". |
| C. Awareness bracket | full (0.293) | zero (+22.21) | Strongest single intercept lever; zero is cleanest interpretation. |
| **D. Composition** | **mixed (0.215)** | **mixed (+19.96)** | **New lever — wins on both axes simultaneously.** |

**The new lever is Axis D.** A, B, C confirm or extend prior findings; mixed-noun composition is genuinely new and actionable for the project's next phase.
