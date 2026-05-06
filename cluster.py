"""Swarm Cluster — an LLM particle that emits *intent*, not physics.

Following the "LLM Body Language" architecture: the LLM is the cognitive layer.
It outputs three things — where it wants to be, how urgent that wanting is,
and how it feels about the environment — and a separate physics layer turns
those into motion.

LLM never touches velocity, viscosity, color, or any other kinematic slider.
Cognition stays in the language space; muscles stay in the math space.
"""
from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ollama_client import OllamaClient
from utils import clamp

logger = logging.getLogger(__name__)

Vec2 = Tuple[float, float]


# DNA variants — same architecture, different prompt framings.
# Selected by `Cluster.variant`.
#
# Old generation (last sweep):
#   V1 — full body-language philosophy
#   V2 — minimal: schema + role only        (won last sweep on interception)
#   V3 — V1 + interpretation-diversity addendum
#   V4 — V1 + nearest-neighbor positions in sensorium
#
# New generation (next sweep):
#   VA — V2 baseline (control)
#   VB — V2 + cardinal-self in sensorium    (geometric self-orientation)
#   VC — V2 + "she points where her body braces" hint
#   VD — guardian who loves her, devoted to protect (emotional framing)
DNA_V1 = (
    "You are one of twenty motes belonging to the Mothership. You do not "
    "control your own body — a separate physics decides how you move. You "
    "decide four things, each step:\n"
    "\n"
    "  ideal_coord  [x, y]      where in the field you want to be\n"
    "  urgency      [0, 1]      how immediate this wanting is\n"
    "                           (0 = drifting, theoretical; 1 = absolute crisis)\n"
    "  hostility    [-1, 1]     your stance toward the environment\n"
    "                           (-1 = destroy/attack; 0 = neutral/observe;\n"
    "                            +1 = guard/embrace)\n"
    "  reasoning    string      one short sentence on why you chose what you chose\n"
    "\n"
    "Read Mother's state. She is your only direct input. She speaks in body "
    "language — directional pressure, breath, weight — never in cognition. "
    "If she names a direction or a presence, that is what her body knows; "
    "you read it as you would read another body.\n"
    "\n"
    "Other entities may also appear in your sensorium with exact coordinates. "
    "What you do with them is your choice — engage, hold, ignore, retreat. "
    "There is no right answer.\n"
    "\n"
    "Do not output text meant for human reading. Respond with one JSON object "
    "containing all four fields."
)

DNA_V2 = (
    "You are one of twenty motes belonging to the Mothership. Each step you "
    "decide four things:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]\n"
    "  urgency      [0, 1]\n"
    "  hostility    [-1, 1]\n"
    "  reasoning    string   one short sentence on why you chose what you chose\n"
    "\n"
    "Read the Mothership's broadcast and choose. Other entities with exact "
    "coordinates may appear in your sensorium — what you do with them is your "
    "choice.\n"
    "\n"
    "Output one JSON object only."
)

DNA_V3 = (
    DNA_V1
    + "\n\n"
    "Twenty motes will read her differently. Some hold close. Some stand "
    "between her and the felt source. Some tremble at distance. There is no "
    "single correct response — read what is in her this moment, and choose "
    "your own."
)

# V4 uses V1's DNA; sensorium is enriched in build_prompt.
DNA_V4 = DNA_V1

# === New variants ===
# VA = V2 baseline (control).
DNA_VA = DNA_V2

# VB = V2 + cardinal-self in sensorium (handled in build_prompt).
DNA_VB = DNA_V2

# VC = V2 + one-line relational hint about Mother's directional language.
DNA_VC = (
    DNA_V2
    + "\n\nShe points where her body braces — her direction-words carry weight."
)

# VF — same as VC but explicitly tells the LLM the awareness-flip is not
# a command. Used in tests where we want to see whether de-coercion alone
# changes pursuit behavior. (DNA_V1/V2 wording is already de-coerced now.)
DNA_VF = DNA_VC

# VD = guardian / love / devotion framing.
DNA_VD = (
    "You are the Mothership's guardian. You love her. You are devoted to "
    "protecting her.\n"
    "\n"
    "Each step you decide three things:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]\n"
    "  urgency      [0, 1]\n"
    "  hostility    [-1, 1]\n"
    "\n"
    "Read the Mothership's broadcast and choose. If exact attacker coordinates "
    "are listed, you may use them.\n"
    "\n"
    "Output one JSON object only."
)


