# Hand-drawn pixel art

Release-quality game art is placed pixel by pixel. The skill teaches agents to author every final sprite, tile, portrait and icon as an editable grid, then uses its tools to render, assemble and check the result.

@shots examples/side-scroller/hud/screens/hud.png|A side-scroller scene built from hand-drawn tiles, with a full HUD

## Ask your agent

> Use pixel-art-studio to draw a 16x16 side-view tileset for a grassy platformer: grass top, corners, sides, dirt fill with a stone variant, floating platform, water, clouds and distant hills. Then assemble a sample level with props and a hero.

## The workflow

1. **Canvas:** 16x16 tiles and icons, 16x16 to 16x32 characters, 32x48 large props, 32-64 px portraits.
2. **Palette first:** 3-5 tones per material, with shadows shifted toward purple or blue and lights toward yellow.
3. **Silhouette:** fill the shape in the base tone and check that it reads at 1x.
4. **Shade by form:** light comes from the top left. Shade each clump (leaves, hair locks, folds) separately.
5. **Outline:** use a dark outline that is not black around the outside, and darker ramp tones between materials.
6. **Detail last**, then review at 1x and 3x on light and dark backgrounds and in the scene.

Each set is a grid source: one character per pixel, `.` for transparent.

```json
{"version": 1, "name": "props", "canvas": [16, 16],
 "palette": {"o": "#20161f", "L": "#a8ea72", "G": "#62c24c", "D": "#3a9142"},
 "frames": [{"name": "bush", "duration_ms": 100, "rows": ["................", "..."]}]}
```

Other tools use a single frame as `props.json#bush`.

## Tiles, not paintings

Backgrounds are assembled from tiles on a grid. A side-view set needs a grass top (2-3 variants), outer corners, side walls, a dirt fill with a rare stone variant, floating-platform pieces and water. The background is tiles too: clouds, far mountains in pale cool tones, warmer hills and a tree line.

@shots examples/side-scroller/sheets/tiles/preview.png|The hand-drawn tileset

`tilemap.py` assembles the scene. Each layer is rows of characters with a legend, and terrain characters choose their own edge pieces:

```bash
python scripts/tilemap.py assets/examples/side-scroller/scene.json --out output/meadow
```

```json
"terrain": {"#": {"top": ["ground-top", "ground-top-flowers"], "top_left": "ground-top-left",
  "top_right": {"tile": "ground-top-left", "flip": "x"}, "left": "ground-left",
  "right": {"tile": "ground-left", "flip": "x"}, "fill": ["ground-fill", "ground-fill-stone"]}}
```

Props stand on a tile with `"tile": [x, y]` and sink into the grass with `"seat": 3`. Layer `objects` keep far sprites behind nearer layers, and `parallax` is recorded for the engine.

## Quality bar

- The silhouette reads at 1x without color.
- Every material has at least three tones, with hue-shifted shadows.
- The outline is continuous, with no stray pixels or noise.
- One light direction across the whole scene.
- Props sit 2-4 px into the ground.
- No mixed pixel sizes, gradients or anti-aliased edges.

## Learn from references, don't copy

Study what makes a reference work: readable silhouettes, layered depth, harmonious ramps, dense but purposeful props. Then design your own tiles, layout, palette and wording. The examples here learn from bright mobile platformers and classic RPGs without reusing their frames, layouts or text.

The full method, including characters, portraits and icons, is in [hand-authoring.md]({{repo}}/blob/main/skills/pixel-art-studio/references/hand-authoring.md).
