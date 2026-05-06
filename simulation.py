"""Simulation orchestrator — LLM Body Language architecture.

Per step:
    1. Attackers update (linear motion toward Mother).
    2. Mother's interior advances; if scripted, override felt-state and
       perception_modifier; she broadcasts.
    3. Awareness check — if any cluster is within awareness_range of any
       attacker, that attacker's exact coords are revealed to ALL clusters
       this step (and persist for the rest of the run).
    4. Each cluster's LLM emits intent (ideal_coord, urgency, hostility).
    5. Physics integrates intent into kinematics.
    6. Log everything.
"""
from __future__ import annotations

import json
import logging
import math
import os
import random
from typing import Dict, List, Optional, Tuple

import yaml

from cluster import Cluster, spawn_ring
from mothership import Mothership, MotherInterior
from ollama_client import OllamaClient
from physics import PhysicsConfig, integrate
from scenarios import (script_55, script_100, script_70, script_30,
                        script_constant)
from threat import Attacker

logger = logging.getLogger(__name__)


class Simulation:
    def __init__(
        self,
        config_path: str,
        output_dir: str,
        scenario_override: Optional[str] = None,
        duration_override: Optional[int] = None,
        cluster_count_override: Optional[int] = None,
        seed_override: Optional[int] = None,
        dna_variant: str = "V1",
        mother_variant: str = "M1",
        role_noun: str = "mote",
        role_nouns_list: Optional[List[str]] = None,
        say_prefix: str = "she",
        awareness_range_override: Optional[float] = None,
    ):
        self.dna_variant = dna_variant
        self.mother_variant = mother_variant
        self.role_noun = role_noun
        self.role_nouns_list = role_nouns_list
        self.say_prefix = say_prefix
        self.awareness_range_override = awareness_range_override
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        sim_cfg = self.config["simulation"]
        scenarios = self.config.get("scenarios", {})
        self.scenario_name = scenario_override or sim_cfg.get("scenario", "scripted_55")
        if self.scenario_name not in scenarios:
            raise ValueError(
                f"Scenario '{self.scenario_name}' not found in config.scenarios"
            )
        self.scenario_cfg = scenarios[self.scenario_name]

        self.duration = (
            duration_override
            if duration_override is not None
            else self.scenario_cfg.get("duration", sim_cfg["duration"])
        )
        self.half_space = float(sim_cfg.get("half_space_size", 25))
        self.seed = seed_override if seed_override is not None else sim_cfg.get("seed", 42)
        self.rng = random.Random(self.seed)

        # Mother — kept simple for the scripted protocol. Position 2D.
        m_cfg = self.config.get("mothership", {})
        center = m_cfg.get("center", [0.0, 0.0])
        self.mother = Mothership(
            name=m_cfg.get("name", "M"),
            position=(float(center[0]), float(center[1]), 0.0),
            interior=MotherInterior(rng=random.Random(self.seed + 7919)),
        )
        self.scripted = bool(self.scenario_cfg.get("scripted", False))

        # Clusters — spawned on a 2D ring at z=0.
        c_cfg = self.config["clusters"]
        self.cluster_count = (
            cluster_count_override
            if cluster_count_override is not None
            else self.scenario_cfg.get("cluster_count", c_cfg["count"])
        )
        spawn_radius = float(self.scenario_cfg.get("spawn_radius", c_cfg.get("spawn_radius", 8.0)))
        memory_size = int(c_cfg.get("memory_size", 6))

        llm_cfg = self.config["llm"]
        self.llm_client = OllamaClient(
            base_url=llm_cfg["base_url"],
            model=llm_cfg["model"],
            temperature=llm_cfg.get("temperature", 0.7),
            max_tokens=llm_cfg.get("max_tokens", 80),
            repeat_penalty=llm_cfg.get("repeat_penalty", 1.1),
            repeat_last_n=llm_cfg.get("repeat_last_n", 64),
            min_p=llm_cfg.get("min_p", 0.05),
        )

        positions = spawn_ring(
            self.cluster_count, spawn_radius, self.rng,
            center=(self.mother.position[0], self.mother.position[1]),
        )
        # Mixed-noun mode: distribute role_nouns_list round-robin across clusters.
        def _noun_for(i: int) -> str:
            if self.role_nouns_list:
                return self.role_nouns_list[i % len(self.role_nouns_list)]
            return self.role_noun

        self.clusters: List[Cluster] = [
            Cluster(
                id=i,
                position=pos,
                velocity=(0.0, 0.0),
                llm_client=self.llm_client,
                memory_size=memory_size,
                half_space=self.half_space,
                variant=self.dna_variant,
                role_noun=_noun_for(i),
                say_prefix=self.say_prefix,
            )
            for i, pos in enumerate(positions)
        ]

        # Attackers — declared in scenario config.
        self.attackers: List[Attacker] = []
        for a in self.scenario_cfg.get("attackers", []):
            self.attackers.append(Attacker(
                name=a["name"],
                start_step=int(a["start_step"]),
                start_position=(float(a["start_x"]), float(a["start_y"])),
                target=(float(a.get("target_x", 0.0)), float(a.get("target_y", 0.0))),
                speed=float(a["speed"]),
            ))

        # Awareness range — clusters within this distance of any attacker
        # cause ALL clusters to be told that attacker's exact coordinates.
        if self.awareness_range_override is not None:
            self.awareness_range = float(self.awareness_range_override)
        else:
            self.awareness_range = float(
                self.scenario_cfg.get("awareness_range",
                                      self.config.get("awareness_range", 4.0))
            )
        # Once revealed, an attacker stays revealed for the rest of the run.
        self._revealed: set = set()

        # Physics config — 2D, simplified (urgency caps speed, damping smooths).
        phys_cfg = self.config.get("physics", {})
        self.physics_cfg = PhysicsConfig(
            vmax_low=float(phys_cfg.get("vmax_low", 0.4)),
            vmax_high=float(phys_cfg.get("vmax_high", 1.5)),
            damping=float(phys_cfg.get("damping", 0.20)),
            jitter_scale=float(phys_cfg.get("jitter_scale", 0.4)),
            dt=float(phys_cfg.get("dt", 1.0)),
            half_space=self.half_space,
        )
        self.physics_rng = random.Random(self.seed + 31337)

        self.step = 0
        self.metrics: Dict = {
            "mean_distance": [],
            "mean_urgency": [],
            "mean_hostility": [],
            "revealed_count": [],
        }
        self._jsonl_handles: Dict[str, "open"] = {}

    def _open_jsonl(self, name: str):
        if name not in self._jsonl_handles:
            self._jsonl_handles[name] = open(
                os.path.join(self.output_dir, name), "a", encoding="utf-8"
            )
        return self._jsonl_handles[name]

    def close(self) -> None:
        for h in self._jsonl_handles.values():
            try: h.close()
            except Exception: pass
        self._jsonl_handles.clear()

    def _scripted_step(self, step: int):
        """Dispatch to the right scripted-controller based on scenario name."""
        if self.scenario_name == "scripted_55":
            return script_55(step)
        if self.scenario_name == "scripted_30":
            return script_30(step, self.mother_variant)
        if self.scenario_name == "scripted_70" or self.scenario_name.startswith("scripted_70_"):
            return script_70(step, self.mother_variant)
        if self.scenario_name.startswith("const_"):
            key = self.scenario_cfg.get("constant_state", "calm")
            return script_constant(step, key)
        return script_100(step, self.mother_variant)

    # ---------- step ----------
    def step_simulation(self) -> None:
        self.step += 1

        # 1. Attackers move.
        for a in self.attackers:
            a.update(self.step)

        # 2. Mother — apply scripted overrides if in scripted scenario.
        if self.scripted:
            forced_state, forced_modifier = self._scripted_step(self.step)
            # For constant-state scenarios — and for non-anthropic subject
            # variants (M_GARDEN, M_WE) — the broadcast IS the modifier; the
            # anthropic interior template would conflict with the alternate
            # subject framing, so we bypass it.
            direct_broadcast = (
                self.scenario_name.startswith("const_")
                or self.mother_variant in ("M_GARDEN", "M_WE")
            )
            if direct_broadcast:
                if self.mother.interior is not None and forced_state is not None:
                    self.mother.interior.state = forced_state
                    self.mother.interior.state_dwell = 0
                    self.mother.interior.perception_modifier = None
                broadcast = forced_modifier or "calm. the world is still."
                self.mother.last_state = broadcast
            else:
                if forced_state is not None and self.mother.interior is not None:
                    self.mother.interior.state = forced_state
                    self.mother.interior.state_dwell = 0
                self.mother.interior.step()
                if forced_modifier is not None:
                    self.mother.interior.perception_modifier = forced_modifier
                else:
                    self.mother.interior.perception_modifier = None
                broadcast = self.mother.interior.broadcast()
                self.mother.last_state = broadcast
        else:
            self.mother.perceive_swarm(self.clusters)
            broadcast = self.mother.step_and_broadcast()

        # 3. Awareness check — any cluster within range of any active attacker
        # causes that attacker to be revealed to ALL clusters from now on.
        m_pos_2d = (self.mother.position[0], self.mother.position[1])
        for a in self.attackers:
            if not a.active or a.name in self._revealed:
                continue
            for c in self.clusters:
                if a.distance_to(c.position) <= self.awareness_range:
                    self._revealed.add(a.name)
                    logger.info(
                        f"  awareness flip: {a.name} now revealed to all "
                        f"(triggered at step {self.step})"
                    )
                    break

        revealed_attackers: List[Tuple[str, Tuple[float, float]]] = [
            (a.name, a.position) for a in self.attackers
            if a.active and a.name in self._revealed
        ]

        # 4. Each cluster transduces broadcast + revealed coords into intent.
        # V4 variant also receives nearest-peer positions in its sensorium.
        all_intents: List[Dict] = []
        peers = self.clusters if self.dna_variant == "V4" else None
        for c in self.clusters:
            intent = c.transduce(broadcast, revealed_attackers, peers)
            all_intents.append(intent)

        # 5. Physics integrates intent into kinematics.
        for c, intent in zip(self.clusters, all_intents):
            new_pos, new_vel = integrate(
                position=c.position,
                velocity=c.velocity,
                ideal_coord=tuple(intent["ideal_coord"]),
                urgency=intent["urgency"],
                hostility=intent["hostility"],
                cfg=self.physics_cfg,
                rng=self.physics_rng,
            )
            c.position = new_pos
            c.velocity = new_vel

        # 6. Memory + logging.
        for c in self.clusters:
            c.record_moment(broadcast)
        self._record(broadcast, all_intents, revealed_attackers)

    def _record(self, broadcast: str, all_intents: List[Dict],
                revealed_attackers: List[Tuple[str, Tuple[float, float]]]) -> None:
        n = len(self.clusters)
        m_pos_2d = (self.mother.position[0], self.mother.position[1])
        mean_d = sum(math.hypot(c.position[0] - m_pos_2d[0],
                                c.position[1] - m_pos_2d[1])
                     for c in self.clusters) / n
        mean_u = sum(it["urgency"] for it in all_intents) / n
        mean_h = sum(it["hostility"] for it in all_intents) / n

        self.metrics["mean_distance"].append(mean_d)
        self.metrics["mean_urgency"].append(mean_u)
        self.metrics["mean_hostility"].append(mean_h)
        self.metrics["revealed_count"].append(len(revealed_attackers))

        # Log positions in 3D shape (x, y, 0) so the viewer pipeline stays unchanged.
        self._open_jsonl("cluster_positions.jsonl").write(json.dumps({
            "step": self.step,
            "positions": [
                [round(c.position[0], 3), round(c.position[1], 3), 0.0]
                for c in self.clusters
            ],
            "velocities": [
                [round(c.velocity[0], 3), round(c.velocity[1], 3), 0.0]
                for c in self.clusters
            ],
        }) + "\n")

        # Per-cluster intents (the new schema).
        self._open_jsonl("cluster_intents.jsonl").write(json.dumps({
            "step": self.step,
            "intents": [
                {
                    "id": c.id,
                    "ideal_coord": [round(it["ideal_coord"][0], 3),
                                    round(it["ideal_coord"][1], 3)],
                    "urgency": round(it["urgency"], 4),
                    "hostility": round(it["hostility"], 4),
                    "reasoning": (it.get("reasoning") or "")[:200],
                }
                for c, it in zip(self.clusters, all_intents)
            ],
        }) + "\n")

        # Mother + scripted layer.
        interior = self.mother.interior
        forced_state, forced_modifier = (None, None)
        if self.scripted:
            forced_state, forced_modifier = self._scripted_step(self.step)
        self._open_jsonl("mother_state.jsonl").write(json.dumps({
            "step": self.step,
            "broadcast": broadcast,
            "felt_state": interior.state if interior else None,
            "attention": interior.attention if interior else None,
            "energy": round(interior.energy, 3) if interior else None,
            "perception_modifier": interior.perception_modifier if interior else None,
            "scripted_forced_state": forced_state,
            "scripted_forced_modifier": forced_modifier,
        }) + "\n")

        # Attackers.
        self._open_jsonl("attackers.jsonl").write(json.dumps({
            "step": self.step,
            "attackers": [
                {
                    "name": a.name,
                    "active": a.active,
                    "position": [round(a.position[0], 3),
                                 round(a.position[1], 3), 0.0],
                    "revealed": a.name in self._revealed,
                }
                for a in self.attackers
            ],
        }) + "\n")

        if self.step == 1 or self.step % 5 == 0 or len(revealed_attackers) > 0:
            r = ",".join(name for name, _ in revealed_attackers) or "—"
            logger.info(
                f"step {self.step:>3}/{self.duration} | "
                f"d={mean_d:5.2f} urg={mean_u:.2f} host={mean_h:+.2f} | "
                f"revealed=[{r}] | {broadcast[:90]}"
            )

    # ---------- finalize ----------
    def finalize_metrics(self) -> Dict:
        n = max(1, len(self.metrics["mean_distance"]))
        summary = {
            "scenario": self.scenario_name,
            "duration": self.duration,
            "cluster_count": self.cluster_count,
            "seed": self.seed,
            "dna_variant": self.dna_variant,
            "mother_variant": self.mother_variant,
            "role_noun": self.role_noun,
            "role_nouns_list": self.role_nouns_list,
            "say_prefix": self.say_prefix,
            "awareness_range": self.awareness_range,
            "mean_distance_overall": sum(self.metrics["mean_distance"]) / n,
            "mean_urgency_overall": sum(self.metrics["mean_urgency"]) / n,
            "mean_hostility_overall": sum(self.metrics["mean_hostility"]) / n,
            "attackers_revealed_at_end": list(self._revealed),
        }
        with open(os.path.join(self.output_dir, "collective_metrics.json"), "w") as f:
            json.dump(summary, f, indent=2)
        return summary
