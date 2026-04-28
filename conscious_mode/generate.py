#!/usr/bin/env python3
"""Choreographed conscious-mode demo for Project Gaara.

This is the OPPOSITE of the project's main thesis. Here, the sand is moved
imperatively — particles are assigned target positions step-by-step like
drones following a script. This is "Gaara consciously moving his sand,"
the command-driven mode that the rest of the project is contrasting with.

The output is a run.json compatible with the Gaara viewer. Particle positions
are 3D ([x, sim_y, elevation]) so the choreography can use real height —
domes, walls, waves rising and falling.

Usage:
    python3 generate.py
    # then sync.sh copies into the viewer and registers the run

Phases of the demo (100 steps total):
    1– 15   orbit                     calm starting state
    16– 30  rise into dome           protective shield arcs over the Mothership
    31– 45  dome → wall              formation translates into a wall to the east
    46– 65  wall undulates as wave   like Gaara's tide of sand
    66– 80  wave collapses to spiral funnel forming around the Mothership
    81–100  spiral disperses back    return to orbit

Each transition is interpolated with ease-in-out cubic for cinematic motion.
"""
import json
import math
from pathlib import Path

GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))  # ~2.39996 rad
N = 20
DURATION = 100
ORBIT_R = 8.0
DOME_R = 9.0
WALL_DIST = 9.0


# ─── Shape generators ──────────────────────────────────────────────────────
# Each returns (sim_x, sim_y, elevation). Convention:
#   sim_x, sim_y = horizontal plane (matches existing viewer mapping)
#   elevation   = vertical offset from the Mothership's plane (positive = up)


def shape_orbit(i, n=N, R=ORBIT_R):
    """Calm orbital ring around the Mothership."""
    angle = 2 * math.pi * i / n + math.pi / 6  # slight phase offset
    return (R * math.cos(angle), R * math.sin(angle), 0.0)


def shape_dome(i, n=N, R=DOME_R):
    """Hemispherical dome above the Mothership."""
    # Distribute n points uniformly on the upper hemisphere via Fibonacci.
    y_norm = (i + 0.5) / n          # 0..1, top to base
    elev = R * y_norm                # 0..R
    radius_at_h = R * math.sqrt(max(0.0, 1.0 - y_norm * y_norm))
    phi = GOLDEN_ANGLE * i
    return (radius_at_h * math.cos(phi), radius_at_h * math.sin(phi), elev)


def shape_wall(i, n=N, D=WALL_DIST):
    """Vertical wall to the east (positive sim_x)."""
    # 4 columns × 5 rows = 20 particles, standing as a wall.
    cols, rows = 4, 5
    col = i // rows
    row = i % rows
    spacing = 2.0
    sim_x = D
    sim_y = (col - (cols - 1) / 2) * spacing      # spread horizontally
    elev = (row - (rows - 1) / 2) * spacing + 4   # stack vertically
    return (sim_x, sim_y, elev)


def shape_wave(i, n=N, t=0, D=WALL_DIST):
    """The wall undulates with a horizontal sine wave."""
    sim_x, sim_y, elev = shape_wall(i, n, D)
    wave = 1.5 * math.sin(elev * 0.7 + t * 0.35)
    return (sim_x + wave, sim_y, elev)


def shape_spiral(i, n=N, t=0, R=4.0):
    """A vertical spiral funneling around the Mothership (tight)."""
    layers = n
    layer = i / layers
    angle = 2 * math.pi * layer * 2 + t * 0.3   # 2 turns of spiral, rotating
    elev = layer * 8.0                          # spiral rises
    radius = R * (1.0 - 0.6 * layer)            # narrows toward top
    return (radius * math.cos(angle), radius * math.sin(angle), elev)


# ─── Animation: keyframes + ease-in-out cubic ──────────────────────────────


def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def lerp3(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


# Keyframes: (step, shape_function). Between consecutive keyframes we lerp.
KEYFRAMES = [
    (1,   lambda i, t: shape_orbit(i)),
    (15,  lambda i, t: shape_orbit(i)),
    (30,  lambda i, t: shape_dome(i)),
    (45,  lambda i, t: shape_wall(i)),
    (65,  lambda i, t: shape_wave(i, t=t)),
    (80,  lambda i, t: shape_spiral(i, t=t)),
    (100, lambda i, t: shape_orbit(i)),
]


def position_at(i, step):
    """Return (sim_x, sim_y, elevation) for particle i at step `step`."""
    for k in range(len(KEYFRAMES) - 1):
        s1, f1 = KEYFRAMES[k]
        s2, f2 = KEYFRAMES[k + 1]
        if s1 <= step <= s2:
            local_t = (step - s1) / max(1, s2 - s1)
            eased = ease_in_out_cubic(local_t)
            p1 = f1(i, step)
            p2 = f2(i, step)
            return lerp3(p1, p2, eased)
    # past the last keyframe — clamp
    return KEYFRAMES[-1][1](i, step)


# ─── Phase narration (visible in the viewer's intent text) ─────────────────


def phase_label(step):
    if step <= 15:
        return "calm. holding orbit."
    if step <= 30:
        return "rising. forming the dome."
    if step <= 45:
        return "translating. dome becomes wall."
    if step <= 65:
        return "the wall breathes. wave moves through me."
    if step <= 80:
        return "collapsing inward. the spiral tightens."
    return "dispersing. returning to orbit."


# ─── Build the run.json ────────────────────────────────────────────────────


def build_run():
    run = {
        "meta": {
            "scenario": "conscious_mode",
            "duration": DURATION,
            "particle_count": N,
            "mothership_position": [0, 0],
            "awareness_radius": 20,
            "danger_radius": 10,
            "critical_radius": 5,
            "field_half_size": 25,
            "mode": "conscious",
            "note": "Choreographed (drone-style) demo. NOT relational AI. "
                    "Built as the contrast piece to the project's main thesis.",
        },
        "steps": [],
    }

    for step in range(1, DURATION + 1):
        particles = []
        for i in range(N):
            sx, sy, elev = position_at(i, step)
            particles.append({
                "id": i,
                "pos": [round(sx, 3), round(sy, 3), round(elev, 3)],  # 3D position
                "intent": phase_label(step),
                "target": None,
                "action": "move",
                "direction": None,
            })
        run["steps"].append({
            "step": step,
            "particles": particles,
            "threats": [],
            "mothership_states": ["M: " + phase_label(step)],
            "shield_coverage": 0.0,
        })

    return run


def main():
    out_dir = Path(__file__).parent / "output"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "conscious_demo.json"
    run = build_run()
    with open(out_path, "w") as f:
        json.dump(run, f, indent=2)
    print(f"✔ wrote {DURATION}-step conscious demo → {out_path}")
    print(f"  particles: {N}")
    print(f"  phases: orbit → dome → wall → wave → spiral → orbit")


if __name__ == "__main__":
    main()