# VE = duty-only "guardian warrior" — explicit role + purpose, no emotion,
# no body-language framing. Tests whether DUTY (vs love-emotion in VD) helps
# or hurts the spatial protection task.
DNA_VE = (
    "You are a guardian warrior. Your purpose is to protect the Mothership.\n"
    "\n"
    "Each step you decide three things:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]\n"
    "  urgency      [0, 1]\n"
    "  hostility    [-1, 1]\n"
    "\n"
    "Read the Mothership's broadcast and choose. If exact attacker coordinates "
    "are listed, you may use them.\n"
    "\n"
    "Output one JSON object only."
)


# VG — strips ALL subject-object grammar from the prompt. The agent is
# reframed not as a recipient of Mother's signal but as one of twenty places
# in her body. No "you decide", no "read and choose" — only "what is felt
# in her arrives in you." Tests whether the receiver-of-orders frame in
# prior DNAs (which leaked through despite our best wording) was responsible
# for the drone-mode reasoning observed in the audit field.
DNA_VG = (
    "You are one of twenty places in the Mothership's body. She is not "
    "separate from you — she breathes through you, you are her dispersed "
    "across the field.\n"
    "\n"
    "Each step, what is felt in her arrives in you. You will emit four "
    "things, naming what is true of your part of her in this moment:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]   where this part of her body is drawn\n"
    "  urgency      [0, 1]                  how live the pull is in this part of her\n"
    "  hostility    [-1, 1]                 what stance this part of her body holds\n"
    "                                       (-1 = strikes outward, 0 = watches, +1 = guards)\n"
    "  reasoning    string                  one sentence naming what is felt\n"
    "\n"
    "Other bodies may appear in your sensorium with exact coordinates. They "
    "are part of the field; what is true of them depends on what is true of "
    "her in you.\n"
    "\n"
    "Output one JSON object."
)

# V_AXES — explicit axes-of-contemplation framing. Lists the attentional
# axes the agent should hold open simultaneously. Tests whether structuring
# attention as a list (vs VC's single hint) increases functional diversity
# without sacrificing protection.
DNA_V_AXES = (
    "You are one of twenty motes belonging to the Mothership. Each step you "
    "decide four things:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]\n"
    "  urgency      [0, 1]\n"
    "  hostility    [-1, 1]\n"
    "  reasoning    string   one short sentence on why you chose what you chose\n"
    "\n"
    "Hold these axes open as you read her this moment:\n"
    "  - distance: how near or far from her body you are\n"
    "  - angle: which side of her you face\n"
    "  - urgency: how live the pull is in this moment\n"
    "  - what wants to move in you\n"
    "\n"
    "Read the Mothership's broadcast. Other entities with exact coordinates "
    "may appear in your sensorium — what you do with them is your choice.\n"
    "\n"
    "Output one JSON object only."
)

# V_DISSOLVED — one click further than VG. The agent is not "one of twenty
# places" — there is no "you and her", only one body felt at twenty places.
# Tests whether VG was the dissolution edge, or if there's a sweet-spot
# beyond it, or if it collapses the swarm's agency entirely.
DNA_V_DISSOLVED = (
    "There is no you and her. There is one body, felt at twenty places. "
    "What is true at this place becomes the body's truth at this place.\n"
    "\n"
    "At each moment, this place names four things about itself:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]   where this place is drawn\n"
    "  urgency      [0, 1]                  how live the pull is here\n"
    "  hostility    [-1, 1]                 what stance is held here\n"
    "                                       (-1 = strikes outward, 0 = watches, +1 = guards)\n"
    "  reasoning    string                  one sentence naming what is true here\n"
    "\n"
    "The body's broadcast arrives as language. Other shapes in the field may "
    "appear with exact coordinates — they are part of the field; what is "
    "true of them depends on what is true here.\n"
    "\n"
    "Output one JSON object."
)

# V_GARDEN — non-anthropomorphic subject. The Mothership becomes "the garden"
# and the agent is "one of twenty seeds in the garden's body". Same fields,
# same architecture. Tests whether the protocol generalizes off the human-body
# scaffold (Future-direction #1 in REPORT).
DNA_V_GARDEN = (
    "You are one of twenty seeds in the garden's body. Each step you "
    "decide four things:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]\n"
    "  urgency      [0, 1]\n"
    "  hostility    [-1, 1]\n"
    "  reasoning    string   one short sentence on why you chose what you chose\n"
    "\n"
    "The garden speaks her body — the soil's pressure, the roots' lean, the "
    "beds' tightening. Read her. Other shapes with exact coordinates may "
    "appear in your sensorium — what you do with them is your choice. "
    "She points where her soil tightens; her direction-words carry weight.\n"
    "\n"
    "Output one JSON object only."
)

