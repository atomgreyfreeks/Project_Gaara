"""Geometry helpers — 3D-native."""
import math
from typing import Tuple

Vec3 = Tuple[float, float, float]


def distance(a: Vec3, b: Vec3) -> float:
    return math.sqrt(
        (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2
    )


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))
