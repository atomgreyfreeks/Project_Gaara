#!/usr/bin/env python3
"""Choreographed conscious-mode demo for Project Gaara.

This is the OPPOSITE of the project's main thesis. Particles are moved imperatively
each step — drone-style — to form specific shapes (dome, wall, wave, spiral).
Built as the contrast piece so the relational simulations can be felt by comparison.

Phases (130 steps, ~26 seconds at default playback):
   1– 12   orbit                    calm starting state
  13– 20   gather to cluster        regather
  21– 30   cluster → tent dome      tight protective shelter over the Mothership
  31– 40   dome held                admire
  41– 48   dome → cluster           regather
  49– 58   cluster → ground line    particles fall to the base of the wave wall
  59– 82   wave wall climbs         sand climbs row by row, leaning forward like a breaking wave
  83– 90   wall → cluster           regather
  91–100   cluster → spiral         tightening vertical spiral
 101–110   spiral held              admire
 111–118   spiral → cluster         regather
 119–130   cluster → orbit          return

Every formation is preceded by a cluster reset. The wave wall is staggered:
bottom rows rise first, top rows last, so the wall visibly climbs from the ground.
"""
import json
import math
from pathlib import Path

GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))
N = 35                      # 7 cols × 5 rows for the wall, fibonacci elsewhere
DURATION = 130

ORBIT_R = 8.0
DOME_R = 4.5                # tighter — tent-like
CLUSTER_R = 1.6             # tight ball
CLUSTER_CENTER = (0.0, 0.0, 3.5)

WALL_COLS, WALL_ROWS = 7, 5  # 7 × 5 = 35
WALL_BASE_X = 8.5
WALL_LEAN = 0.55             # each row leans this much toward the Mothership
WALL_W_SPACING = 1.7
WALL_H_SPACING = 1.4

SPIRAL_TURNS = 2.5
SPIRAL_TOP_R = 0.6
SPIRAL_BOT_R = 3.5
SPIRAL_HEIGHT = 7.5


# ─── Shape generators ──────────────────────────────────────────────────────


def shape_orbit(i, n=N, R=ORBIT_R):
    angle = 2 * math.pi * i / n + math.pi / 6
    return (R * math.cos(angle), R * math.sin(angle), 0.5)


def shape_cluster(i, n=N, R=CLUSTER_R, center=CLUSTER_CENTER):
    """Tight Fibonacci ball — used to reset between formations."""
    y_norm = 1 - 2 * (i + 0.5) / n
    y = R * y_norm
    radius = R * math.sqrt(max(0.0, 1.0 - y_norm * y_norm))
    phi = GOLDEN_ANGLE * i
    return (center[0] + radius * math.cos(phi),
            center[1] + radius * math.sin(phi),
            center[2] + y)


def shape_dome(i, n=N, R=DOME_R):
    """Tent-style dome — tight Fibonacci hemisphere over the Mothership."""
    y_norm = (i + 0.5) / n
    elev = R * y_norm
    radius = R * math.sqrt(max(0.0, 1.0 - y_norm * y_norm))
    phi = GOLDEN_ANGLE * i
    return (radius * math.cos(phi), radius * math.sin(phi), elev)


def _wall_target(i):
    """The wave wall's final position for particle i — angled, with a sine wave along width."""
    col = i % WALL_COLS
    row = i // WALL_COLS
    sim_y = (col - (WALL_COLS - 1) / 2) * WALL_W_SPACING
    target_elev = row * WALL_H_SPACING + 0.6
    # Wall leans forward (toward Mothership) as it rises; top rows curl slightly more.
    lean_total = row * WALL_LEAN + (row * row) * 0.04
    sim_x = WALL_BASE_X - lean_total
    # Wave undulation along width — adds a leaning forward sway near the top of the wall.
    wave = 0.7 * math.sin(sim_y * 0.45) * (row / max(1, WALL_ROWS - 1))
    sim_x += wave
    return (sim_x, sim_y, target_elev)


def shape_wall_at_ground(i, n=N):
    """The wall's footprint — particles sit on the ground at their final x,y, elev=0."""
    sx, sy, _ = _wall_target(i)
    return (sx, sy, 0.05)


