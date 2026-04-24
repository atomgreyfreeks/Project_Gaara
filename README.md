# Swarm Shield Simulation

**Research question:** Can a swarm of LLM particles that can interpret local situations
spontaneously produce collective behaviors (shielding, surrounding, intercepting) that
were never explicitly programmed?

Inspired by Gaara's sand — each grain responds locally to the wielder's state;
the global form (shield, dome, wall) is emergent, never dictated.

## What's in the box

- **`particle.py`** — the LLM particle. Minimal prompt, 5-action space (up/down/left/right/stay),
  local perception only. No behavioral rules. Just a purpose ("protect the Mothership") and raw senses.
- **`mothership.py`** — passive entity. Broadcasts a state string based on nearest threat.
  Never issues commands.
- **`threat.py`** — dumb programmed entity. Moves toward the mothership at fixed speed.
- **`simulation.py`** — step loop: threats move → state recomputed → particles decide → particles move → metrics logged.
- **`analysis.py`** — shield coverage, angular distribution, cohesion, intent categorization, response time.
- **`visualization.py`** — field + stats panel per step.
- **`main.py`** — entry point, saves each run to `saved_simulations/<timestamp>_<scenario>/`.

## Running

```bash
# start Ollama first
ollama pull qwen2.5:7b
ollama serve

# run
python main.py                                  # uses config default (shield_test)
python main.py --scenario surround_test
python main.py --scenario multi_threat --label "temp07"
python main.py --scenario shield_test --notes "Trying lower temperature to reduce wandering."
```

## Saved simulations

Every run creates a directory under `saved_simulations/` containing a **`spec.md`** with a tl;dr
of what was tested and the key results, alongside all raw logs, per-step frames, and a summary plot.

```
saved_simulations/20260424_153012_shield_test/
  spec.md                       # TL;DR of the experiment
  config_snapshot.yaml          # exact config used
  frames/frame_XXXX.png         # per-step visualizations
  particle_positions.jsonl
  particle_intents.jsonl
  threat_positions.jsonl
  mothership_state.jsonl
  shield_coverage.csv
  angular_distribution.csv
  collective_metrics.json
  statistics.png
```

## Scenarios

- **`shield_test`** — 20 particles, 1 threat from the east. Minimum viable experiment.
- **`surround_test`** — 20 particles, 3 threats 120° apart, staggered. Can the swarm split?
- **`multi_threat`** — 30 particles, 5 threats from random directions. Adaptive redistribution.

## Success bands

- **Weak:** shield coverage rises from ~0.1 baseline to ~0.2–0.3. Particles drift toward the threat side.
- **Strong:** coverage > 0.4. Visible clustering between threat and mothership. Intent fields mention "protect".
- **Failure:** coverage stays at baseline. Intent fields are confused or empty.
- **Interesting failure:** all particles charge the threat (attacking) or all flee (self-preservation). Still findings.

## Design principles

1. **No behavioral rules in the prompt.** Particles are told "protect the Mothership" and given sensory data. *How* is never specified.
2. **Prompts are short** (< 150 words). Particles are simple.
3. **`max_tokens: 100`** — forces terse responses.
4. **The threat is dumb.** It moves in a straight line. We're testing particle intelligence, not threat intelligence.
5. **The mothership is passive.** It broadcasts state, issues no commands.
6. **Measure the collective, not the individual.** 15/20 particles doing something vaguely protective still produces a visible shield.
