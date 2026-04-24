"""Rendering for the swarm shield simulation."""
import logging
import math
import os
from typing import List, Optional

import matplotlib

# Backend setup (inherit sensibly)
if not os.environ.get("DISPLAY") and not matplotlib.get_backend():
    matplotlib.use("Agg")
else:
    try:
        matplotlib.use("Agg")  # default to Agg for saving frames reliably
    except Exception:
        pass

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from mothership import Mothership
from particle import Particle, categorize_intent
from threat import Threat

logger = logging.getLogger(__name__)

FIGSIZE = (13, 8)
DPI = 130


class Visualizer:
    def __init__(self, half_space_size: int, show_perception_radius: bool = False):
        self.half = half_space_size
        self.show_perception_radius = show_perception_radius

    def render_step(
        self,
        step: int,
        motherships: List[Mothership],
        particles: List[Particle],
        threats: List[Threat],
        mothership_state: str,
        shield_cov_series: List[float],
        sector_counts: List[int],
        intent_dist: dict,
        threat_distance_series: List[float],
        save_path: Optional[str] = None,
    ) -> None:
        fig = plt.figure(figsize=FIGSIZE)
        gs = fig.add_gridspec(3, 3, width_ratios=[2, 1, 1])

        ax_field = fig.add_subplot(gs[:, 0])
        ax_cov = fig.add_subplot(gs[0, 1:])
        ax_polar = fig.add_subplot(gs[1, 1], projection="polar")
        ax_intent = fig.add_subplot(gs[1, 2])
        ax_dist = fig.add_subplot(gs[2, 1:])

        self._draw_field(ax_field, step, motherships, particles, threats, mothership_state)
        self._draw_coverage(ax_cov, shield_cov_series)
        self._draw_polar(ax_polar, sector_counts)
        self._draw_intents(ax_intent, intent_dist)
        self._draw_threat_dist(ax_dist, threat_distance_series)

        fig.tight_layout()
        if save_path:
            fig.savefig(save_path, dpi=DPI, bbox_inches="tight")
        plt.close(fig)

    def _draw_field(self, ax, step, motherships, particles, threats, state):
        ax.set_xlim(-self.half, self.half)
        ax.set_ylim(-self.half, self.half)
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.25)
        ax.set_title(f"Step {step} — {state}", fontsize=9, fontweight="bold")

        # Motherships (1 or more)
        for m in motherships:
            ax.add_patch(patches.Circle(m.position, 2.0, facecolor="#1f6feb", edgecolor="navy",
                                        alpha=0.85, zorder=5))
            ax.text(m.position[0], m.position[1], m.name, ha="center", va="center",
                    color="white", fontweight="bold", zorder=6, fontsize=9)
            for r, color in [(m.awareness_radius, "#888888"),
                             (m.danger_radius, "#d39a00"),
                             (m.critical_radius, "#cc3333")]:
                ax.add_patch(patches.Circle(m.position, r, fill=False,
                                            edgecolor=color, linestyle=":", alpha=0.25))

        # Active threats
        active_threats = [t for t in threats if t.active and not t.breached]
        for t in active_threats:
            ax.scatter(t.position[0], t.position[1], marker="^", s=180, c="red",
                       edgecolors="darkred", linewidths=1.5, zorder=7)
            # Line to its targeted mothership (or first mothership)
            target_m = next((m for m in motherships if m.name == t.target_mothership), motherships[0])
            ax.plot([t.position[0], target_m.position[0]],
                    [t.position[1], target_m.position[1]],
                    "r--", alpha=0.35, linewidth=1)
            ax.text(t.position[0], t.position[1] + 1.2, t.name, ha="center",
                    fontsize=7, color="darkred")

        # Particles (color by intent category)
        color_map = {"protect": "#f0a500", "explore": "#1abc9c", "retreat": "#8e44ad", "other": "#7f8c8d"}
        for p in particles:
            cat = categorize_intent(p.last_intent)
            ax.scatter(p.position[0], p.position[1], c=color_map[cat], s=45,
                       edgecolors="black", linewidths=0.5, zorder=6)
            ax.text(p.position[0] + 0.3, p.position[1] + 0.3, str(p.id),
                    fontsize=6, alpha=0.7)
            if self.show_perception_radius:
                ax.add_patch(patches.Circle(p.position, p.perception_radius,
                                            fill=False, edgecolor="gray",
                                            alpha=0.08, linewidth=0.5))

        # Legend
        from matplotlib.lines import Line2D
        legend = [
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#f0a500", markersize=8, label="intent: protect"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#1abc9c", markersize=8, label="intent: explore"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#8e44ad", markersize=8, label="intent: retreat"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#7f8c8d", markersize=8, label="intent: other"),
            Line2D([0], [0], marker="^", color="w", markerfacecolor="red", markeredgecolor="darkred",
                   markersize=10, label="threat"),
        ]
        ax.legend(handles=legend, loc="upper right", fontsize=7)

    def _draw_coverage(self, ax, series):
        ax.plot(range(1, len(series) + 1), series, color="#1f6feb")
        ax.set_ylim(0, 1)
        ax.set_title("Shield coverage", fontsize=9)
        ax.set_xlabel("step", fontsize=8)
        ax.grid(True, alpha=0.3)
        ax.axhline(0.3, color="gray", linestyle=":", alpha=0.5)

    def _draw_polar(self, ax, sector_counts):
        n = len(sector_counts) or 8
        theta = np.linspace(0, 2 * math.pi, n, endpoint=False)
        width = 2 * math.pi / n
        ax.bar(theta, sector_counts, width=width, bottom=0.0, alpha=0.7, color="#1abc9c",
               edgecolor="black", linewidth=0.5)
        ax.set_title("Angular density", fontsize=9)
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    def _draw_intents(self, ax, dist: dict):
        labels = list(dist.keys())
        values = [dist[k] for k in labels]
        colors = {"protect": "#f0a500", "explore": "#1abc9c", "retreat": "#8e44ad", "other": "#7f8c8d"}
        ax.bar(labels, values, color=[colors.get(k, "#7f8c8d") for k in labels])
        ax.set_title("Intents", fontsize=9)
        ax.tick_params(axis="x", labelsize=7)

    def _draw_threat_dist(self, ax, series):
        if series:
            ax.plot(range(1, len(series) + 1), series, color="red")
        ax.set_title("Nearest threat → mothership", fontsize=9)
        ax.set_xlabel("step", fontsize=8)
        ax.grid(True, alpha=0.3)


def plot_summary(save_dir: str, metrics: dict, threat_distance_series: List[float]) -> None:
    """Write a post-run summary figure."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    cov = metrics["shield_coverage"]
    coh = metrics["cohesion"]
    std_c = metrics["sector_std"]

    axes[0, 0].plot(cov, color="#1f6feb")
    axes[0, 0].set_title("Shield coverage over time")
    axes[0, 0].set_ylim(0, 1)
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(std_c, color="#f0a500")
    axes[0, 1].set_title("Sector std deviation (clustering)")
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(coh, color="#1abc9c")
    axes[1, 0].set_title("Cohesion (mean nearest-neighbor dist)")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(threat_distance_series, color="red")
    axes[1, 1].set_title("Nearest threat → mothership")
    axes[1, 1].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(os.path.join(save_dir, "statistics.png"), dpi=130, bbox_inches="tight")
    plt.close(fig)
