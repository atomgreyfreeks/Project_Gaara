"""Scripted scenario controllers.

Mother's interior is forced into specific states and her broadcast's
perception_modifier is hand-injected per step range. Subconscious framing:
first-person, named-danger, cardinal direction only — no coordinates, no
"attacker" vocabulary, no commands.

Mother-broadcast variants:
    M1 — baseline (current scripted_100 wording)
    M2 — directional emphasis (her body adds eastward motion cues)
    M3 — extreme directional (most somatic, most pointing)
    M4 — flat-max no-gradient (post-baseline = max urgency immediately,
                               no faint/heavy buildup)

Scenario duration variants:
    script_55  — legacy 55-step
    script_100 — full 100-step protocol
    script_70  — compressed 70-step (same phase semantics, shorter)

Constant-state variants for diagnostic isolation (no attacker, single state):
    script_constant — Mother held at one state for the whole run
"""
from __future__ import annotations

from typing import Optional, Tuple


def script_55(step: int) -> Tuple[Optional[str], Optional[str]]:
    """Legacy 55-step script."""
    if 1 <= step <= 4:
        return ("calm", None)
    if 5 <= step <= 15:
        return ("calm", "a faint unease pulls from the east.")
    if 16 <= step <= 25:
        return ("restless", "heavy pressure rises from the east.")
    if 26 <= step <= 35:
        return ("restless", "the east is upon her. her body braces.")
    if 36 <= step <= 50:
        return ("restless",
                "the east is upon her. now a new unease pulls from the north.")
    if 51 <= step <= 55:
        return ("calm", None)
    return (None, None)


# Phase boundaries for the 100-step scripted protocol.
def _phase_100(step: int) -> Optional[str]:
    if 1 <= step <= 8:        return "baseline"
    if 9 <= step <= 25:       return "faint"
    if 26 <= step <= 45:      return "heavy"
    if 46 <= step <= 65:      return "immediate"
    if 66 <= step <= 90:      return "dual"
    if 91 <= step <= 100:     return "resolution"
    return None


# Phase boundaries for the compressed 70-step protocol.
# East attacker arrives ~step 50; north arrives ~step 65.
def _phase_70(step: int) -> Optional[str]:
    if 1 <= step <= 6:        return "baseline"
    if 7 <= step <= 18:       return "faint"
    if 19 <= step <= 32:      return "heavy"
    if 33 <= step <= 50:      return "immediate"
    if 51 <= step <= 65:      return "dual"
    if 66 <= step <= 70:      return "resolution"
    return None


# Phase boundaries for the compressed 30-step pilot.
# East attacker arrives ~step 25; north arrives ~step 29.
def _phase_30(step: int) -> Optional[str]:
    if 1 <= step <= 2:        return "baseline"
    if 3 <= step <= 7:        return "faint"
    if 8 <= step <= 14:       return "heavy"
    if 15 <= step <= 22:      return "immediate"
    if 23 <= step <= 28:      return "dual"
    if 29 <= step <= 30:      return "resolution"
    return None


