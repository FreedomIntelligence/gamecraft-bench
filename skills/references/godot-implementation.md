# Godot 4 implementation playbook

## Contents

1. Project baseline
2. Scene and state structure
3. Scenario entry points
4. Input and replay stability
5. Data-driven depth
6. UI and feedback wiring
7. Build and runtime traps

## 1. Project baseline

Target the installed Godot 4 version; GameCraft-Bench currently pins Godot 4.6.2. Check with `godot --version` before relying on version-sensitive APIs.

Set a stable 1280x720 canvas in `project.godot`:

```ini
[application]
run/main_scene="res://Main.tscn"

[display]
window/size/viewport_width=1280
window/size/viewport_height=720
window/size/window_width_override=1280
window/size/window_height_override=720
window/stretch/mode="canvas_items"
```

Use the actual section syntax written by the installed engine when possible. Preserve an existing coherent project configuration.

Recommended project shape:

```text
/workspace/game/
  project.godot
  Main.tscn
  scripts/
    main.gd
    game_state.gd
    scenario_loader.gd
  scenes/
    title/
    gameplay/
    results/
  data/
  assets/
  demo_outputs/
```

Keep resources local to the game. Copy selected mounted assets into `res://assets/...` and preserve required license files.

## 2. Scene and state structure

Use a shallow composition that remains easy to inspect and reset:

- `Main`: owns the application flow and scenario initialization.
- `World`: owns gameplay entities, map, and rules.
- `HUD` on `CanvasLayer`: mirrors state and emits UI actions.
- modal screens or panels: title, briefing, upgrade, pause, result.
- `GameState`: central typed state or resource; avoid spreading authoritative state across labels and sprites.

Represent the lifecycle explicitly:

```gdscript
enum Phase { TITLE, BRIEFING, PLAYING, UPGRADE, VICTORY, DEFEAT }
var phase: Phase = Phase.TITLE
```

Use one function for phase transitions. It should update interaction locks, visibility, focus, HUD, and any scenario-specific timers together. Do not let multiple panels remain interactive behind one another.

Use signals for visible state changes:

```gdscript
signal resources_changed(value: int)
signal objective_changed(text: String)
signal phase_changed(phase: Phase)
signal player_hit(amount: int)
```

Update labels, meters, effects, and sounds from these signals. This creates reusable proof hooks and reduces stale UI.

## 3. Scenario entry points

Parse user arguments early in `_ready()` and initialize before normal flow begins:

```gdscript
func _ready() -> void:
    var scenario := _scenario_from_args(OS.get_cmdline_user_args())
    if scenario.is_empty():
        _show_title()
    else:
        _load_scenario(scenario)

func _scenario_from_args(args: PackedStringArray) -> String:
    var index := args.find("--scenario")
    if index >= 0 and index + 1 < args.size():
        return args[index + 1]
    return ""

func _load_scenario(id: String) -> void:
    seed(104729)
    match id:
        "core_loop":
            _start_game({"level": 1, "variant": 0})
        "upgraded":
            _start_game({"level": 3, "upgrades": ["speed", "capacity"]})
        "near_victory":
            _start_game({"level": 2, "objective_left": 1})
        "near_defeat":
            _start_game({"health": 1, "hazard_active": true})
        _:
            push_warning("Unknown scenario: %s" % id)
            _show_title()
```

Requirements for every named scenario:

- build the same state on every fresh process;
- have no hidden warm-up dependency;
- place the camera and UI before the first meaningful frame;
- accept input immediately;
- keep the requested state reachable through real input after initialization;
- avoid auto-completing the feature before the trace can act.

Use fixed arrays and local `RandomNumberGenerator` instances with explicit seeds. Do not rely on frame timing, system time, or unordered directory iteration.

## 4. Input and replay stability

Use named `InputMap` actions for continuous gameplay and normal key events for stable UI shortcuts. Keep benchmark-supported keys in mind.

For continuous movement:

```gdscript
func _physics_process(delta: float) -> void:
    var direction := Input.get_vector("move_left", "move_right", "move_up", "move_down")
    velocity = direction * move_speed
    move_and_slide()
```

For click interaction, keep targets large and stable. Connect `Control` signals for UI. For world clicks, convert viewport coordinates through the active camera once and test at 1280x720.

Replay-safe interaction rules:

- never depend on hover alone;
- use generous hit areas;
- keep interactive controls clear of changing text widths;
- avoid moving buttons under the cursor;
- do not require double-click or pixel-perfect drag unless essential;
- keep focus and mouse filters intentional;
- do not let transparent overlays consume clicks;
- debounce state transitions without swallowing the next scheduled event.

For held input traces, handle `key_down` and `key_up` as normal engine state. Avoid implementing movement only in `_input(event)`; polling in physics is more stable.

## 5. Data-driven depth

Prefer compact data definitions over copy-pasted scenes:

```gdscript
const ENEMY_TYPES := [
    {"id": "runner", "speed": 150.0, "hp": 1, "damage": 1},
    {"id": "tank", "speed": 55.0, "hp": 4, "damage": 2},
    {"id": "shooter", "speed": 80.0, "hp": 2, "range": 260.0},
]
```

For each variant, connect four layers:

1. different data or rule;
2. different behavior under play;
3. different silhouette/asset/animation;
4. different feedback and decision consequence.

Use the same approach for cards, crops, customers, unit classes, upgrades, routes, puzzles, dialogue branches, hazards, tracks, and bosses.

## 6. UI and feedback wiring

Use `Control` nodes and containers for HUDs and menus. Use anchors for outer regions and containers for child layout. Attach a `Theme` at the root so panels, buttons, labels, meters, and tooltips share typography and colors.

Use tweened transient feedback without changing simulation state:

- scale pop and number rise on pickups/resources;
- short flash and health shake on damage;
- selection outline/pulse on legal targets;
- banner or panel transition on phase changes;
- particles or sprite burst for success/destruction;
- short camera shake only for important impact.

Keep feedback visible for sampled frames. An effect that lasts one frame may disappear from 2-FPS evidence; combine it with a persistent changed state, icon, meter, or result.

## 7. Build and runtime traps

Run engine flags before user args:

```bash
godot --headless --quit-after 5 --path /workspace/game
godot --headless --quit-after 5 --path /workspace/game -- --scenario upgraded
```

Common failures:

| Failure | Check |
|---|---|
| Builds but black screen | main scene, camera current state, root visibility, clear color, asset imports |
| Scenario ignored | `--` placement and `OS.get_cmdline_user_args()` parsing |
| Click misses | viewport stretch, anchors, mouse filters, overlay controls, moving targets |
| UI overlaps | container sizing, custom minimum sizes, text wrapping, 1280x720 capture |
| Missing asset | `res://` path case, copied file, import completion, source not mounted at evaluation |
| Collision looks correct but fails | layer/mask, shape size/offset, body type, monitoring state |
| Timer diverges | use deterministic state and delta-based simulation; seed RNG |
| Trace hangs on menu | scenario did not skip modal or input focus was not established |
| Scene loads but later state crashes | validate every proof scenario, not only boot |

Fix parse errors first, then resource/load errors, runtime errors, input/state errors, and finally presentation warnings. Re-run the exact failed scenario after each fix.
