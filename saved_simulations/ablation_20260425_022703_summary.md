# Action-interface ablation — ablation_20260425_022703

**Question:** Under identical conditions today, does the interpreter/executor split
(target_point) still produce emergent attack-swarm behavior that menu interfaces fail to?

**Design:** shield_test, 20 particles, threat at (20,5) start step 4, 50 steps.
Only the LLM's action interface varies.

**Modes tested:** menu_4dir menu_8dir target_point

| # | Mode | Status | Duration | Max cov | Avg cov (post) | Breach | Run dir |
|---|---|---|---|---|---|---|---|
| 1 | `menu_4dir` | ok | 1192s | 0.40 | 0.23 | 41 | `saved_simulations/shield_test/20260425_022704_ablation_menu_4dir` |
| 2 | `menu_8dir` | ok | 1311s | 0.35 | 0.07 | 41 | `saved_simulations/shield_test/20260425_024655_ablation_menu_8dir` |
| 3 | `target_point` | ok | 1808s | 0.65 | 0.22 | 41 | `saved_simulations/shield_test/20260425_030846_ablation_target_point` |

**Finished:** Sat Apr 25 03:38:54 JST 2026

## How to read the table
- **Max cov** / **Avg cov (post)**: higher = more particles on the threat→mothership line.
- **Breach**: step when threat reached the mothership (or '-' if no breach).

## Expected outcome if the architectural claim is correct
- `menu_8dir`: low avg coverage, particles converge on 'up-right' (stampede / conga line).
- `menu_4dir`: moderate coverage (~0.4 max, ~0.25 avg), loose shield.
- `target_point`: high peak coverage (~1.0), tight attack-swarm clustering, 'intercept/neutralize' intents.

If target_point shows clearly different behavior than the menus under identical conditions,
the interpreter/executor split is causal — not a narrative artifact.
