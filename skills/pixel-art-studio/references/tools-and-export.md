# Tools and export

The local tools create UI kits, directional characters, worlds, animations, and edited images, alongside exact pixel-grid rendering. Use them with your preferred editor and the image tools in your agent.

Requires Python 3.10+ and Pillow. From the skill's folder:

```sh
python -m pip install -r requirements.txt
```

The commands below also run from that folder. Resolve script and asset paths relative to the installed skill, and direct output to the user's workspace.

## Choose a tool

For other recipe types, use `python scripts/TOOL.py RECIPE --out OUTPUT`:

| Tool | Guide |
|---|---|
| `ui.py` | [Components, state skins, layouts and interactive preview](ui.md) |
| `character.py` | [Four/eight-direction character recipes](sprites.md#generate-a-directional-character) |
| `world.py` | [Texture, tileset, map and isometric recipes](environments.md#build-terrain-and-maps) |
| `image_ops.py` | [Image transforms and masked patches](image-editing.md) |
| `animate.py` | [Frame imports and layered keyframes](animation-and-fx.md#render-frames-and-layered-keyframes) |
| `tilemap.py` | [Assemble scenes from hand-drawn tilesets](environments.md#assemble-hand-made-tilesets) |
| `pixellab.py` | [Optional PixelLab client: network, account token, and credits; never required](production-workflows.md#optional-pixellab-connection) |

Image fields in recipes accept a PNG or `set.json#frame`, one frame of a grid source or atlas. Generated `source.json` files preserve editable inputs; write the next iteration into a new folder. Every tool except `pixellab.py` runs offline with Pillow alone. `pixellab.py` has its own optional dependencies and is used only when the user has set up PixelLab.

UI, world and layered-animation atlases use `pixel-art-studio-packed-v1`: `frames` is keyed by frame name, with `rect` and `pivot` per entry. Other metadata lives in `ui.json`, `animation.json` or `map.json`. The pixel-grid/character atlas format is described below.

## Render an editable source

```sh
python scripts/pixel_art.py render assets/examples/potion-variants/source.json --out output/potions --scale 6 --columns 3
```

This creates:

| File | Contents |
|---|---|
| `atlas.png` | Native frames arranged in rows, with transparent padding |
| `atlas.json` | Frame names, rectangles, durations, and pivots |
| `preview.png` | Numbered contact sheet on a checkerboard background |

`--columns` sets the atlas columns; `--padding 0..16` sets the gap between frames, with a default of 1 px. `--scale` sets the preview's integer enlargement. Frames retain their full canvas and original orientation.

Preview labels use ASCII and escaped Unicode characters with the default Pillow font. Exact names remain in source and metadata. A custom presentation can use a licensed font covering the desired language.

## Generate a character

```sh
python scripts/character.py assets/examples/characters/researcher/recipe.json --out output/researcher --scale 6
```

The character helper composes role-colored templates and selected parts, then creates 16 poses for four directions or 32 poses for eight. Outputs include `source.json`, `atlas.png`, `atlas.json`, `preview.png`, `animations.json`, `idle.gif`, and `walk.gif`. `--scale` controls preview enlargement; the atlas retains the template's native resolution.

Edit the recipe's material colors, ordered parts, and timing to create a new character. See the [character workflow](sprites.md#generate-a-directional-character) for the recipe fields and template structure. `animations.json` contains named looping clips, each with frame names and durations; frame names resolve through `atlas.json`.

## Convert a PNG into an editable grid

```sh
python scripts/pixel_art.py from-png assets/kenney/tiny-dungeon/tile_0113.png output/editable-potion.json
```

The conversion preserves visible colors and alpha. Fully transparent pixels become `.`, with RGBA `(0,0,0,0)`. The compact source format uses a finite character alphabet; retain an editor source for high-color artwork.

## Make a reference sheet

```sh
python scripts/pixel_art.py sheet assets/kenney/tiny-dungeon/tile_0084.png assets/kenney/tiny-dungeon/tile_0099.png --out output/characters.png --scale 6
```

Create the output parent directory for `from-png` and `sheet` first. `render` creates its own output directory. Use a separate output folder for each iteration; existing destination files are replaced, and source/output collisions are rejected.

## Inspect image properties

```sh
python scripts/pixel_art.py inspect output/potions/atlas.png --binary-alpha --palette assets/examples/potion-variants/source.json
```

Available options: `--size WIDTH HEIGHT`, `--max-colors N`, `--binary-alpha`, `--palette FILE`, and `--scale N`. Palette files contain a `palette` object or list using `#RRGGBB` or `#RRGGBBAA`. Visible colors are compared as exact RGBA values.

Use `--scale N` on a declared integer enlargement to inspect the uniformity of aligned N×N blocks. The command reports dimensions, colors, alpha values, and any mismatches to the requested properties. Exit codes are 0 for a match, 1 for a mismatch, and 2 for an input error.

## Editable grid format

See [beacon/source.json](../assets/examples/beacon/source.json) for a complete example.

- `version`: `1`.
- `name`: a nonempty string.
- `canvas`: `[width, height]`.
- `palette`: single-character keys mapped to hex colors; `.` is reserved for transparency.
- `frames`: entries with a unique `name`, positive `duration_ms`, and exactly `height` rows of `width` characters.
- `pivot`: optional `[x, y]` in native pixels from the top-left. The default is bottom center, `[width // 2, height]`.

Use `allow_empty: true` on an intentional blank frame. Rectangular canvases and semi-transparent palette entries are supported.

## Atlas metadata and handoff

The atlas JSON uses `pixel-art-studio-atlas-v1` and contains the relative image path, native canvas, atlas size, padding, and ordered frames. Each frame includes `name`, `rect: [x,y,width,height]`, `duration_ms`, and `pivot`.

Translate these rectangles and pivots to the target engine's importer. For crisp display, use nearest filtering and consistent integer scaling. If the project uses filtered sampling, configure atlas extrusion and padding for that renderer.

For maps, include placement data and layers. For UI, include slice insets and states. For animation, include timing, loop intent, and a playback preview when available.
