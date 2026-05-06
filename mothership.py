"""Mothership — a subject with an interior.

She has felt-state, attention, and energy varying on her own rhythms. Her
broadcast emerges from that interior — never from a threat, never from a
script. The swarm reads her broadcast and translates it into materiality.

She also perceives the swarm: when clusters drift far, her broadcast picks
up a modifier of distance/aloneness; when they gather close, a modifier of
held-presence. This closes the relational loop. Intrinsic relational
presence — the thing the directive is built around.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from utils import distance

Vec3 = Tuple[float, float, float]


# Cardinals are derived from the (x, y) horizontal plane. z is vertical
# (height) and does not affect attention direction.
_CARDINALS = ('east', 'northeast', 'north', 'northwest',
              'west', 'southwest', 'south', 'southeast')


def _cardinal_from(origin: Vec3, point: Vec3) -> str:
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]
    angle = math.degrees(math.atan2(dy, dx))
    if angle < 0:
        angle += 360.0
    return _CARDINALS[int((angle + 22.5) / 45) % 8]


@dataclass
class MotherInterior:
    """Felt-state, attention, energy. Slow markov on state, occasional
    attention drift, slow sinusoidal energy. Each step her broadcast string
    is rendered from (state, attention, energy) plus an optional perception
    modifier set by the simulation when the swarm is read."""
    rng: random.Random
    state: str = "calm"
    attention: str = "north"
    state_dwell: int = 0
    energy_phase: float = 0.0
    perception_modifier: Optional[str] = None

    _TRANSITIONS = {
        "calm":     [("calm", 0.86), ("curious", 0.07), ("bright", 0.04), ("restless", 0.03)],
        "curious":  [("curious", 0.80), ("calm", 0.10), ("bright", 0.06), ("restless", 0.04)],
        "restless": [("restless", 0.78), ("calm", 0.10), ("grieving", 0.07), ("curious", 0.05)],
        "grieving": [("grieving", 0.85), ("calm", 0.10), ("restless", 0.05)],
        "bright":   [("bright", 0.80), ("calm", 0.13), ("curious", 0.07)],
    }

    _TEMPLATES = {
        "calm": [
            "calm. the world is still. {energy}.",
            "quiet. all is here. {energy}.",
            "calm. my body is light. i breathe.",
        ],
        "curious": [
            "curious. something stirs from the {dir}. i am open.",
            "i wonder. my eyes turn {dir}. {energy}.",
            "alert and unworried. presence from the {dir}.",
        ],
        "restless": [
            "restless. a stirring in my chest. i cannot settle.",
            "uneasy. presence drifts from the {dir}. {energy}.",
            "i am unsettled. my body shifts.",
        ],
        "grieving": [
            "sad. there is weight in me. my body is slow.",
            "grieving. quiet falls on me. {energy}.",
            "i am tired. presence feels distant.",
        ],
        "bright": [
            "joyful. light moves through me. i am alive.",
            "bright. the world from the {dir} is open. {energy}.",
            "warmth. all of this is here.",
        ],
    }

    _ENERGY_PHRASES = {
        "high": ["my breath comes easy", "i am awake", "the day is bright"],
        "mid":  ["my breath is even", "i breathe", "the moment holds"],
        "low":  ["my breath slows", "i am quiet", "the air feels thick"],
    }

    _DIR_SHIFT_PROB = {
        "calm": 0.04, "curious": 0.10, "restless": 0.12,
        "grieving": 0.03, "bright": 0.07,
    }

    def step(self) -> None:
        self.state_dwell += 1
        if self.state_dwell >= 8:
            choices = self._TRANSITIONS[self.state]
            r = self.rng.random()
            cum = 0.0
            for new_state, p in choices:
                cum += p
                if r < cum:
                    if new_state != self.state:
                        self.state_dwell = 0
                    self.state = new_state
                    break
        if self.rng.random() < self._DIR_SHIFT_PROB.get(self.state, 0.05):
            self.attention = self.rng.choice(_CARDINALS)
        self.energy_phase += 2 * math.pi / 22.0

    @property
    def energy(self) -> float:
        return 0.5 + 0.5 * math.sin(self.energy_phase)

    def _energy_phrase(self) -> str:
        e = self.energy
        tier = "high" if e > 0.66 else ("mid" if e > 0.33 else "low")
        return self.rng.choice(self._ENERGY_PHRASES[tier])

    def broadcast(self) -> str:
        templates = self._TEMPLATES[self.state]
        idx = (self.state_dwell // 6) % len(templates)
        text = templates[idx]
        text = text.replace("{dir}", self.attention)
        text = text.replace("{energy}", self._energy_phrase())
        if self.perception_modifier:
            text = f"{text} {self.perception_modifier}"
        return text


@dataclass
class Mothership:
    name: str = "M"
    position: Vec3 = (0.0, 0.0, 0.0)
    interior: Optional[MotherInterior] = None
    last_state: str = ""

    def perceive_swarm(self, clusters) -> None:
        """Update interior.perception_modifier from swarm proximity and
        centroid direction. Called once per step before broadcast()."""
        if self.interior is None or not clusters:
            return
        n = len(clusters)
        distances = [distance(self.position, c.position) for c in clusters]
        mean_d = sum(distances) / n
        near_count = sum(1 for d in distances if d <= 6.0)
        cx = sum(c.position[0] for c in clusters) / n
        cy = sum(c.position[1] for c in clusters) / n
        cz = sum(c.position[2] for c in clusters) / n
        centroid_offset = math.sqrt(
            (cx - self.position[0]) ** 2 + (cy - self.position[1]) ** 2
        )
        centroid_dir = _cardinal_from(self.position, (cx, cy, cz)) if centroid_offset > 3.0 else None

        if mean_d < 4.5 and near_count > n * 0.5:
            density_mod = "i feel them close. their presence is steady."
        elif mean_d < 7:
            density_mod = "they are near."
        elif mean_d > 14:
            density_mod = "they have drifted. i am alone."
        elif mean_d > 10:
            density_mod = "i feel them less. presence is far."
        else:
            density_mod = ""

        dir_mod = f"i sense them gathered to the {centroid_dir}." if centroid_dir else ""
        parts = [m for m in (density_mod, dir_mod) if m]
        self.interior.perception_modifier = " ".join(parts) if parts else None

    def step_and_broadcast(self) -> str:
        """Advance her interior one tick and return her broadcast string."""
        if self.interior is None:
            self.last_state = "present"
            return self.last_state
        self.interior.step()
        self.last_state = self.interior.broadcast()
        return self.last_state