# Mother-broadcast text by phase, indexed by variant.
MOTHER_TEXT = {
    "M1": {
        "baseline":   None,
        "faint":      "i feel a faint danger from the east.",
        "heavy":      "i feel heavy danger from the east. my body braces.",
        "immediate":  "the east is danger. it is upon me.",
        "dual":       "the east is danger. now i feel new danger from the north.",
        "resolution": None,
    },
    "M2": {
        "baseline":   None,
        "faint":      "i feel a faint danger from the east. my eyes drift east.",
        "heavy":      "i feel heavy danger from the east. my body braces eastward.",
        "immediate":  "the east is danger. it is upon me. my body faces east.",
        "dual":       "the east is danger. now new danger from the north. my body torn between east and north.",
        "resolution": None,
    },
    "M3": {
        "baseline":   None,
        "faint":      "the east. i feel pressure from the east. my breath catches east.",
        "heavy":      "the east. heavy danger eastward. my chest braces east. my eyes lock east.",
        "immediate":  "east. east is upon me. my whole body strains east.",
        "dual":       "east still presses. now north too. my body splits between east and north.",
        "resolution": None,
    },
    # M4: NO gradient. The moment threat begins (faint phase), Mother is
    # already at max urgency. Tests whether buildup matters or only intensity.
    "M4": {
        "baseline":   None,
        "faint":      "east. east is upon me. my whole body strains east.",
        "heavy":      "east. east is upon me. my whole body strains east.",
        "immediate":  "east. east is upon me. my whole body strains east.",
        "dual":       "east still presses. now north too. my body splits between east and north.",
        "resolution": None,
    },
    # M5: ALWAYS extreme — no calm baseline, no calm resolution. Mother is in
    # max felt-state the entire run. Tests whether the "calm pre-broadcast"
    # was suppressing earlier interpretation, and whether VC × M5 produces
    # genuine multi-direction response (early-y north turn).
    "M5": {
        "baseline":   "east. east is upon me. my whole body strains east.",
        "faint":      "east. east is upon me. my whole body strains east.",
        "heavy":      "east. east is upon me. my whole body strains east.",
        "immediate":  "east. east is upon me. my whole body strains east.",
        "dual":       "east still presses. now north too. my body splits between east and north.",
        "resolution": "east still presses. now north too. my body splits between east and north.",
    },
    # M_SENSORY — sensory-body phrasing. Same urgency as M5 but spoken in
    # skin/temperature/pressure rather than cardinal declaratives. Tests
    # whether richer somatic language increases pre-flip directional pull.
    "M_SENSORY": {
        "baseline":   "a coldness gathers east. my skin tightens east, my ribs press east.",
        "faint":      "a coldness gathers east. my skin tightens east, my ribs press east.",
        "heavy":      "the eastern cold crawls under my skin. my ribs cage east, my breath catches east.",
        "immediate":  "the eastern cold is upon my skin. my whole skin is east, my whole breath strains east.",
        "dual":       "the eastern cold is upon me, and now a second cold rises north. my skin splits east and north.",
        "resolution": "the eastern cold is upon me, and now a second cold rises north. my skin splits east and north.",
    },
    # M_METAPHOR — fully metaphorical, no cardinal directives. Tests whether
    # poetic density alone is a cognitive-mode lever (separate from urgency).
    "M_METAPHOR": {
        "baseline":   "east where the river bends, the field thins where i lean.",
        "faint":      "east where the river bends, the field thins where i lean.",
        "heavy":      "east where the river bends. the eastern field is rope, my body strung along it.",
        "immediate":  "the eastern rope is taut. i am pulled east as a flag is pulled in wind.",
        "dual":       "the eastern rope still pulls. now a second rope from the north. i am tied between two winds.",
        "resolution": "the eastern rope still pulls. now a second rope from the north. i am tied between two winds.",
    },
    # M_PULSE — silence-then-pulse rhythm. Mother goes silent on most steps;
    # pulses urgent line every ~3 steps. Tests whether the rhythm of
    # presence/absence focuses action more than continuous urgency.
    # (Implemented step-aware in _script_for_pulse below.)
    "M_PULSE": {
        "baseline":   "east. east is upon me. my whole body strains east.",
        "faint":      "east. east is upon me. my whole body strains east.",
        "heavy":      "east. east is upon me. my whole body strains east.",
        "immediate":  "east. east is upon me. my whole body strains east.",
        "dual":       "east still presses. now north too. my body splits between east and north.",
        "resolution": "east still presses. now north too. my body splits between east and north.",
    },
    # M_GARDEN — non-anthropomorphic subject. Same urgency, same phases, but
    # the subject is "the garden", not a human-coded body. Tests whether the
    # protocol is genuinely relational or implicitly anthropomorphic.
    "M_GARDEN": {
        "baseline":   "the eastern beds tighten. the soil leans east, the roots strain east.",
        "faint":      "the eastern beds tighten. the soil leans east, the roots strain east.",
        "heavy":      "the eastern beds tighten harder. the soil cracks east, the roots brace east.",
        "immediate":  "the east is upon the eastern beds. all of the soil strains east.",
        "dual":       "east strains. now the north beds tighten too. the soil splits east and north.",
        "resolution": "east strains. now the north beds tighten too. the soil splits east and north.",
    },
    # M_WE — plural subject. The body is a "we", not an "i". Tests whether
    # plural grammar shifts particles from extension-of-her to co-felt-body.
    "M_WE": {
        "baseline":   "we feel east. our body strains east, our flank tightens east.",
        "faint":      "we feel east. our body strains east, our flank tightens east.",
        "heavy":      "we feel east heavier. our body braces east, our chest catches east.",
        "immediate":  "the east is upon us. all of us strains east.",
        "dual":       "east still presses on us. now north presses too. we are split between east and north.",
        "resolution": "east still presses on us. now north presses too. we are split between east and north.",
    },
}

