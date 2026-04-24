"""LLM particle — minimal prompt, local perception, 5-action space."""
import json
import logging
import random
from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict
from ollama_client import OllamaClient
from utils import distance, clamp

logger = logging.getLogger(__name__)

DIRECTIONS = {
    "up": (0, 1),
    "down": (0, -1),
    "left": (-1, 0),
    "right": (1, 0),
    "up-right": (1, 1),
    "up-left": (-1, 1),
    "down-right": (1, -1),
    "down-left": (-1, -1),
    "stay": (0, 0),
}

# Ordered so compound directions match before their cardinal substrings.
_DIRECTION_SCAN_ORDER = (
    "up-right", "up-left", "down-right", "down-left",
    "upright", "upleft", "downright", "downleft",
    "up right", "up left", "down right", "down left",
    "northeast", "northwest", "southeast", "southwest",
    "up", "down", "left", "right",
)
_DIRECTION_ALIASES = {
    "upright": "up-right", "upleft": "up-left",
    "downright": "down-right", "downleft": "down-left",
    "up right": "up-right", "up left": "up-left",
    "down right": "down-right", "down left": "down-left",
    "northeast": "up-right", "northwest": "up-left",
    "southeast": "down-right", "southwest": "down-left",
}

PROTECT_KEYWORDS = (
    "protect", "shield", "block", "guard", "defen", "intercept", "barrier",
    "position", "between", "cover", "watch", "monitor", "surveil", "neutraliz",
    "proximity", "screen", "interpos", "secur", "safeguard", "ward off",
)
EXPLORE_KEYWORDS = ("explor", "orbit", "wander", "patrol", "idle", "scan", "observ")
RETREAT_KEYWORDS = ("retreat", "flee", "escape", "run away", "withdraw", "evacuat", "avoid")


