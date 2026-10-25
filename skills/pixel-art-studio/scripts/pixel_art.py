"""Portable pixel-grid rendering and explicit raster checks. Requires Pillow."""
import argparse
from collections import Counter
import json
from pathlib import Path
import re
import string
import sys

from PIL import Image, ImageDraw


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def protect_inputs(inputs, outputs):
    for source in map(Path, inputs):
        for output in map(Path, outputs):
            if source.resolve() == output.resolve() or (output.exists() and source.samefile(output)):
                raise ValueError(f"Output would overwrite an input: {output}")


def rgba(value):
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?", value):
        raise ValueError(f"Expected #RRGGBB or #RRGGBBAA, got {value!r}")
    result = tuple(int(value[i:i + 2], 16) for i in range(1, len(value), 2))
    return result if len(result) == 4 else result + (255,)


def positive(value):
    value = int(value)
    if value < 1:
        raise argparse.ArgumentTypeError("Expected a positive integer")
    return value


def integer(value, label, minimum=1):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")
    return value


def load_sprite(path):
    doc = read_json(path)
    if doc.get("version") != 1:
        raise ValueError("Sprite version must be 1")
    if not isinstance(doc.get("name"), str) or not doc["name"].strip():
        raise ValueError("Sprite needs a nonempty name")
    canvas = doc.get("canvas")
    if not isinstance(canvas, list) or len(canvas) != 2:
        raise ValueError("canvas must be [width, height]")
    w, h = [integer(v, "canvas dimension") for v in canvas]
    palette = doc.get("palette")
    if not isinstance(palette, dict) or not palette:
        raise ValueError("palette must be a nonempty character-to-hex object")
    if any(len(k) != 1 or k == "." or k.isspace() for k in palette):
        raise ValueError("Palette keys must be single non-space characters other than '.'")
    colors = {k: rgba(v) for k, v in palette.items()}
    colors["."] = (0, 0, 0, 0)
    pivot = doc.get("pivot", [w // 2, h])
    if not isinstance(pivot, list) or len(pivot) != 2:
        raise ValueError("pivot must be [x, y] in native pixels")
    if any(type(v) is not int or not 0 <= v <= bound for v, bound in zip(pivot, (w, h))):
        raise ValueError("pivot must lie on or within the canvas bounds")
    frames = doc.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("At least one frame is required")
    names, images = set(), []
    for frame in frames:
        name = frame.get("name")
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("Frame names must be nonempty and unique")
        names.add(name)
        integer(frame.get("duration_ms"), "duration_ms")
        rows = frame.get("rows")
        if not isinstance(rows, list) or len(rows) != h or any(not isinstance(r, str) or len(r) != w for r in rows):
            raise ValueError(f"Frame {name}: expected exactly {h} rows of {w} characters")
        unknown = set("".join(rows)) - colors.keys()
        if unknown:
            raise ValueError(f"Frame {name}: unknown palette keys {sorted(unknown)}")
        pixels = [colors[k] for row in rows for k in row]
        if not any(p[3] for p in pixels) and frame.get("allow_empty") is not True:
            raise ValueError(f"Frame {name} is empty; set allow_empty: true for an intentional blank")
        im = Image.new("RGBA", (w, h))
        im.putdata(pixels)
        images.append(im)
    return doc, images, pivot


def checker(size):
    im = Image.new("RGBA", size, "#dce0e4")
    draw = ImageDraw.Draw(im)
    for y in range(0, size[1], 8):
        for x in range(0, size[0], 8):
            if (x // 8 + y // 8) % 2:
                draw.rectangle((x, y, x + 7, y + 7), fill="#b8c0c8")
    return im


def make_sheet(images, labels, scale=4, columns=4):
    # Default Pillow fonts do not cover CJK. Keep previews unambiguous without
    # redistributing a font; exact Unicode names remain in the source/metadata.
    labels = [f"{i + 1:02d}: " + label.encode("ascii", "backslashreplace").decode("ascii") for i, label in enumerate(labels)]
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    font_width = max(measure.textbbox((0, 0), label)[2] for label in labels)
    cell_w = max(max(im.width for im in images) * scale + 16, font_width + 16)
    cell_h = max(im.height for im in images) * scale + 36
    columns = min(columns, len(images))
    out = Image.new("RGBA", (columns * cell_w, ((len(images) + columns - 1) // columns) * cell_h), "#202735")
    draw = ImageDraw.Draw(out)
    for i, (im, label) in enumerate(zip(images, labels)):
        enlarged = im.resize((im.width * scale, im.height * scale), Image.Resampling.NEAREST)
        tile = checker(enlarged.size)
        tile.alpha_composite(enlarged)
        x, y = (i % columns) * cell_w, (i // columns) * cell_h
        out.paste(tile, (x + 8, y + 8))
        draw.text((x + 8, y + cell_h - 20), label, fill="#ffffff")
    return out


def render(source, out, scale=4, columns=4, padding=1):
    out = Path(out)
    protect_inputs([source], [out / name for name in ("atlas.png", "atlas.json", "preview.png")])
    doc, images, pivot = load_sprite(source)
    out.mkdir(parents=True, exist_ok=True)
    w, h = doc["canvas"]
    columns = min(columns, len(images))
    rows = (len(images) + columns - 1) // columns
    atlas = Image.new("RGBA", (columns * (w + padding) - padding, rows * (h + padding) - padding))
    records = []
    for i, (im, frame) in enumerate(zip(images, doc["frames"])):
        x, y = (i % columns) * (w + padding), (i // columns) * (h + padding)
        atlas.paste(im, (x, y))
        records.append({"name": frame["name"], "rect": [x, y, w, h], "duration_ms": frame["duration_ms"], "pivot": pivot})
    atlas.save(out / "atlas.png")
    make_sheet(images, [f["name"] for f in doc["frames"]], scale, columns).save(out / "preview.png")
    write_json(out / "atlas.json", {"format": "pixel-art-studio-atlas-v1", "name": doc["name"], "image": "atlas.png", "canvas": [w, h], "size": list(atlas.size), "padding": padding, "frames": records})
    return {"frames": len(images), "atlas_size": list(atlas.size), "output": str(out)}


def from_png(source, out):
    protect_inputs([source], [out])
    with Image.open(source) as opened:
        im = opened.convert("RGBA")
    keys = string.ascii_letters + string.digits + "!$%&()*+,-/:;<=>?@[]^_{|}~"
    colors = sorted({p for p in im.getdata() if p[3]})
    if len(colors) > len(keys):
        raise ValueError(f"Grid format supports {len(keys)} colors; image has {len(colors)}. Use the original editor source or simplify deliberately; no automatic quantization.")
    mapping = dict(zip(colors, keys))
    pixels = list(im.getdata())
    rows = ["".join(mapping[p] if p[3] else "." for p in pixels[y * im.width:(y + 1) * im.width]) for y in range(im.height)]
    if not colors:
        raise ValueError("Input image is entirely transparent")
    write_json(out, {"version": 1, "name": Path(source).stem, "canvas": list(im.size), "pivot": [im.width // 2, im.height], "palette": {key: "#" + "".join(f"{v:02x}" for v in color) for color, key in mapping.items()}, "frames": [{"name": "default", "duration_ms": 100, "rows": rows}]})
    return {"output": str(out), "colors": len(colors), "size": list(im.size)}


def inspect(source, size=None, palette=None, max_colors=None, binary_alpha=False, scale=None):
    with Image.open(source) as opened:
        im = opened.convert("RGBA")
    pixels = list(im.getdata())
    visible = Counter(p for p in pixels if p[3])
    alpha = Counter(p[3] for p in pixels)
    errors = []
    if not visible:
        errors.append("image is entirely transparent")
    if size and list(im.size) != list(size):
        errors.append(f"expected size {list(size)}, got {list(im.size)}")
    if binary_alpha and any(a not in (0, 255) for a in alpha):
        errors.append("semi-transparent pixels violate binary alpha")
    if max_colors is not None and len(visible) > max_colors:
        errors.append(f"{len(visible)} visible RGBA colors exceed {max_colors}")
    if palette:
        data = read_json(palette)
        values = data["palette"]
        allowed = {rgba(c) for c in (values.values() if isinstance(values, dict) else values)}
        off = sum(count for color, count in visible.items() if color not in allowed)
        if off:
            errors.append(f"{off} visible pixels are outside the declared RGBA palette")
    bad_blocks = 0
    if scale:
        if im.width % scale or im.height % scale:
            errors.append(f"dimensions are not divisible by scale {scale}")
        else:
            # Compare every pixel, including alpha, not just the four block corners.
            px = im.load()
            for y in range(0, im.height, scale):
                for x in range(0, im.width, scale):
                    expected = px[x, y]
                    if any(px[x + dx, y + dy] != expected for dy in range(scale) for dx in range(scale)):
                        bad_blocks += 1
            if bad_blocks:
                errors.append(f"{bad_blocks} nonuniform {scale}x{scale} blocks")
    return {"size": list(im.size), "visible_rgba_colors": len(visible), "alpha_values": sorted(alpha), "visible_bbox": im.getchannel("A").getbbox(), "nonuniform_blocks": bad_blocks, "errors": errors, "passed": not errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("render", help="Render editable grid JSON to atlas, metadata, and labeled preview")
    p.add_argument("source", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--scale", type=positive, default=4)
    p.add_argument("--columns", type=positive, default=4)
    p.add_argument("--padding", type=int, choices=range(0, 17), default=1)
    p = sub.add_parser("from-png", help="Convert exact visible colors to an editable grid; no quantization")
    p.add_argument("source", type=Path)
    p.add_argument("out", type=Path)
    p = sub.add_parser("inspect", help="Report image properties and fail violated explicit constraints")
    p.add_argument("source", type=Path)
    p.add_argument("--size", nargs=2, type=positive, metavar=("WIDTH", "HEIGHT"))
    p.add_argument("--palette", type=Path)
    p.add_argument("--max-colors", type=positive)
    p.add_argument("--binary-alpha", action="store_true")
    p.add_argument("--scale", type=positive)
    p = sub.add_parser("sheet", help="Create a labeled contact sheet without changing source images")
    p.add_argument("sources", nargs="+", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--scale", type=positive, default=4)
    p.add_argument("--columns", type=positive, default=4)
    args = vars(parser.parse_args())
    command = args.pop("command")
    try:
        if command == "sheet":
            protect_inputs(args["sources"], [args["out"]])
            images = []
            for path in args["sources"]:
                with Image.open(path) as opened:
                    images.append(opened.convert("RGBA"))
            make_sheet(images, [p.stem for p in args["sources"]], args["scale"], args["columns"]).save(args["out"])
            result = {"output": str(args["out"]), "images": len(images)}
        else:
            result = {"render": render, "from-png": from_png, "inspect": inspect}[command](**args)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 1 if result.get("passed") is False else 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