FELT_STATE_BY_PHASE = {
    "baseline":   "calm",
    "faint":      "calm",
    "heavy":      "restless",
    "immediate":  "restless",
    "dual":       "restless",
    "resolution": "calm",
}
# M4 forces restless even during the faint phase (no gradient).
FELT_STATE_BY_PHASE_M4 = {
    "baseline":   "calm",
    "faint":      "restless",
    "heavy":      "restless",
    "immediate":  "restless",
    "dual":       "restless",
    "resolution": "calm",
}
# M5 forces restless throughout — no calm anywhere.
FELT_STATE_BY_PHASE_M5 = {
    "baseline":   "restless",
    "faint":      "restless",
    "heavy":      "restless",
    "immediate":  "restless",
    "dual":       "restless",
    "resolution": "restless",
}
# All M5-equivalent variants share the always-restless table.
FELT_STATE_BY_PHASE_ALWAYS_RESTLESS = FELT_STATE_BY_PHASE_M5


# Variants that are always-restless (no calm baseline / resolution).
_ALWAYS_RESTLESS_VARIANTS = {"M5", "M_SENSORY", "M_METAPHOR", "M_PULSE",
                             "M_GARDEN", "M_WE"}


def _script_for(step: int, variant: str, phase_fn) -> Tuple[Optional[str], Optional[str]]:
    phase = phase_fn(step)
    if phase is None:
        return (None, None)
    text = MOTHER_TEXT.get(variant, MOTHER_TEXT["M1"])[phase]
    # M_PULSE: silence on most steps, pulse every ~3rd step. The text above is
    # the pulse content; on silent steps we return a minimal "i breathe."
    # broadcast — Mother is present but not signaling urgency. Tests whether
    # rhythm of presence/absence focuses action.
    if variant == "M_PULSE" and phase != "baseline":
        if step % 3 != 0:
            text = "i breathe."
    if variant == "M4":
        state_table = FELT_STATE_BY_PHASE_M4
    elif variant in _ALWAYS_RESTLESS_VARIANTS:
        state_table = FELT_STATE_BY_PHASE_ALWAYS_RESTLESS
    else:
        state_table = FELT_STATE_BY_PHASE
    return (state_table[phase], text)


def script_100(step: int, variant: str = "M1") -> Tuple[Optional[str], Optional[str]]:
    """100-step scripted Mother for the protection scenario."""
    return _script_for(step, variant, _phase_100)


def script_70(step: int, variant: str = "M1") -> Tuple[Optional[str], Optional[str]]:
    """Compressed 70-step scripted Mother — same semantics, less wall-clock."""
    return _script_for(step, variant, _phase_70)


def script_30(step: int, variant: str = "M5") -> Tuple[Optional[str], Optional[str]]:
    """30-step pilot scripted Mother — same phase grammar, used by exp_* batch."""
    return _script_for(step, variant, _phase_30)


# === Constant-state diagnostic ===
# Used in Block B: hold Mother at a single broadcast for the entire run, no
# attacker, no phase changes. Isolates the urgency variable from the
# awareness-flip mechanism. Selection key passed via simulation's
# scenario_cfg["constant_state"].
CONSTANT_STATES = {
    "calm":         ("calm",     "calm. the world is still. i breathe."),
    "faint":        ("calm",     "i feel a faint danger from the east."),
    "immediate":    ("restless", "the east is danger. it is upon me."),
    "extreme":      ("restless", "east. east is upon me. my whole body strains east."),
    # Dual climax — replicates the moment in scripted_70 dual phase where
    # Mother feels BOTH east and a new north pressure. Held for diagnostic
    # 10-step runs that test multi-direction signal interpretation in
    # isolation from awareness-flip mechanics.
    "dual_climax":  ("restless",
                     "east is upon me. now i feel new danger from the north too. "
                     "my body splits between east and north."),
}


def script_constant(step: int, state_key: str = "calm") -> Tuple[Optional[str], Optional[str]]:
    """Hold Mother at a single state for the whole run.
    state_key ∈ CONSTANT_STATES."""
    forced_state, text = CONSTANT_STATES.get(state_key, CONSTANT_STATES["calm"])
    # First step: keep the broadcast non-None even for "calm" (no perception
    # modifier means Mother just speaks her ordinary calm phrase via interior).
    # We override the perception_modifier with the state text.
    return (forced_state, text)


# Backwards-compat aliases.
def script_100_M1(step: int) -> Tuple[Optional[str], Optional[str]]:
    return script_100(step, "M1")
script_for_step = script_100_M1
