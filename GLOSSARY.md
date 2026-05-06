# Glossary — Project Gaara

A plain-language decoder for every code in saved_simulations/, RUNS_LOG.md, FINDINGS.md, and the viewer's run dropdown.

---

## Particle DNA variants (the system prompt each particle reads)

The particle prompt is the LLM's *only* instruction — what kind of agent it is and what it should output. Every variant outputs the same JSON schema (`ideal_coord`, `urgency`, `hostility`); they differ in *framing*.

### Old generation (first sweep)
| code | name | what's in the prompt |
|---|---|---|
| **V1** | body-language baseline | Long philosophical paragraph: *"she speaks in body language, read her as one body reads another"* + the schema. |
| **V2** | minimal skeleton | Just the schema and "you are one of twenty motes." No philosophy. *Won the first sweep.* |
| **V3** | diversity-explicit | V1 + *"twenty motes will read her differently, no single right answer"* |
| **V4** | peer-aware | V1 + each particle gets the positions of its 3 nearest neighbors in its sensorium |

### New generation (second sweep, current)
| code | name | what's in the prompt |
|---|---|---|
| **VA** | minimal skeleton | Same as V2 — minimal prompt, no role, no framing. The control. |
| **VB** | cardinal-self | VA + sensorium tells the cluster *"you are to the south-east of her, 7.4 away"* |
| **VC** | relational hint | VA + one sentence: *"she points where her body braces — her direction-words carry weight"* |
| **VD** | guardian-love | *"You are the Mothership's guardian. You love her. You are devoted to protecting her."* + schema |
| **VE** | guardian-warrior | *"You are a guardian warrior. Your purpose is to protect the Mothership."* + schema |
| **VG** | no subject-object | *"You are one of twenty places in the Mothership's body. She is not separate from you."* — strips the receiver-of-orders frame. |

### Third generation (`exp_*` batch — May 6 architectural exploration)

| code | name | what's in the prompt |
|---|---|---|
| **V_AXES** | axes-of-contemplation | VA + explicit list: *"hold these axes open: distance, angle, urgency, what wants to move in you"* |
| **V_DISSOLVED** | one-body-felt-at-twenty-places | One click past VG: *"there is no you and her, only one body felt at twenty places"* |
| **V_GARDEN** | non-anthropic subject | *"You are one of twenty seeds in the garden's body."* Same architecture, garden replaces Mothership. |
| **V_WE** | plural shared body | *"You are one of twenty places in our shared body."* Plural-subject grammar. |

---

## Mother broadcast variants (what Mother actually *says*)

The Mother emits a felt-language broadcast each step (e.g., *"i feel danger from the east"*). Variants differ in how directional / urgent the wording is.

| code | name | example faint-phase wording |
|---|---|---|
| **M1** | baseline | *"i feel a faint danger from the east."* |
| **M2** | directional emphasis | *"i feel a faint danger from the east. my eyes drift east."* |
| **M3** | extreme directional | *"the east. i feel pressure from the east. my breath catches east."* |
| **M4** | flat-max no-gradient | *"east. east is upon me. my whole body strains east."* — used **from the very first threat phase**, no faint→heavy buildup |
| **M5** | always-urgent | M4's wording held even during baseline + resolution. Mother is in max felt-state the entire run. |
| **M_SENSORY** | skin/temperature/pressure | *"a coldness gathers east. my skin tightens east, my ribs press east."* Sensory-body phrasing instead of cardinal declaratives. |
| **M_METAPHOR** | fully metaphorical | *"east where the river bends, the field thins where i lean."* No explicit cardinal directives — only metaphor. |
| **M_PULSE** | silence + pulses | M5 wording, but spoken only every 3rd step. On the other steps Mother just says *"i breathe."* — silence-as-signal rhythm. |
| **M_GARDEN** | non-anthropic body | *"the eastern beds tighten. the soil leans east, the roots strain east."* Subject is the garden. Bypasses anthropic interior templates. |
| **M_WE** | plural body | *"we feel east. our body strains east, our flank tightens east."* Plural subject. Bypasses anthropic interior templates. |

---

## Scenario codes (what the run tests)

