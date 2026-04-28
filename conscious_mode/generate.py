#!/usr/bin/env python3
"""Choreographed conscious-mode demo for Project Gaara — story-driven version.

Drone-style choreography. Particles are commanded each step. Built as the
contrast piece to the project's relational architecture.

THE STORY (160 steps, ~32 seconds at default speed)
─────────────────────────────────────────────────────
ACT I — Four threats force the dome
   1 –  15  orbit                  calm starting state
  16 –  23  threats appear         four shards approach from N, S, E, W
  24 –  32  gather to cluster      sand pulls inward, sensing pressure
  33 –  50  cluster → tent dome    a hemispherical shelter rises tightly
                                   over the Mothership
  51 –  58  dome holds; threats    they reach the dome's edge and dissolve
            blocked
  59 –  65  dome → cluster         protective form releases

ACT II — One threat forces the wave wall
  66 –  72  breathing              calm pause, cluster held
  73 –  80  one threat appears     from the east
  81 –  88  cluster → ground line  sand falls to the wall's footprint
  89 – 110  wave wall climbs       sand piles on sand, rising row by row
                                   in a continuous wave; slope faces the
                                   Mothership, peak faces the threat
 111 – 118  threat hits wall;      blocked
            held
 119 – 125  wall → cluster

ACT III — Recapitulation
 126 – 132  breathing
 133 – 140  cluster → spiral
 141 – 145  spiral holds
 146 – 150  spiral → cluster
 151 – 160  cluster → orbit
"""
import json
import math
from pathlib import Path

GOLDEN_ANGLE = math.pi * (3.0 - math.sqrt(5.0))
N = 35
DURATION = 160

ORBIT_R = 8.0
DOME_R = 4.5
CLUSTER_R = 1.6
CLUSTER_CENTER = (0.0, 0.0, 3.5)

# WALL: slope rises from BASE (close to Mothership) upward and OUTWARD (toward threats).
# Visualize: looking from the Mothership, you see a ramp. The peak is far from her,
# facing the incoming threat. The threat's side of the wall is a vertical drop.
WALL_COLS, WALL_ROWS = 7, 5             # 7 × 5 = 35
WALL_BASE_X = 4.0                       # base near Mothership
WALL_LEAN = 0.95                        # each row extends this much further toward threats
WALL_W_SPACING = 1.7
WALL_H_SPACING = 1.45

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
    """Final wave-wall position. Slope rises from Mothership-side base outward.

    Row 0 (lowest, closest to Mothership) is at base x.
    Row 4 (highest, furthest) is far x — peak faces incoming threat.
    """
    col = i % WALL_COLS
    row = i // WALL_COLS
    sim_y = (col - (WALL_COLS - 1) / 2) * WALL_W_SPACING
    target_elev = row * WALL_H_SPACING + 0.6
    # Slope: x INCREASES with row, with slight extra extension at the top to suggest curl
    extension = row * WALL_LEAN + (row * row) * 0.05
    sim_x = WALL_BASE_X + extension
    # Sine undulation along the wall's width — increases with elevation so the top has more wave
    wave = 0.55 * math.sin(sim_y * 0.45) * (row / max(1, WALL_ROWS - 1))
    sim_x += wave
    return (sim_x, sim_y, target_elev)


def shape_wall_at_ground(i, n=N):
    """The wall's footprint — sand has landed at the base, not yet climbed."""
    sx, sy, _ = _wall_target(i)
    return (sx, sy, 0.05)


def _ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    return 1 - pow(-2 * t + 2, 3) / 2


def shape_wave_wall_climb(i, t):
    """Smooth row-by-row climb. Overlapping windows + ease-in-out so motion is continuous."""
    target_x, target_y, target_z = _wall_target(i)
    row = i // WALL_COLS
    col = i % WALL_COLS
    # Each row's climb starts at row/(rows+1) of total time. Window is wider than the
    # spacing between rows, so neighboring rows are climbing simultaneously near the
    # middle of the phase — eliminates the "step ladder" feel.
    row_start = row / (WALL_ROWS + 0.5)
    duration = 0.55
    # Tiny per-particle start jitter from the column index — keeps within-row motion
    # from being perfectly synchronous (granular feel).
    col_jitter = (col / WALL_COLS - 0.5) * 0.04
    local = (t - row_start - col_jitter) / duration
    local = max(0.0, min(1.0, local))
    eased = _ease_in_out_cubic(local)
    elev = target_z * eased
    return (target_x, target_y, elev)


def shape_wave_wall_full(i, t=1.0):
    return _wall_target(i)


def shape_spiral(i, n=N, t=0):
    layer = i / max(1, n - 1)
    angle = 2 * math.pi * SPIRAL_TURNS * layer + t * 0.25
    elev = layer * SPIRAL_HEIGHT + 0.3
    radius = SPIRAL_BOT_R + (SPIRAL_TOP_R - SPIRAL_BOT_R) * layer
    return (radius * math.cos(angle), radius * math.sin(angle), elev)


# ─── Phase schedule ────────────────────────────────────────────────────────


