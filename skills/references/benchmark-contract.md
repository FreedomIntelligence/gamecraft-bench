# GameCraft-Bench contract

Use this reference only for GameCraft-Bench or a task that adopts the same delivery protocol.

## Contract at a glance

GameCraft-Bench evaluates a complete Godot 4 game plus replayable input evidence. The benchmark is engine-grounded, artifact-complete, and interaction-verified.

| Element | Required behavior |
|---|---|
| Project root | `/workspace/game/` |
| Core files | `project.godot`, launchable main scene, scripts/scenes/assets used at runtime |
| Build gate | `godot --headless --path /workspace/game --quit-after 5` |
| Viewport | fixed 1280x720 during replay |
| Traces | 1-10 JSON files under `demo_outputs/`; only first 10 by filename |
| Replay rate | 30 frames per second |
| Duration | no more than 600 frames / 20 seconds per trace |
| Evidence | recorded gameplay video plus frames sampled at 2 FPS |
| Freshness | each trace launches a fresh game instance |

If the project cannot launch or no trace parses, the final score is zero.

## What is scored

The benchmark uses four categories with default weights:

| Category | Weight | What visible evidence must establish |
|---|---:|---|
| Core Mechanics (`M`) | 0.15 | Rules, action-response loop, goals, consequences, success/failure |
| Content Depth (`D`) | 0.35 | Variety, progression, alternate or late states, meaningful functional differences |
| Functional Visuals (`V`) | 0.15 | Readable state, feedback, objectives, warnings, stable 1280x720 UI |
| Art & Presentation (`A`) | 0.35 | Coherent authored visual direction and a publishable vertical-slice feel |

The project must be complete, but completeness alone does not score. The judge sees replayed evidence and scores requirements that are visibly demonstrated.

Scenario-specific properties generally benefit from a demo that clearly shows the state once. Persistent qualities such as readability, visual feedback, art consistency, UI overlap, and presentation must remain strong across demos; one polished screenshot cannot compensate for weak persistent evidence.

## Trace schema

```json
{
  "scenario": "upgraded_run",
  "duration_frames": 450,
  "events": [
    {"frame": 30, "type": "mouse_click", "button": "left", "x": 320, "y": 360},
    {"frame": 90, "type": "key_press", "keycode": "SPACE"},
    {"frame": 300, "type": "wait"}
  ]
}
```

`scenario` is optional. Supported event types:

- `mouse_click`, `mouse_down`, `mouse_up`: require `button` (`left` or `right`) and integer `x`, `y` inside the viewport.
- `mouse_move`: requires integer `x`, `y`.
- `key_press`, `key_down`, `key_up`: require a keycode in `A-Z`, `0-9`, `ESCAPE`, `ENTER`, `SPACE`, `TAB`, `BACKSPACE`, `DELETE`, `SHIFT`, `CTRL`, `ALT`, `UP`, `DOWN`, `LEFT`, or `RIGHT`.
- `wait`: requires only `frame` and `type`.

Frames must be non-negative, time ordered, and no later than `duration_frames`.

## Scenario behavior

The evaluator launches a trace with a scenario similarly to:

```bash
godot --path /workspace/game -- --scenario upgraded_run
```

Engine flags must precede `--`; user arguments follow it. Scenario mode must:

1. parse `OS.get_cmdline_user_args()`;
2. skip menus when appropriate;
3. seed random generators;
4. initialize the named state deterministically;
5. render the state fully;
6. accept trace input immediately.

Scenarios are state fixtures, not prerecorded gameplay. Use them to make late-game or rare states reachable within the evidence window, then let replayed input demonstrate the behavior.

## Empirical implications from the paper

- Strong agents often build launchable projects but still score poorly; build success is only the admission gate.
- Mechanics tend to score higher than content and presentation. Allocate explicit passes to depth and art instead of continuing to add code to the core mechanic.
- Rendered-screen inspection exposes camera, UI, layout, feedback, and evidence failures that logs cannot.
- Tool-call volume is not a quality signal. A write-first, shell-heavy loop can miss demo delivery entirely.
- Mechanics, content, visuals, and art are only partially coupled. Review them as separate quality axes.

## Current public baseline context

The paper's initial strongest result was 41.46%. The public leaderboard later reported stronger configurations, including 60.50% for Codex with GPT-5.6-sol high and 65.70% for Claude Code with Fable 5 high as of July 2026. The task is still far from saturated; a harness should target systematic coverage and evidence rather than rely on model strength alone.

## Sources

- GameCraft-Bench paper: https://arxiv.org/abs/2606.17861
- Benchmark code and task contract: https://github.com/FreedomIntelligence/gamecraft-bench
- Project page and public leaderboard: https://tongxuluo.github.io/gamecraft-bench-website/
