---
name: pixel-art-studio
description: Creates cohesive pixel art game assets — characters, animals, props, inventory icons, tilesets, maps, platform and isometric terrain, backgrounds, HUD and menu UI kits, animation frames, and effects — with editable sources, native PNG atlases, metadata, and previews. Also edits pixel images (recolor, palette reduction, background removal, masked patches, resizing). Use when the user asks for pixel art, sprites, sprite sheets, tiles, tilemaps, game UI, retro or 8-bit/16-bit art, matching an existing pixel style or reference image, or converting PNGs into editable grids. Also triggers on 像素画、像素素材、像素角色、精灵图、瓦片地图、像素界面.
license: MIT. Bundled Kenney artwork is CC0-1.0; see assets/kenney/ATTRIBUTION.md.
compatibility: Works fully offline in any Agent Skills host. Local tools need Python 3.10+ and Pillow (requirements.txt). An optional PixelLab client (requirements-pixellab.txt, user's own API token) is never required.
metadata:
  repository: "https://github.com/MingfengHong/pixel-art-studio"
---

# Pixel Art Studio

Create readable, cohesive pixel art from a brief and visual references. The user's palette, proportions, resolution, viewpoint, and edge treatment take priority over any default in this skill.

All paths below are relative to the folder containing this `SKILL.md`. Resolve scripts and assets against that folder, and write outputs to the user's workspace, never into the skill folder.

## Workflow

1. **Establish the visual direction.** Extract the subject, intended use, native canvas or tile size, palette, outline treatment, lighting, transparency, and output format. For animation, also capture directions, actions, timing, and pivot. Inspect supplied references and the target project's existing assets, then carry their choices forward. Ask only about details that affect compatibility with the project; for open-ended requests, state a few practical assumptions and proceed. See [style-and-quality.md](references/style-and-quality.md) for reference analysis and the optional [style brief](assets/templates/style-brief.json) for larger sets.
2. **Read the relevant guide** from the table below. Load only what the request needs.
3. **Make one representative asset first.** Resolve the silhouette and large color clusters, then material shading, then defining details. Confirm the direction with the user when the set is large or the brief is ambiguous.
4. **Extend the set.** Keep proportions, pixel density, palette roles, lighting, baseline, and pivots consistent with the first asset.
5. **Preview and refine** at native size and integer zoom (see below).
6. **Deliver** sources, exports, and metadata (see below).

| Task | Guide |
|---|---|
| Hand-authoring workflow, quality bar, tiles, characters, enemies, actions, effects, portraits and emotes, icons | [hand-authoring.md](references/hand-authoring.md) |
| Characters, animals, portraits, props, icons | [sprites.md](references/sprites.md) |
| Tiles, maps, platform/isometric terrain, backgrounds | [environments.md](references/environments.md) |
| HUD, bars, controls, panels, inventory, dialogs | [ui.md](references/ui.md) |
| Animation frames, layered keyframes, effects | [animation-and-fx.md](references/animation-and-fx.md) |
| Recoloring, palettes, background removal, masks, canvas | [image-editing.md](references/image-editing.md) |
| Freeform or reference-driven generation, semantic edits | [production-workflows.md](references/production-workflows.md) |
| Helper commands, grid format, atlas metadata | [tools-and-export.md](references/tools-and-export.md) |
| Worked briefs with sources and results | [few-shots.md](references/few-shots.md) |

## Choose a production method

Pick the method that fits the task and the tools available in this host. All of these except the last work offline.

**Final game art is hand-authored.** Place every pixel in a grid source with a planned palette, then use the tools to render, assemble and check it. Shape generators and filters produce programmer art; reserve them for prototypes. Follow [hand-authoring.md](references/hand-authoring.md) for the workflow, the quality bar, tile anatomy, characters, portraits and icons.

- **Hand-authored grid sources** — sprites, tiles, portraits and icons, one character per pixel, rendered with `scripts/pixel_art.py render`. Other tools take one frame as `set.json#frame`. Character variants can share one grid with swapped palettes and parts.
- **Tile assembly** — build scenes from a hand-drawn tileset on a grid with `scripts/tilemap.py`: legends, side-view or mask autotiling, parallax layers, and props seated into the ground. See [environments.md](references/environments.md#assemble-hand-made-tilesets).
- **Character generator** — compact 16×16 humans in 4 or 8 directions. Copy a [character recipe](assets/examples/characters/researcher/recipe.json), set material colors and parts, and run `scripts/character.py`. See the [character workflow](references/sprites.md#generate-a-directional-character).
- **UI kit generator** — use `scripts/ui.py` with three frame styles. It covers HUDs, bars with labels, minimaps, icon buttons, toggles, sliders, dropdowns, panels, scroll views, hotbars, lists, NPC dialogue boxes, day/night dials, tooltips, modals and floating text. Start from the [RPG interface kit](assets/examples/interface-kit/recipe.json) or the [side-scroller HUD](assets/examples/side-scroller/hud.json). Its `preview.html` is an interactive playground; optional `locales` translate its screen names.
- **World generator** — use `scripts/world.py` for procedural top-down terrain: grass variants, paths, farmland, water banks, drop shadows, scatter, and platform or isometric samples. Use it for prototypes and backgrounds; use hand-drawn tiles and `tilemap.py` for final art.
- **Image editor and animator** — palette, background, patch, and canvas operations with `scripts/image_ops.py`; frame imports and parented keyframe animation with `scripts/animate.py`.
- **Edit or combine existing assets** — convert a PNG with `scripts/pixel_art.py from-png`, then edit the grid. Only combine assets whose licenses allow it.
- **Host image or pixel-editor tools** — for freeform and reference-driven work, use whatever the host provides, then redraw contours, pixel sizes, color clusters, and transparency on the intended native grid. Never ship an upscaled or filtered image as pixel art.
- **PixelLab (optional)** — a third-party generation service. Use it only under the conditions below.

### PixelLab is optional

Every request in this skill can be completed without PixelLab: use the local tools, the host's own image tools, or hand-authored grids. Use PixelLab only when **all** of these hold:

1. The user asked for PixelLab, or agreed to it after you offered it as one option.
2. A PixelLab connector is already configured in the host, or `PIXELLAB_API_KEY` is already set in the environment.
3. The user has confirmed the credit-consuming generation calls you are about to make.

Otherwise, do not install its dependencies, ask for a token, or stop to recommend it; continue with the local and host routes. Never write a token into files, recipes, or chat. Details are in [production-workflows.md](references/production-workflows.md#optional-pixellab-connection).

## Helper commands

Requires Python 3.10+ and Pillow (`python -m pip install -r requirements.txt`). Run from this skill's folder or pass absolute paths. All of these run locally with no network access.

| Goal | Command |
|---|---|
| Render a grid to atlas, metadata, and preview | `python scripts/pixel_art.py render SOURCE.json --out DIR [--scale 4] [--columns 4] [--padding 1]` |
| Generate a 4/8-direction idle/walk character | `python scripts/character.py RECIPE.json --out DIR [--scale 6]` |
| Generate UI components, states, screens, and interactive preview | `python scripts/ui.py RECIPE.json --out DIR [--scale 2]` |
| Assemble a scene from hand-drawn tiles and props | `python scripts/tilemap.py RECIPE.json --out DIR [--scale 3]` |
| Generate procedural terrain and maps | `python scripts/world.py RECIPE.json --out DIR [--scale 2]` |
| Apply image edits or composite masked patches | `python scripts/image_ops.py RECIPE.json --out DIR` |
| Render imported frames or layered keyframes | `python scripts/animate.py RECIPE.json --out DIR [--scale 4]` |
| Convert a PNG into an editable grid | `python scripts/pixel_art.py from-png IMAGE.png OUT.json` |
| Build a labeled contact sheet | `python scripts/pixel_art.py sheet A.png B.png ... --out SHEET.png [--scale 4]` |
| Check size, colors, alpha, or zoom uniformity | `python scripts/pixel_art.py inspect IMAGE.png [--size W H] [--max-colors N] [--binary-alpha] [--palette FILE] [--scale N]` |

Complete starting points: [side-scroller](assets/examples/side-scroller/scene.json) (hand-drawn tiles, scene and HUD), [RPG kit](assets/examples/rpg-kit) (characters, emotes, icons), [interface kit](assets/examples/interface-kit/recipe.json), [world workshop](assets/examples/world-workshop/recipe.json), [image edit](assets/examples/image-editing/recipe.json), and [layered animation](assets/examples/layered-animation/recipe.json). `inspect` exits 0 on a match, 1 on a mismatch, and 2 on an input error, so it can serve as an automated check. If Python or Pillow is unavailable, continue with the host's own image tools and say which checks were skipped.

## Preview and refine

- View output at native size and at an integer enlargement with nearest-neighbor scaling.
- Show transparent sprites on both light and dark backgrounds, and in their intended scene or UI where practical.
- Check silhouette, material separation, text legibility, seams, clipping, and stray semi-transparent pixels.
- **Animation:** compare registration across frames, inspect contact and extreme poses, and play the loop at its intended timing when a playback tool exists.
- **Tiles:** repeat tiles in a 3×3 arrangement and inspect transitions, corners, and junctions.
- **UI:** use the longest real labels, largest expected counts, and every requested state; open `preview.html` to check interactions.

## Deliver

Save assets in the user's chosen output folder, one folder per iteration. Include:

- Editable sources (grid JSON, recipe or portable `source.json` with `inputs/`, or editor files).
- Native-resolution PNGs or an atlas, plus a zoomed preview.
- Frame timing, pivots, and loop intent for animation; placement and layers for maps; slice insets, states, and layout for UI.

Summarize the files and key design choices in a few lines. Keep originals intact, and credit reused artwork with its source and license.

## Pitfalls

- Shape generators, noise and filters look like programmer art. Hand-author final assets and hold them to the quality bar in [hand-authoring.md](references/hand-authoring.md).
- Painted, freeform backgrounds do not read as pixel games. Assemble backgrounds from tiles on a grid.
- Copying a reference's layout, frames or text is not learning from it. Keep its qualities and design an original look.
- Mixing pixel densities, or scaling by non-integer factors, breaks the grid. Keep one logical grid and integer zoom.
- Global color replacement can recolor unrelated materials. Map recolors by semantic role and check which pixels changed.
- Mirroring flips handed tools, text, and asymmetric clothing. Redraw those details per direction.
- Changing canvas size or pivot between frames causes playback jitter. Keep both stable across a clip.
- Baking labels into UI skins blocks localization. Keep text-free skins and editable strings.
- Regenerating output replaces existing files. Use a fresh output folder rather than overwriting the user's edits.

The bundled [Kenney reference tiles](assets/kenney/ATTRIBUTION.md) (CC0) illustrate compact sprites, modular scenes, and small UI components.
