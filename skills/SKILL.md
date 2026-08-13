---
name: gamecraft-create
description: Build, repair, and polish complete 2D Godot 4 micro-games from natural-language specifications, with special support for GameCraft-Bench and similar interaction-grounded game-generation tasks. Use when an agent must create a launchable Godot project, infer observable requirements from a game brief, select and integrate coherent assets, implement mechanics and progression, add readable UI and game feel, create deterministic scenario entry points and replay traces, inspect rendered gameplay, or preflight a submission for build, trace, visual, content-depth, and presentation failures.
---

# GameCraft Create

Build a game that proves itself through play. Treat source code as implementation, the running Godot project as the artifact, and replayed gameplay as the evidence.

## Load only what the task needs

- Read [benchmark-contract.md](references/benchmark-contract.md) for GameCraft-Bench paths, scoring, trace constraints, and hard gates.
- Read [score-aware-production.md](references/score-aware-production.md) before planning a new game or recovering a weak prototype.
- Read [godot-implementation.md](references/godot-implementation.md) when creating project structure, gameplay state, UI, scenarios, or input in Godot 4.
- Read [art-and-ui.md](references/art-and-ui.md) when selecting assets, defining the visual language, laying out the HUD, or polishing presentation.
- Read [demos-and-scenarios.md](references/demos-and-scenarios.md) before implementing scenario entry points or writing replay traces.
- Read [genre-recipes.md](references/genre-recipes.md) for the dominant family; do not load unrelated genre sections.
- Read [visual-debugging.md](references/visual-debugging.md) when the project boots, but the rendered result or demos remain weak.

## Non-negotiable outcome

For GameCraft-Bench, deliver both:

1. A self-contained Godot project at `/workspace/game` that launches cleanly.
2. One to ten deterministic replay traces at `/workspace/game/demo_outputs/*.json` that visibly exercise the game.

A clean build without useful traces is incomplete. A convincing screenshot without player-controlled state change is incomplete. A functioning mechanic shown with placeholder presentation is still a weak submission.

## Production loop

### 1. Inspect before writing

1. Read the entire specification and all environment/tool instructions.
2. Inspect Godot version, workspace contents, asset libraries, helper scripts, and the exact launch command.
3. If a project exists, run it and inspect screenshots before modifying it.
4. Identify the dominant interaction archetype and genre. Read only the matching references.

Prefer the benchmark's `/workspace/tools/screenshot.sh` when present. Otherwise use the bundled `scripts/capture_screenshot.sh` on Linux with Godot and Xvfb available.

Do not begin with a large write-first scaffold. Establish the contract and the evidence plan first.

### 2. Build an observable coverage map

Translate the brief into player-visible requirements. Maintain a compact table with:

| Requirement | Category | Player action | Visible state change | Proof scenario | Proof trace |
|---|---|---|---|---|---|

Use the four categories `M` mechanics, `D` content depth, `V` functional visuals, and `A` art/presentation. Infer likely hidden rubric items from phrases in the specification, but never claim access to a hidden rubric.

Every major requirement must have all three: implementation, a reachable state, and observable evidence. If a requirement cannot fit into a deterministic 20-second demonstration, add a scenario entry point or reduce scope while preserving the player-facing promise.

### 3. Establish the vertical slice

Implement one short but complete arc early:

`title -> start/briefing -> player action -> system response -> goal/failure -> result -> retry`

Make the first slice launchable, controllable, and visually legible before adding breadth. Use real project assets early enough that scale, collision, framing, and UI are validated against the final visual language.

### 4. Add depth deliberately

Expand along orthogonal axes instead of cloning content:

- at least three functionally distinct entities, abilities, orders, cards, upgrades, encounters, or level variants when the brief implies variety;
- a visible progression or escalation state;
- both success and failure consequences;
- a late-game, upgraded, boss, result, or alternate-state scenario;
- differences that change decisions, not labels or colors only.

Prioritize content and presentation after the core loop works. They carry most of the benchmark weight and are common failure modes.

### 5. Make state readable and authored

At 1280x720, make the following unambiguous without source inspection:

- what the player controls;
- current goal and available action;
- selected, targeted, legal, dangerous, damaged, completed, and failed states;
- resource, timer, health, progress, or turn changes;
- transitions between title, play, upgrade/briefing, victory, defeat, and retry.

Use a coherent asset pack, palette, typography, spacing system, and styled controls. Avoid default widgets, raw debug geometry, dense text, decorative labels standing in for behavior, and unrelated asset packs.

### 6. Close the render-debug loop

After every meaningful slice:

1. Run the build gate.
2. Capture the relevant normal or named scenario.
3. Inspect the image, not just its existence.
4. Exercise the same input path the trace will use.
5. Fix visible and runtime failures, then repeat.

Inspect at least title, normal gameplay, a dense or late-game state, victory, and defeat. Use [visual-debugging.md](references/visual-debugging.md) for the failure order.

### 7. Engineer demonstrations as part of the game

Create traces while features are implemented, not at the end. Prefer five to eight short, purposeful demos over ten redundant ones:

- normal title-to-core-loop flow;
- primary mechanic and consequence;
- distinct content/ability variant;
- progression, upgrade, or late-game state;
- victory/result/retry;
- failure or hazard when important;
- one genre-specific showcase.

Keep coordinates stable, seed randomness, start accepting input immediately in scenario mode, and remove dead time. Read [demos-and-scenarios.md](references/demos-and-scenarios.md) before writing traces.

### 8. Preflight and stop only on evidence

Run:

```bash
python3 <skill-root>/scripts/validate_submission.py /workspace/game
```

The validator runs the normal build gate and, by default, smoke-launches every named trace scenario when Godot is available. Also replay or screenshot every submitted scenario. Finish only when:

- the project boots with the benchmark command and logs contain no parse/runtime errors;
- every trace is valid and deterministic;
- every claimed major feature is visible in at least one replay;
- persistent visual qualities remain good across all relevant demos;
- no demo exposes broken menus, overlapping UI, off-screen content, placeholder art, or long idle periods.

## Bundled tools

### Find coherent assets

```bash
python3 <skill-root>/scripts/asset_finder.py \
  /workspace/assets/library /workspace/assets/library-oga \
  --query "harbor boat water ui font" --limit 40
```

Searches by path and type and reports nearby license files. Copy chosen assets into the project; do not reference read-only libraries directly.

### Build a contact sheet

```bash
python3 <skill-root>/scripts/contact_sheet.py \
  /path/to/candidate/pack --output /workspace/asset-sheet.png --limit 80
```

Inspect the resulting image before committing to a pack.

### Capture a rendered scenario outside the benchmark image

Use this only when `/workspace/tools/screenshot.sh` is absent:

```bash
bash <skill-root>/scripts/capture_screenshot.sh \
  --path /workspace/game \
  --out /workspace/core-loop.png --frames 90 --scenario core_loop
```

This launches a real X11/OpenGL rendering path under Xvfb. It is not a substitute for replaying the actual trace.

### Validate the submission contract

```bash
python3 <skill-root>/scripts/validate_submission.py /workspace/game --json
```

The validator checks structure, display settings, asset references, trace schema, scenario evidence, placeholder-risk heuristics, and the Godot build gate when `godot` is available. Treat warnings as review prompts; inspect the game before deciding they are safe.

## Time allocation

Use this default budget unless the task dictates otherwise:

- 10% inspect, decompose, and plan evidence;
- 25% implement the complete core arc;
- 20% add meaningful content and progression;
- 25% integrate art, UI, feedback, and transitions;
- 20% capture, inspect, repair, and validate demos.

When time becomes tight, preserve a coherent complete arc and strong proof. Cut unproven side systems before cutting build verification, scenarios, traces, visual inspection, or result states.

## Guardrails

- Do not expose, reconstruct, or hard-code hidden benchmark rubrics.
- Do not fake interaction with self-playing showcase logic when player input is required. Scenarios may initialize state; traces must still demonstrate requested player actions.
- Do not use labels, colors, or static screens as substitutes for functional content.
- Do not stop at launch success.
- Do not spend time on audio-only qualities for a visually scored benchmark; make rhythm, warning, and impact cues visible as well.
- Do not add external dependencies when native Godot nodes and bundled assets suffice.