PHASES = [
    ("lerp",   1,  15, shape_orbit, shape_orbit),                           # orbit (calm)
    ("lerp",  16,  23, shape_orbit, shape_orbit),                           # orbit (threats appear; particles still calm)
    ("lerp",  24,  32, shape_orbit, shape_cluster),                         # gather to cluster
    ("lerp",  33,  50, shape_cluster, shape_dome),                          # cluster → dome
    ("lerp",  51,  58, shape_dome, shape_dome),                             # dome holds; threats blocked
    ("lerp",  59,  65, shape_dome, shape_cluster),                          # dome → cluster
    ("lerp",  66,  72, shape_cluster, shape_cluster),                       # breathing
    ("lerp",  73,  80, shape_cluster, shape_cluster),                       # threat appears (cluster holds)
    ("lerp",  81,  88, shape_cluster, shape_wall_at_ground),                # cluster → ground footprint
    ("evolve", 89, 110, shape_wave_wall_climb),                             # wave wall climbs
    ("lerp", 111, 118, shape_wave_wall_full, shape_wave_wall_full),         # wall held; threat blocked
    ("lerp", 119, 125, shape_wave_wall_full, shape_cluster),                # wall → cluster
    ("lerp", 126, 132, shape_cluster, shape_cluster),                       # breathing
    ("lerp", 133, 140, shape_cluster, shape_spiral),                        # cluster → spiral
    ("lerp", 141, 145, shape_spiral, shape_spiral),                         # spiral holds
    ("lerp", 146, 150, shape_spiral, shape_cluster),                        # spiral → cluster
    ("lerp", 151, 160, shape_cluster, shape_orbit),                         # cluster → orbit
]


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
            eased = _ease_in_out_cubic(local_t)
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


# ─── Threat schedule ───────────────────────────────────────────────────────


def _interp_threat(start_pos, end_pos, t):
    return [start_pos[0] + (end_pos[0] - start_pos[0]) * t,
            start_pos[1] + (end_pos[1] - start_pos[1]) * t]


def threats_at_step(step):
    """Choreographed threat trajectories that motivate each formation."""
    threats = []

    # ACT I — four threats from N/S/E/W (steps 16-58)
    # They appear at distance 12, approach to distance ~5 (just outside dome edge),
    # then deactivate to suggest they were "blocked" by the dome.
    if 16 <= step <= 58:
        elapsed = step - 16
        # Travel from distance 12 to distance 5 over ~35 steps
        progress = min(1.0, elapsed / 35.0)
        approach_factor = progress  # linear
        for name, far_pos in [("threat_N", (0, 12)), ("threat_S", (0, -12)),
                              ("threat_E", (12, 0)), ("threat_W", (-12, 0))]:
            # Interpolate from far_pos to a point at distance 5 from origin
            dx, dy = -far_pos[0], -far_pos[1]
            dist = math.hypot(dx, dy)
            stop_at_dist = 5.0
            move_dist = (dist - stop_at_dist) * approach_factor
            ux, uy = dx / dist, dy / dist
            pos = [far_pos[0] + ux * move_dist, far_pos[1] + uy * move_dist]
            # Active until step 51 (dome forms by then). After that, deactivate.
            active = step <= 51
            threats.append({"name": name, "pos": pos, "active": active, "breached": False})

    # ACT II — single threat from east (steps 73-118)
    if 73 <= step <= 118:
        elapsed = step - 73
        progress = min(1.0, elapsed / 38.0)
        far_pos = (15, 4)
        # Stops at the wall's far edge (where the peak is, around x=8.5)
        stop_pos = (8.5, 1.0)
        pos = _interp_threat(far_pos, stop_pos, progress)
        active = step <= 113  # wall fully formed by step 110
        threats.append({"name": "wave_threat", "pos": pos, "active": active, "breached": False})

    return threats


# ─── Phase narration ───────────────────────────────────────────────────────


def phase_label(step):
    if step <= 15:
        return "calm. holding orbit."
    if step <= 23:
        return "presence. four threats appear."
    if step <= 32:
        return "gathering. pulling inward."
    if step <= 50:
        return "rising. forming the tent."
    if step <= 58:
        return "the dome is set. she is sheltered."
    if step <= 65:
        return "releasing. dispersing the dome."
    if step <= 72:
        return "stillness."
    if step <= 80:
        return "presence from the east."
    if step <= 88:
        return "settling. preparing the wall's base."
    if step <= 110:
        return "the wave climbs. sand piling on sand."
    if step <= 118:
        return "the wall holds. blocked."
    if step <= 125:
        return "regathering."
    if step <= 132:
        return "stillness."
    if step <= 140:
        return "tightening into the spiral."
    if step <= 145:
        return "the spiral holds."
    if step <= 150:
        return "spiral falls inward."
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
            "note": ("Story-driven choreographed demo. Threats trigger formations. "
                     "NOT relational AI — this is the contrast piece."),
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
            "threats": threats_at_step(step),
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
    print(f"✔ wrote {DURATION}-step story-driven conscious demo → {out_path}")
    print(f"  particles: {N}")
    print(f"  acts: I (4 threats → dome) → breathing → II (1 threat → wave wall) → III (spiral) → orbit")


if __name__ == "__main__":
    main()
