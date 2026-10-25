# Worlds

Two tools build game worlds. `tilemap.py` assembles hand-drawn tilesets on a grid, for final art. `world.py` generates top-down terrain procedurally, for quick layouts and backgrounds.

@shots examples/world-workshop/scene.png|A top-down town: procedural ground, hand-drawn houses, trees and characters, examples/side-scroller/scene/scene.png|A side-view scene assembled from hand-drawn tiles

## Ask your agent

> Use pixel-art-studio to build a small top-down town on a 16 px grid: a main road, two houses, a field of herbs and a pond. Place the hero and three villagers, and give me the map data.

## Hand-drawn tilesets: tilemap.py

```bash
python scripts/tilemap.py assets/examples/side-scroller/scene.json --out output/meadow
```

| Recipe field | Use |
|---|---|
| `tilesets` | Grid sources, atlas JSON or PNGs whose frames become named tiles and sprites |
| `size`, `tile_size` | The map in tiles and the tile size in pixels |
| `background` | A color, or color bands for a sky gradient |
| `layers[].rows` + `legend` | One character per cell, mapped to a tile, a variant list, or `{"tile", "flip"}` |
| `layers[].terrain` | Autotiling: the side-view rule picks top, corners, sides and fill; `"rule": "mask"` picks by four neighbours for top-down sets |
| `layers[].objects`, `parallax` | Sprites at that layer's depth, and its scroll factor |
| `objects` | Props and characters: `tile`, `seat`, `dx`, `z`, `shadow` |

It writes `scene.png`, one PNG per layer, `map.json` with tile names per layer and placed objects, and a portable `source.json`. The [hand-drawn guide](hand-drawn.html) covers which tiles a set needs.

## Procedural terrain: world.py

```bash
python scripts/world.py assets/examples/world-workshop/recipe.json --out output/town
```

```json
{
  "name": "river-town",
  "tile_size": 16,
  "seed": 5,
  "map": [
    "gggggggggggggggggggg",
    "pppppppppppppppppppp",
    "ggfffgggggppgggwwwgg"
  ],
  "objects": [
    {"source": "town.json#house-red", "at": [176, 32], "depth": -8},
    {"source": "../rpg-kit/warrior.json#down-stand", "at": [144, 88], "shadow": true}
  ],
  "scatter": [{"source": "../side-scroller/props.json#flowers", "count": 6, "on": "g"}]
}
```

| Cell | Terrain |
|---|---|
| `g` | Grass in four variants: tufts, clumps, flowers, pebbles |
| `p` | Dirt path; grass grows over its open sides |
| `f` | Tilled farmland with furrows |
| `w` | Water with a dirt bank to the north and ripples along the other shores |

- **Tile names:** `grass-0` to `grass-3`, and `path-NN`, `farm-NN` and `water-NN`, where `NN` is the neighbour mask (north 1, east 2, south 4, west 8).
- **Look and repeatability:** `palette` overrides the material ramps, and `seed` makes the result repeatable.
- **Objects:** they accept PNGs or `set.json#frame`, are sorted by their base line, and can cast `shadow`. `scatter` drops copies on random cells.
- **Extras:** optional `platform` and `isometric` rows produce side-view terrain and isometric blocks.

## What it writes

| File | Contents |
|---|---|
| `scene.png`, `ground.png` | The composed map, and the ground alone |
| `tiles/*.png`, `atlas.png`, `atlas.json` | Every generated tile |
| `map.json` | Tile names, layers and object placement |
| `source.json`, `inputs/` | A portable recipe with copied images |

Read [environments.md]({{repo}}/blob/main/skills/pixel-art-studio/references/environments.md) for tile grammar, buildings and parallax backgrounds.