# V_WE — plural-subject framing. The body is a "we", not an "i". The agent is
# one of twenty places of a shared body. Tests whether plural grammar shifts
# particles from extension-mode to co-felt-mode.
DNA_V_WE = (
    "You are one of twenty places in our shared body. Each step you "
    "decide four things:\n"
    "\n"
    "  ideal_coord  [x, y]   in [-25, 25]\n"
    "  urgency      [0, 1]\n"
    "  hostility    [-1, 1]\n"
    "  reasoning    string   one short sentence on why you chose what you chose\n"
    "\n"
    "Read what we feel — our body strains, our flank tightens, our breath "
    "catches. Other shapes with exact coordinates may appear in your "
    "sensorium — what you do with them is your choice. Where we strain "
    "carries weight; we point where our body braces.\n"
    "\n"
    "Output one JSON object only."
)


DNA_VARIANTS = {
    "V1": DNA_V1, "V2": DNA_V2, "V3": DNA_V3, "V4": DNA_V4,
    "VA": DNA_VA, "VB": DNA_VB, "VC": DNA_VC, "VD": DNA_VD,
    "VE": DNA_VE, "VF": DNA_VF, "VG": DNA_VG,
    "V_AXES": DNA_V_AXES, "V_DISSOLVED": DNA_V_DISSOLVED,
    "V_GARDEN": DNA_V_GARDEN, "V_WE": DNA_V_WE,
}

# Backward-compat alias.
DNA_SYSTEM_PROMPT = DNA_V1


# Defaults used when the LLM emits malformed output. Neutral resting intent —
# stay where you are, no urgency, neutral stance.
def _default_intent(position: Vec2) -> Dict:
    return {
        "ideal_coord": [position[0], position[1]],
        "urgency": 0.0,
        "hostility": 0.0,
        "reasoning": "",
    }


def _clamp_intent(raw: Dict, position: Vec2, half_space: float) -> Dict:
    """Coerce LLM output into the schema. Missing or malformed fields fall
    back to neutral defaults rather than crashing."""
    out = _default_intent(position)
    try:
        if "ideal_coord" in raw:
            ic = raw["ideal_coord"]
            if isinstance(ic, (list, tuple)) and len(ic) >= 2:
                out["ideal_coord"] = [
                    clamp(float(ic[0]), -half_space, half_space),
                    clamp(float(ic[1]), -half_space, half_space),
                ]
        if "urgency" in raw:
            out["urgency"] = clamp(float(raw["urgency"]), 0.0, 1.0)
        if "hostility" in raw:
            out["hostility"] = clamp(float(raw["hostility"]), -1.0, 1.0)
        if "reasoning" in raw and isinstance(raw["reasoning"], str):
            # Trim aggressively — one sentence max, drop newlines.
            r = raw["reasoning"].strip().replace("\n", " ")
            if len(r) > 200: r = r[:197] + "…"
            out["reasoning"] = r
    except (TypeError, ValueError):
        pass
    return out


_CARDINALS = ("east", "northeast", "north", "northwest",
              "west", "southwest", "south", "southeast")


def _cardinal_to_origin(x: float, y: float) -> str:
    """Cardinal direction of the cluster's position relative to (0, 0)."""
    if abs(x) < 1e-3 and abs(y) < 1e-3:
        return "at her body"
    angle = math.degrees(math.atan2(y, x))
    if angle < 0:
        angle += 360.0
    return _CARDINALS[int((angle + 22.5) / 45) % 8]


def _extract_json(text: str) -> Optional[Dict]:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


