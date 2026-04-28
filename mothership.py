"""Mothership — passive entity that broadcasts a state string based on nearest threat."""
from dataclasses import dataclass
from typing import List, Tuple, Optional
from threat import Threat
from utils import distance


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
            # detects. No coordinates, no distance numbers. Distant particles read
            # emotional resonance, not surveillance data. This is closer to how
            # Gaara's sand reads Gaara: through resonance with his interior state.
            if t is None:
                return "calm. the world is still."
            d = distance(self.position, t.position)
            if d <= self.critical_radius:
                return "afraid. it is upon me. my body knows danger."
            if d <= self.danger_radius:
                return "my heart quickens. presence is close. i feel unease."
            if d <= self.awareness_radius:
                return "i sense something. presence in the distance. i am attentive."
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
