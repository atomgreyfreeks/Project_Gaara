#!/usr/bin/env python3
"""Copy the conscious-mode demo into the Gaara viewer and register it in runs.json.

Usage: python3 sync.py
"""
import json
import shutil
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "output" / "conscious_demo.json"
VIEWER_RUNS = Path("/Users/yukitakashima/Desktop/PUBLISH/Gaara viewer/public/runs")
DEST = VIEWER_RUNS / "conscious_mode-demo_v1.json"
MANIFEST = VIEWER_RUNS / "runs.json"

ENTRY = {
    "id": "conscious_mode-demo_v1",
    "path": "conscious_mode-demo_v1.json",
    "scenario": "conscious_mode",
    "timestamp": "demo_v1",
    "summary": "Choreographed (drone-style) demo. The contrast piece. orbit → dome → wall → wave → spiral → orbit.",
}


def main():
    if not SRC.exists():
        raise SystemExit(f"missing {SRC} — run generate.py first")

    shutil.copy(SRC, DEST)
    print(f"✔ copied → {DEST}")

    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else []
    # Replace existing entry with this id, otherwise prepend
    manifest = [m for m in manifest if m.get("id") != ENTRY["id"]]
    manifest.insert(0, ENTRY)
    MANIFEST.write_text(json.dumps(manifest, indent=2))
    print(f"✔ registered in {MANIFEST}")
    print(f"  scenario: {ENTRY['scenario']}")
    print(f"  open the viewer and find: 'conscious_mode / demo_v1'")


if __name__ == "__main__":
    main()
