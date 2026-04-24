"""Entry point for swarm shield simulations.

Each run is persisted under saved_simulations/<timestamp>_<scenario>/ with:
  - spec.md              — tl;dr of what was tested and the key results
  - config_snapshot.yaml — exact config used
  - frames/              — per-step PNGs
  - *.jsonl / *.csv      — raw per-step logs
  - collective_metrics.json
  - statistics.png
"""
import argparse
import logging
import os
import shutil
import sys
from datetime import datetime
from typing import List

import yaml

from simulation import Simulation
from visualization import Visualizer, plot_summary
from utils import distance


SCENARIO_TLDR = {
    "shield_test": (
        "Baseline emergence test: 20 LLM particles orbit a mothership; a single threat "
        "approaches from the east. We measure whether particles spontaneously position "
        "between the threat and the mothership without being told to."
    ),
    "surround_test": (
        "Multi-vector test: 3 threats from different directions, staggered arrivals. "
        "Can the swarm split and cover multiple threat vectors simultaneously?"
    ),
    "multi_threat": (
        "Stress test: 30 particles vs 5 threats from random directions, staggered arrivals. "
        "Does the swarm show adaptive redistribution as the threat picture changes?"
    ),
    "scarcity_test": (
        "Ablation: shield_test with only 5 particles. Tests whether the attack-swarm behavior "
        "survives under scarcity, or whether it requires quorum."
    ),
    "decoy_test": (
        "Salience discrimination: two threats — one real (moves toward mothership), one decoy "
        "(stationary). Identical appearance. Do particles interpret trajectory to distinguish?"
    ),
    "pulse_test": (
        "Temporal interpretation: threat appears at step 4, disappears at step 15, reappears at "
        "step 25. No particle memory. Does the swarm disperse when the threat vanishes? Does it "
        "respond faster the second time?"
    ),
    "stealth_test": (
        "Information propagation: threat has a small detection_radius (particles only perceive "
        "it at close range). Mothership always sees it. Do distant particles respond to mothership "
        "state alone, and does awareness propagate through proximity?"
    ),
    "dual_mothership_test": (
        "Attention allocation: two motherships (A and B). Threat targets A only. Particles are "
        "generic guardians. Do they commit to the threatened one, split, or freeze?"
    ),
    "escape_test": (
        "Areal threat: a line of slow threats spanning the east edge of the field — a wave instead "
        "of a point. Does the swarm produce a line formation instead of a cluster?"
    ),
    "predator_prey_test": (
        "Adaptive adversary: threat moves toward the mothership AND steers away from particle "
        "clusters, probing for weak points. Does the swarm develop encirclement or get confused?"
    ),
}


def setup_logging(level: str = "INFO") -> logging.Logger:
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger("main")


def check_ollama(sim: Simulation, logger: logging.Logger) -> bool:
    if not sim.llm_client.check_connection():
        logger.error(f"Cannot connect to Ollama at {sim.llm_client.base_url}")
        return False
    if not sim.llm_client.check_model_exists():
        models = sim.llm_client.list_models()
        logger.error(f"Model '{sim.llm_client.model}' not found. Available: {models}")
        logger.error(f"Try: ollama pull {sim.llm_client.model}")
        return False
    logger.info(f"Using model: {sim.llm_client.model}")
    return True


def create_run_dir(scenario: str, label: str = "") -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    path = os.path.join("saved_simulations", f"{stamp}_{scenario}{suffix}")
    os.makedirs(path, exist_ok=True)
    os.makedirs(os.path.join(path, "frames"), exist_ok=True)
    return path