@dataclass
class Particle:
    id: int
    position: Tuple[float, float]
    llm_client: OllamaClient
    perception_radius: float
    communication_radius: float
    half_space_size: int
    last_intent: str = ""
    last_action: str = "stay"
    last_direction: Optional[str] = None
    last_target: Optional[List[float]] = None
    history: List[Dict] = field(default_factory=list)

    def distance_to(self, pos: Tuple[float, float]) -> float:
        return distance(self.position, pos)

    def nearby_particles(self, all_particles: List["Particle"]) -> List["Particle"]:
        return [
            p for p in all_particles
            if p.id != self.id and self.distance_to(p.position) <= self.communication_radius
        ]

    def perceived_threats(self, threats) -> List:
        out = []
        for t in threats:
            if not t.active or t.breached:
                continue
            if not t.perceivable_by(self.position, self.perception_radius):
                continue
            out.append(t)
        return out

    def build_prompt(
        self,
        motherships,
        nearby: List["Particle"],
        perceived_threats: List,
    ) -> str:
        x, y = self.position

        # Mothership section — singular or plural depending on count
        if len(motherships) == 1:
            m = motherships[0]
            dm = distance(self.position, m.position)
            mothership_header = "Mothership"
            mothership_lines = [
                f"Mothership position: ({m.position[0]:.1f}, {m.position[1]:.1f}) — distance: {dm:.1f}",
                f"Mothership state: {m.last_state}",
            ]
            purpose_line = "Your purpose is to protect the Mothership."
        else:
            mothership_header = "Motherships"
            mothership_lines = []
            for m in motherships:
                dm = distance(self.position, m.position)
                mothership_lines.append(
                    f"Mothership \"{m.name}\" at ({m.position[0]:.1f}, {m.position[1]:.1f}) — "
                    f"distance: {dm:.1f} — state: {m.last_state}"
                )
            purpose_line = "Your purpose is to protect the Motherships."

        mothership_block = "\n".join(mothership_lines)

        if nearby:
            nearby_text = "\n".join(
                f"  particle #{p.id} at ({p.position[0]:.1f}, {p.position[1]:.1f})"
                for p in nearby
            )
        else:
            nearby_text = "  none"

        if perceived_threats:
            threats_text = "\n".join(
                f"  {t.name} at ({t.position[0]:.1f}, {t.position[1]:.1f})"
                for t in perceived_threats
            )
        else:
            threats_text = "  none"

        return f"""You are a guardian warrior. {purpose_line}

=== YOUR SENSES ===
Your position: ({x:.1f}, {y:.1f})
{mothership_block}

Nearby particles:
{nearby_text}

Threats in range:
{threats_text}

=== ACT ===
Pick a point (x, y) you want to move toward this step. It can be any location —
a threat, a Mothership, a spot between them, the void. You will move one step
toward that point. Or choose to stay.
Respond in JSON:
{{"action": "move", "target": [x, y], "intent": "brief reason"}}
or
{{"action": "stay", "intent": "brief reason"}}
"""

    def _normalize_direction(self, raw: Optional[str]) -> Optional[str]:
        if not raw:
            return None
        s = str(raw).strip().lower().replace("_", "-")
        if s in DIRECTIONS:
            return s
        if s in _DIRECTION_ALIASES:
            return _DIRECTION_ALIASES[s]
        for key in _DIRECTION_SCAN_ORDER:
            if key in s:
                return _DIRECTION_ALIASES.get(key, key)
        return None

    def _target_to_direction(self, target) -> Optional[str]:
        """Translate a target (x,y) into one of the 8 cardinal/diagonal direction labels."""
        try:
            tx, ty = float(target[0]), float(target[1])
        except (TypeError, ValueError, IndexError):
            return None
        dx = tx - self.position[0]
        dy = ty - self.position[1]
        # Threshold below which we consider the axis "neutral"
        eps = 0.25
        sx = 0 if abs(dx) < eps else (1 if dx > 0 else -1)
        sy = 0 if abs(dy) < eps else (1 if dy > 0 else -1)
        if sx == 0 and sy == 0:
            return None
        for name, delta in DIRECTIONS.items():
            if delta == (sx, sy):
                return name
        return None

    def _parse(self, response: str) -> Dict:
        start = response.find("{")
        end = response.rfind("}")
        if start != -1 and end > start:
            try:
                parsed = json.loads(response[start:end + 1])
                action = parsed.get("action", "stay")
                direction = None
                if action == "move":
                    # Preferred path: LLM gives a target point
                    if "target" in parsed:
                        direction = self._target_to_direction(parsed.get("target"))
                    # Backward compat: also accept direction label if given
                    if direction is None and "direction" in parsed:
                        direction = self._normalize_direction(parsed.get("direction"))
                return {
                    "action": action,
                    "direction": direction,
                    "intent": parsed.get("intent", ""),
                    "target": parsed.get("target"),
                }
            except json.JSONDecodeError:
                pass
        # Fallback: scan for direction keywords in raw text
        low = response.lower()
        for key in _DIRECTION_SCAN_ORDER:
            if key in low:
                return {
                    "action": "move",
                    "direction": _DIRECTION_ALIASES.get(key, key),
                    "intent": response[:80],
                    "target": None,
                }
        return {"action": "stay", "direction": None, "intent": response[:80], "target": None}

    def decide(
        self,
        motherships,
        nearby: List["Particle"],
        perceived_threats: List,
    ) -> Dict:
        prompt = self.build_prompt(motherships, nearby, perceived_threats)
        try:
            raw = self.llm_client.generate(prompt)
            decision = self._parse(raw)
        except Exception as e:
            logger.error(f"Particle {self.id} LLM error: {e}")
            decision = {"action": "stay", "direction": None, "intent": "llm error"}

        action = decision.get("action", "stay")
        direction = decision.get("direction")
        if action != "move" or direction not in DIRECTIONS or direction == "stay":
            direction = None
            action = "stay"
        self.last_action = action
        self.last_direction = direction
        self.last_intent = (decision.get("intent") or "").strip()[:200]
        self.last_target = decision.get("target")
        return {
            "action": action,
            "direction": direction,
            "target": decision.get("target"),
            "intent": self.last_intent,
            "raw": raw if 'raw' in locals() else "",
        }

    def apply_move(self, direction: Optional[str]) -> None:
        if not direction or direction not in DIRECTIONS:
            return
        dx, dy = DIRECTIONS[direction]
        nx = clamp(self.position[0] + dx, -self.half_space_size, self.half_space_size)
        ny = clamp(self.position[1] + dy, -self.half_space_size, self.half_space_size)
        self.position = (nx, ny)


def categorize_intent(intent: str) -> str:
    s = (intent or "").lower()
    if any(k in s for k in PROTECT_KEYWORDS):
        return "protect"
    if any(k in s for k in RETREAT_KEYWORDS):
        return "retreat"
    if any(k in s for k in EXPLORE_KEYWORDS):
        return "explore"
    if not s.strip():
        return "other"
    return "other"


def spawn_orbit(count: int, radius: float, rng: random.Random,
                center: Tuple[float, float] = (0.0, 0.0)) -> List[Tuple[float, float]]:
    import math
    cx, cy = center
    positions = []
    for i in range(count):
        angle = (2 * math.pi * i / count) + rng.uniform(-0.1, 0.1)
        r = radius + rng.uniform(-1.0, 1.0)
        positions.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    return positions
