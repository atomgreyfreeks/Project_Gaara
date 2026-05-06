"""Entry point for Project Gaara — Technology Animism resonance runs.

Each run lands in saved_simulations/<scenario>/<timestamp>_<label>/ with:
    config_snapshot.yaml
    cluster_positions.jsonl   3D positions + velocities per step
    cluster_params.jsonl      attraction/viscosity/agitation/color_temp per step
    mother_state.jsonl        Mother's broadcast + interior fields per step
    collective_metrics.json   summary metrics
    spec.md                   one-line tl;dr + key numbers

Visualize with the companion Gaara Animism Viewer.
"""
from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys
from datetime import datetime

import yaml

from simulation import Simulation


SCENARIO_TLDR = {
    "resonance": (
        "20 swarm clusters orbit a Mothership with her own interior. Her "
        "felt-state drives a broadcast each step; clusters translate it into "
        "material parameters (attraction, viscosity, agitation, color). No "
        "threats. The only signal is the Mother. The only output is matter."
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
        logger.error(
            f"Model '{sim.llm_client.model}' not found. Available: {models}"
        )
        logger.error(f"Try: ollama pull {sim.llm_client.model}")
        return False
    logger.info(f"Using model: {sim.llm_client.model}")
    return True


def create_run_dir(scenario: str, label: str = "") -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = f"_{label}" if label else ""
    path = os.path.join("saved_simulations", scenario, f"{stamp}{suffix}")
    os.makedirs(path, exist_ok=True)
    return path


def write_spec(run_dir: str, scenario: str, config: dict, summary: dict, notes: str = "") -> None:
    tldr = SCENARIO_TLDR.get(scenario, "Custom resonance run.")
    lines = [
        f"# Gaara Animism — {scenario}",
        f"_Run: {os.path.basename(run_dir)}_",
        "",
        "## TL;DR",
        tldr,
        "",
        "## Configuration",
        f"- Scenario: **{scenario}**",
        f"- Clusters: {summary.get('cluster_count')}",
        f"- Duration: {summary.get('duration')} steps",
        f"- Seed: {summary.get('seed')}",
        f"- Model: `{config['llm']['model']}` (temp={config['llm'].get('temperature')})",
        "",
        "## Aggregate metrics",
        f"- Mean cluster distance from Mother (overall): {summary.get('mean_distance_overall', 0):.2f}",
        f"- Mean color temperature (overall): {summary.get('mean_color_temp_overall', 0):.0f} K",
        f"- Mean agitation (overall): {summary.get('mean_agitation_overall', 0):.3f}",
        "",
        "## Files",
        "- `config_snapshot.yaml`",
        "- `cluster_positions.jsonl` — 3D positions + velocities per step",
        "- `cluster_params.jsonl` — transducer outputs per step",
        "- `mother_state.jsonl` — broadcast + interior per step",
        "- `collective_metrics.json` — summary",
    ]
    if notes:
        lines += ["", "## Notes", notes]
    with open(os.path.join(run_dir, "spec.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Project Gaara — Affective Transducer simulation."
    )
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--scenario", default=None,
                        help="Scenario key from config.yaml. Default: resonance.")
    parser.add_argument("--duration", type=int, default=None,
                        help="Override scenario duration (steps).")
    parser.add_argument("--cluster-count", type=int, default=None,
                        help="Override cluster count.")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed override.")
    parser.add_argument("--label", default="", help="Suffix appended to run directory name.")
    parser.add_argument("--notes", default="", help="Free-form notes appended to spec.md.")
    parser.add_argument("--dna-variant", default="VA",
                        choices=["V1", "V2", "V3", "V4", "VA", "VB", "VC", "VD",
                                 "VE", "VF", "VG", "V_AXES", "V_DISSOLVED",
                                 "V_GARDEN", "V_WE"],
                        help="DNA prompt variant. VA=skeleton, VB=cardinal-self, "
                             "VC=relational-hint, VD=guardian-love, VE=guardian-warrior-duty, "
                             "VG=no subject-object grammar. V_AXES=axes-of-contemplation, "
                             "V_DISSOLVED=one body felt at twenty places, V_GARDEN=non-anthropic "
                             "subject (the garden), V_WE=plural shared body.")
    parser.add_argument("--mother-variant", default="M1",
                        choices=["M1", "M2", "M3", "M4", "M5",
                                 "M_SENSORY", "M_METAPHOR", "M_PULSE",
                                 "M_GARDEN", "M_WE"],
                        help="Mother broadcast variant (scripted scenarios only). "
                             "M1=baseline, M2=directional, M3=extreme, M4=flat-max-no-gradient, "
                             "M5=always-urgent. M_SENSORY=skin/temp/pressure phrasing, "
                             "M_METAPHOR=fully metaphorical, M_PULSE=silence+pulses, "
                             "M_GARDEN=non-anthropic body, M_WE=plural body.")
    parser.add_argument("--role-noun", default="mote",
                        help="Word naming the agent — substituted into the DNA prompt "
                             "wherever 'mote' / 'motes' appears. Defaults to 'mote'. "
                             "Tested values: guardian, warrior, sentinel, defender, vanguard.")
    parser.add_argument("--role-nouns", default="",
                        help="Comma-separated list of role nouns, distributed round-robin "
                             "across clusters. Overrides --role-noun if set. "
                             "Example: 'sentinel,warrior' for a 50/50 mixed swarm.")
    parser.add_argument("--say-prefix", default="she",
                        help="Subject label in the prompt's '<x> says:' line. "
                             "Default 'she'. Use 'the garden' for V_GARDEN, 'we' for V_WE.")
    parser.add_argument("--awareness-range", type=float, default=None,
                        help="Override the scenario's awareness_range. Use 0.0 to never "
                             "reveal attacker coords (pure-interpretation test) or 100.0 "
                             "to always reveal (drone-pursuit ceiling test).")
    args = parser.parse_args()

    with open(args.config, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)
    logger = setup_logging(raw_config.get("logging", {}).get("level", "INFO"))

    scenario = args.scenario or raw_config["simulation"].get("scenario", "resonance")
    run_dir = create_run_dir(scenario, args.label)
    logger.info(f"Run directory: {run_dir}")
    shutil.copy(args.config, os.path.join(run_dir, "config_snapshot.yaml"))

    role_nouns_list = (
        [n.strip() for n in args.role_nouns.split(",") if n.strip()]
        if args.role_nouns else None
    )
    sim = Simulation(
        config_path=args.config,
        output_dir=run_dir,
        scenario_override=scenario,
        duration_override=args.duration,
        cluster_count_override=args.cluster_count,
        seed_override=args.seed,
        dna_variant=args.dna_variant,
        mother_variant=args.mother_variant,
        role_noun=args.role_noun,
        role_nouns_list=role_nouns_list,
        say_prefix=args.say_prefix,
        awareness_range_override=args.awareness_range,
    )
    if not check_ollama(sim, logger):
        sys.exit(1)

    try:
        while sim.step < sim.duration:
            sim.step_simulation()
        logger.info("Simulation completed")
    except KeyboardInterrupt:
        logger.info("Interrupted — finalizing partial run")
    finally:
        summary = sim.finalize_metrics()
        write_spec(run_dir, scenario, raw_config, summary, notes=args.notes)
        sim.close()

    logger.info(f"Saved run to: {run_dir}")
    logger.info(f"Summary: {summary}")


if __name__ == "__main__":
    main()
