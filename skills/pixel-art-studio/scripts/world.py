"""Create terrain tiles, layered top-down maps, platform terrain and isometric blocks."""
import argparse
from copy import deepcopy
import json
from pathlib import Path
import random

from PIL import Image, ImageDraw
import pixel_art as pa
from art_common import atlas, load_image


# Material ramps: base first, then darker, lighter and accent tones.
DEFAULT = {
    'grass': ['#5a9b3c', '#4a8433', '#6db347', '#86c957', '#3d6e2b'],
    'water': ['#3f8fc0', '#3a7fb0', '#5aa8d6', '#c9ecf5', '#2f6c99'],
    'path':  ['#c8995c', '#b38550', '#dbb072', '#9a6f42'],
    'soil':  ['#8a5634', '#6e4229', '#a46a40', '#5a3520'],
    'bank':  ['#9a6b3e', '#7a5030', '#b88a55', '#5e3d24'],
    'flowers': ['#f7e26b', '#ffffff', '#f2a0c0', '#9cc7ff'],
    'stone': ['#b9b3a6', '#7d776c'],
}
SIDES = [(1, 0, -1), (2, 1, 0), (4, 0, 1), (8, -1, 0)]  # north, east, south, west


def neighbors(grid, x, y, accept):
    """Bit mask of the four neighbors whose cell is in `accept`; cells outside the map count as connected."""
    result = 0
    for bit, dx, dy in SIDES:
        nx, ny = x+dx, y+dy
        if not (0 <= ny < len(grid) and 0 <= nx < len(grid[0])) or grid[ny][nx] in accept:
            result |= bit
    return result


def put(px, n, x, y, color):
    px[x % n, y % n] = pa.rgba(color)


def grass(c, n, rng, variant=0):
    """Grass with tufts; variants add clumps, flowers or a pebble so large fields don't repeat."""
    im = Image.new('RGBA', (n, n), c[0]); px = im.load()
    for _ in range(n*n//9):
        x, y = rng.randrange(n), rng.randrange(n)
        put(px, n, x, y, c[1])
    for _ in range(n*n//28 + (n*n//20 if variant == 1 else 0)):
        x, y = rng.randrange(n), rng.randrange(n)
        put(px, n, x, y+1, c[1]); put(px, n, x+1, y, c[2]); put(px, n, x+2, y+1, c[1]); put(px, n, x+1, y+1, c[4])
        if rng.random() < .35:
            put(px, n, x+1, y-1, c[3])
    if variant == 2:
        flowers = DEFAULT['flowers']
        for _ in range(rng.choice([1, 2])):
            x, y, petal = rng.randrange(2, n-2), rng.randrange(2, n-2), rng.choice(flowers[1:])
            for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1)]:
                put(px, n, x+dx, y+dy, petal)
            put(px, n, x, y, flowers[0]); put(px, n, x, y+2, c[4])
    if variant == 3:
        stone = DEFAULT['stone']
        x, y = rng.randrange(2, n-3), rng.randrange(2, n-3)
        for dx in range(2):
            put(px, n, x+dx, y, stone[0]); put(px, n, x+dx, y+1, stone[1])
        put(px, n, x+2, y+1, stone[1])
    return im


