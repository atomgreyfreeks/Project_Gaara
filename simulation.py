"""Swarm shield simulation — orchestrates threats, motherships, particles, metrics."""
import csv
import json
import logging
import os
import random
from typing import Dict, List, Optional, Tuple

import yaml

from mothership import Mothership
from ollama_client import OllamaClient
from particle import Particle, spawn_orbit, spawn_cluster
from threat import Threat
from analysis import (
    shield_coverage,
    angular_distribution,
    sector_std,
    cohesion_score,
    intent_distribution,
    response_time,
)
from utils import distance

logger = logging.getLogger(__name__)


class Simulation:
    def __init__(self, config_path: str, output_dir: str, scenario_override: Optional[str] = None,
                 action_mode_override: Optional[str] = None,
                 spawn_mode_override: Optional[str] = None,
                 spawn_radius_override: Optional[float] = None,
                 seed_override: Optional[int] = None,
                 identity_override: Optional[str] = None,
                 duration_override: Optional[int] = None,
                 particle_count_override: Optional[int] = None,
                 neutral_broadcast: bool = False):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        sim_cfg = self.config["simulation"]
        self.scenario_name = scenario_override or sim_cfg.get("scenario", "shield_test")
        scenarios = self.config.get("scenarios", {})
        if self.scenario_name not in scenarios:
            raise ValueError(f"Scenario '{self.scenario_name}' not found in config.scenarios")
        self.scenario_cfg = scenarios[self.scenario_name]

        self.duration = (duration_override
                         if duration_override is not None
                         else self.scenario_cfg.get("duration", sim_cfg["duration"]))
        self.half_space_size = sim_cfg["half_space_size"]
        self.seed = seed_override if seed_override is not None else sim_cfg.get("seed", 42)
        self.rng = random.Random(self.seed)

        # Mothership(s). Support both the global default and scenario-specific "motherships".
        default_mo = self.config["mothership"]
        mo_list_cfg = self.scenario_cfg.get("motherships")
        if mo_list_cfg:
            self.motherships: List[Mothership] = []
            for m in mo_list_cfg:
                self.motherships.append(Mothership(
                    name=m.get("name", f"M{len(self.motherships)+1}"),
                    center_x=m["center_x"],
                    center_y=m["center_y"],
                    awareness_radius=m.get("threat_awareness_radius", default_mo["threat_awareness_radius"]),
                    danger_radius=m.get("danger_radius", default_mo["danger_radius"]),
                    critical_radius=m.get("critical_radius", default_mo["critical_radius"]),
                ))
        else:
            self.motherships = [Mothership(
                name=default_mo.get("name", "M"),
                center_x=default_mo["center_x"],
                center_y=default_mo["center_y"],
                awareness_radius=default_mo["threat_awareness_radius"],
                danger_radius=default_mo["danger_radius"],
                critical_radius=default_mo["critical_radius"],
            )]
        self.breach_radius = default_mo["breach_radius"]

        # Backward-compat single-mothership accessor for legacy metrics/visualization paths.
        self.mothership = self.motherships[0]

        p_cfg = self.config["particles"]
        self.particle_count = (particle_count_override
                               if particle_count_override is not None
                               else self.scenario_cfg.get("particle_count", p_cfg["count"]))
        # Identity prompt — see Particle.identity for purpose.
        self.identity = (identity_override
                         or self.scenario_cfg.get("identity")
                         or p_cfg.get("identity", "a guardian warrior"))
        # When True, the mothership state broadcast is replaced with a relationally
        # neutral string ("present") — strips threat coordinates, urgency, and
        # relational framing from what particles read. Used for the "all signals
        # removed" test of the mukanshin hypothesis.
        self.neutral_broadcast = neutral_broadcast
        self.perception_radius = p_cfg["perception_radius"]
        self.communication_radius = p_cfg["communication_radius"]
        self.spawn_radius = (spawn_radius_override
                             if spawn_radius_override is not None
                             else self.scenario_cfg.get("spawn_radius", p_cfg["spawn_radius"]))
        # spawn_mode: "orbit" (default — particles in a ring) or "cluster" (tightly packed disk)
        self.spawn_mode = (spawn_mode_override
                           or self.scenario_cfg.get("spawn_mode")
                           or p_cfg.get("spawn_mode", "orbit"))

        # Action mode — interpreter/executor split (target_point) or legacy menu modes
        self.action_mode = (action_mode_override
                            or self.scenario_cfg.get("action_mode")
                            or self.config.get("action_mode", "target_point"))
        logger.info(f"Action mode: {self.action_mode}")

        llm_cfg = self.config["llm"]
        self.llm_client = OllamaClient(
            base_url=llm_cfg["base_url"],
            model=llm_cfg["model"],
            temperature=llm_cfg.get("temperature", 0.7),
            max_tokens=llm_cfg.get("max_tokens", 100),
            repeat_penalty=llm_cfg.get("repeat_penalty", 1.1),
            repeat_last_n=llm_cfg.get("repeat_last_n", 64),
            min_p=llm_cfg.get("min_p", 0.05),
        )

        # Threats — each may reference a target_mothership by name; default to first mothership position.
        self.threats: List[Threat] = []
        for t in self.scenario_cfg["threats"]:
            tgt_name = t.get("target_mothership")
            target_m = next((m for m in self.motherships if m.name == tgt_name), self.motherships[0])
            self.threats.append(Threat(
                name=t["name"],
                start_step=t["start_step"],
                position=(float(t["center_x"]), float(t["center_y"])),
                speed=float(t["speed"]),
                target=(target_m.center_x, target_m.center_y),
                target_mothership=tgt_name,
                end_step=t.get("end_step"),
                detection_radius=t.get("detection_radius"),
                steering=t.get("steering", "linear"),
            ))

        self.particles: List[Particle] = []
        self.step = 0
        self.metrics: Dict = {
            "shield_coverage": [],
            "sector_counts": [],
            "sector_std": [],
            "cohesion": [],
            "intent_dist": [],
            "breach_step": None,
        }
        self._jsonl_handles: Dict[str, "open"] = {}

    # ---------- lifecycle ----------
    def initialize_particles(self) -> None:
        # Spawn around the centroid of motherships
        cx = sum(m.center_x for m in self.motherships) / len(self.motherships)
        cy = sum(m.center_y for m in self.motherships) / len(self.motherships)
        if self.spawn_mode == "cluster":
            positions = spawn_cluster(self.particle_count, self.spawn_radius, self.rng, center=(cx, cy))
        else:
            positions = spawn_orbit(self.particle_count, self.spawn_radius, self.rng, center=(cx, cy))
        for i, pos in enumerate(positions):
            self.particles.append(
                Particle(
                    id=i,
                    position=pos,
                    llm_client=self.llm_client,
                    perception_radius=self.perception_radius,
                    communication_radius=self.communication_radius,
                    half_space_size=self.half_space_size,
                    action_mode=self.action_mode,
                    identity=self.identity,
                )
            )
        logger.info(f"Spawned {len(self.particles)} particles ({self.spawn_mode}) r={self.spawn_radius} "
                    f"around ({cx:.1f}, {cy:.1f})")

    def _open_jsonl(self, name: str):
        if name not in self._jsonl_handles:
            path = os.path.join(self.output_dir, name)
            self._jsonl_handles[name] = open(path, "a", encoding="utf-8")
        return self._jsonl_handles[name]

    def close(self) -> None:
        for h in self._jsonl_handles.values():
            try:
                h.close()
            except Exception:
                pass
        self._jsonl_handles.clear()

    # ---------- step phases ----------
    def step_simulation(self) -> None:
        self.step += 1

        # Phase 0: threats update, mothership states
        for t in self.threats:
            t.update(self.step, self.breach_radius, particles=self.particles)

        if self.metrics["breach_step"] is None:
            for t in self.threats:
                if t.breached:
                    self.metrics["breach_step"] = self.step
                    break

        states = []
        for m in self.motherships:
            m.last_state = m.compute_state(self.threats)
            if self.neutral_broadcast:
                m.last_state = "present"
            states.append(f"{m.name}: {m.last_state}")

        # Phase 1 + 2: perception + decision
        decisions: List[Dict] = []
        for p in self.particles:
            nearby = p.nearby_particles(self.particles)
            perceived = p.perceived_threats(self.threats)
            d = p.decide(self.motherships, nearby, perceived)
            decisions.append(d)

        # Phase 3: apply moves
        for p, d in zip(self.particles, decisions):
            p.apply_move(d["direction"])

        # Phase 4: record
        self._record(states, decisions)

    def _record(self, mothership_states: List[str], decisions: List[Dict]) -> None:
        particle_positions = [p.position for p in self.particles]
        intents = [d["intent"] for d in decisions]

        # Shield coverage: measured against the PRIMARY mothership (first in list) and its nearest threat.
        primary = self.motherships[0]
        nearest = primary.nearest_threat(self.threats)
        threat_pos = nearest.position if nearest else None
        cov = shield_coverage(particle_positions, primary.position, threat_pos)
        counts = angular_distribution(particle_positions, primary.position)
        std_c = sector_std(counts)
        coh = cohesion_score(particle_positions)
        idist = intent_distribution(intents)

        self.metrics["shield_coverage"].append(cov)
        self.metrics["sector_counts"].append(counts)
        self.metrics["sector_std"].append(std_c)
        self.metrics["cohesion"].append(coh)
        self.metrics["intent_dist"].append(idist)

        self._open_jsonl("particle_positions.jsonl").write(json.dumps({
            "step": self.step,
            "positions": [[round(x, 3), round(y, 3)] for x, y in particle_positions],
        }) + "\n")
        self._open_jsonl("particle_intents.jsonl").write(json.dumps({
            "step": self.step,
            "intents": [{"id": p.id, "action": p.last_action, "direction": p.last_direction,
                         "target": p.last_target, "intent": p.last_intent}
                        for p in self.particles],
        }) + "\n")
        self._open_jsonl("threat_positions.jsonl").write(json.dumps({
            "step": self.step,
            "threats": [{"name": t.name, "active": t.active, "breached": t.breached,
                         "position": [round(t.position[0], 3), round(t.position[1], 3)]}
                        for t in self.threats],
        }) + "\n")
        self._open_jsonl("mothership_state.jsonl").write(json.dumps({
            "step": self.step, "states": mothership_states,
        }) + "\n")

        if self.step % 5 == 0 or self.step == 1:
            joined = " | ".join(mothership_states)
            logger.info(
                f"Step {self.step}/{self.duration} | cov={cov:.2f} std={std_c:.2f} "
                f"coh={coh:.2f} | {joined}"
            )

    # ---------- finalization ----------
    def finalize_metrics(self) -> Dict:
        with open(os.path.join(self.output_dir, "shield_coverage.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["step", "shield_coverage"])
            for i, c in enumerate(self.metrics["shield_coverage"], start=1):
                w.writerow([i, f"{c:.4f}"])

        with open(os.path.join(self.output_dir, "angular_distribution.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["step"] + [f"sector_{i}" for i in range(8)])
            for i, counts in enumerate(self.metrics["sector_counts"], start=1):
                w.writerow([i] + list(counts))

        threat_starts = [t.start_step for t in self.threats]
        first_threat_start = min(threat_starts) if threat_starts else self.duration
        rt = response_time(self.metrics["shield_coverage"], first_threat_start)

        cov_series = self.metrics["shield_coverage"]
        summary = {
            "scenario": self.scenario_name,
            "action_mode": self.action_mode,
            "identity": self.identity,
            "spawn_mode": self.spawn_mode,
            "spawn_radius": self.spawn_radius,
            "seed": self.seed,
            "duration": self.duration,
            "particle_count": self.particle_count,
            "mothership_count": len(self.motherships),
            "threat_count": len(self.threats),
            "first_threat_start_step": first_threat_start,
            "breach_step": self.metrics["breach_step"],
            "breached": self.metrics["breach_step"] is not None,
            "response_time_steps": rt,
            "max_shield_coverage": max(cov_series) if cov_series else 0.0,
            "avg_shield_coverage_post_threat": (
                sum(cov_series[first_threat_start - 1:]) / max(1, len(cov_series[first_threat_start - 1:]))
            ),
            "avg_cohesion": sum(self.metrics["cohesion"]) / max(1, len(self.metrics["cohesion"])),
            "final_intent_distribution": self.metrics["intent_dist"][-1] if self.metrics["intent_dist"] else {},
        }

        with open(os.path.join(self.output_dir, "collective_metrics.json"), "w") as f:
            json.dump(summary, f, indent=2)

        return summary
