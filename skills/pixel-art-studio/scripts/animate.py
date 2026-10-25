"""Render sprite sequences or layered keyframe animation into PNG frames and GIF."""
import argparse
from copy import deepcopy
import json
import math
from pathlib import Path

from PIL import Image
import pixel_art as pa
from art_common import atlas, gif, load_image, safe_name


def sample(keys,time):
    if time<=keys[0]['time']:
        return keys[0]
    if time>=keys[-1]['time']:
        return keys[-1]
    a,b=next((a,b) for a,b in zip(keys,keys[1:]) if a['time']<=time<=b['time'])
    weight=(time-a['time'])/(b['time']-a['time'])
    if a.get('hold'):
        weight=0
    result={}
    for field,default in [('x',0),('y',0),('angle',0),('opacity',1)]:
        result[field]=a.get(field,default)*(1-weight)+b.get(field,default)*weight
    return result


def picture(base,source,rect=None):
    """A PNG or one frame of a grid source or atlas (`set.json#frame`), optionally cropped."""
    im=load_image(base,source).convert('RGBA')
    if rect:
        x,y,w,h=rect;im=im.crop((x,y,x+w,y+h))
    return im


def active_source(layer,time):
    """A key with `source` swaps the layer's image from that time on."""
    current=(layer['source'],layer.get('rect'))
    for key in layer['keys']:
        if key['time']<=time and key.get('source'):
            current=(key['source'],key.get('rect'))
    return current


def generate(recipe,out,scale=4):
    recipe,out=Path(recipe),Path(out)
    doc=pa.read_json(recipe)
    sources=[layer['source'] for layer in doc.get('layers',[])]
    sources+=[key['source'] for layer in doc.get('layers',[]) for key in layer['keys'] if key.get('source')]
    sources+=[frame['source'] for frame in doc.get('frames',[])]
    inputs=[recipe]+[recipe.parent/source.split('#')[0] for source in sources]
    pa.protect_inputs(inputs,[out/'source.json',out/'atlas.png',out/'atlas.json',out/'preview.gif'])
    frames,durations=[],[]
    if doc.get('frames'):
        for frame in doc['frames']:
            im=picture(recipe.parent,frame['source'],frame.get('rect'))
            canvas=Image.new('RGBA',tuple(doc['canvas']))
            canvas.alpha_composite(im,tuple(frame.get('at',[0,0])))
            frames.append(canvas);durations.append(frame.get('duration_ms',100))
    else:
        cache={}
        def image(source,rect):
            key=(source,tuple(rect) if rect else None)
            if key not in cache:cache[key]=picture(recipe.parent,source,rect)
            return cache[key]
        for layer in doc['layers']:
            safe_name(layer['id'])
            image(layer['source'],layer.get('rect'))
        count=pa.integer(doc.get('frame_count',8),'frame count')
        for index in range(count):
            time=index/(count-1) if count>1 else 0
            canvas=Image.new('RGBA',tuple(doc['canvas']))
            transforms={}
            for layer in doc['layers']:
                pose=sample(layer['keys'],time)
                x,y,angle=pose.get('x',0),pose.get('y',0),pose.get('angle',0)
                if layer.get('parent'):
                    px,py,pa_deg=transforms[layer['parent']]
                    rad=math.radians(pa_deg)
                    x,y=px+x*math.cos(rad)+y*math.sin(rad),py-x*math.sin(rad)+y*math.cos(rad)
                    angle+=pa_deg
                transforms[layer['id']]=(x,y,angle)
                im=image(*active_source(layer,time)).copy()
                opacity=pose.get('opacity',1)
                im.putalpha(im.getchannel('A').point(lambda v:round(v*opacity)))
                pivot=layer.get('pivot',[im.width//2,im.height//2])
                # Center the pivot before rotating so child attachments stay registered.
                radius=math.ceil(math.hypot(max(pivot[0],im.width-pivot[0]),max(pivot[1],im.height-pivot[1])))
                tile=Image.new('RGBA',(radius*2+1,radius*2+1))
                tile.alpha_composite(im,(radius-pivot[0],radius-pivot[1]))
                tile=tile.rotate(angle,resample=Image.Resampling.NEAREST,center=(radius+0.5,radius+0.5))
                canvas.alpha_composite(tile,(round(x)-radius,round(y)-radius))
            frames.append(canvas);durations.append(doc.get('duration_ms',100))
    outputs=[out/name for name in ('source.json','atlas.png','atlas.json','animation.json','preview.png','preview.gif')]
    outputs.extend(out/'frames'/f'frame-{i:03}.png' for i in range(len(frames)))
    outputs.extend(out/'inputs'/f'{i}.png' for i in range(len(doc.get('layers',[]) or doc.get('frames',[]))))
    pa.protect_inputs(inputs,outputs)
    out.mkdir(parents=True,exist_ok=True)
    dest=out/'frames';dest.mkdir(exist_ok=True)
    images={f'frame-{index:03}':im for index,im in enumerate(frames)}
    for name,im in images.items():im.save(dest/f'{name}.png')
    atlas(images,out)
    gif(frames,durations,out/'preview.gif',scale=scale,loop=0 if doc.get('loop',True) else None)
    pa.make_sheet(frames,list(images),scale=scale,columns=4).save(out/'preview.png')
    pa.write_json(out/'animation.json',{'atlas':'atlas.json','canvas':doc['canvas'],
        'pivot':doc.get('pivot',[doc['canvas'][0]//2,doc['canvas'][1]]),'loop':doc.get('loop',True),
        'frames':[{'name':name,'duration_ms':duration} for name,duration in zip(images,durations)]})
    portable=deepcopy(doc)
    folder=out/'inputs'
    def save(item,name):
        folder.mkdir(exist_ok=True)
        picture(recipe.parent,item['source'],item.pop('rect',None)).save(folder/f'{name}.png')
        item['source']=f'inputs/{name}.png'
    for index,item in enumerate(portable.get('layers',[]) or portable.get('frames',[])):
        for k,key in enumerate(item.get('keys',[])):
            if key.get('source'):save(key,f'{index}-{k}')
        save(item,str(index))
    pa.write_json(out/'source.json',portable)
    return {'frames':len(frames),'output':str(out)}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe',type=Path);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--scale',type=pa.positive,default=4)
    args=parser.parse_args()
    try:print(json.dumps(generate(args.recipe,args.out,args.scale)))
    except (OSError,ValueError,KeyError,TypeError) as error:parser.exit(2,f'Error: {error}\n')


if __name__=='__main__':main()
