"""Mothership — passive entity that broadcasts a state string based on nearest threat."""
from dataclasses import dataclass
from typing import List, Tuple, Optional
from threat import Threat
from utils import distance


@dataclass
class Mothership:
    center_x: float = 0.0
    center_y: float = 0.0
    awareness_radius: float = 20.0
    danger_radius: float = 10.0
    critical_radius: float = 5.0

    @property
    def position(self) -> Tuple[float, float]:
        return (self.center_x, self.center_y)

    def nearest_threat(self, threats: List[Threat]) -> Optional[Threat]:
        active = [t for t in threats if t.active and not t.breached]
        if not active:
            return None
        return min(active, key=lambda t: distance(self.position, t.position))

    def compute_state(self, threats: List[Threat]) -> str:
        t = self.nearest_threat(threats)
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