| scenario | what it is |
|---|---|
| **scripted_55** | Original 55-step protocol (legacy). |
| **scripted_100** | Full 100-step protocol — east attacker arrives ~step 65, north arrives ~step 90. |
| **scripted_70** | Compressed 70-step (current default). East ~step 50, north ~step 65. |
| **scripted_30** | 30-step pilot used for the `exp_*` batch. East attacker arrives ~step 25, north ~step 29. Used to fast-screen architectural variants before re-running winners at full length. |
| **scripted_70_aware2** | scripted_70 with `awareness_range = 2` — exact attacker coords reveal *late* (closer proximity required). |
| **scripted_70_aware6** | scripted_70 with `awareness_range = 6` — reveal earlier than default. |
| **scripted_70_aware8** | scripted_70 with `awareness_range = 8` — reveal very early. |
| **const_calm** | Constant state diagnostic — Mother held at *"calm. the world is still."* for 40 steps, **no attacker**. |
| **const_faint** | Mother held at *"i feel a faint danger from the east."* for 40 steps, no attacker. |
| **const_immediate** | Mother held at *"the east is danger. it is upon me."* for 40 steps, no attacker. |
| **const_extreme** | Mother held at the M4 wording for 40 steps, no attacker. |

---

## Block labels (which experiment a run belongs to)

In the v3 sweep, each run's label starts with a block letter:

| prefix | meaning |
|---|---|
| **A_** | **Block A** — Mother phrasing sweep (M1/M2/M3/M4 × seeds, scripted_70). |
| **B_** | **Block B** — constant-state diagnostic (no attacker, isolated urgency test). |
| **C_** | **Block C** — signaling architecture (varied awareness_range). |
| **D_** | **Block D** — premium combo + replication. |
| **iter_** | follow-up runs launched after the main sweep, based on findings. |
| **noun_** | single-variable noun-substitution battery (sentinel/guardian/warrior/etc., all VC + M5 + s42). |
| **exp_** | architectural exploration batch (May 6) — 30-step pilots across four axes: signal modality, subject identity, awareness bracket, swarm composition. |

---

## Metrics (what each number in RUNS_LOG.md means)

| metric | meaning | high = good? |
|---|---|---|
| **interception_score** | Fraction of (cluster, step) samples where a cluster sat within 2 units of the line between Mother and an active attacker. *Caveat: heavily weighted toward 1st-attacker — a high score doesn't necessarily mean the swarm interpreted multi-direction signals.* | usually yes |
| **pre_flip_mean_ideal_x** | Mean of clusters' chosen `ideal_coord.x` *before* the awareness-flip exposed exact coords. The cleanest "did the LLM read her direction?" signal. Positive = aiming east (toward east attacker). | yes |
| **post_flip_mean_ideal_x** | Same, *after* the flip. Compare with pre to see what the flip changed. | yes |
| **early_y (51-58)** | Mean ideal_coord.y during the early dual phase (before north attacker comes close). Positive = swarm is genuinely turning toward Mother's "north" cue. **The honest test of multi-direction response.** | yes |
| **response_time_v1** | First step ≥5 where mean urgency crosses 0.5. | low = good |
| **awareness_flips** | Per attacker: which step did its exact coords first reveal? (Triggered by any cluster coming within `awareness_range` units of it.) | — |
| **final_within_5_units_pct** | % of clusters that ended within 5 units of Mother. | depends — high = clustered tight; low = spread or chasing threat |
| **mean_urgency_overall** | Average urgency value across all (cluster, step) samples. | — |
| **mean_hostility_overall** | Average hostility value. + = guard, − = attack. | — |
| **urg_σ / host_σ** | Standard deviation of urgency / hostility across clusters per step (mean of stdevs). High σ = particles diverge in stance, low σ = consensus. | depends |

---

## Quick decoder examples

- `A_M4_s101` → Block A · Mother variant M4 (flat-max) · seed 101 · particle prompt VA (default for Block A).
- `iter_VC_M4_s42` → follow-up run · particle prompt VC (relational hint) · Mother variant M4 · seed 42.
- `B_extreme` → Block B · constant-state · Mother held at extreme M4 wording · no attacker.
- `C_aware6_M3` → Block C · awareness_range = 6 · Mother variant M3.
- `D_VC_M3` → Block D · particle prompt VC · Mother variant M3.
- `D_VA_M1_s202` → Block D · particle prompt VA · Mother variant M1 · seed 202 (replication).

---

## Which run is which finding

The runs that empirically support our central claims:

| run | what it shows |
|---|---|
| **A_M4_s42**, **A_M4_s101**, **iter_VA_M4_s202** | Headline: stronger Mother wording → genuine pre-flip directional response (pre_x +18.22 ± 0.35 across 3 seeds). |
| **B_extreme** | Pure-interpretation proof: no attacker, particles still aim +24 east just from Mother's voice. |
| **B_calm** | Control for B_extreme: same setup, Mother just calm — particles drift gently, no direction. |
| **iter_VC_M4_s42**, **D_VC_M3** | The *true* multi-direction responders: only runs where particles turned north *before* the awareness-flip exposed coords. (Underweighted by the basic interception score — see the 2026-05-05 correction in FINDINGS.md.) |

---

*Last updated: 2026-05-06.*
