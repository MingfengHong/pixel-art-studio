# Animation

The animation tool does two jobs: it imports frame sequences you already have, and it animates layered cutouts with keyframes. Positions snap to whole pixels so motion stays crisp.

@shots examples/layered-animation/preview.gif|A sword swing made from two layers, examples/rpg-kit/sheets/slash.gif|Hand-drawn slash effect, examples/rpg-kit/sheets/spark.gif|Hit spark

## Ask your agent

> Use pixel-art-studio to make a short sword swing for my 16×16 adventurer. Keep the sword as a separate layer, loop it, and export frames, timing and a GIF.

## Run it yourself

```bash
python scripts/animate.py assets/examples/layered-animation/recipe.json --out output/attack
```

## Layered keyframes

```json
{
  "name": "layered-attack",
  "canvas": [48, 48],
  "pivot": [24, 38],
  "frame_count": 12,
  "duration_ms": 80,
  "loop": true,
  "layers": [
    {"id": "body", "source": "atlas.png", "rect": [0, 17, 16, 16], "pivot": [8, 16],
     "keys": [{"time": 0, "x": 24, "y": 34}, {"time": 0.4, "x": 24, "y": 32}, {"time": 1, "x": 24, "y": 34}]},
    {"id": "blade", "parent": "body", "source": "weapon.png", "pivot": [3, 13],
     "keys": [{"time": 0, "x": 5, "y": -5, "angle": -15}, {"time": 0.55, "x": 7, "y": -5, "angle": -70}, {"time": 1, "x": 5, "y": -5, "angle": -15}]}
  ]
}
```

| Field | Use |
|---|---|
| `id`, `source`, `rect` | The layer and its image region |
| `pivot` | Rotation anchor inside the cropped image |
| `parent` | An earlier layer; the child moves and rotates with it |
| `keys` | `time` 0–1 with `x`, `y`, `angle` (degrees) and `opacity` (0–1) |
| `keys[].source` | Swaps the layer to another image or `set.json#frame` from that key on |
| `hold` | `true` on a key holds it until the next one |

Keys interpolate linearly. Give loops matching first and last poses, and leave room on the canvas for moving limbs.

## Play a skill

A layer can swap its frame at any key, so one recipe can stage a whole skill from hand-drawn frames: the mage switches to its cast pose, a fireball flies across, then a burst plays flash, fire ring and smoke over the slime.

@shots examples/skill-cast/preview.gif|Fireball: cast, flight, burst

```bash
python scripts/animate.py assets/examples/skill-cast/recipe.json --out output/fireball
```

## Import a frame sequence

A sequence recipe lists frames instead of layers. Each frame has an image `source`, an optional `rect`, a destination `at` and a `duration_ms`, plus the shared `canvas`, `pivot` and `loop`. Use it to bring in an existing sprite sheet or generated frames.

## What it writes

@shots examples/layered-animation/preview.png|Every frame of the swing on a contact sheet

| File | Contents |
|---|---|
| `frames/*.png` | Ordered native frames with alpha |
| `atlas.png`, `atlas.json` | Packed frames |
| `animation.json` | Timing, pivot and loop |
| `preview.png`, `preview.gif` | Contact sheet and playback |
| `source.json`, `inputs/` | Portable recipe |

For frame planning, effects and timing advice see [animation-and-fx.md]({{repo}}/blob/main/skills/pixel-art-studio/references/animation-and-fx.md).
