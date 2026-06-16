# Top-Down Shooter — Implementation Plan

## Context
The user wants a simple, retro 2D **top-down shooter** that runs in the browser by
double-clicking a file (same self-contained pattern as the existing
`tic-tac-toe.html` in this folder). Gameplay: move the character with the arrow
keys, aim with the mouse, click to shoot enemies that close in from all sides.
The game needs a menu screen, clear level progression, and animated pixel-art
characters with a gun.

**Confirmed design decisions:**
- **Art:** Procedural pixel art drawn in code (no external image files — avoids the
  browser's `file://` image-loading restrictions; keeps it one portable file).
- **Levels:** Wave-based and escalating — clear all waves in a level to advance;
  enemies get more numerous/faster/tougher each level.
- **Enemies:** A single enemy type that scales (count, speed, size, health). A
  larger "brute" variant of the same creature appears as a mini-boss on later levels.

## Approach & Tech
- **One self-contained file:** `D:\Dropbox\Claude-NM\top-down-shooter.html`
  (HTML + CSS + vanilla JS, no libraries, no build step). Matches the existing
  `tic-tac-toe.html` style so the user can just open it.
- **Rendering:** A single `<canvas>` (e.g. 960×640) using the 2D context. Pixel
  art achieved by drawing small filled rects ("pixels") and using
  `imageSmoothingEnabled = false`. A dark retro palette.
- **Loop:** `requestAnimationFrame` with delta-time (so movement is framerate-
  independent). A global frame counter drives sprite animation.

## Game architecture (single IIFE, organized sections)
1. **State machine** — `MENU`, `PLAYING`, `PAUSED`, `LEVEL_CLEAR`, `GAME_OVER`,
   `VICTORY`. The loop renders/updates based on current state.
2. **Input** — `keydown`/`keyup` track arrow keys (+ WASD as a bonus) into a
   `keys` set; `mousemove` tracks aim position (canvas-relative); `mousedown`/
   `mouseup` drive shooting (hold-to-fire with a fire-rate cooldown). `Esc`/`P`
   pauses; `Enter`/click advances menu & between-level screens.
3. **Entities** (plain objects in arrays):
   - **Player** — `{x, y, hp, maxHp, angle, walkFrame}`. Moves via arrow keys
     (normalized diagonal speed), clamped to the arena. `angle` always faces the
     mouse. Brief invulnerability flash after taking a hit.
   - **Bullets** — spawned at the gun muzzle toward the mouse angle; `{x,y,vx,vy,life}`.
   - **Enemies** — `{x,y,hp,speed,size,walkFrame}`; spawn off-screen at random
     edges/angles and steer toward the player. Contact damages the player on a
     cooldown.
   - **Particles** — short-lived squares for muzzle flash, blood/hit bursts, and
     enemy death puffs (the "cool" feedback).
4. **Collision** — circle vs circle (distance checks): bullet↔enemy (enemy takes
   damage / dies), enemy↔player (player takes damage). Simple and cheap.

## Procedural pixel-art sprites
Dedicated draw functions, each rendering a small grid of colored "pixels",
rotated/positioned via canvas transforms:
- `drawPlayer(ctx, p)` — top-down body + head, with a **gun arm that rotates to
  point at the mouse**; 2–4 frame leg/idle animation; muzzle-flash overlay when
  firing; flicker when hit.
- `drawEnemy(ctx, e)` — a menacing creature (e.g. red blob/bug with legs/eyes);
  2-frame waddle animation; size scales for brutes.
- `drawBullet`, `drawParticle` — tiny glowing rects.
Animation = pick frame from `Math.floor(frameCounter / N) % frames`.

## Gameplay & progression
- **Shooting:** click or hold mouse → fires bullets from the muzzle toward the
  cursor at a fixed fire-rate; bullets travel until off-screen or on hit.
- **Waves & levels:** each level = a list of waves (`{count, speed, hp, size,
  spawnInterval}`). Spawner releases enemies over time; when a wave's enemies are
  all dead and spawned, the next wave starts; clearing the last wave shows a
  **LEVEL CLEAR** screen, then escalates difficulty for the next level. A handful
  of hand-tuned levels (e.g. 5) ending in **VICTORY**; brute mini-boss on later
  levels.
- **Health & death:** player HP bar; reaching 0 → **GAME OVER** with score and a
  Retry option. Score from kills; persists across levels, shown in HUD.

## Screens / UI
- **Menu:** title, "Click / Press Enter to Start", brief controls (Arrows = move,
  Mouse = aim, Click = shoot, P = pause), all drawn on the canvas.
- **In-game HUD:** HP bar, score, level number, wave/enemies-remaining.
- **Between levels:** "Level N Clear!" → continue. **Game Over** and **Victory**
  screens with restart.

## Implementation steps
1. Scaffold the HTML/CSS shell + canvas + game-state constants and the rAF loop.
2. Input handling (keyboard set, mouse position/aim, fire, pause).
3. Player entity: movement, aiming, arena clamping, `drawPlayer` pixel art.
4. Shooting + bullets + muzzle flash particles.
5. Enemy entity, edge-spawning, steering AI, `drawEnemy`, contact damage.
6. Collision + death + score + particle bursts.
7. Wave/level manager + difficulty scaling + level-clear/victory flow.
8. Menu, HUD, pause, game-over screens + restart wiring.
9. Polish: screen shake on hit, color/animation tuning, palette pass.

## Verification
- Open `D:\Dropbox\Claude-NM\top-down-shooter.html` in the browser (I can launch
  it with `Start-Process`).
- Confirm end-to-end: menu starts the game; arrow keys move; the gun tracks the
  mouse; clicking shoots; enemies spawn from multiple edges and chase; bullets
  kill enemies with particle feedback; HP drops on contact; clearing waves
  advances levels with rising difficulty; death shows Game Over and restart works;
  finishing the last level shows Victory.
- Sanity-check the browser console for runtime errors during a full playthrough of
  level 1.
