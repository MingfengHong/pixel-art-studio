# Image editing

The image tool applies an ordered list of pixel-exact operations to a source image: background removal, recoloring, palettes, outlines, masked patches, resizing and canvas changes.

@shots examples/image-editing/preview.png|A potion before and after editing, examples/potion-variants/preview.png|One potion in three color variants

## Ask your agent

> Use pixel-art-studio to turn this gray potion into a purple magic potion: remove the flat background, add a dark outline and a small sparkle.

## Run it yourself

```bash
python scripts/image_ops.py assets/examples/image-editing/recipe.json --out output/potion-edit
```

## The recipe

```json
{
  "name": "enchanted-potion",
  "source": "input.png",
  "operations": [
    {"op": "remove-background", "color": "#efe3c8"},
    {"op": "recolor", "map": {"#c0cbdc": "#e1a1ef", "#8b9bb4": "#9f61c1"}},
    {"op": "outline", "color": "#3d244f", "width": 1},
    {"op": "extend", "size": [32, 32], "at": [4, 4]},
    {"op": "patch", "source": "spark.png", "at": [24, 3]},
    {"op": "reduce-colors", "colors": 12}
  ]
}
```

## Operations

| Operation | Fields | What it does |
|---|---|---|
| `resize` | `size` or integer `factor` | Nearest-neighbor resize |
| `pixelate` | native `size`, optional `keep_size` | Average into a coarse grid |
| `crop` | `rect` | Cut out a region |
| `mirror` | `axis` `x` or `y` | Flip |
| `rotate` | `degrees` | Rotate on an expanded canvas |
| `remove-background` | `color`, `tolerance`, `connected` | Remove border-connected matches, or all matches |
| `recolor` | `map` | Exact color replacement |
| `palette` | `colors` | Snap to a palette, keeping alpha |
| `reduce-colors` | `colors` | Quantize to a color count |
| `outline` | `width`, `color` | Grow an outline inside the canvas |
| `patch` | `source`, `at`, `mask`, `replace` | Composite a patch; mask brightness scales alpha |
| `extend` | `size`, `at`, `color` or `tile` | Grow the canvas |

## What it writes

`image.png`, a before-and-after `preview.png`, and a portable `source.json` with copied inputs. Run that source into a new folder to keep earlier versions.

## Tips

- Extend the canvas before outlining so the outline has room.
- Recolor by material: a global swap can catch unrelated pixels that share a color.
- For semantic edits such as new clothing or inpainting, see [generation](generation.html), then composite the result with `patch`.

Full reference: [image-editing.md]({{repo}}/blob/main/skills/pixel-art-studio/references/image-editing.md).
