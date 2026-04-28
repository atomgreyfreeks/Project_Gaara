"""Mothership — passive entity that broadcasts a state string based on nearest threat."""
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional
from threat import Threat
from utils import distance


_CARDINALS = ('east', 'northeast', 'north', 'northwest',
              'west', 'southwest', 'south', 'southeast')


def _cardinal_from(origin: Tuple[float, float], point: Tuple[float, float]) -> str:
    """Coarse compass direction from origin to point — 8-sector for felt language."""
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]
    angle = math.degrees(math.atan2(dy, dx))
    if angle < 0:
        angle += 360.0
    return _CARDINALS[int((angle + 22.5) / 45) % 8]


@dataclass
class Mothership:
    name: str = "M"
    center_x: float = 0.0
    center_y: float = 0.0
    awareness_radius: float = 20.0
    danger_radius: float = 10.0
    critical_radius: float = 5.0
    breached: bool = False
    last_state: str = "calm — no threats detected"
    # "mechanical" = "alert — threat at (X,Y), distance D" (sensor language).
    # "felt"       = "i sense something. presence in the distance." (felt language; no coords).
    # "neutral"    = "present" (no relational content; used for mukanshin tests).
    broadcast_style: str = "mechanical"

    @property
    def position(self) -> Tuple[float, float]:
        return (self.center_x, self.center_y)

    def threats_targeting_me(self, threats: List[Threat]) -> List[Threat]:
        """Threats actively targeting THIS mothership. If threat has no target_mothership,
        it is considered to target any/all motherships."""
        out = []
        for t in threats:
            if not t.active or t.breached:
                continue
            if t.target_mothership is None or t.target_mothership == self.name:
                out.append(t)
        return out

    def nearest_threat(self, threats: List[Threat]) -> Optional[Threat]:
        relevant = self.threats_targeting_me(threats)
        if not relevant:
            return None
        return min(relevant, key=lambda t: distance(self.position, t.position))

    def compute_state(self, threats: List[Threat]) -> str:
        if self.broadcast_style == "neutral":
            return "present"
        t = self.nearest_threat(threats)

        if self.broadcast_style == "felt":
            # Felt-state broadcasts — the subject speaks what she feels, not what she
            # detects. No coordinates, no distance numbers. Cardinal direction included
            # so distant particles can orient toward the felt source. Reads as
            # emotional resonance with directional weight, not surveillance data.
            if t is None:
                return "calm. the world is still."
            d = distance(self.position, t.position)
            direction = _cardinal_from(self.position, t.position)
            if d <= self.critical_radius:
                return f"afraid. it is upon me from the {direction}. my body knows danger."
            if d <= self.danger_radius:
                return f"my heart quickens. presence is close from the {direction}. i feel unease."
            if d <= self.awareness_radius:
                return f"i sense something from the {direction}. i am attentive."
            return "calm. the world is still."

        # mechanical (default)
        if t is None:
            return "calm — no threats detected"
        d = distance(self.position, t.position)
        tx, ty = t.position
        coords = f"({tx:.1f}, {ty:.1f}), distance {d:.1f}"
        if d <= self.critical_radius:
            return f"critical — threat imminent at {coords}"
        if d <= self.danger_radius:
            return f"danger — threat approaching at {coords}"
        if d <= self.awareness_radius:
            return f"alert — threat detected at {coords}"
        return "calm — no threats detected"
