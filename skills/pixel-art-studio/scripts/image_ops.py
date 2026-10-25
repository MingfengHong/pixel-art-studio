"""Apply a reproducible pixel image editing recipe and keep editable inputs."""
import argparse
from collections import deque
from copy import deepcopy
from pathlib import Path
import json

from PIL import Image, ImageChops, ImageFilter
import pixel_art as pa


def load(path):
    with Image.open(path) as im:
        return im.convert('RGBA')


def remove_background(im, color, tolerance=0, connected=True):
    im = im.copy()
    px, w, h = im.load(), im.width, im.height
    rgb = pa.rgba(color)[:3]
    matches = lambda x,y: sum((px[x,y][i]-rgb[i])**2 for i in range(3)) <= tolerance**2
    if connected:
        queue = deque([(x,y) for x in range(w) for y in (0,h-1)]+[(x,y) for y in range(h) for x in (0,w-1)])
        seen = set()
        while queue:
            x,y = queue.popleft()
            if (x,y) in seen or not (0<=x<w and 0<=y<h):
                continue
            seen.add((x,y))
            if matches(x,y):
                px[x,y] = (0,0,0,0)
                queue.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    else:
        for y in range(h):
            for x in range(w):
                if matches(x,y):
                    px[x,y] = (0,0,0,0)
    return im


def apply(im, step, base):
    op = step['op']
    if op == 'resize':
        size = step.get('size') or [im.width*step['factor'],im.height*step['factor']]
        return im.resize(tuple(size),Image.Resampling.NEAREST)
    if op == 'pixelate':
        small = im.resize(tuple(step['size']),Image.Resampling.BOX)
        return small.resize(im.size,Image.Resampling.NEAREST) if step.get('keep_size') else small
    if op == 'crop':
        x,y,w,h = step['rect']
        return im.crop((x,y,x+w,y+h))
    if op == 'mirror':
        return im.transpose(Image.Transpose.FLIP_TOP_BOTTOM if step.get('axis')=='y' else Image.Transpose.FLIP_LEFT_RIGHT)
    if op == 'rotate':
        return im.rotate(step['degrees'],resample=Image.Resampling.NEAREST,expand=True)
    if op == 'remove-background':
        return remove_background(im,step['color'],step.get('tolerance',0),step.get('connected',True))
    if op == 'recolor':
        mapping = {pa.rgba(k):pa.rgba(v) for k,v in step['map'].items()}
        out = im.copy()
        out.putdata([mapping.get(p,p) for p in im.getdata()])
        return out
    if op == 'palette':
        colors = [pa.rgba(c) for c in step['colors']]
        mapping = {p:min(colors,key=lambda c:sum((p[i]-c[i])**2 for i in range(3)))[:3]+(p[3],)
                   for p in set(im.getdata()) if p[3]}
        out = im.copy()
        out.putdata([mapping[p] if p[3] else (0,0,0,0) for p in im.getdata()])
        return out
    if op == 'reduce-colors':
        alpha = im.getchannel('A')
        out = im.quantize(colors=step['colors'],method=Image.Quantize.FASTOCTREE,dither=Image.Dither.NONE).convert('RGBA')
        out.putalpha(alpha)
        return out
    if op == 'outline':
        radius = pa.integer(step.get('width',1),'outline width')
        alpha = im.getchannel('A')
        grown = alpha.filter(ImageFilter.MaxFilter(radius*2+1))
        out = Image.new('RGBA',im.size,step.get('color','#242036'))
        out.putalpha(ImageChops.subtract(grown,alpha))
        out.alpha_composite(im)
        return out
    if op == 'patch':
        patch = load(base/step['source'])
        if step.get('mask'):
            with Image.open(base/step['mask']) as mask:
                patch.putalpha(ImageChops.multiply(patch.getchannel('A'),mask.convert('L')))
        out = im.copy()
        if step.get('replace'):
            out.paste(patch,tuple(step.get('at',[0,0])))
        else:
            out.alpha_composite(patch,tuple(step.get('at',[0,0])))
        return out
    if op == 'extend':
        out = Image.new('RGBA',tuple(step['size']),step.get('color',(0,0,0,0)))
        if step.get('tile'):
            tile = load(base/step['tile'])
            for y in range(0,out.height,tile.height):
                for x in range(0,out.width,tile.width):
                    out.alpha_composite(tile,(x,y))
        out.alpha_composite(im,tuple(step.get('at',[0,0])))
        return out
    raise ValueError(f'Unknown image operation: {op}')


def generate(recipe,out):
    recipe,out = Path(recipe),Path(out)
    doc = pa.read_json(recipe)
    inputs = [recipe,recipe.parent/doc['source']]
    for step in doc['operations']:
        inputs.extend(recipe.parent/step[k] for k in ('source','mask','tile') if step.get(k))
    outputs=[out/name for name in ('image.png','source.json','original.png','preview.png')]
    outputs.extend(out/f'input-{i}-{key}.png' for i,step in enumerate(doc['operations']) for key in ('source','mask','tile') if step.get(key))
    pa.protect_inputs(inputs,outputs)
    original = load(inputs[1])
    current = original.copy()
    for step in doc['operations']:
        current = apply(current,step,recipe.parent)
    out.mkdir(parents=True,exist_ok=True)
    current.save(out/'image.png')
    original.save(out/'original.png')
    portable = deepcopy(doc)
    portable['source'] = 'original.png'
    for index,step in enumerate(portable['operations']):
        for key in ('source','mask','tile'):
            if step.get(key):
                dest = out/f'input-{index}-{key}.png'
                load(recipe.parent/step[key]).save(dest)
                step[key] = dest.name
    pa.write_json(out/'source.json',portable)
    pa.make_sheet([original,current],['original','edited'],scale=4,columns=2).save(out/'preview.png')
    return {'size':list(current.size),'output':str(out)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    try:
        print(json.dumps(generate(args.recipe,args.out)))
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,f'Error: {error}\n')


if __name__=='__main__':
    main()
