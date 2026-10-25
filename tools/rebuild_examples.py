"""Rebuild the small teaching examples using only files in this repository."""
import json
from pathlib import Path
import shutil
import string
import sys

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "pixel-art-studio"
sys.path.insert(0, str(SKILL / "scripts"))
import pixel_art as pa
import character
import ui
import world
import image_ops
import animate
import tilemap
import art_common

EXAMPLES = SKILL / "assets" / "examples"
KENNEY = SKILL / "assets" / "kenney"


def grid_source(name, images, names):
    colors = sorted({p for im in images for p in im.getdata() if p[3]})
    symbols = string.ascii_letters + string.digits + "!$%&()*+,-/:;<=>?@[]^_{|}~"
    if len(colors) > len(symbols):
        raise ValueError("Too many colors for example grid")
    mapping = dict(zip(colors, symbols))
    w, h = images[0].size
    frames = []
    for im, label in zip(images, names):
        if im.size != (w, h):
            raise ValueError("Example frames need equal canvases")
        pixels = list(im.getdata())
        rows = ["".join(mapping[p] if p[3] else "." for p in pixels[y*w:(y+1)*w]) for y in range(h)]
        frames.append({"name": label, "duration_ms": 100, "rows": rows})
    return {"version": 1, "name": name, "canvas": [w, h], "pivot": [w // 2, h], "palette": {key: "#" + "".join(f"{v:02x}" for v in color) for color, key in mapping.items()}, "frames": frames}


def load(path):
    with Image.open(path) as im:
        return im.convert("RGBA")


def main():
    base = load(KENNEY / "tiny-dungeon" / "tile_0113.png")
    variants = [base]
    for light, dark in [("#8fe6ff", "#2582c4"), ("#d0b8ff", "#8062bd")]:
        mapping = {pa.rgba("#c0cbdc"): pa.rgba(light), pa.rgba("#8b9bb4"): pa.rgba(dark)}
        im = base.copy()
        im.putdata([mapping.get(p, p) for p in base.getdata()])
        variants.append(im)
    for folder, doc in [
        ("potion-variants", grid_source("potion-variants", variants, ["original", "azure", "violet"])),
        ("ui-components", grid_source("ui-components", [load(KENNEY / "ui-pixel-adventure" / f"tile_{i:04}.png") for i in [0, 1, 2, 33]], ["round-empty", "round-plus", "round-star", "panel"]))
    ]:
        dest = EXAMPLES / folder
        dest.mkdir(parents=True, exist_ok=True)
        pa.write_json(dest / "source.json", doc)
        pa.render(dest / "source.json", dest, scale=6, columns=4)

    scene = pa.read_json(EXAMPLES / "tile-scene" / "layout.json")
    tile = scene["tile_size"]
    w, h = scene["columns"], scene["rows"]
    canvas = Image.new("RGBA", (w * tile, h * tile))
    for layer in scene["layers"]:
        for y, row in enumerate(layer["tiles"]):
            for x, index in enumerate(row):
                if index is not None:
                    canvas.alpha_composite(load(KENNEY / "tiny-town" / f"tile_{index:04}.png"), (x * tile, y * tile))
    dest = EXAMPLES / "tile-scene"
    canvas.save(dest / "scene.png")
    canvas.resize((canvas.width * 4, canvas.height * 4), Image.Resampling.NEAREST).save(dest / "preview.png")
    pa.render(EXAMPLES / "beacon" / "source.json", EXAMPLES / "beacon", scale=8)
    cast, labels = [], []
    for name in ("researcher", "ranger"):
        dest = EXAMPLES / "characters" / name
        character.generate(dest / "recipe.json", dest)
        _, images, _ = pa.load_sprite(dest / "source.json")
        cast.extend(images[::4])
        labels.extend(f"{name}-{view}" for view in character.VIEWS)
    pa.make_sheet(cast, labels, scale=6, columns=4).save(EXAMPLES / "characters" / "preview.png")
    dest = EXAMPLES / 'characters' / 'adventurer'
    character.generate(dest / 'recipe.json', dest, scale=5)
    # Side-scroller: hand-drawn grid sources -> sprite sheets, a tile-assembled scene and a HUD over it.
    side = EXAMPLES / 'side-scroller'
    for name in ('tiles', 'props', 'big', 'hero', 'items'):
        pa.render(side / f'{name}.json', side / 'sheets' / name, scale=4, columns=8)
    shutil.rmtree(side / 'scene', ignore_errors=True); shutil.rmtree(side / 'hud', ignore_errors=True)
    tilemap.generate(side / 'scene.json', side / 'scene', scale=3)
    shutil.rmtree(side / 'battle', ignore_errors=True)
    tilemap.generate(side / 'battle.json', side / 'battle', scale=3)
    ui.generate(side / 'hud.json', side / 'hud', scale=3)
    # RPG kit: hand-drawn class heroes, a merchant, enemies, effects and icons.
    rpg = EXAMPLES / 'rpg-kit'
    walk = ['down-walk-a', 'down-stand', 'down-walk-b', 'down-stand', 'right-walk-a', 'right-stand', 'right-walk-b', 'right-stand', 'up-walk-a', 'up-stand', 'up-walk-b', 'up-stand']
    for name in ('merchant', 'warrior', 'mage', 'summoner', 'archer', 'class-actions', 'projectiles', 'emotes', 'items',
                 'monsters', 'goblin', 'enemies', 'slash', 'effects'):
        pa.render(rpg / f'{name}.json', rpg / 'sheets' / name, scale=4, columns=9)
    # Battle animations as GIFs: enemies idle and attack, the hero's swing, and the effects.
    clips = {'slime': ('monsters', ['slime-a', 'slime-b'], 260), 'bat': ('monsters', ['bat-a', 'bat-b'], 160),
             'goblin-attack': ('goblin', ['goblin-idle', 'goblin-attack-a', 'goblin-attack-b', 'goblin-idle'], 180),
             'skeleton-attack': ('enemies', ['skeleton-idle', 'skeleton-attack-a', 'skeleton-attack-b', 'skeleton-idle'], 180),
             'mushroom': ('enemies', ['mushroom-a', 'mushroom-b'], 240), 'ghost': ('enemies', ['ghost-a', 'ghost-b'], 300),
             'warrior-attack': ('class-actions', ['warrior-attack-a', 'warrior-attack-b', 'warrior-attack-b'], 140),
             'mage-cast': ('class-actions', ['mage-cast-a', 'mage-cast-b', 'mage-cast-b'], 160),
             'archer-shoot': ('class-actions', ['archer-shoot-a', 'archer-shoot-a', 'archer-shoot-b'], 160),
             'summoner-cast': ('class-actions', ['summoner-cast-a', 'summoner-cast-b', 'summoner-cast-b'], 160),
             'fireball': ('projectiles', ['fireball-a', 'fireball-b'], 100), 'wisp': ('projectiles', ['spirit-a', 'spirit-b'], 160),
             'slash': ('slash', ['slash-0', 'slash-1', 'slash-2'], 70), 'spark': ('effects', ['spark-a', 'spark-b', 'spark-c'], 80),
             'heal': ('effects', ['heal-a', 'heal-b', 'heal-c'], 120)}
    for clip, (source, names, ms) in clips.items():
        frames = art_common.load_frames(rpg / f'{source}.json')
        art_common.gif([frames[n] for n in names], [ms] * len(names), rpg / 'sheets' / f'{clip}.gif', scale=4)
    for name in ('merchant', 'warrior', 'mage', 'summoner', 'archer'):
        doc, images, _ = pa.load_sprite(rpg / f'{name}.json')
        frames = {f['name']: im for f, im in zip(doc['frames'], images)}
        art_common.gif([frames[k] for k in walk], [160] * len(walk), rpg / 'sheets' / name / 'walk.gif', scale=4)
    pa.render(EXAMPLES / 'world-workshop' / 'town.json', EXAMPLES / 'world-workshop' / 'sheets' / 'town', scale=4, columns=3)
    for folder, generated in [('world-workshop', ('tiles', 'inputs')), ('interface-kit', ('components', 'screens', 'inputs'))]:
        dest = EXAMPLES / folder
        # Clear generated folders so files from an older recipe do not linger.
        for name in generated:
            shutil.rmtree(dest / name, ignore_errors=True)
        (world if folder == 'world-workshop' else ui).generate(dest / 'recipe.json', dest)
    dest = EXAMPLES / 'image-editing'
    original = Image.new('RGBA', (24,24), '#efe3c8')
    original.alpha_composite(base, (4,4))
    original.save(dest / 'input.png')
    spark = Image.new('RGBA', (5,5))
    for x,y in [(2,0),(2,1),(0,2),(1,2),(2,2),(3,2),(4,2),(2,3),(2,4)]:
        spark.putpixel((x,y), (255,235,180,255))
    spark.save(dest / 'spark.png')
    image_ops.generate(dest / 'recipe.json', dest)
    # A skill: the mage casts a fireball that bursts on a slime (layer source swaps over time).
    dest = EXAMPLES / 'skill-cast'
    for name in ('frames', 'inputs'):
        shutil.rmtree(dest / name, ignore_errors=True)
    animate.generate(dest / 'recipe.json', dest)
    dest = EXAMPLES / 'layered-animation'
    rows = ['...o...','..oLo..','..oLo..','..oLo..','..oLo..','..oMo..','..oMo..','..oMo..',
            '..oMo..','..oMo..','.ooMoo.','oGGGGGo','.ooBoo.','..oBo..','..oBo..','..ooo..']
    colors = {'.':(0,0,0,0),'o':pa.rgba('#343443'),'L':pa.rgba('#e5e9d8'),
              'M':pa.rgba('#98b7bf'),'G':pa.rgba('#e1bf79'),'B':pa.rgba('#835e48')}
    weapon = Image.new('RGBA',(7,16))
    weapon.putdata([colors[key] for row in rows for key in row])
    weapon.save(dest / 'weapon.png')
    animate.generate(dest / 'recipe.json', dest)
    packs = []
    for pack in ["tiny-dungeon", "tiny-town", "ui-pixel-adventure"]:
        files = sorted((KENNEY / pack).glob("*.png"))
        pa.make_sheet([load(f) for f in files], [f.stem for f in files], scale=4, columns=7).save(KENNEY / f"{pack}-contact.png")
        packs.extend(files)
    pa.make_sheet([load(f) for f in packs], [f.parent.name + "/" + f.stem for f in packs], scale=4, columns=5).save(KENNEY / "contact-sheet.png")
    print(json.dumps({"examples_rebuilt": 11, "reference_tiles": len(packs)}))


if __name__ == "__main__":
    main()
