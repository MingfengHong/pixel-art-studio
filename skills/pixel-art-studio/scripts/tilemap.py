"""Assemble scenes from hand-made tilesets: grid layers, autotiled terrain, parallax layers and seated props."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import zlib

from PIL import Image, ImageDraw
import pixel_art as pa
from art_common import load_frames as load_set


class Library:
    def __init__(self, base, sets):
        self.images, self.files = {}, []
        for path in sets:
            self.files.append(base / path)
            for name, im in load_set(base / path).items():
                if name in self.images:
                    raise ValueError(f'Duplicate tile or sprite name across sets: {name}')
                self.images[name] = im

    def pick(self, spec, x=0, y=0):
        """A legend value: a name, a list of variants (stable per cell), or {tile, flip}."""
        if isinstance(spec, list):
            spec = spec[zlib.crc32(f'{x},{y}'.encode()) % len(spec)]
        name, flip = (spec, None) if isinstance(spec, str) else (spec['tile'], spec.get('flip'))
        if name not in self.images:
            raise ValueError(f'Unknown tile or sprite: {name}')
        im = self.images[name]
        if flip in ('x', 'xy'):
            im = im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        if flip in ('y', 'xy'):
            im = im.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        return im, name


def side_piece(rows, x, y, ch, rule):
    """Side-view terrain: pick top, corner, side or fill from which neighbours are open."""
    same = lambda xx, yy: 0 <= yy < len(rows) and (xx < 0 or xx >= len(rows[0]) or rows[yy][xx] == ch) if yy >= 0 else False
    up, left, right = same(x, y-1), same(x-1, y), same(x+1, y)
    if not up and not left and 'top_left' in rule:
        return rule['top_left']
    if not up and not right and 'top_right' in rule:
        return rule['top_right']
    if not up:
        return rule['top']
    if not left and 'left' in rule:
        return rule['left']
    if not right and 'right' in rule:
        return rule['right']
    return rule.get('fill', rule['top'])


def mask_piece(rows, x, y, ch, rule):
    """Top-down terrain: 4-bit neighbour mask (north 1, east 2, south 4, west 8); edges count as connected."""
    mask = 0
    for bit, dx, dy in [(1, 0, -1), (2, 1, 0), (4, 0, 1), (8, -1, 0)]:
        nx, ny = x+dx, y+dy
        if not (0 <= ny < len(rows) and 0 <= nx < len(rows[0])) or rows[ny][nx] == ch:
            mask |= bit
    return rule.get(str(mask), rule.get('default'))


def render_layer(lib, layer, size, n, base_x=0):
    w, h = size
    im = Image.new('RGBA', (w*n, h*n))
    rows = layer['rows']
    if len(rows) != h or any(len(r) != w for r in rows):
        raise ValueError(f"Layer {layer.get('name')}: expected {h} rows of {w} characters")
    names = []
    for y, row in enumerate(rows):
        names.append([])
        for x, ch in enumerate(row):
            if ch == '.':
                names[-1].append(None)
                continue
            terrain = layer.get('terrain', {}).get(ch)
            if terrain:
                pick = mask_piece if terrain.get('rule') == 'mask' else side_piece
                spec = pick(rows, x, y, ch, terrain)
            elif ch in layer.get('legend', {}):
                spec = layer['legend'][ch]
            else:
                raise ValueError(f"Layer {layer.get('name')}: no legend entry for {ch!r}")
            if spec is None:
                raise ValueError(f"Layer {layer.get('name')}: no tile for {ch!r} at {x},{y}")
            tile, name = lib.pick(spec, x + base_x, y)
            im.alpha_composite(tile, (x*n, y*n + n - tile.height))
            names[-1].append(name)
    return im, names


def background(size, spec):
    im = Image.new('RGBA', size)
    if isinstance(spec, str):
        im.paste(Image.new('RGBA', size, spec))
        return im
    d = ImageDraw.Draw(im)
    for band in spec:  # [{color, from, to}] in pixels, top to bottom
        d.rectangle((0, band['from'], size[0]-1, band['to']), fill=band['color'])
    return im


def place(lib, items, n):
    """Resolve object positions; `tile` stands a sprite on the bottom of a cell, sunk by `seat` pixels."""
    placed = []
    for item in items:
        sprite, name = lib.pick(item['sprite'] if 'flip' not in item else {'tile': item['sprite'], 'flip': item['flip']})
        if 'tile' in item:
            tx, ty = item['tile']
            x = tx*n + (n - sprite.width)//2 + item.get('dx', 0)
            y = (ty+1)*n - sprite.height + item.get('seat', 0)
        else:
            x, y = item['at']
        placed.append((y + sprite.height, x, y, sprite, name, item))
    placed.sort(key=lambda p: (p[5].get('z', 0), p[0]))
    return placed


def draw(canvas, placed):
    for _, x, y, sprite, name, item in placed:
        if item.get('shadow'):
            layer = Image.new('RGBA', canvas.size)
            sw = max(4, round(sprite.width*.8))
            ImageDraw.Draw(layer).ellipse((x+(sprite.width-sw)//2, y+sprite.height-3, x+(sprite.width+sw)//2, y+sprite.height+1),
                                          fill=(20, 12, 24, 70))
            canvas.alpha_composite(layer)
        canvas.alpha_composite(sprite, (x, y))


def generate(recipe, out, scale=3):
    recipe, out = Path(recipe), Path(out)
    doc = pa.read_json(recipe)
    n = pa.integer(doc.get('tile_size', 16), 'tile size')
    w, h = doc['size']
    lib = Library(recipe.parent, doc['tilesets'])
    outputs = [out/name for name in ('scene.png', 'preview.png', 'map.json', 'source.json')]
    outputs += [out/'layers'/f"{layer['name']}.png" for layer in doc['layers']]
    outputs += [out/'inputs'/Path(p).name for p in doc['tilesets']]
    pa.protect_inputs([recipe, *lib.files], outputs)
    scene = background((w*n, h*n), doc.get('background', '#00000000'))
    layers, data, placed_all = {}, [], []
    for layer in doc['layers']:
        im, names = render_layer(lib, layer, (w, h), n)
        # Objects listed on a layer belong to its depth (a far windmill stays behind nearer hills).
        own = place(lib, layer.get('objects', []), n)
        draw(im, own)
        layers[layer['name']] = im
        data.append({'name': layer['name'], 'parallax': layer.get('parallax', 1), 'tiles': names,
                     'objects': [{'sprite': p[4], 'at': [p[1], p[2]]} for p in own]})
        scene.alpha_composite(im)
    placed = place(lib, doc.get('objects', []), n)
    draw(scene, placed)
    out.mkdir(parents=True, exist_ok=True)
    (out/'layers').mkdir(exist_ok=True)
    for name, im in layers.items():
        im.save(out/'layers'/f'{name}.png')
    scene.save(out/'scene.png')
    scene.resize((scene.width*scale, scene.height*scale), Image.Resampling.NEAREST).save(out/'preview.png')
    portable = deepcopy(doc)
    (out/'inputs').mkdir(exist_ok=True)
    portable['tilesets'] = []
    for path in doc['tilesets']:
        src = recipe.parent/path
        (out/'inputs'/src.name).write_bytes(src.read_bytes())
        portable['tilesets'].append(f'inputs/{src.name}')
    pa.write_json(out/'source.json', portable)
    pa.write_json(out/'map.json', {'tile_size': n, 'size': [w, h], 'layers': data,
                                   'objects': [{'sprite': p[4], 'at': [p[1], p[2]], 'size': list(p[3].size)} for p in placed]})
    return {'layers': len(layers), 'objects': len(placed), 'size': [w*n, h*n], 'output': str(out)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scale', type=pa.positive, default=3)
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.recipe, args.out, args.scale)))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Error: {error}\n')


if __name__ == '__main__':
    main()
