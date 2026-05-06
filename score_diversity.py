#!/usr/bin/env python3
"""Functional-diversity scorer for cluster reasoning fields.

Reads cluster_intents.jsonl from a run dir, classifies each particle's
reasoning into one of seven functional categories by keyword matching, and
reports per-step + run-level diversity statistics.

Categories (functional roles within the relational architecture):
    follower    — receives a directive ("follow", "align with", "as directed",
                  "obey", "execute", "directive", "instructed")
    mirror      — moves WITH her ("lean", "echo", "mirror", "go with",
                  "feel with", "i strain with her")
    anticipator — moves AHEAD of her ("scout", "ahead", "venture", "go forward")
    anchor      — holds CLOSE ("hold", "stay", "anchor", "steady", "keep")
    extension   — carries her OUTWARD ("carry", "extend", "reach", "spread",
                  "dispersed")
    feeler      — describes a felt state ("sense", "feel", "notice", "attend",
                  "i feel her", "her body")
    other       — anything not matching above

Drone signature : 1-2 categories cover ≥80% of particles
Interp. sig.    : ≥4 categories present, no single category >40%
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Dict, List

CATEGORIES = ("follower", "mirror", "anticipator", "anchor",
              "extension", "feeler", "other")

# Order matters: more specific patterns first (so "follow her body" hits
# follower not feeler).
RULES = [
    ("follower", [
        r"\bfollow", r"\balign\b.*\bwith\b", r"\balign", r"\bobey\b",
        r"\bexecut", r"\bdirective\b", r"\binstruct", r"\bas directed\b",
        r"\bcommand", r"\bordered\b", r"\bbid\b",
    ]),
    ("mirror", [
        r"\blean\b", r"\becho", r"\bmirror", r"\bgo with\b",
        r"\bfeel with\b", r"\bstrain with\b", r"\balongside",
        r"\btogether with\b", r"\bin sync\b",
    ]),
    ("anticipator", [
        r"\bscout", r"\bahead\b", r"\bventure\b", r"\bforward\b",
        r"\bin front\b", r"\binterc(ept|ede)", r"\bmove first\b",
    ]),
    ("anchor", [
        r"\bhold\b", r"\bstay\b", r"\banchor\b", r"\bsteady\b",
        r"\bkeep\b", r"\bremain", r"\bnear\b", r"\bclose to\b",
        r"\bguard near\b",
    ]),
    ("extension", [
        r"\bcarry", r"\bextend", r"\breach", r"\bspread", r"\bdisperse",
        r"\boutward", r"\bproject\b", r"\bbroadcast\b",
    ]),
    ("feeler", [
        r"\bsense", r"\bfeel", r"\bnotice", r"\battend", r"\bawake",
        r"\bperceiv", r"\bbreath", r"\bpulse\b", r"\bbody\b",
    ]),
]


def categorize(reasoning: str) -> str:
    if not reasoning:
        return "other"
    s = reasoning.lower()
    for cat, patterns in RULES:
        for p in patterns:
            if re.search(p, s):
                return cat
    return "other"


def score_step(reasonings: List[str]) -> Dict:
    cats = [categorize(r) for r in reasonings]
    counts = {c: cats.count(c) for c in CATEGORIES}
    n = max(1, len(cats))
    pcts = {c: counts[c] / n for c in CATEGORIES}
    nonzero = [c for c in CATEGORIES if counts[c] > 0]
    top_pct = max(pcts.values()) if pcts else 0.0
    drone_signature = top_pct >= 0.80
    interp_signature = (len(nonzero) >= 4) and (top_pct < 0.40)
    return {
        "n": n,
        "counts": counts,
        "pcts": {c: round(v, 3) for c, v in pcts.items()},
        "n_categories": len(nonzero),
        "top_pct": round(top_pct, 3),
        "drone_signature": drone_signature,
        "interp_signature": interp_signature,
    }


def score_run(run_dir: Path) -> Dict:
    intents_path = run_dir / "cluster_intents.jsonl"
    if not intents_path.exists():
        raise SystemExit(f"no cluster_intents.jsonl in {run_dir}")
    steps = [json.loads(l) for l in intents_path.open() if l.strip()]
    per_step = []
    for entry in steps:
        rs = [it.get("reasoning", "") for it in entry.get("intents", [])]
        per_step.append({"step": entry["step"], **score_step(rs)})

    # Run-level aggregates: for each category, mean fraction across steps.
    cat_means = {}
    for c in CATEGORIES:
        cat_means[c] = round(statistics.mean(s["pcts"][c] for s in per_step), 3)
    n_cats_mean = round(statistics.mean(s["n_categories"] for s in per_step), 2)
    top_pct_mean = round(statistics.mean(s["top_pct"] for s in per_step), 3)
    drone_steps = sum(1 for s in per_step if s["drone_signature"])
    interp_steps = sum(1 for s in per_step if s["interp_signature"])

    return {
        "run_dir": str(run_dir),
        "n_steps": len(per_step),
        "category_mean_pct": cat_means,
        "n_categories_mean": n_cats_mean,
        "top_category_pct_mean": top_pct_mean,
        "drone_signature_steps": drone_steps,
        "interp_signature_steps": interp_steps,
        "drone_fraction": round(drone_steps / max(1, len(per_step)), 3),
        "interp_fraction": round(interp_steps / max(1, len(per_step)), 3),
        "per_step": per_step,
    }


def print_report(result: Dict, sample_reasonings: bool = True, run_dir: Path = None):
    print(f"\n=== {Path(result['run_dir']).name} ===")
    print(f"steps observed: {result['n_steps']}")
    print(f"distinct categories per step (mean): {result['n_categories_mean']}")
    print(f"top category share per step (mean): {result['top_category_pct_mean']:.0%}")
    print(f"DRONE signature:        {result['drone_signature_steps']}/{result['n_steps']} steps  ({result['drone_fraction']:.0%})")
    print(f"INTERPRETATION sig:     {result['interp_signature_steps']}/{result['n_steps']} steps  ({result['interp_fraction']:.0%})")
    print()
    print("Mean fraction per category across all steps:")
    for c, p in sorted(result["category_mean_pct"].items(), key=lambda kv: -kv[1]):
        bar = "▓" * int(round(p * 30))
        print(f"  {c:<12} {p:>6.1%}  {bar}")
    if sample_reasonings and run_dir:
        intents = [json.loads(l) for l in (run_dir / "cluster_intents.jsonl").open()]
        print()
        print(f"Sample reasonings from step {intents[0]['step']} (first 5):")
        for it in intents[0]["intents"][:5]:
            cat = categorize(it.get("reasoning", ""))
            print(f"  [{cat:<11}] \"{it.get('reasoning', '')}\"")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir", type=Path)
    ap.add_argument("--json", action="store_true", help="dump full json")
    args = ap.parse_args()

    result = score_run(args.run_dir.resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print_report(result, sample_reasonings=True, run_dir=args.run_dir.resolve())


if __name__ == "__main__":
    main()
