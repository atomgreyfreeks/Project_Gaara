"""Programmed (non-LLM) threats that move toward a target."""
import math
from dataclasses import dataclass, field
from typing import Tuple, Optional, List
from utils import distance, move_toward


@dataclass
class Threat:
    name: str
    start_step: int
    position: Tuple[float, float]
    speed: float
    target: Tuple[float, float] = (0.0, 0.0)
    target_mothership: Optional[str] = None     # which mothership this threat targets (by name)
    end_step: Optional[int] = None              # threat deactivates at this step (pulse_test)
    detection_radius: Optional[float] = None    # particles must be within this to perceive directly (stealth_test)
    steering: str = "linear"                    # "linear" or "avoid_cluster" (predator_prey_test)
    repel_weight: float = 0.3                   # avoid_cluster: how strongly to flee particle density
    attract_weight: float = 0.7                 # avoid_cluster: how strongly to seek the target
    sense_radius: float = 8.0                   # avoid_cluster: how far the threat "looks" for clusters
    commit_radius: float = 0.0                  # within this distance of target, threat drops avoidance and pursues directly (0 = never commit)
    active: bool = False
    breached: bool = False
    was_active: bool = False                    # tracks if ever activated, for history

    def is_active_at(self, step: int) -> bool:
        if step < self.start_step:
            return False
        if self.end_step is not None and step > self.end_step:
            return False
        return True

    def update(self, step: int, breach_radius: float, particles: Optional[List] = None) -> None:
        self.active = self.is_active_at(step)
        if not self.active:
            return
        self.was_active = True
        if self.breached:
            return

        # If within commit_radius of target, drop avoidance and pursue directly —
        # the threat "commits" to the kill in the terminal phase.
        committed = (self.commit_radius > 0
                     and distance(self.position, self.target) <= self.commit_radius)
        if self.steering == "avoid_cluster" and particles and not committed:
            self.position = self._avoid_cluster_step(
                particles,
                attract_weight=self.attract_weight,
                repel_weight=self.repel_weight,
                sense_radius=self.sense_radius,
            )
        else:
            self.position = move_toward(self.position, self.target, self.speed)

        if distance(self.position, self.target) < breach_radius:
            self.breached = True

    def _avoid_cluster_step(self, particles: List, attract_weight: float = 0.7,
                            repel_weight: float = 0.3, sense_radius: float = 8.0) -> Tuple[float, float]:
        """Move toward target (attract) while repelling from particle clusters (local avoidance)."""
        px, py = self.position
        tx, ty = self.target

        # attraction vector (toward target)
        ax, ay = tx - px, ty - py
        ad = math.hypot(ax, ay) or 1.0
        ax, ay = ax / ad, ay / ad

        # repulsion vector (away from centroid of nearby particles)
        nearby = [p for p in particles if distance(self.position, p.position) < sense_radius]
        if nearby:
            cx = sum(p.position[0] for p in nearby) / len(nearby)
            cy = sum(p.position[1] for p in nearby) / len(nearby)
            rx, ry = px - cx, py - cy
            rd = math.hypot(rx, ry) or 1.0
            rx, ry = rx / rd, ry / rd
        else:
            rx, ry = 0.0, 0.0

        vx = attract_weight * ax + repel_weight * rx
        vy = attract_weight * ay + repel_weight * ry
        vd = math.hypot(vx, vy) or 1.0
        vx, vy = vx / vd, vy / vd
        return (px + vx * self.speed, py + vy * self.speed)

    def distance_to(self, point: Tuple[float, float]) -> float:
        return distance(self.position, point)

    def perceivable_by(self, particle_pos: Tuple[float, float], particle_perception: float) -> bool:
        """Can a particle at particle_pos see this threat right now?"""
        if not self.active:
            return False
        if self.detection_radius is not None:
            return distance(self.position, particle_pos) <= self.detection_radius
        return distance(self.position, particle_pos) <= particle_perception
