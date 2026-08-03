# Art, UI, and functional visuals

## Contents

1. Asset-first workflow
2. Micro art bible
3. Scene composition
4. Functional visual language
5. UI system
6. Polish pass
7. Acceptance checks

## 1. Asset-first workflow

GameCraft-Bench supplies large mounted asset libraries. Browse them before inventing placeholder geometry.

1. Extract nouns, materials, mood words, UI motifs, and required states from the brief.
2. Search candidate packs with `scripts/asset_finder.py`.
3. Build contact sheets for the best two or three packs.
4. Choose one primary pack and at most one compatible support pack.
5. Copy required files and license notices into the project.
6. Validate real sprite dimensions and import behavior before layout and collisions solidify.
7. Record the chosen palette, font, outline, scale, and UI style in a short art-bible note.

Do not reference `/workspace/assets/...` at runtime. Those mounts are discovery sources; the submitted project must be self-contained.

If no coherent pack exists, create a deliberate restricted style with authored sprites or generated raster assets where tools permit. Avoid turning raw Godot rectangles, circles, lines, and default controls into the dominant visual language.

## 2. Micro art bible

Decide these before polishing:

| Decision | Example |
|---|---|
| Mood | cozy maritime logistics with quiet urgency |
| Palette | deep navy, sea green, sunlit cream, coral accent |
| Sprite scale | 32px source sprites rendered at 2x or 3x consistently |
| Edge language | crisp pixel edges or soft painted edges, never mixed casually |
| Typography | one display face plus one readable UI face |
| Panel language | dark translucent cards with cream borders and 8px corners |
| Feedback colors | cyan selection, amber warning, red danger, green completion |
| Motion | buoyant ease-out for rewards, sharp punch for damage |

Apply the same decisions to title, gameplay, HUD, briefing, upgrade, and result screens.

## 3. Scene composition

Use the full 1280x720 frame intentionally:

- establish a clear focal play area;
- reserve stable HUD zones rather than floating labels over action;
- use landmarks, framing, paths, lanes, or contrast to guide attention;
- avoid large empty fields, accidental dead margins, and tiny central gameplay;
- separate foreground interactables from decorative background by contrast and silhouette;
- keep camera motion bounded so UI and objectives remain visible.

For dense management/strategy screens, use a dominant board or world region plus one consistent side/bottom control region. For continuous-action games, keep the world dominant and the HUD compact.

## 4. Functional visual language

Encode state with more than color:

| State | Combine at least two channels |
|---|---|
| Selected | outline/halo + scale/pulse + info panel |
| Legal action | tile/icon highlight + cursor/arrow + short instruction |
| Illegal action | blocked marker + shake/flash + no state mutation |
| Damage | sprite flash + impact motion + health change |
| Pickup/delivery | carried sprite/icon + HUD update + target marker |
| Danger | telegraph shape/sprite + warning icon + countdown |
| Cooldown | radial/bar fill + dimmed icon + remaining value |
| Progression | meter/unlock animation + changed stats/world visuals |
| Victory/defeat | stable authored result screen + cause/stats + retry |

Keep important state persistent long enough to appear in sampled evidence. Pair fast effects with a lasting visual outcome.

## 5. UI system

Use `CanvasLayer` for screen-space UI and `Control` containers for layout.

Quality bar:

- all controls use a shared theme;
- buttons have normal, hover/focus, pressed, and disabled states;
- text has sufficient contrast and does not clip;
- hierarchy distinguishes game title, section, objective, value, and helper text;
- numeric values align and update without reflowing the entire layout;
- progress bars and meters include meaningful labels/icons;
- result and upgrade screens visually belong to the same game;
- keyboard/mouse focus is obvious where applicable.

Avoid showing every internal variable. Display the decision-relevant state and use short, player-facing language.

## 6. Polish pass

Apply polish in this order:

1. composition and camera framing;
2. asset coherence and scale;
3. state readability and HUD hierarchy;
4. transitions between game phases;
5. action feedback and game feel;
6. environmental detail and ambient motion;
7. final text, spacing, and edge cleanup.

High-value, low-risk additions:

- parallax or subtle background motion;
- animated water, conveyor, glow, dust, stars, fog, or foliage;
- themed panel textures, borders, icons, and cursor;
- brief tweened screen transitions;
- objective markers and world-space feedback;
- distinct victory/defeat illustrations or compositions;
- small idles on characters/machines/entities.

Do not add polish that obscures state or makes traces unreliable.

## 7. Acceptance checks

Inspect screenshots from title, normal gameplay, busiest/late state, victory, and defeat.

Reject the pass if any frame shows:

- default gray Godot widgets or debug text as the dominant UI;
- raw geometry standing in for requested characters, terrain, cards, machines, or props;
- inconsistent sprite scaling or multiple unrelated art styles;
- unreadable text, clipped panels, overlap, or off-screen UI;
- unclear selected/target/hazard/objective state;
- empty composition or excessive unused space;
- result screens that look unrelated to gameplay;
- labels claiming features not visible in play.

The benchmark judge is slightly permissive on content and presentation relative to preliminary humans; do not use that as a target. Build to an authored vertical-slice standard.
