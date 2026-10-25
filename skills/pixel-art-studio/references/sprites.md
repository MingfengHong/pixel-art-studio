# Characters, props, and icons

## Characters and animals

For final art, draw characters, portraits and icons by hand as grid sources; [hand-authoring.md](hand-authoring.md) covers proportions, walk frames, palette-variant casts, portrait construction and icon rules, with the [RPG kit](../assets/examples/rpg-kit) as a worked example. The generator below is for quick, consistent 16×16 casts.

Start with viewpoint, canvas, silhouette, head/body proportions, eye line, and foot anchor. Reserve room for hair, ears, hats, tails, and carried equipment before filling the canvas. Draw one neutral pose first; compare new characters against that pose to maintain a cast's proportions.

Draw the visible forms for each direction. Back views emphasize hair and clothing; side views clarify face direction, shoulder overlap, and feet. Mirroring works for symmetric features. Draw handed tools, text, badges, and asymmetric clothing with their orientation preserved. Animals may be front, side, or three-quarter view according to the brief.

Separate material roles (hair, skin/fur, cloth, metal) from specific colors. Variants can reuse a silhouette and role map. Preserve enough value contrast for hair and face or hand and tool to remain separate. Set skin colors and body proportions from the character brief.

Compose portraits at their intended size. Choose the level of detail to suit the brief, from an enlarged crop of the sprite to a dedicated portrait drawing.

### Generate a directional character

The bundled character tool turns a recipe into a small animated character. Start with the [researcher](../assets/examples/characters/researcher/recipe.json) or [ranger](../assets/examples/characters/ranger/recipe.json), then adapt colors and parts to the brief.

1. Copy the recipe to the user's workspace and give the character a name.
2. Set `colors` by material role and choose `parts` in back-to-front drawing order.
3. Generate the assets using the installed skill's `scripts/character.py`.
4. Open the contact sheet and animation previews. Refine the resulting `source.json` for distinctive silhouettes, equipment, or asymmetry.
5. Render edited grids with `scripts/pixel_art.py render SOURCE --out OUTPUT` and retain the clip definitions alongside the atlas.

From the skill folder:

```sh
python scripts/character.py assets/examples/characters/researcher/recipe.json --out output/researcher
```

The default [template](../assets/templates/character.json) draws a 16×16 human with a shared `[8,16]` foot pivot. Each requested direction has `stand`, `idle`, `walk-a`, and `walk-b` poses. The left directions mirror their right counterparts. Edit handed equipment and asymmetric markings in the resulting frames.

| Recipe field | Use |
|---|---|
| `name` | Character name in the source and atlas |
| `directions` | `4` (default) or `8`; see the [adventurer recipe](../assets/examples/characters/adventurer/recipe.json) |
| `parts` | Ordered list of `long-hair`, `glasses`, `beard`, `cap`, `coat`, `apron` |
| `colors` | Hex colors for selected material roles; omitted roles use the template palette |
| `timing_ms` | `stand`, `idle`, and `step` durations in milliseconds |
| `template` | Optional path to a custom template, relative to the recipe file |

Color roles are `ink`, `hair`, `hair_shadow`, `skin`, `skin_shadow`, `eyes`, `top`, `top_shadow`, `pants`, `pants_shadow`, `shoes`, `glint`, `cap`, `cap_shadow`, `apron`, and `apron_shadow`. Coat pixels use the top colors. Parts are drawn in list order, so place glasses after hair and headwear.

The template separates pixel roles from colors. Its `views` contain front, back, right, front-right and back-right grids; each part stores per-view strokes as `[row, column, text]`. `steps` lifts alternate feet, and `idle_band` shifts a band of upper-body rows down one pixel. When changing anatomy or canvas size, update views, overlays, motion and pivot together.

With `directions: 8`, the output contains 32 poses ordered front, front-right, right, back-right, back, back-left, left, front-left. Diagonal views have their own drawn forms; left-facing counterparts mirror the right. For a supplied character reference, use the [reference-driven workflow](production-workflows.md).

The output contains editable `source.json`, transparent `atlas.png`, frame rectangles in `atlas.json`, a labeled `preview.png`, `animations.json`, and `idle.gif` / `walk.gif`. Animation clips refer to frame names and carry their own timings: a walk loops through `walk-a → stand → walk-b → stand`. The GIFs show the requested directions on a checkerboard; use the native PNG atlas for game import.

Keep recipe-driven iterations in their own output folder. Regenerating a character replaces the generated files. For detailed frame edits, work from a copy of `source.json` and keep the recipe as the starting point.

## Props and inventory icons

Identify the feature that makes the object recognizable: a mug handle, lantern loop, shovel blade, or bottle neck. Build that silhouette before adding surface marks. Compare with reference objects of similar size and function.

Use small material ramps when they help clarity. Place a highlight where it conveys shape or reflectivity. Keep tiny labels abstract unless the canvas supports legible glyphs. Deliver sign text separately if localization or runtime text is expected.

Use consistent canvases and visual centers for an icon set. Balance the visual weight of narrow tools and wide bags. Fit icons by choosing suitable slot sizes and refining silhouettes on the native grid.

## Variations and transformations

For recolors, map semantic roles and verify which pixels change. Global replacement can accidentally recolor an unrelated material. Preserve geometry unless a silhouette variation was requested. Keep the original reference and identify the adaptation in provenance notes.

Photo-to-pixel work requires redesign: simplify form, choose a palette, reconstruct contours, then judge readability. Quantization and automatic outlines are intermediate operations. Repeated outline dilation can grow the silhouette and erase interior detail.

For animation, continue with [animation-and-fx.md](animation-and-fx.md). For reference-to-editable-source examples, see [few-shots.md](few-shots.md).