def shape_wave_wall_climb(i, t):
    """Self-animating phase: particles climb from ground to their wall positions,
    staggered by row so the wave visibly forms from the bottom up."""
    target_x, target_y, target_z = _wall_target(i)
    row = i // WALL_COLS
    # Each row starts climbing at fraction (row / rows) of total time and takes
    # ~50% of total time to finish. Overlapping windows produce continuous climb.
    row_start = row / WALL_ROWS
    row_window = 0.55
    local = (t - row_start) / row_window
    local = max(0.0, min(1.0, local))
    eased = 1 - pow(1 - local, 3)  # ease-out cubic
    # Slight horizontal shake during climb (sand granular feel)
    shake = 0.05 * math.sin(t * 12 + i * 0.7) * (1 - eased) * eased
    return (target_x + shake, target_y, target_z * eased)


def shape_wave_wall_full(i, t=1.0):
    """Wall fully formed — passes t for the wave undulation phase."""
    return _wall_target(i)


def shape_spiral(i, n=N, t=0):
    """Vertical spiral funneling around the Mothership."""
    layer = i / max(1, n - 1)
    angle = 2 * math.pi * SPIRAL_TURNS * layer + t * 0.25
    elev = layer * SPIRAL_HEIGHT + 0.3
    radius = SPIRAL_BOT_R + (SPIRAL_TOP_R - SPIRAL_BOT_R) * layer
    return (radius * math.cos(angle), radius * math.sin(angle), elev)


# ─── Phase machine ──────────────────────────────────────────────────────────
#
# Each phase is one of:
#   ("lerp", start, end, fn_a, fn_b)        — interpolate from fn_a → fn_b
#   ("evolve", start, end, fn_evolve)       — fn_evolve(i, local_t) drives motion


PHASES = [
    ("lerp",   1,  12, shape_orbit, shape_orbit),                           # hold orbit
    ("lerp",  13,  20, shape_orbit, shape_cluster),                         # gather
    ("lerp",  21,  30, shape_cluster, shape_dome),                          # cluster → tent dome
    ("lerp",  31,  40, shape_dome, shape_dome),                             # dome held
    ("lerp",  41,  48, shape_dome, shape_cluster),                          # dome → cluster
    ("lerp",  49,  58, shape_cluster, shape_wall_at_ground),                # cluster → ground line
    ("evolve", 59, 82, shape_wave_wall_climb),                              # wave wall climbs
    ("lerp",  83,  90, shape_wave_wall_full, shape_cluster),                # wall → cluster
    ("lerp",  91, 100, shape_cluster, shape_spiral),                        # cluster → spiral
    ("lerp", 101, 110, shape_spiral, shape_spiral),                         # spiral held
    ("lerp", 111, 118, shape_spiral, shape_cluster),                        # spiral → cluster
    ("lerp", 119, 130, shape_cluster, shape_orbit),                         # cluster → orbit
]


def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def lerp3(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def position_at(i, step):
    for kind, s1, s2, *args in PHASES:
        if not (s1 <= step <= s2):
            continue
        local_t = (step - s1) / max(1, s2 - s1)
        if kind == "lerp":
            f1, f2 = args
            eased = ease_in_out_cubic(local_t)
            try:
                p1 = f1(i, step)
            except TypeError:
                p1 = f1(i)
            try:
                p2 = f2(i, step)
            except TypeError:
                p2 = f2(i)
            return lerp3(p1, p2, eased)
        if kind == "evolve":
            (fn,) = args
            return fn(i, local_t)
    return PHASES[-1][3](0)


# ─── Phase narration ───────────────────────────────────────────────────────


def phase_label(step):
    if step <= 12:
        return "calm. holding orbit."
    if step <= 20:
        return "gathering. pulling inward."
    if step <= 30:
        return "rising. forming the tent."
    if step <= 40:
        return "the dome is set. she is sheltered."
    if step <= 48:
        return "releasing. dispersing the dome."
    if step <= 58:
        return "settling. preparing the wall's base."
    if step <= 82:
        return "the wave climbs. sand piling on sand."
    if step <= 90:
        return "the wall falls. regathering."
    if step <= 100:
        return "tightening into the spiral."
    if step <= 110:
        return "the spiral holds."
    if step <= 118:
        return "spiral falls inward. regathering."
    return "dispersing. returning to orbit."


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
            "note": ("Choreographed (drone-style) demo. NOT relational AI. "
                     "Built as the contrast piece to the project's main thesis."),
        },
        "steps": [],
    }
    for step in range(1, DURATION + 1):
        particles = []
        for i in range(N):
            sx, sy, elev = position_at(i, step)
            particles.append({
                "id": i,
                "pos": [round(sx, 3), round(sy, 3), round(elev, 3)],
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
    print(f"  phases: orbit → cluster → tent → cluster → wave wall (climbs!) → cluster → spiral → cluster → orbit")


if __name__ == "__main__":
    main()
