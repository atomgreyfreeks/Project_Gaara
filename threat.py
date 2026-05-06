"""Attacker — minimal deterministic body that moves toward the Mothership.

No steering, no perception, no breach logic. The attacker exists only to
provide a moving disturbance the architecture can react to. All interesting
behavior lives in the swarm's interpretation, not the attacker.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Tuple

Vec2 = Tuple[float, float]


@dataclass
class Attacker:
    name: str
    start_step: int               # step at which the attacker first appears
    start_position: Vec2          # (x, y) where it spawns
    target: Vec2                  # (x, y) it walks toward (usually Mother)
    speed: float                  # units per step

    position: Vec2 = (0.0, 0.0)
    active: bool = False

    def __post_init__(self):
        self.position = self.start_position

    def update(self, step: int) -> None:
        """Advance one step. Activates at start_step and moves linearly toward
        target at constant speed. Stops once target is reached."""
        if step < self.start_step:
            self.active = False
            return
        self.active = True
        dx = self.target[0] - self.position[0]
        dy = self.target[1] - self.position[1]
        d = math.sqrt(dx * dx + dy * dy)
        if d <= self.speed or d == 0.0:
            self.position = self.target
            return
        self.position = (
            self.position[0] + dx / d * self.speed,
            self.position[1] + dy / d * self.speed,
        )

    def distance_to(self, point: Vec2) -> float:
        return math.hypot(self.position[0] - point[0],
                          self.position[1] - point[1])