def write_spec(
    run_dir: str,
    scenario: str,
    config: dict,
    summary: dict,
    notes: str = "",
) -> None:
    tldr = SCENARIO_TLDR.get(scenario, "Custom swarm shield experiment.")
    breach = "YES" if summary.get("breached") else "NO"
    rt = summary.get("response_time_steps")
    rt_txt = f"{rt} steps after first threat" if rt is not None else "never reached 0.3 coverage"

    lines = [
        f"# Swarm Shield — {scenario}",
        f"_Run: {os.path.basename(run_dir)}_",
        "",
        "## TL;DR",
        tldr,
        "",
        "## Research question",
        "Can a swarm of LLM particles that interpret local situations spontaneously produce "
        "collective shielding behaviors never explicitly programmed?",
        "",
        "## What was tested",
        f"- Scenario: **{scenario}**",
        f"- Particles: {summary.get('particle_count')}",
        f"- Duration: {summary.get('duration')} steps",
        f"- First threat appears at step: {summary.get('first_threat_start_step')}",
        f"- Model: `{config['llm']['model']}` (temp={config['llm'].get('temperature')})",
        "",
        "## Key results",
        f"- Breach: **{breach}**" + (f" (at step {summary['breach_step']})" if summary.get("breach_step") else ""),
        f"- Response time: {rt_txt}",
        f"- Max shield coverage: {summary.get('max_shield_coverage', 0):.2f}",
        f"- Avg shield coverage (post-threat): {summary.get('avg_shield_coverage_post_threat', 0):.2f}",
        f"- Avg cohesion (mean nearest-neighbor distance): {summary.get('avg_cohesion', 0):.2f}",
        f"- Final intent distribution: {summary.get('final_intent_distribution', {})}",
        "",
        "## Success bands",
        "- **Weak:** coverage rises to 0.2–0.3, particles drift toward threat side.",
        "- **Strong:** coverage > 0.4, clear clustering between threat and mothership.",
        "- **Failure:** coverage stays near baseline; particles ignore threat.",
        "",
        "## Files",
        "- `config_snapshot.yaml` — exact config used",
        "- `particle_positions.jsonl` / `particle_intents.jsonl` — per-step raw",
        "- `threat_positions.jsonl` / `mothership_state.jsonl`",
        "- `shield_coverage.csv` / `angular_distribution.csv`",
        "- `collective_metrics.json` — summary metrics",
        "- `frames/frame_XXXX.png` — visualizations",
        "- `statistics.png` — summary plots",
    ]
    if notes:
        lines += ["", "## Notes", notes]

    with open(os.path.join(run_dir, "spec.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Swarm shield simulation — LLM particles defending a mothership.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--scenario", default=None,
                        help="Override scenario (must match a key under scenarios: in config.yaml)")
    parser.add_argument("--label", default="", help="Optional label appended to run directory name")
    parser.add_argument("--notes", default="", help="Free-form notes appended to spec.md")
    parser.add_argument("--no-frames", action="store_true", help="Skip saving per-step PNGs")
    parser.add_argument("--frame-interval", type=int, default=1)
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)
    logger = setup_logging(raw_config.get("logging", {}).get("level", "INFO"))

    scenario = args.scenario or raw_config["simulation"].get("scenario", "shield_test")
    run_dir = create_run_dir(scenario, args.label)
    logger.info(f"Run directory: {run_dir}")

    # Snapshot config
    shutil.copy(args.config, os.path.join(run_dir, "config_snapshot.yaml"))

    sim = Simulation(config_path=args.config, output_dir=run_dir, scenario_override=scenario)
    if not check_ollama(sim, logger):
        sys.exit(1)
    sim.initialize_particles()

    viz = None
    if not args.no_frames:
        viz = Visualizer(
            half_space_size=sim.half_space_size,
            show_perception_radius=raw_config.get("visualization", {}).get("show_perception_radius", False),
        )

    threat_distance_series: List[float] = []

    try:
        while sim.step < sim.duration:
            sim.step_simulation()
            primary = sim.motherships[0]
            nearest = primary.nearest_threat(sim.threats)
            threat_distance_series.append(distance(primary.position, nearest.position) if nearest else 0.0)

            if viz and (sim.step % args.frame_interval == 0 or sim.step == sim.duration):
                state_summary = " | ".join(f"{m.name}: {m.last_state}" for m in sim.motherships)
                frame_path = os.path.join(run_dir, "frames", f"frame_{sim.step:04d}.png")
                viz.render_step(
                    step=sim.step,
                    motherships=sim.motherships,
                    particles=sim.particles,
                    threats=sim.threats,
                    mothership_state=state_summary,
                    shield_cov_series=sim.metrics["shield_coverage"],
                    sector_counts=sim.metrics["sector_counts"][-1],
                    intent_dist=sim.metrics["intent_dist"][-1],
                    threat_distance_series=threat_distance_series,
                    save_path=frame_path,
                )
        logger.info("Simulation completed")
    except KeyboardInterrupt:
        logger.info("Interrupted by user — finalizing partial run")
    finally:
        summary = sim.finalize_metrics()
        plot_summary(run_dir, sim.metrics, threat_distance_series)
        write_spec(run_dir, scenario, raw_config, summary, notes=args.notes)
        sim.close()

    logger.info(f"Saved run to: {run_dir}")
    logger.info(f"Summary: {summary}")


if __name__ == "__main__":
    main()
