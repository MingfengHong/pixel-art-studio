"""Build directional pixel characters from a role palette and layered parts."""
import argparse
import json
from pathlib import Path
import sys

from PIL import Image

import pixel_art as pa


DEFAULT_TEMPLATE = Path(__file__).resolve().parents[1] / "assets/templates/character.json"
VIEWS = ("front", "back", "right", "left")
VIEWS_8 = ("front", "front-right", "right", "back-right", "back", "back-left", "left", "front-left")
POSES = ("stand", "idle", "walk-a", "walk-b")


def overlay(rows, strokes):
    grid = [list(row) for row in rows]
    for y, x, text in strokes:
        if not 0 <= y < len(grid) or x < 0 or x + len(text) > len(grid[y]):
            raise ValueError(f"Part extends outside the canvas at ({x}, {y})")
        grid[y][x:x + len(text)] = text
    return ["".join(row) for row in grid]


def build_source(recipe, template):
    colors = template["colors"] | recipe.get("colors", {})
    unknown = colors.keys() - template["colors"].keys()
    if unknown:
        raise ValueError(f"Unknown color roles: {', '.join(sorted(unknown))}")
    palette = {key: colors[role] for key, role in template["roles"].items()}
    for color in palette.values():
        pa.rgba(color)
    parts = recipe.get("parts", [])
    unknown = set(parts) - template["parts"].keys()
    if unknown:
        raise ValueError(f"Unknown parts: {', '.join(sorted(unknown))}")
    timing = {"stand": 600, "idle": 180, "step": 150} | recipe.get("timing_ms", {})
    for key, value in timing.items():
        pa.integer(value, key + " duration")
    directions = recipe.get("directions", 4)
    if directions not in (4, 8):
        raise ValueError("directions must be 4 or 8")
    views = VIEWS_8 if directions == 8 else VIEWS
    frames, clips = [], {}
    mirrors = {"left": "right", "front-left": "front-right", "back-left": "back-right"}
    for view in views:
        base_view = mirrors.get(view, view)
        base = template["views"][base_view]
        for part in parts:
            base = overlay(base, template["parts"][part].get(base_view, []))
        for pose in POSES:
            rows = list(base)
            if pose == "idle":
                top, bottom = template["idle_band"]
                rows[top:bottom + 1] = ["." * template["canvas"][0]] + rows[top:bottom]
            elif pose.startswith("walk-"):
                rows = overlay(rows, template["steps"][pose][base_view])
            if view in mirrors:
                rows = [row[::-1] for row in rows]
            duration = timing["step" if pose.startswith("walk-") else pose]
            frames.append({"name": f"{view}-{pose}", "duration_ms": duration, "rows": rows})
        clips[f"{view}-idle"] = {
            "loop": True,
            "frames": [{"name": f"{view}-{pose}", "duration_ms": timing[pose]} for pose in ("stand", "idle")],
        }
        clips[f"{view}-walk"] = {
            "loop": True,
            "frames": [{"name": f"{view}-{pose}", "duration_ms": timing["step"]} for pose in ("walk-a", "stand", "walk-b", "stand")],
        }
    source = {
        "version": 1, "name": recipe["name"], "canvas": template["canvas"],
        "pivot": template["pivot"], "palette": palette, "frames": frames,
    }
    return source, clips


def playback(images, clips, action, out, scale):
    frames = []
    views = [name.removesuffix("-idle") for name in clips if name.endswith("-idle")]
    first_clip = clips[f"front-{action}"]["frames"]
    for index in range(len(first_clip)):
        selected = [images[clips[f"{view}-{action}"]["frames"][index]["name"]] for view in views]
        frames.append(pa.make_sheet(selected, views, scale=scale, columns=4).convert("RGB"))
    # A shared palette keeps colors stable through the entire GIF loop.
    strip = Image.new("RGB", (frames[0].width, frames[0].height * len(frames)))
    for index, frame in enumerate(frames):
        strip.paste(frame, (0, index * frame.height))
    palette = strip.quantize(colors=256, dither=Image.Dither.NONE)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(out, save_all=True, append_images=indexed[1:], loop=0,
                    duration=[frame["duration_ms"] for frame in first_clip], disposal=2, optimize=False)


def generate(recipe_path, out, scale=6):
    recipe_path, out = Path(recipe_path), Path(out)
    recipe = pa.read_json(recipe_path)
    template_path = recipe_path.parent / recipe["template"] if "template" in recipe else DEFAULT_TEMPLATE
    filenames = ("source.json", "atlas.png", "atlas.json", "preview.png", "animations.json", "idle.gif", "walk.gif")
    pa.protect_inputs([recipe_path, template_path], [out / name for name in filenames])
    source, clips = build_source(recipe, pa.read_json(template_path))
    out.mkdir(parents=True, exist_ok=True)
    pa.write_json(out / "source.json", source)
    result = pa.render(out / "source.json", out, scale=scale, columns=4)
    pa.write_json(out / "animations.json", {"name": source["name"], "atlas": "atlas.json", "clips": clips})
    doc, images, _ = pa.load_sprite(out / "source.json")
    by_name = dict(zip((frame["name"] for frame in doc["frames"]), images))
    for action in ("idle", "walk"):
        playback(by_name, clips, action, out / f"{action}.gif", scale)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("recipe", type=Path, help="Character recipe JSON")
    parser.add_argument("--out", type=Path, required=True, help="Destination folder")
    parser.add_argument("--scale", type=pa.positive, default=6, help="Integer preview enlargement")
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.recipe, args.out, args.scale), ensure_ascii=False))
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
