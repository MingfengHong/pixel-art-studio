# References and generation

Text-to-image, photo-to-pixel, style matching and semantic edits use your agent's own image tools, or careful redrawing on the native grid. The local tools then turn the result into clean, editable assets. PixelLab is an optional extra and never required.

## Work from a reference

> Here is a screenshot of my game. Use pixel-art-studio to draw three new enemies that match its palette, outline and proportions.

The agent reads the reference for grid size, silhouette, view, palette, edges, light and detail level, then draws to match. Generated or painted images are always redrawn on the target grid: contours, pixel sizes, color clusters and transparency. An upscaled or filtered image is never shipped as pixel art.

## Which route for which request

| Request | Default route |
|---|---|
| Text to pixel art, concept or style references | The agent's image tool, then refinement on the grid, or a hand-authored grid |
| Photo or image to pixel art | Redraw on the target grid; `image_ops.py` for palette and size |
| Character turnarounds | `character.py` templates, or redraw each view from the reference |
| Outfit and color variants | Character parts and role colors, or `image_ops.py` recolor and patch |
| Actions and in-betweens | Key poses assembled with `animate.py` |
| Inpainting and repair | Draw the patch, then composite it with a mask |
| Tiles, maps, isometric | `world.py`, with custom art placed as objects |
| UI | `ui.py` |

## Optional: PixelLab

[PixelLab](https://www.pixellab.ai) is a third-party pixel art generation service with its own account and paid credits. The skill uses it only when all three hold:

1. You ask for PixelLab, or agree when the agent offers it.
2. A PixelLab connector is already set up in your agent, or `PIXELLAB_API_KEY` is already set.
3. You confirm the generation calls, because each one spends your credits.

Otherwise the agent continues with the routes above and never asks for a token. To set up the bundled client:

```bash
python -m pip install -r requirements-pixellab.txt
python scripts/pixellab.py list
```

`list` and `schema` only read the live tool catalog; `call` generates. Returned images are saved locally and refined on the grid like any other generated art. Details are in [production-workflows.md]({{repo}}/blob/main/skills/pixel-art-studio/references/production-workflows.md).
