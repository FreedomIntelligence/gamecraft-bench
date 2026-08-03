# Genre recipes for GameCraft-Bench

## Contents

1. How to use this reference
2. Continuous-action families
3. Rule-and-board families
4. Progression-and-economy families
5. Exploration-and-narrative families
6. Cross-family quality floor

## 1. How to use this reference

Read only the dominant family and any clearly required secondary pattern. A recipe is a coverage guide, not a fixed implementation. Preserve the specification's fantasy, mechanics, and art direction.

For every family, complete the arc, add meaningful depth, expose state visually, and design scenarios before traces.

## 2. Continuous-action families

### Platformer

- **Core loop:** responsive movement plus the brief's defining verb: jump/dash/climb/dig/fly/deliver/transform; hazards and a spatial goal must respond to input.
- **Depth:** three obstacle or enemy patterns, at least two terrain/level rhythms, collectibles or ability progression, a finish/failure state.
- **Functional visuals:** grounded/airborne state, hazards, checkpoints, goals, damage, pickups, and route affordances must be obvious.
- **Proof scenarios:** tutorial segment; signature mechanic challenge; upgraded/late segment; near-goal victory; low-health hazard defeat.
- **Trap:** building a generic run-and-jump controller while the named fantasy remains decorative.

### Shooter

- **Core loop:** aim/move/fire, hit detection, enemy threat, damage, death, and a clear objective.
- **Depth:** three enemy behaviors or weapon modes, wave/mission escalation, pickup or upgrade, boss/final wave.
- **Functional visuals:** projectile/aim direction, hit confirmation, enemy telegraph, health/ammo/cooldown, objective, wave state.
- **Proof scenarios:** combat arena; weapon/ability variant; dense wave; boss/near-victory; overwhelmed defeat.
- **Trap:** lots of projectiles with no readable targeting, enemy behavior, or objective progression.

### Racing

- **Core loop:** steer/accelerate/brake or drift with track boundaries, checkpoints/laps, timer/place, and finish state.
- **Depth:** multiple track sections or layouts, surface/hazard/boost variety, vehicle upgrade or rival behavior.
- **Functional visuals:** next checkpoint, route, speed, drift/boost state, lap progress, collision, finish.
- **Proof scenarios:** clean start; drift/boost section; alternate track/hazard; final lap; timeout/crash failure.
- **Trap:** moving a vehicle in an empty field without a verifiable race structure.

### Rhythm

- **Core loop:** timed visible cues, player response window, hit grading, combo/score, miss consequence, song/end state.
- **Depth:** at least three patterns or lanes, increasing density, modifier or phase, final sequence.
- **Functional visuals:** approach timing, hit window, grade, combo, beat/progress, misses. Make audio-dependent information visible.
- **Proof scenarios:** basic pattern; mixed pattern; high-combo dense section; near-finish; miss/failure.
- **Trap:** relying on audio or automatic note playback when the judge evaluates visual interaction.

### Sports

- **Core loop:** the sport's irreducible action, scoring/rules, opponent or challenge, round/match result.
- **Depth:** multiple techniques, targets/opponents, difficulty phases, tournament/progression or stat upgrade.
- **Functional visuals:** aim/power/timing, legal area, score, round state, opponent response, success/foul/failure.
- **Proof scenarios:** tutorial action; advanced technique; competitive round; match point; loss/foul.
- **Trap:** presenting a themed minigame whose mechanics do not express the named sport.

## 3. Rule-and-board families

### Strategy

- **Core loop:** select, inspect legal actions, commit move/build/attack, resolve opponent/world response, repeat toward victory or defeat.
- **Depth:** three functionally distinct units/buildings/resources, terrain or positional rule, multiple layouts or escalation.
- **Functional visuals:** ownership, selection, legal/illegal cells, range, targets, turn/phase, HP/resources, objectives.
- **Proof scenarios:** first tactical turn; unit/ability contrast; terrain/objective interaction; near-victory; near-defeat.
- **Trap:** static board art or scripted combat with no player-controlled decision and response.

### Card game

- **Core loop:** deck/hand/board/discard or equivalent zones, playable-card rules and costs, resolution, opponent/round response, win/loss.
- **Depth:** card archetypes with real rule differences, synergy/status/economy, multiple encounters or deck progression.
- **Functional visuals:** readable cards, costs, legal targets, played effects, zone changes, turn, health/score, disabled states.
- **Proof scenarios:** normal hand and play; target/combination; archetype/synergy; late encounter; victory/defeat.
- **Trap:** cards as labeled buttons with no spatial zones, rules, animation, or observable consequence.

### Puzzle

