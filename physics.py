"""Physics integrator — LLM Body Language architecture (v2, simplified).

The LLM emits intent (ideal_coord, urgency, hostility); this layer turns
intent into kinematics. Architecture choices:

  - Urgency controls SPEED CAP, not force magnitude. A particle at urgency=0
    physically cannot move fast; at urgency=1 it can move quickly. Intent
    becomes a "physical capability dial," not a "push-strength dial."
  - Damping = inertia. Velocity eases toward the desired velocity each tick.
    Smooth motion, no instant teleport.
  - Hostility = jitter on velocity (noise sigma proportional to |hostility|).
    Sign passes through to the viewer for color/morphology.

No pull_gain coefficient — speed cap subsumes that role.

2D only — z is always 0; the viewer renders the plane in 3D.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Tuple

Vec2 = Tuple[float, float]


@dataclass
class PhysicsConfig:
    vmax_low: float = 0.4        # speed cap when urgency = 0 (slower than attacker)
    vmax_high: float = 1.5       # speed cap when urgency = 1 (~3× attacker)
    damping: float = 0.20        # how slowly velocity eases toward desired (0 = instant, 1 = stuck)
    jitter_scale: float = 0.4    # gaussian sigma at |hostility|=1
    dt: float = 1.0
    half_space: float = 25.0


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def integrate(
    position: Vec2,
    velocity: Vec2,
    ideal_coord: Vec2,
    urgency: float,
    hostility: float,
    cfg: PhysicsConfig,
    rng: random.Random,
) -> tuple[Vec2, Vec2]:
    """Advance one cluster by dt. Returns (new_position, new_velocity)."""
    dx = ideal_coord[0] - position[0]
    dy = ideal_coord[1] - position[1]
    distance = math.sqrt(dx * dx + dy * dy)

    # Urgency caps speed; the particle physically cannot exceed this.
    target_speed = cfg.vmax_low + urgency * (cfg.vmax_high - cfg.vmax_low)

    # Desired velocity: direction toward target × min(target_speed, distance/dt).
    # Capping at distance/dt prevents overshoot when very close to ideal_coord.
    if distance > 1e-6:
        speed = min(target_speed, distance / cfg.dt)
        desired_vx = dx / distance * speed
        desired_vy = dy / distance * speed
    else:
        desired_vx = 0.0
        desired_vy = 0.0

    # Smooth current velocity toward desired (damping = inertia).
    # damping=0 → instant snap; damping=1 → stuck at current velocity.
    keep = cfg.damping
    inject = 1.0 - keep
    vx = velocity[0] * keep + desired_vx * inject
    vy = velocity[1] * keep + desired_vy * inject

    # Hostility magnitude → jitter noise.
    sigma = abs(hostility) * cfg.jitter_scale
    if sigma > 0:
        vx += rng.gauss(0.0, sigma)
        vy += rng.gauss(0.0, sigma)

    # Hard speed cap (jitter could push us over).
    speed = math.sqrt(vx * vx + vy * vy)
    if speed > cfg.vmax_high:
        s = cfg.vmax_high / speed
        vx, vy = vx * s, vy * s

    # Update position; clamp to field.
    px = _clamp(position[0] + vx * cfg.dt, -cfg.half_space, cfg.half_space)
    py = _clamp(position[1] + vy * cfg.dt, -cfg.half_space, cfg.half_space)

    return (px, py), (vx, vy)
