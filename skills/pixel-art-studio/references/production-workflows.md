# Generation and production workflows

Local recipe tools handle exact grids, layouts, states, and exports. Freeform generation and semantic edits come from the host's own image tools, or from hand redrawing on the native grid. PixelLab is an optional extra for users who already use it; no route below depends on it.

| Request | Default route (no PixelLab) | Optional PixelLab route |
|---|---|---|
| Text to pixel art; concept or style references | Host image tool, then native-grid refinement; or author a grid directly | Image generation tools |
| Image to image; photo to pixel art | Redraw from the reference on the target grid; `image_ops.py` for palette, size, and cleanup | Reference-guided generation |
| Character rotation | `character.py` 4/8-direction templates; redraw each view from a supplied reference | Character rotation tools |
| Variants and outfit transfer | Role colors and parts in `character.py`; `image_ops.py` recolor and patch | Semantic editing |
| Pose guidance; skeletal animation | Cutout joints and keyframes in `animate.py`; hand-drawn key poses | Pose-conditioned generation |
| Text-driven actions; animation editing | Draw key poses, then assemble with `animate.py` | Generate a sequence, then import it with `animate.py` |
| Interpolation | Position/angle/opacity keyframes in `animate.py`; hand-drawn in-betweens | Generated in-between poses |
| Inpainting and repair | Draw the patch, then composite it with `image_ops.py` and a mask | Mask-based inpainting |
| Background removal, resize, unzoom, palette reduction | `image_ops.py` | — |
| Textures, connected tiles, maps, extension | `world.py` recipes; custom art placed as map objects | Tileset and map-object tools |
| Isometric tiles | `world.py` block palettes and layouts; hand-drawn detail objects | Isometric tile tools |
| UI components and screens | `ui.py` and the [UI guide](ui.md) | — |

## Host image tools

Follow the host's tool requirements and pass references through its image-input mechanism. Describe subject, viewpoint, proportions, native resolution, silhouette, palette roles, outline, lighting, transparency, and composition.

For characters, specify direction order and identifying clothing details. For animation, establish the neutral pose, anchor, contact poses, frame count, and timing. For maps, separate artwork from placement and connectivity. For UI, generate skins and icons, then compose exact states and labels with `ui.py`.

Use masks for local edits and composite the approved patch into the original. Whole-image rotation only transforms the raster; other character directions need their visible forms redrawn. Open the result, refine contours and alpha on the chosen grid, and keep editable sources and attribution.

If the host has no image tool, author the art as pixel grids or recipes with the local tools. Say so briefly instead of blocking on a missing generator.

## Optional PixelLab connection

[PixelLab](https://www.pixellab.ai) is a third-party pixel art generation service with its own account, API token, and paid credits. Pixel Art Studio does not require it, does not contact it unless asked, and none of the local tools import it.

### When to use it

Use PixelLab only when all of these hold:

1. The user asked for PixelLab, or agreed after you offered it as one option alongside the local route.
2. A PixelLab connector is already configured in the host, or `PIXELLAB_API_KEY` is already set in the environment.
3. The user has confirmed the generation calls you are about to make, since each one spends credits from their account.

If any condition is missing, continue with the default route above. Do not install the optional dependencies, ask for a token, or pause the task to recommend the service. Never print, store, or commit the token; keep it in the environment only.

### Use a configured connector

Prefer a PixelLab connector or MCP server that the host already provides. The [tool catalog](https://api.pixellab.ai/mcp/docs) lists current methods, and the [artist documentation](https://www.pixellab.ai/docs) explains the workflows.

### Use the bundled client

The included Python client is an alternative entry point. It needs the separate optional dependencies in `requirements-pixellab.txt`:

```sh
python -m pip install -r requirements-pixellab.txt
python scripts/pixellab.py list
python scripts/pixellab.py schema create_character
```

`list` and `schema` read the live catalog without generating anything. To generate, save a request such as:

```json
{
  "description": "a traveling botanist with a green coat and canvas satchel",
  "n_directions": 8,
  "size": 48
}
```

```sh
python scripts/pixellab.py call create_character character-request.json
```

Discover exact tool names and schemas with `list` and `schema` before calling; the catalog changes over time. Submit the job, keep its identifier, and poll its retrieval tool until it completes or fails, respecting retry delays. Save returned assets locally, preserve their frame and direction information, then refine them on the native grid like any generated image. Report service errors directly.

The client exits with code 2 and a short message when the dependencies or token are missing.
