# Pixel grids and export

For small, exact sprites and icons, the agent writes the pixels directly as a text grid. `pixel_art.py` renders those grids, converts PNGs back into grids, builds reference sheets and checks images automatically.

@shots examples/beacon/preview.png|An 8×8 beacon in two poses, examples/ui-components/preview.png|Small UI controls, examples/tile-scene/preview.png|A cottage built from tiles

## The grid format

```json
{
  "version": 1,
  "name": "outline-free-beacon",
  "canvas": [8, 8],
  "pivot": [4, 8],
  "palette": {"a": "#f2edd7", "b": "#8fb9a8", "c": "#3a6b73"},
  "frames": [
    {"name": "rest", "duration_ms": 400, "rows": [
      "........", "...bb...", "..baab..", ".baaaab.",
      "..baab..", "...cc...", "..cccc..", "........"]}
  ]
}
```

Each palette key is one character; `.` is transparent. Every frame has a unique `name`, a positive `duration_ms` and exactly one row per pixel line. `pivot` defaults to bottom center.

## Commands

Run from the skill folder:

```bash
python scripts/pixel_art.py render assets/examples/beacon/source.json --out output/beacon --scale 8
```

| Goal | Command |
|---|---|
| Render a grid to an atlas, metadata and preview | `pixel_art.py render SOURCE --out DIR [--scale] [--columns] [--padding]` |
| Turn a PNG into an editable grid | `pixel_art.py from-png IMAGE.png OUT.json` |
| Build a labeled reference sheet | `pixel_art.py sheet A.png B.png --out SHEET.png` |
| Check size, colors, alpha or zoom | `pixel_art.py inspect IMAGE.png [--size W H] [--max-colors N] [--binary-alpha] [--palette FILE] [--scale N]` |

`inspect` exits with 0 on a match, 1 on a mismatch and 2 on bad input, so agents can use it as an automated check.

## Atlas metadata

`atlas.json` (format `pixel-art-studio-atlas-v1`) lists the image, native canvas, padding and ordered frames. Each frame has a `name`, `rect: [x, y, width, height]`, `duration_ms` and `pivot`. The UI, world and animation tools use a packed variant keyed by frame name.

To import into an engine, map each `rect` and `pivot` onto its sprite importer, use nearest-neighbor filtering and integer scaling. If your renderer filters textures, add padding or extrusion to the atlas.

## Pixel discipline

- Keep one logical grid; never mix pixel densities or scale by fractions.
- Look at every asset at native size and at an integer zoom, on light and dark backgrounds.
- Prefer clean color clusters to noise; single pixels are fine when they are eyes, highlights or stars.

The craft checklist is in [style-and-quality.md]({{repo}}/blob/main/skills/pixel-art-studio/references/style-and-quality.md); every command and format detail is in [tools-and-export.md]({{repo}}/blob/main/skills/pixel-art-studio/references/tools-and-export.md).
