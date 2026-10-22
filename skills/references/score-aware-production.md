# Score-aware production

## Contents

1. Observable coverage
2. Scope selection
3. Phase gates
4. Category review
5. Time-pressure recovery
6. Failure patterns

## 1. Observable coverage

Specifications describe experiences; evaluation observes pixels after inputs. Convert each promise into a visible action-state-outcome chain.

Bad decomposition:

- “Implement research.”
- “Add three enemies.”
- “Polish the UI.”

Useful decomposition:

| Promise | Action | State transition | Visible proof |
|---|---|---|---|
| Research changes production | Click affordable upgrade | credits decrease; multiplier increases | button changes to purchased; rate value jumps; machines animate faster |
| Enemies differ tactically | Approach/attack each type | distinct movement, attack, or defense behavior | silhouette, telegraph, response, and outcome differ |
| Failure matters | collide, time out, or lose HP | failure state enters | readable cause, result panel, stats, retry affordance |

Create a coverage map before architecture. Add a proof scenario and trace name to each major row. If two rows need incompatible states, plan separate scenarios.

## 2. Scope selection

Choose a scope that can become authored, not merely broad.

Use one dominant loop, one secondary progression loop, and one complete presentation arc. Prefer a smaller number of systems with visible consequences over many disconnected systems.

Minimum healthy scope:

- one primary verb with feedback;
- one meaningful choice or tradeoff;
- one opposition, constraint, timer, hazard, or rule;
- three content variants when the brief asks for variety;
- one progression or escalation step;
- victory, defeat, result, and retry;
- title/briefing plus stable HUD;
- deterministic proof states.

Avoid speculative architecture. Use data-driven arrays or small resources for variants, a clear state enum for flow, and signals for visible updates. Keep the system simple enough to debug through screenshots and traces.

## 3. Phase gates

Do not move forward on intent alone.

### Gate 0: contract

- Paths, Godot version, viewport, launch command, assets, screenshot helper, and trace format are known.
- The coverage map exists.
- The dominant genre recipe and visual direction are chosen.

### Gate 1: playable spine

- The project launches.
- The player can perform the primary verb through real input.
- The world responds and exposes a goal or consequence.
- One screenshot shows a legible gameplay state.

### Gate 2: complete arc

- Title/start, gameplay, success, failure, result, and retry are reachable.
- A normal trace can move from start into the core loop.
- No scene transition strands the player or trace.

### Gate 3: depth

- Functional variants change decisions.
- Progression/escalation is visible.
- A late or alternate state is deterministic and demonstrable.

### Gate 4: authored presentation

- One asset language, palette, typography, and control style are applied across all states.
- Feedback makes actions and transitions readable.
- No default/debug presentation dominates the frame.

### Gate 5: proof

- Every trace validates and replays from a fresh launch.
- The recorded window contains useful change, not setup or idle time.
- The full demo set covers the coverage map.

## 4. Category review

Review categories separately because strength in one does not imply strength in another.

### Mechanics

Ask:

- Does player input cause the requested state change?
- Are legal and illegal actions handled?
- Do goals, consequences, victory, and defeat actually occur?
- Are mechanics simulated rather than shown as a label or scripted slideshow?

### Content depth

Ask:

- Are there at least three meaningful variants where appropriate?
- Do variants differ in function, not just name or color?
- Is there an upgrade, escalation, alternate layout, phase, branch, or late-game state?
- Can the evaluator see those states within the trace budget?

### Functional visuals

Ask:

- Can a viewer identify control, target, danger, legal action, objective, and outcome without guessing?
- Do HUD values update visibly after events?
- Are selection, hit, pickup, cooldown, warning, turn, timer, and result states visually distinct?
- Does every scenario remain readable at 1280x720?

### Art and presentation

Ask:

- Do title, gameplay, HUD, panels, characters, terrain, effects, and results share one art direction?
- Are sprites/assets doing the visual storytelling, or are raw rectangles and labels carrying the scene?
- Does the game have composition, hierarchy, spacing, transitions, and authored detail?
- Does it look like a small released game rather than an editor/debug view?

## 5. Time-pressure recovery

When behind schedule:

1. Freeze architecture changes.
2. Preserve the build and one working core loop.
3. Ensure at least one valid trace immediately.
4. Add deterministic scenarios for expensive-to-reach states.
5. Complete victory/defeat/result/retry.
6. Consolidate visuals around one strong asset pack and theme.
7. Add the highest-value depth axis visible in a short demo.
8. Remove broken or unproven features from UI and traces.

Do not spend the final window on new subsystems. Use it to improve visible evidence and eliminate zero-score risks.

## 6. Failure patterns

| Pattern | Why it fails | Recovery |
|---|---|---|
| Write-first mega scaffold | integration and presentation failures surface too late | build one complete vertical slice and render it early |
| Build-only validation | proves launch, not playability | use real input, scenarios, screenshots, and traces |
| One generic demo | cannot expose progression or alternate states | create focused deterministic scenarios |
| Ten near-identical demos | wastes evidence budget and can lower persistent mean quality | use fewer orthogonal demos |
| Labels as features | judge sees no behavioral consequence | connect state, action, feedback, and outcome |
| Color-only variants | weak functional and artistic distinction | change behavior, silhouette, animation, and feedback |
| Default UI over assets | reads as prototype and weakens art | theme all controls and integrate coherent imagery |
| Large silent maps | screenshots show empty space and unclear goals | increase meaningful visual density and guide framing |
| Late trace authoring | coordinates and states no longer match | write and replay traces alongside features |
| Random scenario setup | fresh launches diverge | seed every RNG and use fixed state construction |

## Design basis

This workflow combines progressive skill routing, explicit quality gates, proof-from-running-game, and structured Godot validation, adapted to GameCraft-Bench's interaction-grounded evaluation. Reference projects include:

- https://github.com/gamedev-skills/awesome-gamedev-agent-skills
- https://github.com/MRCalderon3D/everything-game-dev-code
- https://github.com/htdt/godogen
- https://github.com/haxqer/godot-skill
