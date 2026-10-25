# Tiles, maps, and backgrounds

## Tile grammar

Read tile size, sheet margin/spacing, numbering origin, and rows/columns before extraction. Packed and spaced sheets have different coordinates. Identify pieces from the source files or a labeled contact sheet.

Define fill, straight edges, external/internal corners, narrow passages, and transitions. Draw a representative patch first. Use nine-piece layouts for rectangular patches and a broader corner/neighbor set for irregular terrain. For bitmask-based autotiles, specify neighbor order and the pieces used at each junction.

Repeat tiles in 3×3 context to reveal seams and texture repetition. Connect rivers, roads, and fences through turns, junctions, and boundaries. Keep river exits open where water continues offscreen.

## Buildings and scenes

Assemble buildings from compatible roof, wall, corner, and doorway modules. Match roof width to the footprint; align doors with the walking surface. Match perspective and pixel density when combining assets from different packs.

Separate ground, low decoration, objects, and foreground. Top-down overlap often sorts by a common foot/base anchor; tall sprites and canopies may need separate pieces. Specify anchors for objects of different heights. Include collision/navigation data when requested.

Create a focal area with calmer surroundings, paths, and framing objects. Look across the whole scene for unfinished regions. Choose object density and safe areas to suit the gameplay, composition, and mood.

## Backgrounds and parallax

Design behind the real foreground. Leave quiet space for titles, dialogue, and HUD where requested. Choose aspect ratio and safe crop from the current brief. Keep distant layers lower in contrast or simpler in detail when depth separation needs it.

Preview repeating backgrounds across their wrap axes. For parallax, separate layers and specify origins/repeat axes. Snap final rendering consistently if the style requires integer movement. Palette-remapped day/night variants preserve a strict palette; translucent overlays create additional colors for atmospheric effects.

Deliver tiles/atlas, an example scene, and editable placement data for a map request.

## Assemble hand-made tilesets

For final art, draw the tiles by hand (see [hand-authoring.md](hand-authoring.md)) and assemble scenes with `tilemap.py`:

```sh
python scripts/tilemap.py assets/examples/side-scroller/scene.json --out output/meadow
```

The [scene recipe](../assets/examples/side-scroller/scene.json) lists `tilesets` (grid sources, atlas JSON or PNGs; frame names must be unique across sets), a `size` in tiles, an optional `background` of colour bands, and ordered `layers`:

| Field | Use |
|---|---|
| `rows` | One string per tile row; `.` leaves a cell empty |
| `legend` | Character to tile: a frame name, a list of variants chosen per cell, or `{"tile": name, "flip": "x"}` |
| `terrain` | Character to an autotile rule (see below) |
| `parallax` | Scroll factor recorded in `map.json` for the engine |
| `objects` | Sprites that belong to this layer's depth, such as a far windmill behind nearer hills |

Terrain rules:

- **Side view** (the default) picks `top`, `top_left`, `top_right`, `left`, `right` or `fill` from which neighbours are open above and to the sides.
- **`"rule": "mask"`** picks by a four-bit neighbour mask for top-down sets, with keys `"0"` to `"15"` and a `default`.

Every value can be a variant list or a flipped tile.

Top-level `objects` are drawn after all layers, sorted by their bottom edge, with an optional `z` to force order:

- `tile: [x, y]` stands a sprite on the bottom of that cell, centred.
- `seat` sinks it by a few pixels into the ground.
- `dx` nudges it sideways.
- `shadow: true` adds a soft drop shadow.

Outputs: `scene.png`, `preview.png`, one PNG per layer in `layers/`, `map.json` (tile names per layer, parallax and objects), and a portable `source.json` with copied tilesets.

## Generate terrain and maps

`world.py` generates top-down terrain procedurally. Use it for quick layouts, prototypes and backgrounds; switch to `tilemap.py` with a hand-drawn tileset for final art.

```sh
python scripts/world.py assets/examples/world-workshop/recipe.json --out output/town
```

Map cells:

- `g` is grass: four variants with tufts, flowers and pebbles, chosen by `grass_variants` weights.
- `p` is a dirt path and `f` is tilled farmland. Grass grows over their open sides.
- `w` is water: a dirt bank and foam where land lies to the north, and a ripple edge on the other shores.

Tiles are named `grass-0` to `grass-3`, and `path-NN`, `farm-NN` and `water-NN`. `NN` is the four-neighbour mask: north = 1, east = 2, south = 4, west = 8. `palette` overrides the material ramps for `grass`, `water`, `path`, `soil` and `bank`. `seed` makes the result repeatable.

`objects` place images by pixel `at`, with an optional `rect` crop, `shadow` and `depth`, and are sorted by their base line. A source can be a PNG or `set.json#frame`. `scatter` drops `count` copies of a sprite on random cells of the types in `on`. The [town recipe](../assets/examples/world-workshop/recipe.json) combines Kenney CC0 houses and trees with hand-drawn characters and props.

Optional `platform` rows (`#` solid) and `isometric` rows (nonzero cells) produce side-view terrain and isometric blocks. Outputs: tiles, `atlas.png/json`, `ground.png`, the composed `scene.png`, `map.json`, and a portable `source.json` with copied inputs.
