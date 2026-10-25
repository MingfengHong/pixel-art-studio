# Animation and effects

## Frame planning

Choose action, direction, loop behavior, frame count, and timing first. Keep canvas dimensions and a common pivot stable to avoid playback jitter. State pivots in native pixels, top-left (0, 0), unless an engine explicitly expects normalized coordinates.

Build walking motion around foot contact, weight shifts, and hand/tool position. Use small bobs for idle motion. Draw the appropriate silhouette and visible features for each requested direction, preserving asymmetric details.

Store per-frame durations. Use a contact sheet to refine anatomy and registration, and playback to refine timing and the loop seam.

## Effects

Give the effect a purpose: impact, reward, weather, movement, attention, or transition. Sketch anticipation, peak, and decay as applicable. Animate cluster shapes and silhouettes alongside opacity. Match outline, palette, and density to the host art unless the brief distinguishes magic/light/UI effects.

Start with a short 3–6-pose impact or puff to establish the motion, then expand the sequence as needed. Use smears, additive glow, rotation, and alpha trails when the style supports them.

Record random seeds for reproducible particle previews. For crisp pixels, quantize rendered positions and avoid accidental fractional camera transforms. Shake needs sufficient overscan and usually keeps reading-critical HUD stable; specify which layers move.

Deliver ordered frames, timing, pivot, loop/one-shot intent, and a playback preview where available. Adapt frame rectangles and pivots to the target engine when integration is requested.

## Render frames and layered keyframes

```sh
python scripts/animate.py assets/examples/layered-animation/recipe.json --out output/attack
```

Run from the skill folder. The [example](../assets/examples/layered-animation/recipe.json) animates a character and attached sword on a 48×48 canvas.

A sequence recipe uses `canvas`, `pivot`, `loop` and `frames`. Each frame has an image `source` (a PNG or `set.json#frame`), optional source `rect`, destination `at` and `duration_ms`. Use it to import an existing sprite sheet or generated frame sequence.

A layered recipe uses `frame_count`, `duration_ms` and ordered `layers`:

- `id`, `source` and optional `rect` identify a layer. A `source` is a PNG or one frame of a grid source or atlas (`set.json#frame`).
- `pivot` gives its rotation anchor within the cropped image.
- `keys` contain ordered `time` values from 0 to 1, `x`, `y`, `angle` in degrees and `opacity` in 0–1.
- Optional `parent` refers to an earlier layer; child positions are offsets from its pivot and inherit its angle.
- Keys interpolate linearly. `hold: true` holds a key until the next; sampled positions snap to pixels.
- A key with its own `source` (and optional `rect`) swaps the layer's image from that time on. Use it to play hand-drawn frames on a moving layer, for example a cast pose, a flickering projectile or the three beats of an explosion. Show or hide a layer with `opacity` 0 or 1 on held keys.

The [skill-cast example](../assets/examples/skill-cast/recipe.json) combines these: a mage switches to its cast frame, a fireball layer flies across with two flicker frames, and a burst layer swaps through flash, fire ring and smoke while the target shows its hurt frame.

Give loops matching end poses and leave room around moving limbs. For a static pose use one frame and a key at zero. Use layers for cutout motion; redraw joint silhouettes for articulated pixel animation where needed. Use [production workflows](production-workflows.md) for text-driven motion and generated in-between drawings.

Outputs include ordered PNGs in `frames/`, a named atlas, `animation.json` with timing/pivot, a contact sheet and `preview.gif`. GIFs show transparency on a checkerboard; PNGs retain alpha. Portable `source.json` includes copied image inputs.
