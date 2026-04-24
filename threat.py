"""Programmed (non-LLM) threats that move toward the mothership."""
from dataclasses import dataclass
from typing import Tuple
from utils import distance, move_toward


@dataclass
class Threat:
    name: str
    start_step: int
    position: Tuple[float, float]
    speed: float
    target: Tuple[float, float] = (0.0, 0.0)
    active: bool = False
    breached: bool = False

    def is_due(self, step: int) -> bool:
        return step >= self.start_step

    def update(self, step: int, breach_radius: float) -> None:
        if not self.is_due(step):
            return
        if not self.active:
            self.active = True
        if self.breached:
            return
        self.position = move_toward(self.position, self.target, self.speed)
        if distance(self.position, self.target) < breach_radius:
            self.breached = True

    def distance_to(self, point: Tuple[float, float]) -> float:
        return distance(self.position, point)
