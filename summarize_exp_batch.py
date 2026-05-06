#!/usr/bin/env python3
"""Morning-after summarizer for the exp_* batch.

Walks saved_simulations/scripted_30/, finds every run whose label starts
with "exp_", computes per-run metrics adapted to the 30-step pilot
schedule (east attacker active 3-30, north attacker active 20-30), and
prints a ranked table.

Metrics:
  intercept_30      — fraction of (cluster, step) samples within 2u of the
                      M↔active-attacker segment, over steps 5-30.
  pre_flip_x        — mean ideal_coord.x BEFORE east attacker is revealed
                      (or BEFORE the awareness flip, whichever earlier).
  early_y_north     — mean ideal_coord.y over steps 18-25 (the "did the
                      swarm turn north before north was visible?" diagnostic
                      adapted to the compressed 30-step protocol).
  follower_pct      — mean fraction of follower-mode reasonings.
  drone_sig_steps   — steps where 1-2 categories cover ≥80% of particles.
  cats_per_step     — mean # distinct categories per step.

The ranking uses interception_score as the primary key (the demo-video
criterion: which architecture protects best), with early_y_north as the
multi-direction tiebreaker.

Usage:
  python3 summarize_exp_batch.py
  python3 summarize_exp_batch.py --json    # full json dump
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
from pathlib import Path
from typing import Dict, List, Optional

from score_diversity import score_run as score_diversity_run


SAVED = Path("saved_simulations/scripted_30")


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


def analyze_30(run_dir: Path) -> Dict:
    positions = read_jsonl(run_dir / "cluster_positions.jsonl")
    intents = read_jsonl(run_dir / "cluster_intents.jsonl")
    attackers = read_jsonl(run_dir / "attackers.jsonl")
    metrics = json.loads((run_dir / "collective_metrics.json").read_text())

    m_pos = (0.0, 0.0)

    # Awareness flips.
    flips: Dict[str, Optional[int]] = {}
    for entry in attackers:
        for atk in entry["attackers"]:
            name = atk["name"]
            if atk["revealed"] and name not in flips:
                flips[name] = entry["step"]
    if attackers:
        for atk in attackers[0]["attackers"]:
            flips.setdefault(atk["name"], None)

    # Interception over scripted_30's incursion window.
    pos_by_step = {e["step"]: e["positions"] for e in positions}
    atk_by_step = {e["step"]: e["attackers"] for e in attackers}
    samples_total = 0
    samples_intercepting = 0
    for s in range(5, 31):
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
                if d_seg <= 2.0:
                    samples_intercepting += 1
                    break
    intercept = (samples_intercepting / samples_total) if samples_total else 0.0

    # Pre-flip mean ideal_x — directional response BEFORE attacker reveal.
    east_flip = flips.get("east")
    pre_flip_xs: list = []
    post_flip_xs: list = []
    for entry in intents:
        s = entry["step"]
        if s < 3:
            continue
        avg_x = (sum(it["ideal_coord"][0] for it in entry["intents"])
                 / max(1, len(entry["intents"])))
        if east_flip is None or s < east_flip:
            pre_flip_xs.append(avg_x)
        else:
            post_flip_xs.append(avg_x)

    pre_flip_x = statistics.mean(pre_flip_xs) if pre_flip_xs else 0.0
    post_flip_x = statistics.mean(post_flip_xs) if post_flip_xs else 0.0

    # Early_y for north — north attacker starts step 20 in scripted_30.
    # Window steps 18-25 captures pre-arrival turn (north arrives ~step 29).
    early_y_vals: list = []
    for entry in intents:
        if 18 <= entry["step"] <= 25:
            avg_y = (sum(it["ideal_coord"][1] for it in entry["intents"])
                     / max(1, len(entry["intents"])))
            early_y_vals.append(avg_y)
    early_y = statistics.mean(early_y_vals) if early_y_vals else 0.0

    # Final distribution.
    final = positions[-1]["positions"] if positions else []
    final_close = sum(1 for p in final if math.hypot(p[0], p[1]) <= 5.0) / max(1, len(final))

    return {
        "run_dir": str(run_dir),
        "label": run_dir.name,
        "dna_variant": metrics.get("dna_variant"),
        "mother_variant": metrics.get("mother_variant"),
        "role_noun": metrics.get("role_noun"),
        "role_nouns_list": metrics.get("role_nouns_list"),
        "say_prefix": metrics.get("say_prefix"),
        "awareness_range": metrics.get("awareness_range"),
        "intercept_30": round(intercept, 3),
        "pre_flip_x": round(pre_flip_x, 3),
        "post_flip_x": round(post_flip_x, 3),
        "early_y_north": round(early_y, 3),
        "final_within_5_pct": round(final_close * 100, 1),
        "awareness_flips": flips,
    }


def summarize_run(run_dir: Path) -> Dict:
    a = analyze_30(run_dir)
    try:
        d = score_diversity_run(run_dir)
    except SystemExit:
        d = {}
    a["follower_pct"] = round(d.get("category_mean_pct", {}).get("follower", 0.0) * 100, 1)
    a["drone_sig_steps"] = d.get("drone_signature_steps")
    a["interp_sig_steps"] = d.get("interp_signature_steps")
    a["cats_per_step"] = d.get("n_categories_mean")
    a["top_cat_pct"] = round(d.get("top_category_pct_mean", 0.0) * 100, 1)
    return a


def find_exp_runs() -> List[Path]:
    if not SAVED.exists():
        return []
    out = []
    for p in sorted(SAVED.iterdir()):
        # Skip runs that haven't finalized yet (no collective_metrics.json).
        if (p.is_dir() and "_exp_" in p.name
                and (p / "collective_metrics.json").exists()):
            out.append(p)
    return out


def render_table(rows: List[Dict]) -> str:
    rows = sorted(rows, key=lambda r: (-r["intercept_30"], -abs(r["early_y_north"])))
    headers = [
        ("rank",          4,  "{:>3}"),
        ("label",         24, "{:<22}"),
        ("DNA",           14, "{:<14}"),
        ("Mother",        12, "{:<12}"),
        ("noun",          18, "{:<18}"),
        ("aware",         6,  "{:>5}"),
        ("intercept",     10, "{:>9.3f}"),
        ("pre_x",         8,  "{:>+7.2f}"),
        ("early_y",       9,  "{:>+8.2f}"),
        ("foll%",         7,  "{:>6.1f}"),
        ("drone",         7,  "{:>6}"),
        ("cats",          6,  "{:>5.2f}"),
    ]
    head = "  ".join(f"{h[0]:<{h[1]}}" for h in headers)
    sep = "  ".join("-" * h[1] for h in headers)
    lines = [head, sep]
    for i, r in enumerate(rows, 1):
        noun_label = ",".join(r["role_nouns_list"]) if r["role_nouns_list"] else (r["role_noun"] or "—")
        cells = [
            f"{i:>3}",
            f"{r['label'][:22]:<22}",
            f"{(r['dna_variant'] or ''):<14}",
            f"{(r['mother_variant'] or ''):<12}",
            f"{noun_label[:18]:<18}",
            f"{r['awareness_range']:>5}",
            f"{r['intercept_30']:>9.3f}",
            f"{r['pre_flip_x']:>+7.2f}",
            f"{r['early_y_north']:>+8.2f}",
            f"{r['follower_pct']:>6.1f}",
            f"{(str(r['drone_sig_steps']) + '/30'):>6}",
            f"{r['cats_per_step']:>5.2f}",
        ]
        lines.append("  ".join(cells))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    runs = find_exp_runs()
    if not runs:
        print("No exp_* runs found in saved_simulations/scripted_30/")
        return
    rows = [summarize_run(p) for p in runs]
    if args.json:
        print(json.dumps(rows, indent=2))
        return
    print(render_table(rows))
    print()
    print(f"Total exp_* runs: {len(rows)}")


if __name__ == "__main__":
    main()