- **Core loop:** manipulate a state under a clear rule, receive immediate valid/invalid feedback, progress toward a solved state.
- **Depth:** at least three levels or rule combinations, increasing complexity, undo/reset, completion flow.
- **Functional visuals:** interactable pieces, constraints, legal/illegal state, progress, solved feedback, next-level affordance.
- **Proof scenarios:** basic rule; compound mechanic; advanced level; one move from solution; failed/invalid state.
- **Trap:** several static boards that do not differ in reasoning or lack reset/solution feedback.

### Simulation

- **Core loop:** inspect a changing system, make a constrained decision, see causal consequences, manage toward an objective.
- **Depth:** multiple actors/resources/events, competing tradeoffs, escalation or shifts/days, success and failure outcomes.
- **Functional visuals:** system state, queues/flows, alerts, cause/effect, resource changes, time/phase, objective health.
- **Proof scenarios:** normal operation; decision with consequence; crisis/dense state; successful resolution; system failure.
- **Trap:** dashboard values changing automatically with little meaningful player control.

## 4. Progression-and-economy families

### Tycoon

- **Core loop:** earn, spend/place/upgrade, watch production/service respond, reinvest toward a milestone.
- **Depth:** three business/production elements, meaningful upgrade branches, bottleneck or demand variation, new tier/area.
- **Functional visuals:** placement legality, flows/queues, income/cost, capacity, satisfaction/throughput, unlocks.
- **Proof scenarios:** first purchase; functioning chain/service; upgrade choice; mature layout; milestone/result.
- **Trap:** clickable income counter with decorative buildings disconnected from production logic.

### Idle

- **Core loop:** automatic production plus active purchase/placement/optimization; visible rate growth and prestige/reset logic when specified.
- **Depth:** multi-stage chain or generators, upgrades with different effects, unlock thresholds, late state/prestige.
- **Functional visuals:** production motion, rate, inventory/currency, costs, bottlenecks, locked/unlocked and purchased states.
- **Proof scenarios:** initial purchase; operating chain; upgrade impact; advanced/prestige-ready; prestige/restart.
- **Trap:** numbers rise, but entities, chains, upgrades, and world state never visibly change.

## 5. Exploration-and-narrative families

### Open world

- **Core loop:** traverse a bounded but dense world, discover landmarks/characters/resources, perform the defining interaction, complete objectives.
- **Depth:** distinct regions or landmarks, several activities/quests, inventory/progression, world-state change.
- **Functional visuals:** player/location, routes/landmarks, interaction prompts, objective markers, inventory/status, discovered/completed state.
- **Proof scenarios:** starting hub; signature activity; second region/content type; progressed inventory/world; objective completion/failure.
- **Trap:** a large empty map whose scale consumes time and frame area without meaningful content.

### Roguelike

- **Core loop:** enter encounter/room, make combat or rule decisions, gain loot/upgrade, move to next room, risk death/restart.
- **Depth:** procedural or varied rooms, three enemy/item/ability types, build synergy, escalating floor/boss, permadeath/result.
- **Functional visuals:** room exits, threats, attack/turn state, loot choice, build stats, floor progress, death.
- **Proof scenarios:** early encounter; loot/build choice; alternate room; strong build/boss; death/restart.
- **Trap:** random tile layout without a repeated risk-reward-progression loop.

### Visual novel

- **Core loop:** readable scene/dialogue, player choice, state/relationship/clue consequence, branch or ending.
- **Depth:** multiple characters/locations, several consequential choices, tracked evidence/relationship, distinct outcomes.
- **Functional visuals:** speaker identity, portraits/backgrounds, readable text, selectable choices, state change, history/objective if specified.
- **Proof scenarios:** opening flow; consequential choice; clue/relationship response; alternate branch; ending/retry.
- **Trap:** long linear text with cosmetic choices and no visible branch consequence.

### Horror

- **Core loop:** explore/observe, detect threat or anomaly, manage limited safety/resource, survive or uncover the objective.
- **Depth:** multiple spaces/events/threat behaviors, escalating phases, clues or tools, alternate scare/outcome.
- **Functional visuals:** interactables, threat telegraph, visibility/resource state, objective/clues, danger and cause of failure. Make audio cues visible too.
- **Proof scenarios:** atmospheric opening; investigation interaction; threat encounter; late escalation; escape/death.
- **Trap:** dark static rooms and jumpscare labels with no sustained threat or readable interaction.

## 6. Cross-family quality floor

Every family should include:

- authored title and result screens;
- real player input and observable state change;
- at least one meaningful decision or constraint;
- visible success and failure;
- coherent real assets rather than dominant debug geometry;
- stable 1280x720 HUD and controls;
- deterministic normal and special-state demonstrations;
- retry without relaunching where the specification expects a complete arc.

If a hybrid game spans families, select one dominant loop and use the secondary family only to add a supporting system. Do not implement two shallow games side by side.
