# Visual debugging loop

## Contents

1. Minimum loop
2. Capture matrix
3. Triage order
4. Frame review
5. Runtime review
6. Final evidence review

## 1. Minimum loop

For every meaningful feature:

1. run the exact build command;
2. capture the target state;
3. inspect the actual image;
4. exercise the input path;
5. capture the resulting state;
6. inspect logs and warnings;
7. fix one failure class at a time;
8. repeat the same scenario.

Never infer visual success from a zero exit code.

## 2. Capture matrix

Maintain this minimum matrix:

| State | What to inspect |
|---|---|
| Title/briefing | identity, style, start affordance, hierarchy, no dead controls |
| Normal play | core loop, camera, HUD, objective, controlled entity, world density |
| Primary action after-state | state change, feedback, value update, consequence |
| Dense/late state | overlap, readability, performance, progression visibility |
| Upgrade/choice | costs, effects, affordance, purchased/disabled state |
| Victory | cause, result, stats, authored transition, retry |
| Defeat | visible cause, result, retry, no stuck simulation |

Use the benchmark screenshot helper when present:

```bash
/workspace/tools/screenshot.sh --path /workspace/game \
  -- --out /workspace/frame.png --frames 90 --scenario core_loop
```

If the helper is unavailable on Linux, use the bundled rendered fallback:

```bash
bash <skill-root>/scripts/capture_screenshot.sh \
  --path /workspace/game \
  --out /workspace/frame.png --frames 90 --scenario core_loop
```

It requires `godot` and `Xvfb`. Headless build output alone is not a visual capture.

## 3. Triage order

Fix in this order to avoid polishing invalid states:

1. project/scene/script parse failures;
2. missing assets and black/empty frames;
3. broken input, rules, collisions, and state transitions;
4. camera framing and off-screen content;
5. UI clipping, overlap, hierarchy, and mouse interception;
6. unclear state and missing feedback;
7. inconsistent art, scale, palette, and default widgets;
8. motion polish and environmental detail;
9. trace timing and evidence density.

## 4. Frame review

For each frame, answer in five seconds:

- What is the game?
- What can the player act on?
- What is the immediate objective?
- What changed recently or is about to happen?
- Does this look authored or debug-like?

If any answer requires reading tiny helper text or knowing the code, strengthen visual hierarchy and feedback.

Check edges and dense regions at full resolution. Common defects include:

- clipped labels and buttons;
- world objects behind opaque HUD panels;
- status colors with insufficient contrast;
- small sprites on large empty backgrounds;
- inconsistent texture filtering or sprite scale;
- camera exposing outside the level;
- overlays blocking mouse events;
- result screens with gameplay still visibly running underneath;
- tooltips or debug banners left open in proof states.

## 5. Runtime review

After visual inspection, scan logs for `SCRIPT ERROR`, `Parse Error`, `ERROR`, and `WARNING`. Test each named scenario separately because late states exercise different code paths.

Use bounded commands:

```bash
timeout 15s godot --headless --path /workspace/game --quit-after 5
timeout 15s godot --headless --path /workspace/game --quit-after 5 -- --scenario upgraded
```

Do not use an interactive debugger flag in automation. Treat timeout, repeated error spam, and resource warnings as unfinished work even if a screenshot appeared.

## 6. Final evidence review

Review demos as a portfolio:

- no two demos are redundant;
- every major requirement has a visible before/action/after chain;
- persistent visual quality remains high across the set;
- no demo shows startup/import delay, a dead menu, or long idle time;
- victory and defeat arise from replayed input when required;
- late-state scenarios still look like the same authored game;
- every coordinate and timing remains correct after the last UI change.

The final claim should be “the trace visibly proves it,” not “the code contains it.”
