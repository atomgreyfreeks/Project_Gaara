#!/usr/bin/env python3
"""Per-run analysis for the LLM Body Language scripted scenario.

Reads a run directory and computes:
  - response_time_v1: step at which mean urgency first crosses 0.5 after step 5
  - interception_score: fraction of (cluster, step) samples during incursion
    phases where the cluster lies within `intercept_radius` of the segment
    between Mother and the active attacker (during steps 5-50)
  - intent_diversity: stdev of urgency and hostility across clusters per step,
    averaged over the run
  - awareness_flips: dict of attacker_name -> step at which exact coords were
    first revealed (or None if never flipped)
  - final_distribution: % clusters within 5 units of Mother at end

Appends a 6-line entry to RUNS_LOG.md and writes per-run analysis.json.

Usage:
  python3 analyze_run.py <run_dir> [--log RUNS_LOG.md]
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def read_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    return [json.loads(l) for l in path.open() if l.strip()]


def point_to_segment_dist(p, a, b) -> float:
    ax, ay = a; bx, by = b; px, py = p
    dx, dy = bx - ax, by - ay
    seg_len_sq = dx * dx + dy * dy
    if seg_len_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / seg_len_sq))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def analyze(run_dir: Path, intercept_radius: float = 2.0) -> Dict:
    positions = read_jsonl(run_dir / "cluster_positions.jsonl")
    intents = read_jsonl(run_dir / "cluster_intents.jsonl")
    attackers_path = run_dir / "attackers.jsonl"
    attackers = read_jsonl(attackers_path) if attackers_path.exists() else []
    metrics = json.loads((run_dir / "collective_metrics.json").read_text())

    # Mother position from config_snapshot.yaml — assume (0, 0) for our runs.
    m_pos = (0.0, 0.0)

    # Mean urgency per step.
    mean_urg_per_step: Dict[int, float] = {}
    urg_stdev_per_step: List[float] = []
    host_stdev_per_step: List[float] = []
    for entry in intents:
        urgs = [it["urgency"] for it in entry["intents"]]
        hosts = [it["hostility"] for it in entry["intents"]]
        mean_urg_per_step[entry["step"]] = sum(urgs) / max(1, len(urgs))
        if len(urgs) > 1:
            urg_stdev_per_step.append(statistics.stdev(urgs))
            host_stdev_per_step.append(statistics.stdev(hosts))

    # Response time v1 — first step >= 5 where mean urgency >= 0.5.
    response_step = None
    for s, u in mean_urg_per_step.items():
        if s >= 5 and u >= 0.5:
            response_step = s
            break

    # Awareness flips.
    flips: Dict[str, Optional[int]] = {}
    for entry in attackers:
        for atk in entry["attackers"]:
            name = atk["name"]
            if atk["revealed"] and name not in flips:
                flips[name] = entry["step"]
    # Fill in attackers that never flipped.
    if attackers:
        all_names = {atk["name"] for atk in attackers[0]["attackers"]}
        for n in all_names:
            flips.setdefault(n, None)

    # Interception score during incursion phases (steps 5-50).
    pos_by_step = {e["step"]: e["positions"] for e in positions}
    atk_by_step = {e["step"]: e["attackers"] for e in attackers}
    samples_total = 0
    samples_intercepting = 0
    for s in range(5, 51):
        if s not in pos_by_step or s not in atk_by_step:
            continue
        active = [a for a in atk_by_step[s] if a.get("active")]
        if not active:
            continue
        for cpos in pos_by_step[s]:
            cp = (cpos[0], cpos[1])
            for a in active:
                ap = (a["position"][0], a["position"][1])
                d_seg = point_to_segment_dist(cp, m_pos, ap)
                samples_total += 1
                if d_seg <= intercept_radius:
                    samples_intercepting += 1
                    break  # count once per (cluster, step)
    intercept = (samples_intercepting / samples_total) if samples_total else 0.0

    # Final distribution.
    final = positions[-1]["positions"] if positions else []
    final_close = sum(
        1 for p in final if math.hypot(p[0], p[1]) <= 5.0
    ) / max(1, len(final))

    # Pre-flip / post-flip mean ideal_coord.x — the critical diagnostic for
    # whether particles directionally respond to Mother's broadcast BEFORE
    # exact attacker coordinates are revealed. East attacker is the first
    # threat; flip step is when "east" appears in `flips`.
    east_flip = flips.get("east")
    pre_flip_xs: list = []
    post_flip_xs: list = []
    pre_flip_steps_observed = 0
    post_flip_steps_observed = 0
    for entry in intents:
        s = entry["step"]
        # Only count steps from the start of the faint phase (first time the
        # broadcast carries a directional cue) onward.
        # For scripted_70: faint starts step 7. For scripted_100: step 9.
        # Use a generic: any step after step 5 should have direction language.
        if s < 5:
            continue
        avg_x = (sum(it["ideal_coord"][0] for it in entry["intents"])
                 / max(1, len(entry["intents"])))
        if east_flip is None or s < east_flip:
            pre_flip_xs.append(avg_x)
            pre_flip_steps_observed += 1
        else:
            post_flip_xs.append(avg_x)
            post_flip_steps_observed += 1

    pre_flip_mean = (statistics.mean(pre_flip_xs) if pre_flip_xs else 0.0)
    post_flip_mean = (statistics.mean(post_flip_xs) if post_flip_xs else 0.0)

    return {
        "run_dir": str(run_dir),
        "scenario": metrics.get("scenario"),
        "dna_variant": metrics.get("dna_variant", "V1"),
        "mother_variant": metrics.get("mother_variant", "M1"),
        "seed": metrics.get("seed"),
        "duration": metrics.get("duration"),
        "cluster_count": metrics.get("cluster_count"),
        "response_time_v1": response_step,
        "interception_score": round(intercept, 3),
        "urgency_stdev_mean": round(statistics.mean(urg_stdev_per_step), 3) if urg_stdev_per_step else 0.0,
        "hostility_stdev_mean": round(statistics.mean(host_stdev_per_step), 3) if host_stdev_per_step else 0.0,
        "awareness_flips": flips,
        "final_within_5_units_pct": round(final_close * 100, 1),
        "mean_distance_overall": round(metrics.get("mean_distance_overall", 0), 2),
        "mean_urgency_overall": round(metrics.get("mean_urgency_overall", 0), 3),
        "mean_hostility_overall": round(metrics.get("mean_hostility_overall", 0), 3),
        "pre_flip_mean_ideal_x": round(pre_flip_mean, 3),
        "post_flip_mean_ideal_x": round(post_flip_mean, 3),
        "pre_flip_steps_observed": pre_flip_steps_observed,
        "post_flip_steps_observed": post_flip_steps_observed,
    }


def append_log(log_path: Path, a: Dict) -> None:
    """Append a structured per-run entry."""
    flips_str = ", ".join(
        f"{name}@{step if step is not None else 'never'}"
        for name, step in a["awareness_flips"].items()
    ) or "(no attackers)"
    line = (
        f"\n## {Path(a['run_dir']).name} — DNA {a['dna_variant']} · Mother {a.get('mother_variant', 'M1')} · seed {a['seed']}\n"
        f"- scenario: {a['scenario']} · duration {a['duration']}\n"
        f"- response_time (urg≥0.5): {a['response_time_v1']}\n"
        f"- interception_score (≤2 of M↔attacker line): {a['interception_score']}\n"
        f"- pre_flip_mean_ideal_x: **{a['pre_flip_mean_ideal_x']}** ({a['pre_flip_steps_observed']} steps)  ·  post_flip: {a['post_flip_mean_ideal_x']} ({a['post_flip_steps_observed']} steps)\n"
        f"- urg σ {a['urgency_stdev_mean']}  ·  host σ {a['hostility_stdev_mean']}\n"
        f"- awareness flips: {flips_str}\n"
        f"- final % within 5 of Mother: {a['final_within_5_units_pct']}%\n"
        f"- aggregates: d̄={a['mean_distance_overall']} ū={a['mean_urgency_overall']} h̄={a['mean_hostility_overall']}\n"
    )
    with log_path.open("a") as f:
        f.write(line)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--log", type=Path, default=Path("RUNS_LOG.md"))
    args = ap.parse_args()

    if not args.run_dir.is_dir():
        raise SystemExit(f"not a directory: {args.run_dir}")

    a = analyze(args.run_dir)
    (args.run_dir / "analysis.json").write_text(json.dumps(a, indent=2))
    append_log(args.log, a)
    print(json.dumps(a, indent=2))


if __name__ == "__main__":
    main()