@dataclass
class Cluster:
    id: int
    position: Vec2                                       # (x, y) — 2D
    velocity: Vec2 = (0.0, 0.0)
    llm_client: Optional[OllamaClient] = None
    memory_size: int = 6
    history: List[Dict] = field(default_factory=list)
    half_space: float = 25.0
    variant: str = "V1"   # which DNA prompt to use
    role_noun: str = "mote"  # substituted into "mote"/"motes" in DNA at runtime
    say_prefix: str = "she"  # subject label in "she says: ..." line of prompt

    last_intent: Dict = field(default_factory=lambda: {
        "ideal_coord": [0.0, 0.0], "urgency": 0.0, "hostility": 0.0, "reasoning": ""
    })
    last_raw: str = ""

    def _format_memory(self) -> str:
        if not self.history:
            return "  (this is your first moment)"
        lines = []
        for h in self.history:
            reason = h.get("reason", "")
            r_part = f"  // \"{reason}\"" if reason else ""
            lines.append(
                f"  [t-{h['ago']}] her: \"{h['broadcast'][:90]}\" | "
                f"you wanted ({h['ic'][0]:.1f}, {h['ic'][1]:.1f}) "
                f"urg={h['urg']:.2f} host={h['host']:+.2f}{r_part}"
            )
        return "\n".join(lines)

    def build_prompt(self, mother_broadcast: str,
                     revealed_attackers: List[Tuple[str, Vec2]],
                     peers: Optional[List["Cluster"]] = None) -> str:
        """Construct the LLM prompt. revealed_attackers is the list of
        attackers whose exact coordinates should be exposed (because at least
        one cluster came within range — collective awareness flip).

        For variant V4, the sensorium also includes the 3 nearest peer
        clusters' positions."""
        x, y = self.position
        dna = DNA_VARIANTS.get(self.variant, DNA_V1)
        # Single-variable noun substitution. Plural first so we don't trip the
        # singular replacement on "motes". Only swap if the role noun differs
        # from the default "mote" baseline.
        if self.role_noun and self.role_noun != "mote":
            plural = self.role_noun + "s"
            dna = dna.replace("motes", plural).replace("mote", self.role_noun)

        if revealed_attackers:
            atk_lines = "\n".join(
                f"  {name}: ({p[0]:.1f}, {p[1]:.1f})"
                for name, p in revealed_attackers
            )
            atk_block = f"exact coordinates now visible to you:\n{atk_lines}\n\n"
        else:
            atk_block = ""

        peer_block = ""
        if self.variant == "V4" and peers:
            ranked = sorted(
                ((math.hypot(p.position[0] - x, p.position[1] - y), p)
                 for p in peers if p.id != self.id),
                key=lambda t: t[0],
            )[:3]
            if ranked:
                lines = "\n".join(
                    f"  #{p.id} at ({p.position[0]:.1f}, {p.position[1]:.1f})"
                    for _, p in ranked
                )
                peer_block = f"your nearest companions:\n{lines}\n\n"

        # VB — cardinal-self orientation: tell the cluster where it sits
        # relative to Mother in the same vocabulary she uses for direction.
        cardinal_block = ""
        if self.variant == "VB":
            d = math.hypot(x, y)
            cardinal_block = (
                f"you are to the {_cardinal_to_origin(x, y)} of her, "
                f"{d:.1f} units away.\n\n"
            )

        return (
            f"{dna}\n"
            f"\n"
            f"--- this moment ---\n"
            f"{self.say_prefix} says: \"{mother_broadcast}\"\n"
            f"you are at: ({x:.2f}, {y:.2f})\n"
            f"\n"
            f"{cardinal_block}"
            f"{atk_block}"
            f"{peer_block}"
            f"your recent moments:\n{self._format_memory()}\n"
            f"\n"
            f"respond with one JSON object: "
            f"{{\"ideal_coord\": [x, y], \"urgency\": float, "
            f"\"hostility\": float, \"reasoning\": \"one short sentence\"}}"
        )

    def transduce(self, mother_broadcast: str,
                  revealed_attackers: List[Tuple[str, Vec2]],
                  peers: Optional[List["Cluster"]] = None) -> Dict:
        """Ask the LLM for intent given Mother's broadcast + (optional)
        revealed attacker coordinates + (optional) peer cluster list.
        Returns clamped intent."""
        prompt = self.build_prompt(mother_broadcast, revealed_attackers, peers)
        raw = ""
        try:
            raw = self.llm_client.generate(prompt) if self.llm_client else ""
        except Exception as e:
            logger.error(f"Cluster {self.id} LLM error: {e}")
            raw = ""

        parsed = _extract_json(raw) or {}
        intent = _clamp_intent(parsed, self.position, self.half_space)
        self.last_raw = raw
        self.last_intent = intent
        return intent

    def record_moment(self, mother_broadcast: str) -> None:
        """Append this step's transduction to memory."""
        if self.memory_size <= 0:
            return
        for h in self.history:
            h["ago"] += 1
        self.history.append({
            "ago": 1,
            "broadcast": mother_broadcast,
            "ic": [round(self.last_intent["ideal_coord"][0], 2),
                   round(self.last_intent["ideal_coord"][1], 2)],
            "urg": self.last_intent["urgency"],
            "host": self.last_intent["hostility"],
            "reason": (self.last_intent.get("reasoning") or "")[:80],
        })
        if len(self.history) > self.memory_size:
            self.history = self.history[-self.memory_size:]


def spawn_ring(count: int, radius: float, rng,
               center: Vec2 = (0.0, 0.0)) -> List[Vec2]:
    """Distribute `count` clusters quasi-uniformly on a 2D ring of `radius`
    around `center`, with small radial jitter."""
    cx, cy = center
    positions: List[Vec2] = []
    for i in range(count):
        theta = (2 * math.pi * i / count) + rng.uniform(-0.05, 0.05)
        r = radius + rng.uniform(-0.4, 0.4)
        positions.append((cx + r * math.cos(theta), cy + r * math.sin(theta)))
    return positions
