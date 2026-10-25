# Pixel image editing

From the installed skill folder:

```sh
python scripts/image_ops.py assets/examples/image-editing/recipe.json --out output/potion-edit
```

The [recipe](../assets/examples/image-editing/recipe.json) removes a potion's flat background, recolors its fill, adds an outline, expands the canvas and composites a sparkle. Recipes contain `source` and ordered `operations`. Input paths resolve relative to the recipe.

| Operation | Fields | Behavior |
|---|---|---|
| `resize` | `size: [w,h]` or integer `factor` | Nearest-neighbor resize |
| `pixelate` | Native `size`, optional `keep_size` | Average into a coarse grid, optionally enlarge back |
| `crop` | `rect: [x,y,w,h]` | Extract a region |
| `mirror` | `axis: "x"` or `"y"` | Flip |
| `rotate` | `degrees` | Rotate on an expanded canvas |
| `remove-background` | `color`, `tolerance`, `connected` | Remove border-connected matches; `connected: false` removes all matches |
| `recolor` | `map: {"#old":"#new"}` | Exact RGBA replacement |
| `palette` | `colors: ["#..."]` | Match RGB to a palette, preserving alpha |
| `reduce-colors` | `colors` count | Quantize color, preserving alpha |
| `outline` | `width`, `color` | Grow an outline within the canvas |
| `patch` | `source`, `at`, optional `mask`, `replace` | Composite a patch; mask brightness multiplies alpha; replace mode copies transparency |
| `extend` | `size`, `at`, optional `color` or `tile` | Expand with a transparent, solid or tiled background |

Allow room before outlining. Use a flat-background key for isolated artwork and masking tools for complex backgrounds. For semantic inpainting, outpainting, style or outfit changes, use [production workflows](production-workflows.md), then composite the result.

Outputs include `image.png`, before/after `preview.png`, and portable `source.json` with copied inputs. Re-run that source into a new folder to preserve earlier iterations.
