# Conscious Mode — the contrast piece

This folder is the deliberate **opposite** of the project's main thesis.

The rest of Project Gaara explores AI driven by **relationship** — particles interpreting a subject's state through identity, with no commands. Behavior emerges. It is unpredictable in specifics, coherent in character.

This folder does the inverse: **drone-style choreography.** Each particle's position is computed mathematically each step. Particles do not interpret. They follow a script. Beautiful, predictable, dead.

The demo exists for one reason: **so you can put the two side by side.** When a viewer of the project compares the relational simulations to this one, the difference is felt immediately. One has the rhythm of an entity reading the world. The other has the precision of a machine being told what to do.

This is "Gaara consciously moving his sand" — the mode the project is *not* about, made visible so the mode the project *is* about can be recognized for what it is.

---

## How to use

### Generate the demo
```bash
cd conscious_mode
python3 generate.py
```
Outputs `output/conscious_demo.json` — a 100-step, 20-particle, 3D choreography.

### Sync to the viewer
```bash
python3 sync.py
```
Copies into `Gaara viewer/public/runs/` and registers in `runs.json`.

### View
Open the Gaara viewer (http://localhost:5173/), pick from the run dropdown:
```
conscious_mode / demo_v1
```

---

## What you'll see — the six phases

| Steps | Shape | Description |
|---|---|---|
| 1 – 15 | **orbit** | Particles in a calm ring around the Mothership. |
| 16 – 30 | **dome rise** | Hemispherical shield arcs over the Mothership. |
| 31 – 45 | **dome → wall** | Dome translates and stands as a wall on the east. |
| 46 – 65 | **wave** | Wall undulates with a horizontal sine wave. |
| 66 – 80 | **spiral collapse** | Particles funnel inward as a tightening vertical spiral. |
| 81 – 100 | **return to orbit** | Spiral disperses back into the original ring. |

Transitions use ease-in-out cubic interpolation between keyframes for cinematic motion. Particles still have the visual sand-grain rendering from the viewer (each "particle" is a colony of grains with subtle swirl), so even a programmed dome looks granular.

---

## What this demonstrates (and what it doesn't)

**Demonstrates:**
- The viewer renders 3D particle positions (the elevation channel was added for this).
- A choreographed swarm can produce striking shapes if you tell each particle exactly where to go.
- The aesthetic ceiling of pure command-driven control — beautiful, but inert.

**Does not demonstrate:**
- Anything about the LLM-driven relational architecture. There is no LLM in this folder.
- Anything about emergence. There is no emergence in command-driven motion.
- Anything about the project's actual research thesis.

**This is a contrast piece. It is not part of the research findings.** Its only purpose is to make the relational mode legible by sitting next to it.

---

## Files

```
conscious_mode/
├── README.md          (this file)
├── generate.py        (writes output/conscious_demo.json)
├── sync.py            (copies into viewer + updates manifest)
└── output/
    └── conscious_demo.json
```

To make a new variant — different shapes, different timing — edit the `KEYFRAMES` list and the `shape_*` functions in `generate.py`, then re-run `generate.py` and `sync.py`.
