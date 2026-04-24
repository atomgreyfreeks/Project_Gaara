"""Geometry helpers for the swarm shield simulation."""
import math
from typing import Tuple


def distance(a: Tuple[float, float], b: Tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def angle_deg(origin: Tuple[float, float], point: Tuple[float, float]) -> float:
    """Angle from origin to point in degrees, 0..360 (0 = +x axis, CCW)."""
    dx = point[0] - origin[0]
    dy = point[1] - origin[1]
    ang = math.degrees(math.atan2(dy, dx))
    return ang % 360.0


def sector_index(angle: float, num_sectors: int = 8) -> int:
    sector_size = 360.0 / num_sectors
    return int(angle // sector_size) % num_sectors


def distance_point_to_segment(
    p: Tuple[float, float],
    a: Tuple[float, float],
    b: Tuple[float, float],
) -> float:
    """Perpendicular distance from p to segment a-b (clamped to segment)."""
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def move_toward(
    pos: Tuple[float, float],
    target: Tuple[float, float],
    speed: float,
) -> Tuple[float, float]:
    dx = target[0] - pos[0]
    dy = target[1] - pos[1]
    dist = math.hypot(dx, dy)
    if dist <= speed or dist == 0:
        return target
    return (pos[0] + dx / dist * speed, pos[1] + dy / dist * speed)


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