def speckled(c, n, rng, density=6):
    im = Image.new('RGBA', (n, n), c[0]); px = im.load()
    for _ in range(n*n//density):
        x, y = rng.randrange(n), rng.randrange(n)
        put(px, n, x, y, rng.choice(c[1:3]))
    return im


def fringe(tile, lawn, mask, rng, lip):
    """Let grass grow over the sides of a tile that do not connect to the same material."""
    im = tile.copy(); px, gx = im.load(), lawn.load(); n = im.width
    for bit, _, _ in SIDES:
        if mask & bit:
            continue
        for i in range(n):
            depth = 2 + (rng.random() < .45)
            for k in range(depth+1):
                x, y = {1: (i, k), 2: (n-1-k, i), 4: (i, n-1-k), 8: (k, i)}[bit]
                px[x, y] = pa.rgba(lip) if k == depth else gx[x, y]
    return im


def water(c, bank, n, rng, mask):
    """Water with ripples; a dirt bank where land lies to the north and foam along every shore."""
    im = Image.new('RGBA', (n, n), c[0]); px = im.load()
    for _ in range(n//3):
        x, y, length = rng.randrange(n), rng.randrange(n), rng.choice([2, 3, 3, 4])
        for dx in range(length):
            put(px, n, x+dx, y, c[2])
        put(px, n, x+1, y+1, c[1])
    d = ImageDraw.Draw(im)
    if not mask & 1:
        d.rectangle((0, 0, n-1, 2), fill=bank[0]); d.line((0, 0, n-1, 0), fill=bank[2])
        for x in range(0, n, 3):
            px[x, 1] = pa.rgba(bank[1])
        d.line((0, 3, n-1, 3), fill=bank[3]); d.line((0, 4, n-1, 4), fill=c[3])
    # Other shores: a dirt edge with a pale ripple just inside it.
    top = 5 if not mask & 1 else 0
    if not mask & 4:
        d.line((0, n-2, n-1, n-2), fill=c[2]); d.line((0, n-1, n-1, n-1), fill=bank[1])
    if not mask & 2:
        d.line((n-2, top, n-2, n-1), fill=c[2]); d.line((n-1, top, n-1, n-1), fill=bank[1])
    if not mask & 8:
        d.line((1, top, 1, n-1), fill=c[2]); d.line((0, top, 0, n-1), fill=bank[1])
    return im


def farmland(c, n, rng):
    im = Image.new('RGBA', (n, n), c[0]); px = im.load()
    for y in range(n):
        for x in range(n):
            if y % 4 == 1:
                px[x, y] = pa.rgba(c[1])
            elif y % 4 == 2 and rng.random() < .7:
                px[x, y] = pa.rgba(c[2])
    return im


def shadow(scene, x, y, w, h):
    """A soft drop shadow under an object whose box is (x, y, w, h)."""
    sw, sh = max(4, round(w*.7)), max(3, w//5)
    layer = Image.new('RGBA', scene.size)
    ImageDraw.Draw(layer).ellipse((x+(w-sw)//2, y+h-sh+1, x+(w-sw)//2+sw-1, y+h), fill=(25, 35, 15, 80))
    scene.alpha_composite(layer)


def generate(recipe, out, scale=2):
    recipe, out = Path(recipe), Path(out)
    doc = pa.read_json(recipe); n = pa.integer(doc.get('tile_size', 16), 'tile size')
    if n < 8:
        raise ValueError('Terrain tiles need at least 8 pixels')
    custom = dict(doc.get('palette', {}))
    if 'ground' in custom:
        custom.setdefault('grass', custom.pop('ground'))
    pal = DEFAULT | custom
    pal['grass'] = (pal['grass'] + DEFAULT['grass'])[:5]
    pal['water'] = (pal['water'] + DEFAULT['water'])[:5]
    seed = doc.get('seed', 7)
    rng = random.Random(seed)
    tiles = {f'grass-{v}': grass(pal['grass'], n, random.Random(seed*31+v), v) for v in range(4)}
    lawn = tiles['grass-0']
    dirt = speckled(pal['path'], n, random.Random(seed+1))
    soil = farmland(pal['soil'], n, random.Random(seed+2))
    for mask in range(16):
        tiles[f'path-{mask:02}'] = fringe(dirt, lawn, mask, random.Random(seed*7+mask), pal['grass'][4])
        tiles[f'farm-{mask:02}'] = fringe(soil, lawn, mask, random.Random(seed*11+mask), pal['grass'][4])
        tiles[f'water-{mask:02}'] = water(pal['water'], pal['bank'], n, random.Random(seed*13+mask), mask)
    grid = doc['map']
    if not grid or any(len(row) != len(grid[0]) for row in grid):
        raise ValueError('Map rows must have equal widths')
    w, h = len(grid[0]), len(grid)
    scene = Image.new('RGBA', (w*n, h*n))
    cells = []
    weights = doc.get('grass_variants', [60, 22, 12, 6])
    for y, row in enumerate(grid):
        cells.append([])
        for x, char in enumerate(row):
            if char == 'w':
                key = f"water-{neighbors(grid, x, y, 'w'):02}"
            elif char == 'p':
                key = f"path-{neighbors(grid, x, y, 'p'):02}"
            elif char == 'f':
                key = f"farm-{neighbors(grid, x, y, 'f'):02}"
            elif char == 'g':
                key = f"grass-{rng.choices(range(4), weights)[0]}"
            else:
                raise ValueError(f'Unknown map cell {char!r}; use g grass, p path, f farmland, w water')
            scene.alpha_composite(tiles[key], (x*n, y*n)); cells[-1].append(key)
    ground = scene.copy()

    # Objects: explicit placements plus seeded scatter, drawn with shadows and sorted by their base.
    inputs = [recipe]
    images = {}
    def load(source):
        # A PNG path, or "set.json#frame" for one frame of a grid source or atlas.
        if source not in images:
            inputs.append(recipe.parent/str(source).partition('#')[0])
            images[source] = load_image(recipe.parent, source)
        return images[source]
    placed = [dict(item) for item in doc.get('objects', [])]
    taken = set()
    for group in doc.get('scatter', []):
        local = random.Random(group.get('seed', seed+100+len(taken)))
        spots = [(x, y) for y, row in enumerate(grid) for x, ch in enumerate(row)
                 if ch in group.get('on', 'g') and (x, y) not in taken]
        local.shuffle(spots)
        for x, y in spots[:group.get('count', 6)]:
            taken.add((x, y))
            art = load(group['source'])
            jitter = max(0, n - art.width)
            placed.append({'source': group['source'], 'at': [x*n + local.randrange(jitter+1), (y+1)*n - art.height - local.randrange(3)],
                           'shadow': group.get('shadow', False), 'scattered': True})
    for item in placed:
        art = load(item['source'])
        if item.get('rect'):
            x, y, ww, hh = item['rect']; art = art.crop((x, y, x+ww, y+hh))
        item['_art'] = art
    if doc.get('sort', True):
        placed.sort(key=lambda item: item['at'][1] + item['_art'].height + item.get('depth', 0))
    for item in placed:
        art = item['_art']
        if item.get('shadow'):
            # Size the shadow from the visible pixels, so padding around a frame does not widen it.
            left, top, right, bottom = art.getbbox() or (0, 0, art.width, art.height)
            shadow(scene, item['at'][0] + left, item['at'][1] + top, right - left, bottom - top)
        scene.alpha_composite(art, tuple(item['at']))

    texture_names = ['grass', 'water', 'path', 'soil']
    textures = {'grass': lawn, 'water': water(pal['water'], pal['bank'], n, random.Random(seed), 15), 'path': dirt, 'soil': soil}
    outputs = [out/name for name in ('scene.png', 'source.json', 'ground.png', 'map.json', 'atlas.png', 'atlas.json', 'preview.png',
                                     'platformer.png', 'platform-top.png', 'isometric.png', 'isometric-tile.png')]
    outputs.extend(out/'tiles'/f'{name}.png' for name in tiles)
    outputs.extend(out/f'texture-{name}.png' for name in texture_names)
    sources = sorted({item['source'] for item in placed})
    suffix = lambda s: '.png' if '#' in s else Path(s).suffix
    outputs.extend(out/'inputs'/f'object-{i}{suffix(s)}' for i, s in enumerate(sources))
    pa.protect_inputs(inputs, outputs)
    out.mkdir(parents=True, exist_ok=True)
    (out/'tiles').mkdir(exist_ok=True)
    for name, im in tiles.items():
        im.save(out/'tiles'/f'{name}.png')
    for name, im in textures.items():
        im.save(out/f'texture-{name}.png')
    atlas(tiles, out, width=n*8+8)
    scene.save(out/'scene.png'); ground.save(out/'ground.png')
    previews, labels = [scene], ['top-down']

    if doc.get('platform'):
        rows = doc['platform']
        side = Image.new('RGBA', (len(rows[0])*n, len(rows)*n), pal['water'][1])
        top = Image.new('RGBA', (n, n)); tp = top.load()
        body = speckled(pal['soil'][:3], n, random.Random(seed+5), 9)
        top.alpha_composite(body)
        d = ImageDraw.Draw(top)
        d.rectangle((0, 0, n-1, 4), fill=pal['grass'][0]); d.line((0, 0, n-1, 0), fill=pal['grass'][3])
        for x in range(n):
            if x % 3 != 1:
                tp[x, 5] = pa.rgba(pal['grass'][4])
            if x % 4 == 2:
                tp[x, 1] = pa.rgba(pal['grass'][2])
        for y, row in enumerate(rows):
            for x, key in enumerate(row):
                if key == '#':
                    tile = (top if y == 0 or rows[y-1][x] != '#' else body).copy()
                    td = ImageDraw.Draw(tile)
                    if x == 0 or row[x-1] != '#':
                        td.line((0, 0, 0, n-1), fill=pal['soil'][3])
                    if x == len(row)-1 or row[x+1] != '#':
                        td.line((n-1, 0, n-1, n-1), fill=pal['soil'][3])
                    side.alpha_composite(tile, (x*n, y*n))
        side.save(out/'platformer.png'); top.save(out/'platform-top.png')
        previews.append(side); labels.append('platformer')
    if doc.get('isometric'):
        rows = doc['isometric']; depth = n//2
        block = Image.new('RGBA', (2*n, n+depth+1)); d = ImageDraw.Draw(block)
        d.polygon([(0, n//2), (n, n), (n, n+depth), (0, n//2+depth)], fill=pal['soil'][0])
        d.polygon([(n, n), (2*n-1, n//2), (2*n-1, n//2+depth), (n, n+depth)], fill=pal['soil'][1])
        d.polygon([(0, n//2), (n, 0), (2*n-1, n//2), (n, n)], fill=pal['grass'][0], outline=pal['grass'][2])
        iso = Image.new('RGBA', ((len(rows[0])+len(rows))*n, (len(rows[0])+len(rows))*n//2+depth+1))
        for y, row in enumerate(rows):
            for x, value in enumerate(row):
                if value:
                    iso.alpha_composite(block, ((x-y+len(rows)-1)*n, (x+y)*n//2))
        iso.save(out/'isometric.png'); block.save(out/'isometric-tile.png')
        previews.append(iso); labels.append('isometric')
    pa.make_sheet(previews, labels, scale=scale, columns=1).save(out/'preview.png')

    portable = deepcopy(doc)
    folder = out/'inputs'; folder.mkdir(exist_ok=True)
    renamed = {}
    for index, source in enumerate(sources):
        target = folder/f'object-{index}{suffix(source)}'
        if '#' in source:
            images[source].save(target)
        else:
            target.write_bytes((recipe.parent/source).read_bytes())
        renamed[source] = f'inputs/{target.name}'
    for item in portable.get('objects', []):
        item['source'] = renamed[item['source']]
    for group in portable.get('scatter', []):
        group['source'] = renamed[group['source']]
    pa.write_json(out/'source.json', portable)
    objects = [{k: v for k, v in item.items() if not k.startswith('_')} | {'source': renamed[item['source']]} for item in placed]
    pa.write_json(out/'map.json', {'tile_size': n, 'size': [w, h], 'mask_bits': {'north': 1, 'east': 2, 'south': 4, 'west': 8},
                                   'layers': [{'name': 'ground', 'tiles': cells}, {'name': 'objects', 'objects': objects}]})
    return {'tiles': len(tiles), 'objects': len(placed), 'map_size': [w, h], 'output': str(out)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe', type=Path); parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--scale', type=pa.positive, default=2)
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.recipe, args.out, args.scale)))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f'Error: {error}\n')


if __name__ == '__main__':
    main()
