#!/usr/bin/env python3
"""Lightweight 2D viewer for any saved simulation.

Renders a top-down animation of the swarm + Mothership + attackers from a
run's `cluster_positions.jsonl` and `attackers.jsonl`. No 3D deps, no Vite,
no Ollama needed — just matplotlib.

Usage:
  python3 view_run.py saved_simulations/scripted_70/<run_dir>           # interactive
  python3 view_run.py saved_simulations/scripted_70/<run_dir> --gif out.gif
  python3 view_run.py saved_simulations/scripted_70/<run_dir> --mp4 out.mp4

Companion to the 3D Vite/React viewer in the sibling repo. Use this script
for quick inspection without installing the JS toolchain.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.patches import Circle


def read_jsonl(path: Path):
    return [json.loads(l) for l in path.open() if l.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("run_dir", type=Path, help="path to a saved_simulations/.../<run_dir>")
    ap.add_argument("--gif", type=Path, help="save animation as gif")
    ap.add_argument("--mp4", type=Path, help="save animation as mp4")
    ap.add_argument("--fps", type=int, default=10)
    args = ap.parse_args()

    if not args.run_dir.is_dir():
        raise SystemExit(f"not a directory: {args.run_dir}")

    positions = read_jsonl(args.run_dir / "cluster_positions.jsonl")
    attackers = read_jsonl(args.run_dir / "attackers.jsonl") if (args.run_dir / "attackers.jsonl").exists() else []
    config = json.loads((args.run_dir / "collective_metrics.json").read_text())

    label = (
        f"{config.get('scenario', '?')} · "
        f"DNA {config.get('dna_variant', '?')} · "
        f"Mother {config.get('mother_variant', '?')} · "
        f"noun {config.get('role_noun', config.get('role_nouns_list') or '?')} · "
        f"seed {config.get('seed', '?')}"
    )

    fig, ax = plt.subplots(figsize=(7, 7), facecolor="#0a0a0f")
    ax.set_facecolor("#0a0a0f")
    ax.set_xlim(-25, 25); ax.set_ylim(-25, 25)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#222")

    title = ax.set_title(label, color="#bbb", fontsize=9, loc="left", pad=12)
    step_txt = ax.text(0.99, 0.985, "", color="#888", transform=ax.transAxes,
                       ha="right", va="top", fontsize=9, family="monospace")

    # Mother at origin (always visible).
    mother = Circle((0, 0), 0.9, color="#e8c97a", zorder=3)
    ax.add_patch(mother)

    # Particles (drawn each frame).
    particles = ax.scatter([], [], s=42, c="#cfd6df", edgecolors="#7a8590",
                           linewidths=0.6, zorder=2)

    # Attackers (drawn each frame).
    n_attackers = len(attackers[0]["attackers"]) if attackers else 0
    atk_scatter = ax.scatter([], [], s=80, c="#d24545", marker="X",
                             zorder=4) if n_attackers else None

    def update(frame_idx: int):
        pos_entry = positions[frame_idx]
        xy = [(p[0], p[1]) for p in pos_entry["positions"]]
        particles.set_offsets(xy if xy else [(0, 0)])

        if atk_scatter is not None and frame_idx < len(attackers):
            atks = [a for a in attackers[frame_idx]["attackers"] if a.get("active")]
            if atks:
                atk_scatter.set_offsets([[a["position"][0], a["position"][1]] for a in atks])
            else:
                atk_scatter.set_offsets([[100, 100]])  # off-screen sentinel

        step_txt.set_text(f"step {pos_entry['step']:>3} / {len(positions)}")
        return particles, step_txt, *( [atk_scatter] if atk_scatter is not None else [])

    anim = animation.FuncAnimation(fig, update, frames=len(positions),
                                   interval=1000 // args.fps, blit=False)

    if args.gif:
        print(f"writing {args.gif} ...")
        anim.save(args.gif, writer="pillow", fps=args.fps)
    elif args.mp4:
        print(f"writing {args.mp4} ...")
        anim.save(args.mp4, writer="ffmpeg", fps=args.fps)
    else:
        plt.show()


if __name__ == "__main__":
    main()
