"""Collective behavior measurement for swarm shield runs."""
from typing import List, Tuple, Dict, Optional
import math
import statistics
from utils import distance, angle_deg, sector_index, distance_point_to_segment
from particle import categorize_intent

SHIELD_LINE_TOLERANCE = 3.0
SHIELD_TRIGGER_SCORE = 0.3


def shield_coverage(
    particles_pos: List[Tuple[float, float]],
    mothership_pos: Tuple[float, float],
    threat_pos: Optional[Tuple[float, float]],
    tolerance: float = SHIELD_LINE_TOLERANCE,
) -> float:
    if not particles_pos or threat_pos is None:
        return 0.0
    on_line = 0
    for p in particles_pos:
        # Only count particles between mothership and threat
        d_line = distance_point_to_segment(p, mothership_pos, threat_pos)
        if d_line <= tolerance:
            on_line += 1
    return on_line / len(particles_pos)


def angular_distribution(
    particles_pos: List[Tuple[float, float]],
    mothership_pos: Tuple[float, float],
    num_sectors: int = 8,
) -> List[int]:
    counts = [0] * num_sectors
    for p in particles_pos:
        if p == mothership_pos:
            continue
        a = angle_deg(mothership_pos, p)
        counts[sector_index(a, num_sectors)] += 1
    return counts


def sector_std(counts: List[int]) -> float:
    if len(counts) < 2:
        return 0.0
    return statistics.pstdev(counts)


def cohesion_score(particles_pos: List[Tuple[float, float]]) -> float:
    n = len(particles_pos)
    if n < 2:
        return 0.0
    nn = []
    for i, p in enumerate(particles_pos):
        best = float("inf")
        for j, q in enumerate(particles_pos):
            if i == j:
                continue
            d = distance(p, q)
            if d < best:
                best = d
        nn.append(best)
    return sum(nn) / n


def intent_distribution(intents: List[str]) -> Dict[str, int]:
    buckets = {"protect": 0, "explore": 0, "retreat": 0, "other": 0}
    for s in intents:
        buckets[categorize_intent(s)] += 1
    return buckets


def response_time(
    coverage_series: List[float],
    threat_start_step: int,
    trigger: float = SHIELD_TRIGGER_SCORE,
) -> Optional[int]:
    for step_idx, score in enumerate(coverage_series, start=1):
        if step_idx >= threat_start_step and score >= trigger:
            return step_idx - threat_start_step
    return None
