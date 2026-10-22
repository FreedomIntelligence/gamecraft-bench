# Demonstration and scenario engineering

## Contents

1. Evidence design
2. Scenario design
3. Trace construction
4. Demo portfolio
5. Verification
6. Failure patterns

## 1. Evidence design

Treat demos as test cases with visual assertions. Each demo should answer:

- What requirement is this proving?
- What player input causes the evidence?
- What before/after state will be visible?
- Which seconds contain the decisive evidence?
- Does this demo strengthen or weaken persistent presentation/readability?

Name traces in evaluation order:

```text
001_title_to_core.json
002_primary_mechanic.json
003_variant_or_choice.json
004_progression.json
005_late_game.json
006_victory_result.json
007_defeat_retry.json
```

Only the first ten filenames are evaluated. Use zero-padded names and remove stale experiments.

## 2. Scenario design

Use scenarios when normal play cannot reach a proof state quickly and deterministically.

Good scenario fixtures:

- a battle with the correct unit selected and several legal targets available;
- a production chain with one missing connection for the player to complete;
- an upgrade screen with enough currency for one meaningful choice;
- a boss or final wave ready to start;
- a nearly completed objective requiring one final player action;
- low health near a visible hazard for failure proof;
- a narrative branch immediately before a consequential choice.

Bad scenario fixtures:

- a static gallery of all entities;
- an automatically playing cutscene that claims a mechanic;
- a victory screen loaded directly with no player-caused outcome;
- a debug menu containing feature labels;
- random state that varies between fresh processes.

Scenario initialization may compress setup, but the trace must still perform the relevant action and reveal the consequence.

## 3. Trace construction

Keep traces under 600 frames. Prefer 240-480 frames when enough.

### Key movement pattern

```json
{
  "scenario": "delivery_run",
  "duration_frames": 420,
  "events": [
    {"frame": 30, "type": "key_down", "keycode": "RIGHT"},
    {"frame": 120, "type": "key_up", "keycode": "RIGHT"},
    {"frame": 140, "type": "key_down", "keycode": "UP"},
    {"frame": 220, "type": "key_up", "keycode": "UP"},
    {"frame": 250, "type": "key_press", "keycode": "SPACE"},
    {"frame": 360, "type": "wait"}
  ]
}
```

### Click and drag pattern

```json
{
  "scenario": "machine_placement",
  "duration_frames": 360,
  "events": [
    {"frame": 30, "type": "mouse_down", "button": "left", "x": 1100, "y": 210},
    {"frame": 45, "type": "mouse_move", "x": 900, "y": 260},
    {"frame": 60, "type": "mouse_move", "x": 620, "y": 360},
    {"frame": 75, "type": "mouse_up", "button": "left", "x": 620, "y": 360},
    {"frame": 260, "type": "wait"}
  ]
}
```

Trace rules:

- use integer frames and coordinates;
- keep events in nondecreasing order;
- balance every held key and mouse button with an `up` event;
- allow a short settling window before the first action;
- leave enough post-action frames for feedback and state change;
- avoid excessive idle time;
- keep mouse targets at least 32-48 pixels across when possible;
- do not place critical controls within a few pixels of window edges;
- do not reuse coordinates after UI layout changes without replaying.

## 4. Demo portfolio

Cover different evidence, not different camera views of the same evidence.

| Demo | Typical proof |
|---|---|
| Title-to-core | authored title/briefing, start flow, normal input, first response |
| Primary mechanic | irreducible player action, rule, consequence, feedback |
| Variant/choice | functionally distinct entity, card, tool, route, ability, or branch |
| Progression | currency/XP/research/upgrade changes future play |
| Late-game | escalation, denser state, boss, advanced layout, final phase |
| Victory | player action completes goal; result and retry are visible |
| Defeat | visible cause, loss state, result, and retry |
| Genre showcase | combo, drift, rhythm chain, dialogue consequence, tactical turn, etc. |

Five strong demos are better than ten weak ones. Add a demo only if it covers a new requirement or provides necessary persistent evidence.

## 5. Verification

Run the bundled validator first:

```bash
python3 <skill-root>/scripts/validate_submission.py /workspace/game
```

Then verify every scenario visually with the provided screenshot helper:

```bash
/workspace/tools/screenshot.sh --path /workspace/game \
  -- --out /workspace/core.png --frames 90 --scenario core_loop
```

If that benchmark helper is absent, use `scripts/capture_screenshot.sh` from this skill with the same `--path`, `--out`, `--frames`, and `--scenario` arguments.

Finally replay the actual trace through the benchmark verifier when available. Screenshot initialization alone does not prove trace coordinates or timing.

Check determinism by replaying the same trace from two fresh launches and comparing the key visible outcome. Small particle differences are acceptable only if the mechanic, UI values, result, and evidence state remain identical.

## 6. Failure patterns

| Symptom | Likely cause | Fix |
|---|---|---|
| Demo remains on title | stale coordinate, overlay, scenario not parsed | inspect first frame; enlarge target; parse user args |
| Held key never stops | missing `key_up` | balance input events |
| Click selects wrong tile | stretch/camera transform or moving UI | test at 1280x720; stabilize layout |
| Feature happens off-screen | camera or spawn position | initialize proof state inside the composed frame |
| Judge misses fast effect | transient shorter than sampled interval | add persistent feedback/outcome |
| Late state differs per replay | unseeded RNG or time-based setup | seed and construct fixed state |
| Demo lowers visual quality | debug fixture or crowded UI | make scenario a player-facing authored state |
| Ten demos still miss depth | redundant evidence | replace duplicates with progression/variant scenarios |
