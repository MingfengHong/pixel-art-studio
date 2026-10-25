# Style and pixel craft

## Reference → brief

Study the reference image and translate its visual features into drawing decisions:

| Decision | Inspect | Record |
|---|---|---|
| Grid | Unscaled edges and repeated details | Native sprite/tile dimensions; display scale separately |
| Silhouette | Large masses, negative space, head/body relation | Proportions and distinguishing features |
| View | Visible top/front/side planes | Side view, top-down, three-quarter, or isometric conventions |
| Color | Repeated ramps and neighboring materials | Exact palette if required; otherwise tonal relationships |
| Edges | External and internal boundaries | No outline, selective outline, or measured outline width/color |
| Light | Consistent highlight/shadow placement | Direction and tones per material |
| Detail | Clusters, texture, dithering, isolated accents | Detail budget appropriate to output size |

Choose dimensions, edge treatment, and palette for the current asset. A compact 16×16 sprite, a 32×48 character, and an outline-free four-color icon each benefit from proportions and detail suited to their canvas.

## Pixel discipline

- Work on one intentional logical grid. Keep critical coordinates integral. Native sprites and display zoom are separate outputs.
- Use nearest-neighbor for integer enlargement. At fractional scales, nearest-neighbor still produces unequal pixel widths.
- Prefer readable clusters to accidental noise. Single pixels can be essential eyes, highlights, stars, or texture.
- Use selective anti-aliasing, dithering, colored outlines, and semi-transparency when they support the chosen visual direction.
- Establish contrast by value and shape as well as hue. Review similar items in grayscale or silhouette if they are hard to distinguish.
- Keep pixel density, baseline, pivot, material ramps, and light consistent across a set.

## Finishing the artwork

At native size: can a viewer identify the object, distinguish states, and see important features? At enlarged size: are contours intentional, clusters clean, and transparent edges free of unintended halos? In context: does the asset remain visible without competing with the focal point?

For motion, inspect extreme/contact frames and the loop seam, and play the sequence if possible. For terrain, repeat tiles in a 3×3 arrangement and inspect intersections as well as straight edges. For UI, use the actual longest labels and largest expected counts.

