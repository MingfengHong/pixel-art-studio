"""Create pixel UI components, state atlases, composed screens and a browser demo."""
import argparse
from copy import deepcopy
import html
import json
import math
from pathlib import Path
import sys

from PIL import Image, ImageDraw
import pixel_art as pa
from art_common import atlas, gif, load_image, put_text, safe_name, text_image, wrap_text


THEME = dict(ink='#111a29', border='#566783', light='#91a3b8', surface='#33445c',
             inset='#202d40', text='#f2eddc', muted='#91a0b4', accent='#79ceb3',
             health='#e57c85', mana='#75a9ee', xp='#e1bf79', shadow='#0c1320')
# Frame styles. "slate" keeps the original bevelled panels; the others draw a framed rim around a fill.
STYLES = {
    'slate': {},
    'wood': dict(ink='#3b2214', frame='#c06a2e', frame_light='#eda25a', frame_dark='#7a3b1a',
                 surface='#f8dca4', inset='#e7b979', border='#c58a4f', light='#fff1cf', text='#4b2a16',
                 muted='#9b6b43', accent='#6eaa3c', health='#df4a3c', mana='#3f8fd8', xp='#f1b83c',
                 shadow='#5a2e14', button='#f3c983', title='#7a3b1a', select='#e2492f', bar_bg='#5a2e14',
                 corner=2, rim=4),
    'arcade': dict(ink='#151515', frame='#e9e2cf', frame_light='#ffffff', frame_dark='#9f9786',
                   surface='#3a4656', inset='#252d38', border='#6d7a8a', light='#c9d2dc', text='#ffffff',
                   muted='#9aa6b3', accent='#f4c542', health='#e84a3f', mana='#4aa3e8', xp='#f4c542',
                   shadow='#151515', button='#56657a', title='#f4c542', select='#f4c542', bar_bg='#252d38',
                   corner=1, rim=2),
}
ICONS = {
    'heart':['.##.##.','#######','#######','.#####.','..###..','...#...','.......'],
    'drop':['...#...','..###..','..###..','.#####.','#######','#######','.#####.'],
    'star':['...#...','...#...','#######','.#####.','..###..','.##.##.','.#...#.'],
    'coin':['..###..','.#####.','##.#.##','##.#.##','##.#.##','.#####.','..###..'],
    'sword':['.....##','....###','...###.','#.###..','.###...','###.#..','##.....'],
    'shield':['#######','#######','#######','.#####.','.#####.','..###..','...#...'],
    'bag':['..###..','..###..','.#####.','#######','##.#.##','#######','.#####.'],
    'gear':['..###..','#.###.#','#######','##...##','#######','#.###.#','..###..'],
    'close':['##...##','.##.##.','..###..','...#...','..###..','.##.##.','##...##'],
    'check':['......#','.....##','#...##.','##.##..','.###...','..#....','.......'],
    'arrow':['.......','#######','.#####.','..###..','...#...','.......','.......'],
    'sun':['#..#..#','..###..','.#####.','#######','.#####.','..###..','#..#..#'],
    'moon':['..###..','.##....','##.....','##.....','##.....','.##....','..###..'],
    'music':['..#####','..#...#','..#...#','..#...#','###.###','###.###','.......'],
}


def mix(a, b, f):
    a, b = pa.rgba(a), pa.rgba(b)
    return '#%02x%02x%02x' % tuple(round(a[i]+(b[i]-a[i])*f) for i in range(3))


def theme_for(doc):
    custom = doc.get('theme', {})
    style = custom.get('style', 'slate')
    if style not in STYLES:
        raise ValueError(f"Unknown theme style {style!r}; use {', '.join(STYLES)}")
    t = THEME | STYLES[style] | custom
    t['style'] = style
    # Roles the framed styles use; derived for slate so every component can rely on them.
    t.setdefault('frame', t['border']); t.setdefault('frame_light', t['light']); t.setdefault('frame_dark', t['shadow'])
    t.setdefault('button', t['surface']); t.setdefault('title', t['xp']); t.setdefault('select', t['accent'])
    t.setdefault('bar_bg', t['inset']); t.setdefault('rim', 3); t.setdefault('corner', 2)
    return t


def box(im, rect, t, fill=None, pressed=False):
    """A panel in the theme's frame style."""
    x, y, w, h = rect
    d = ImageDraw.Draw(im)
    r = min(t.get('corner', 2), (w-1)//2, (h-1)//2)
    points = [(x+r,y),(x+w-r-1,y),(x+w-1,y+r),(x+w-1,y+h-r-1),
              (x+w-r-1,y+h-1),(x+r,y+h-1),(x,y+h-r-1),(x,y+r)]
    if t.get('style', 'slate') == 'slate':
        d.polygon(points, fill=fill or t['surface'], outline=t['ink'])
        d.line((x+r,y+1,x+w-r-1,y+1), fill=t['border'] if pressed else t['light'])
        d.line((x+1,y+r,x+1,y+h-r-1), fill=t['border'])
        d.line((x+r,y+h-2,x+w-r-1,y+h-2), fill=t['shadow'])
        return
    rim = max(1, min(t.get('rim', 3), (min(w, h)-5)//3))
    hi, lo = (t['frame_dark'], t['frame_light']) if pressed else (t['frame_light'], t['frame_dark'])
    d.polygon(points, fill=t['frame'], outline=t['ink'])
    d.line((x+r,y+1,x+w-r-1,y+1), fill=hi); d.line((x+1,y+r,x+1,y+h-r-1), fill=hi)
    d.line((x+r,y+h-2,x+w-r-1,y+h-2), fill=lo); d.line((x+w-2,y+r,x+w-2,y+h-r-1), fill=lo)
    if t['style'] == 'wood' and rim >= 3:
        # Plank grain: short darker dashes along the top and bottom rims.
        for gx in range(x+5, x+w-7, 11):
            d.line((gx, y+2, gx+3, y+2), fill=t['frame_dark'])
            d.line((gx+5, y+h-3, gx+8, y+h-3), fill=t['frame_dark'])
    x0, y0, x1, y1 = x+rim+1, y+rim+1, x+w-rim-2, y+h-rim-2
    if x1 >= x0 and y1 >= y0:
        d.rectangle((x0-1, y0-1, x1+1, y1+1), outline=t['frame_dark'])
        d.rectangle((x0, y0, x1, y1), fill=fill or t['surface'])
        if y1 > y0:
            d.line((x0, y0, x1, y0), fill=mix(fill or t['surface'], t['frame_dark'], .25))


def slot(im, rect, t, selected=False):
    """A sunken square for inventory, hotbar and equipment slots."""
    x, y, w, h = rect
    d = ImageDraw.Draw(im)
    d.rectangle((x, y, x+w-1, y+h-1), fill=t['inset'])
    d.line((x, y, x+w-1, y), fill=t['frame_dark']); d.line((x, y, x, y+h-1), fill=t['frame_dark'])
    d.line((x+1, y+h-1, x+w-1, y+h-1), fill=mix(t['inset'], '#ffffff', .35))
    d.line((x+w-1, y+1, x+w-1, y+h-1), fill=mix(t['inset'], '#ffffff', .35))
    if selected:
        d.rectangle((x-1, y-1, x+w, y+h), outline=t['select'])
        d.rectangle((x-2, y-2, x+w+1, y+h+1), outline=t['select'])


def icon(name, size, color):
    rows = ICONS[name]
    scale = max(1, min(size)//8)
    image = Image.new('RGBA', size)
    d = ImageDraw.Draw(image)
    ox, oy = (size[0]-7*scale)//2, (size[1]-7*scale)//2
    for y, row in enumerate(rows):
        for x, char in enumerate(row):
            if char == '#':
                d.rectangle((ox+x*scale, oy+y*scale, ox+(x+1)*scale-1, oy+(y+1)*scale-1), fill=color)
    return image


def fit(image, size):
    """Center an image in a box with the largest whole-number zoom; crop the center if it is too big."""
    w, h = size
    k = max(1, min(w // image.width, h // image.height))
    big = image.resize((image.width*k, image.height*k), Image.Resampling.NEAREST)
    out = Image.new('RGBA', size)
    out.alpha_composite(big.crop((max(0,(big.width-w)//2), max(0,(big.height-h)//2),
                                  max(0,(big.width-w)//2)+min(w,big.width), max(0,(big.height-h)//2)+min(h,big.height))),
                        (max(0,(w-big.width)//2), max(0,(h-big.height)//2)))
    return out


class Studio:
    def __init__(self, doc, base):
        self.doc, self.base = doc, Path(base)
        self.theme = theme_for(doc)
        self.specs = {safe_name(c['id']): c for c in doc['components']}
        if len(self.specs) != len(doc['components']):
            raise ValueError('Component IDs must be unique')
        self.built, self.active = {}, set()
        self.font = self.base / doc['font'] if doc.get('font') else None
        self.font_size = self.doc.get('font_size', 9)

    def label(self, im, text, xy, color=None, align='left', scale=1, outline=None):
        put_text(im, text, xy, color or self.theme['text'], align=align, outline=outline,
                 scale=scale, font=self.font, font_size=self.font_size)

    def picture(self, source, crop=None):
        image = load_image(self.base, source)
        if crop:
            x, y, cw, ch = crop
            image = image.crop((x, y, x+cw, y+ch))
        return image

    def item_art(self, item, size):
        if item.get('source'):
            return fit(self.picture(item['source'], item.get('crop')), size)
        return icon(item.get('icon', 'coin'), size, item.get('color', self.theme['xp']))

    def compose(self, size, children, background=None):
        im = Image.new('RGBA', size, background or (0,0,0,0))
        if isinstance(background, str) and not background.startswith('#'):
            im = fit(self.picture(background), size)
        for child in children:
            states, meta, _ = self.build(child['component'])
            frame = states[child.get('state', meta['default'])]
            im.alpha_composite(frame, tuple(child['at']))
        return im

    def build(self, name):
        if name in self.built:
            return self.built[name]
        if name in self.active:
            raise ValueError(f'Circular component group: {name}')
        self.active.add(name)
        c, t = self.specs[name], self.theme
        kind = {'popup':'modal','pop-up':'modal'}.get(c['type'],c['type'])
        w, h = [pa.integer(v, 'component size') for v in c['size']]
        if kind in ('tooltip', 'modal'):
            # Grow the box so every line fits: title, rule, one row per line, then the pointer or the buttons.
            m = 8 if t['style'] == 'slate' else t['rim'] + 5
            need = m + 19 + len(c.get('lines', [])) * 11 + (6 if kind == 'tooltip' else m + 22)
            h = max(h, need)
        empty = lambda: Image.new('RGBA', (w,h))
        states, layers = {}, {}
        meta = {'type':kind, 'size':[w,h], 'label':c.get('label','')}
        if kind in ('panel','button','dropdown','modal','tooltip','scroll-view'):
            inset = 4 if t['style'] == 'slate' else t['rim'] + 2
            meta['nine_slice'] = [inset]*4
            skin = Image.new('RGBA',(w,h-4 if kind=='tooltip' else h))
            box(skin,(0,0,skin.width,skin.height),t)
            layers['skin'] = skin
            meta['slice_source'] = 'skin'
            meta['minimum_skin_size'] = [inset*2+1]*2
        if kind in ('canvas','hud'):
            states['normal'] = self.compose((w,h), c.get('children',[]), c.get('background'))
            meta['children'] = c.get('children',[])
        elif kind == 'panel':
            im = empty()
            box(im, (0,0,w,h), t)
            if c.get('label'):
                top = 7 if t['style'] == 'slate' else t['rim'] + 5
                self.label(im, c['label'], (w//2 if c.get('align') == 'center' else top+1, top),
                           t['title'] if t['style'] != 'slate' else t['text'], c.get('align', 'left'))
                ImageDraw.Draw(im).line((top-2, top+13, w-top+1, top+13), fill=t['border'])
            states['normal'] = im
        elif kind == 'button':
            for state in ('normal','hover','focus','pressed','disabled','selected'):
                im = empty()
                if t['style'] == 'slate':
                    fill = t['border'] if state in ('hover','focus') else t['surface']
                else:
                    fill = mix(t['button'], '#ffffff', .25) if state in ('hover','focus') else t['button']
                if state == 'selected':
                    fill = t['accent']
                if state == 'disabled' and t['style'] != 'slate':
                    fill = mix(t['button'], t['muted'], .5)
                if c.get('shape') == 'round':
                    d = ImageDraw.Draw(im)
                    d.ellipse((0,0,w-1,h-1), fill=fill, outline=t['ink'])
                    d.arc((2,2,w-3,h-3), 200, 300, fill=t['frame_dark'] if state=='pressed' else t['frame_light'])
                    d.arc((2,2,w-3,h-3), 20, 120, fill=t['frame_light'] if state=='pressed' else t['frame_dark'])
                else:
                    box(im, (0,0,w,h), t, fill, state == 'pressed')
                if state == 'focus':
                    ImageDraw.Draw(im).rectangle((2,2,w-3,h-3), outline=t['select'] if t['style'] != 'slate' else t['accent'])
                if c.get('opacity', 1) < 1:
                    im.putalpha(im.getchannel('A').point(lambda v, k=c['opacity']: round(v*k)))
                layers['skin-'+state] = im.copy()
                color = t['muted'] if state == 'disabled' else (t['ink'] if state == 'selected' else t['text'])
                text = c.get('label','')
                dy = state == 'pressed'
                art = None
                if c.get('source'):
                    art = fit(self.picture(c['source'], c.get('crop')), tuple(c.get('icon_size', [16, 16])))
                elif c.get('icon'):
                    art = icon(c['icon'], (10,10), color)
                if art and c.get('layout') == 'stack':
                    # Icon above, label below: the large square buttons of mobile HUDs.
                    top = (h - art.height - (10 if text else 0))//2
                    im.alpha_composite(art, ((w-art.width)//2, top+dy))
                    if text:
                        self.label(im, text, (w//2, top+art.height+3+dy), color, 'center', outline=c.get('outline'))
                elif art:
                    width = art.width + 2 + (text_image(text).width if text else -2)
                    im.alpha_composite(art, (w//2-width//2, (h-art.height)//2+dy))
                    if text:
                        self.label(im, text, (w//2-width//2+art.width+2+text_image(text).width//2, (h-7)//2+dy), color, 'center', outline=c.get('outline'))
                elif text:
                    self.label(im, text, (w//2, (h-7)//2+dy), color, 'center', outline=c.get('outline'))
                states[state] = im
        elif kind in ('health-bar','mana-bar','xp-bar','stamina-bar','bar'):
            role = kind.split('-')[0]
            color = c.get('color', t.get(role, t['accent']))
            track = empty()
            d = ImageDraw.Draw(track)
            d.rectangle((1,0,w-2,h-1), fill=t['ink']); d.rectangle((0,1,w-1,h-2), fill=t['ink'])
            d.rectangle((1,1,w-2,h-2), fill=t['bar_bg'])
            fill = Image.new('RGBA', (w-4,h-4), color)
            fd = ImageDraw.Draw(fill)
            fd.line((0,0,fill.width-1,0), fill=mix(color,'#ffffff',.45))
            if fill.height > 2:
                fd.line((0,fill.height-1,fill.width-1,fill.height-1), fill=mix(color,'#000000',.3))
            layers = {'track':track, 'fill':fill}
            meta['fill_rect'] = [2,2,w-4,h-4]
            value = c.get('value',0.7)
            text = Image.new('RGBA', (w,h))
            if c.get('label') or c.get('max'):
                ty = (h-7)//2
                if c.get('label'):
                    put_text(text, c['label'], (5, ty), c.get('text_color', '#ffffff'), outline=t['ink'],
                             font=self.font, font_size=self.font_size)
                if c.get('max'):
                    current = round(value*c['max'])
                    meta['value_text'] = f"{current}/{c['max']}"
                    put_text(text, meta['value_text'], (w-4, ty), c.get('text_color', '#ffffff'), 'right',
                             outline=t['ink'], font=self.font, font_size=self.font_size)
                layers['text'] = text
            for state, v in [('empty',0),('half',0.5),('full',1),('normal',value)]:
                im = track.copy()
                count = round((w-4)*max(0,min(1,v)))
                if count:
                    im.alpha_composite(fill.crop((0,0,count,h-4)), (2,2))
                im.alpha_composite(text)
                states[state] = im
            meta['value'] = value
        elif kind in ('toggle','switch'):
            for state in ('off','on','disabled'):
                im = empty()
                box(im, (0,2,w,h-4), t, t['accent'] if state=='on' else t['inset'])
                x = w-h if state=='on' else 0
                box(im, (x,0,h,h), t, t['muted'] if state=='disabled' else (t['light'] if t['style']=='slate' else t['button']))
                states[state] = im
            meta['value'] = c.get('value',False)
        elif kind == 'slider':
            track = empty()
            box(track, (0,h//2-3,w,6), t, t['inset'])
            thumb = Image.new('RGBA',(8,h))
            box(thumb, (0,0,8,h), t, t['light'] if t['style']=='slate' else t['button'])
            layers = {'track':track,'thumb':thumb}
            for state, value in [('min',0),('half',0.5),('max',1),('normal',c.get('value',0.5))]:
                im = track.copy()
                im.alpha_composite(thumb, (round((w-8)*value),0))
                states[state] = im
            states['disabled'] = states['normal'].copy()
            states['disabled'].alpha_composite(Image.new('RGBA',(w,h),(20,25,40,120)))
            meta.update(value=c.get('value',0.5), thumb_size=[8,h], range=c.get('range',[0,100]))
        elif kind == 'dropdown':
            options = c.get('options',['LOW','MEDIUM','HIGH'])
            selected = c.get('selected',0)
            for index, option in enumerate(options):
                im = empty()
                box(im,(0,0,w,h),t,t['button'] if t['style']!='slate' else None)
                self.label(im,option,(7 if t['style']=='slate' else t['rim']+4,(h-7)//2))
                im.alpha_composite(icon('arrow',(10,10),t['text']),(w-15,(h-10)//2))
                states[f'selected-{index}'] = im
            states['normal'] = states[f'selected-{selected}'].copy()
            states['disabled'] = states['normal'].copy()
            states['disabled'].alpha_composite(Image.new('RGBA',(w,h),(20,25,40,120)))
            for chosen in range(len(options)):
                opened = Image.new('RGBA',(w,h+len(options)*14+4))
                opened.alpha_composite(states[f'selected-{chosen}'])
                box(opened,(0,h,w,opened.height-h),t,t['inset'])
                for index, option in enumerate(options):
                    if index == chosen:
                        ImageDraw.Draw(opened).rectangle((3,h+2+index*14,w-4,h+15+index*14), fill=t['surface'] if t['style']=='slate' else t['button'])
                    self.label(opened,option,(7,h+5+index*14))
                states[f'open-{chosen}'] = opened
            states['open'] = states[f'open-{selected}'].copy()
            meta.update(options=options, selected=selected, row_height=14)
        elif kind == 'minimap':
            grid = c['tiles']
            colors = c.get('colors',{'g':'#355650','w':'#314e70','p':'#a39265','r':'#747b89'})
            im = empty()
            box(im,(0,0,w,h),t,t['inset'])
            edge = 4 if t['style'] == 'slate' else t['rim'] + 2
            tile = Image.new('RGBA',(len(grid[0]),len(grid)))
            tile.putdata([pa.rgba(colors[key]) for row in grid for key in row])
            layers['map'] = tile.resize((w-2*edge,h-2*edge),Image.Resampling.NEAREST)
            layers['frame'] = im.copy()
            ImageDraw.Draw(layers['frame']).rectangle((edge,edge,w-edge-1,h-edge-1),fill=(0,0,0,0))
            layers['markers'] = empty()
            im.alpha_composite(layers['map'],(edge,edge))
            for marker in c.get('markers',[]):
                x = edge+int(marker['at'][0]*(w-2*edge-1))
                y = edge+int(marker['at'][1]*(h-2*edge-1))
                ImageDraw.Draw(layers['markers']).rectangle((x-1,y-1,x+1,y+1),fill=marker.get('color',t['text']),outline=t['ink'])
            im.alpha_composite(layers['markers'])
            states['normal'] = im
            mask = Image.new('RGBA',(w,h))
            ImageDraw.Draw(mask).rectangle((edge,edge,w-edge-1,h-edge-1),fill='white')
            layers['mask'] = mask
            meta.update(viewport=[edge,edge,w-2*edge,h-2*edge], markers=c.get('markers',[]))
        elif kind in ('text','label','floating-text'):
            label = text_image(c.get('label','LABEL'),c.get('color',t['text']),scale=c.get('scale',1),
                               font=self.font,font_size=self.font_size,outline=c.get('outline'))
            frames = c.get('frames',6) if kind=='floating-text' else 1
            for index in range(frames):
                im = empty()
                y = max(0,h-label.height-2-index*c.get('rise',2)) if kind=='floating-text' else (h-label.height)//2
                x = {'left':0,'right':w-label.width}.get(c.get('align'),(w-label.width)//2)
                im.alpha_composite(label,(x,y))
                if kind=='floating-text':
                    alpha = int(255*(1-index/max(1,frames)))
                    im.putalpha(im.getchannel('A').point(lambda v: v*alpha//255))
                states[f'frame-{index}' if frames>1 else 'normal'] = im
            meta.update(text=c.get('label',''), duration_ms=c.get('duration_ms',90), editable_text=True)
        elif kind in ('image','sprite','icon'):
            im = empty()
            pad = 0
            if c.get('frame'):
                box(im,(0,0,w,h),t,t['inset'])
                pad = 4 if t['style'] == 'slate' else t['rim'] + 2
            elif c.get('slot'):
                slot(im,(0,0,w,h),t)
                pad = 2
            inner = (w-2*pad, h-2*pad)
            if kind == 'icon':
                art = icon(c.get('icon','star'),inner,c.get('color',t['xp']))
            else:
                art = fit(self.picture(c['source'], c.get('crop')), inner)
                meta['source'] = c['source']
            im.alpha_composite(art,(pad,pad))
            states['normal'] = im
        elif kind == 'scroll-view':
            cols, cell = c.get('columns',4), c.get('cell',24)
            items = c.get('items',[])
            edge = 4 if t['style'] == 'slate' else t['rim'] + 2
            viewport = [edge,edge,w-2*edge-7,h-2*edge]
            if cols*cell > viewport[2]:
                raise ValueError(f'{name}: columns × cell must fit inside width - {2*edge+7}')
            cells = max(len(items), c.get('slots', 0))
            content = Image.new('RGBA',(viewport[2],max(viewport[3],((cells+cols-1)//cols)*cell)),t['surface'] if t['style']!='slate' else t['inset'])
            for index in range(cells):
                x,y = index%cols*cell+1,index//cols*cell+1
                if t['style'] == 'slate':
                    box(content,(x-1,y-1,cell-2,cell-2),t)
                else:
                    slot(content,(x,y,cell-3,cell-3),t)
            for index, item in enumerate(items):
                x,y = index%cols*cell+1,index//cols*cell+1
                content.alpha_composite(self.item_art(item,(cell-7,cell-7)),(x+2,y+2))
                if item.get('count'):
                    put_text(content,str(item['count']),(x+cell-5,y+cell-11),'#ffffff','right',outline=t['ink'],
                             font=self.font,font_size=self.font_size)
            layers['content'] = content
            for state, value in [('top',0),('middle',0.5),('bottom',1)]:
                im = empty()
                box(im,(0,0,w,h),t,t['inset'])
                offset = round((content.height-viewport[3])*value)
                im.alpha_composite(content.crop((0,offset,viewport[2],offset+viewport[3])),(edge,edge))
                d = ImageDraw.Draw(im)
                d.rectangle((w-edge-4,edge,w-edge-1,h-edge-1),fill=t['frame_dark'] if t['style']!='slate' else t['shadow'])
                thumb_h = max(6,round((h-2*edge)*viewport[3]/content.height))
                yy = edge+round((h-2*edge-thumb_h)*value)
                d.rectangle((w-edge-4,yy,w-edge-1,yy+thumb_h-1),fill=t['light'] if t['style']=='slate' else t['frame_light'])
                states[state] = im
            meta.update(viewport=viewport,content_size=list(content.size),items=items,
                        scrollbar=[w-edge-4,edge,4,h-2*edge])
        elif kind == 'hotbar':
            items = c.get('items',[])
            count, cell, gap = c.get('slots',max(len(items),1)), c.get('cell',20), c.get('gap',2)
            total = count*cell + (count-1)*gap
            if total > w-8:
                raise ValueError(f'{name}: slots × cell + gaps must fit inside the width')
            x0, y0 = (w-total)//2, (h-cell)//2
            skin = empty()
            box(skin,(0,0,w,h),t)
            rects = []
            for index in range(count):
                x = x0 + index*(cell+gap)
                slot(skin,(x,y0,cell,cell),t)
                rects.append([x,y0,cell,cell])
            base = skin.copy()
            for index, item in enumerate(items[:count]):
                x, y = rects[index][:2]
                base.alpha_composite(self.item_art(item,(cell-4,cell-4)),(x+2,y+2))
                if item.get('count'):
                    put_text(base,str(item['count']),(x+cell-2,y+cell-9),'#ffffff','right',outline=t['ink'],
                             font=self.font,font_size=self.font_size)
            if c.get('numbers', True):
                for index, rect in enumerate(rects[:9]):
                    put_text(base,str(index+1),(rect[0]+2,rect[1]+1),t['muted'] if t['style']!='slate' else t['light'],
                             font=self.font,font_size=self.font_size)
            layers['skin'] = skin
            selected = c.get('selected',0)
            for index in range(count):
                im = base.copy()
                x, y, cw, ch = rects[index]
                slot_sel = Image.new('RGBA',(w,h))
                ImageDraw.Draw(slot_sel).rectangle((x-1,y-1,x+cw,y+ch),outline=t['select'])
                ImageDraw.Draw(slot_sel).rectangle((x-2,y-2,x+cw+1,y+ch+1),outline=t['select'])
                im.alpha_composite(slot_sel)
                states[f'selected-{index}'] = im
            states['normal'] = states[f'selected-{selected}'].copy()
            meta.update(slot_rects=rects,selected=selected,items=items)
        elif kind == 'dialogue':
            states, layers = self.dialogue(c, w, h, meta)
        elif kind == 'dial':
            states, layers = self.dial(c, w, h, meta)
        elif kind == 'list':
            states, layers = self.listing(c, w, h, meta)
        elif kind in ('modal','tooltip'):
            im = empty()
            panel_h = h-4 if kind=='tooltip' else h
            box(im,(0,0,w,panel_h),t)
            m = 8 if t['style']=='slate' else t['rim']+5
            self.label(im,c.get('label','NOTICE'),(m,m),c.get('color',t['title'] if t['style']!='slate' else t['xp']))
            ImageDraw.Draw(im).line((m-2,m+12,w-m+1,m+12),fill=t['border'])
            for index,line in enumerate(c.get('lines',[])):
                self.label(im,line,(m,m+19+index*11),t['text'])
            if kind=='tooltip':
                ImageDraw.Draw(im).polygon([(12,h-5),(19,h-5),(15,h-1)],fill=t['frame'] if t['style']!='slate' else t['surface'],outline=t['ink'])
                meta['pointer'] = [15,h-1]
            else:
                bw = w//2-m-4
                rects = [[m+i*(w//2-m//2), h-m-18, bw, 18] for i in range(len(c.get('buttons',['CANCEL','OK'])))]
                for (bx,by,bww,bh),label in zip(rects, c.get('buttons',['CANCEL','OK'])):
                    box(im,(bx,by,bww,bh),t,t['button'] if t['style']!='slate' else None)
                    self.label(im,label,(bx+bww//2,by+(bh-7)//2),align='center')
                meta['buttons'] = c.get('buttons',['CANCEL','OK'])
                meta['button_rects'] = rects
            states['normal'] = im
        else:
            raise ValueError(f'Unknown UI component: {kind}')
        meta['default'] = ('on' if c.get('value') else 'off') if kind in ('toggle','switch') else next(iter(states))
        if 'normal' in states:
            meta['default'] = 'normal'
        self.active.remove(name)
        self.built[name] = states,meta,layers
        return self.built[name]

    def dial(self, c, w, h, meta):
        """Day/night dial: a round face, day on the right and night on the left, a hand for `time` (0-1)."""
        t = self.theme
        size = min(w, h - (12 if c.get('label') else 0))
        face = Image.new('RGBA', (size, size))
        d = ImageDraw.Draw(face)
        night, day = c.get('night', '#2b3a6b'), c.get('day', '#8fd3f5')
        d.ellipse((0, 0, size-1, size-1), fill=t['ink'])
        d.ellipse((2, 2, size-3, size-3), fill=t['frame'])
        d.pieslice((4, 4, size-5, size-5), 90, 270, fill=night)
        d.pieslice((4, 4, size-5, size-5), 270, 90, fill=day)
        cx = cy = size//2
        for sx, sy in [(-.3, -.2), (-.18, .22), (-.35, .12), (-.1, -.33)]:
            face.putpixel((round(cx+sx*size), round(cy+sy*size)), (255, 255, 255, 255))
        sun = round(size*.12)
        d.ellipse((cx+size*.18-sun, cy-size*.18-sun, cx+size*.18+sun, cy-size*.18+sun), fill='#ffd257', outline=t['ink'])
        d.ellipse((cx-size*.28-sun, cy+size*.12-sun, cx-size*.28+sun, cy+size*.12+sun), fill='#f4f1d0')
        d.ellipse((cx-size*.28-sun+2, cy+size*.12-sun-1, cx-size*.28+sun+2, cy+size*.12+sun-1), fill=night)
        def with_hand(time):
            im = Image.new('RGBA', (w, h))
            hand = face.copy()
            hd = ImageDraw.Draw(hand)
            angle = math.radians(time*360 - 90)
            ex, ey = cx + math.cos(angle)*(size/2-6), cy + math.sin(angle)*(size/2-6)
            hd.line((cx, cy, ex, ey), fill=t['ink'], width=3)
            hd.line((cx, cy, ex, ey), fill='#ffffff', width=1)
            hd.ellipse((cx-2, cy-2, cx+2, cy+2), fill=t['ink'])
            im.alpha_composite(hand, ((w-size)//2, 0))
            if c.get('label'):
                self.label(im, c['label'], (w//2, size+3), c.get('color', '#ffffff'), 'center', outline=c.get('outline', t['ink']))
            return im
        states = {'normal': with_hand(c.get('time', .3))}
        for index, time in enumerate((0, .25, .5, .75)):
            states[f'quarter-{index}'] = with_hand(time)
        meta.update(time=c.get('time', .3), face_rect=[(w-size)//2, 0, size, size])
        return states, {'face': face}

    def dialogue(self, c, w, h, meta):
        """NPC dialogue with typewriter frames and choices.

        layout "panel" (default): a separate portrait panel beside the text box with a name plate under it.
        layout "inset": the portrait sits inside the box on the left and the name is a tab above the box.
        """
        t = self.theme
        portrait = self.picture(c['portrait'], c.get('portrait_crop')) if c.get('portrait') else None
        speaker = c.get('speaker', '')
        pad = 9 if t['style'] == 'slate' else t['rim'] + 6
        ppad = 4 if t['style'] == 'slate' else t['rim'] + 3
        line_h = c.get('line_height', (self.font_size if self.font else 7) + 4)
        skin = Image.new('RGBA', (w, h))
        name_rect = portrait_rect = None
        name_in_text = False
        if c.get('layout') == 'inset':
            tab_h = 14 if speaker else 0
            top = tab_h - 4 if speaker else 0
            box(skin, (0, top, w, h - top), t)
            if portrait:
                side = h - top - 2*ppad
                portrait_rect = [ppad, top + ppad, side, side]
                d = ImageDraw.Draw(skin)
                d.rectangle((ppad-1, top+ppad-1, ppad+side, top+ppad+side), fill=t['frame_dark'])
                d.rectangle((ppad, top+ppad, ppad+side-1, top+ppad+side-1), fill=t['inset'])
                skin.alpha_composite(fit(portrait, (side, side)), (ppad, top + ppad))
            if speaker:
                tw = text_image(speaker, font=self.font, font_size=self.font_size).width + 14
                name_rect = [pad + (portrait_rect[2] if portrait else 0), 0, tw, tab_h + 2]
                box(skin, tuple(name_rect), t, t['button'] if t['style'] != 'slate' else t['inset'])
                self.label(skin, speaker, (name_rect[0] + 7, 4), t['title'])
            ox = (portrait_rect[0] + portrait_rect[2] + 7) if portrait else pad
            oy = top + pad - 1
            text_rect = [ox - pad, top, w - ox + pad, h - top]
        else:
            side = c.get('side', 'right')
            pw = c.get('portrait_width', h) if portrait else 0
            gap = 4 if portrait else 0
            tx = pw + gap if side == 'left' else 0
            text_rect = [tx, 0, w - pw - gap, h]
            box(skin, tuple(text_rect), t)
            if portrait:
                px = 0 if side == 'left' else w - pw
                box(skin, (px, 0, pw, h), t)
                plate_h = 15
                portrait_rect = [px+ppad, ppad, pw-2*ppad, h-2*ppad-plate_h-1]
                name_rect = [px+ppad-1, h-ppad-plate_h, pw-2*ppad+2, plate_h]
                ImageDraw.Draw(skin).rectangle((portrait_rect[0], portrait_rect[1], portrait_rect[0]+portrait_rect[2]-1,
                                                portrait_rect[1]+portrait_rect[3]-1), fill=t['inset'])
                skin.alpha_composite(fit(portrait, tuple(portrait_rect[2:])), tuple(portrait_rect[:2]))
                box(skin, tuple(name_rect), t, t['button'] if t['style'] != 'slate' else t['inset'])
                if speaker:
                    self.label(skin, speaker, (name_rect[0]+name_rect[2]//2, name_rect[1]+(plate_h-7)//2), t['text'], 'center')
            elif speaker:
                name_in_text = True
            ox, oy = tx + pad, pad
        inner_w = text_rect[0] + text_rect[2] - ox - pad - 8
        lines = c['lines'] if c.get('lines') else wrap_text(c.get('text', ''), inner_w, self.font, self.font_size)
        if name_in_text:
            self.label(skin, speaker, (ox, oy), t['title'])
            lines = [''] + list(lines)
        choices = c.get('choices', [])
        if oy + (len(lines)+len(choices))*line_h > h - pad + 6:
            raise ValueError(f"{c['id']}: the text needs {len(lines)+len(choices)} lines; enlarge the box or split it into pages")
        total = sum(len(line) for line in lines)

        def page(chars, arrow=False, choice=None):
            im = skin.copy()
            left = chars
            for row, line in enumerate(lines):
                shown = line[:max(0, left)]
                left -= len(line)
                if shown:
                    self.label(im, shown, (ox, oy + row*line_h), t['text'])
            if chars >= total:
                for index, option in enumerate(choices):
                    y = oy + (len(lines)+index)*line_h
                    if index == choice:
                        self.label(im, '>', (ox, y), t['select'])
                    self.label(im, option, (ox + 8, y), t['title'] if index == choice else t['muted'])
            if arrow:
                ax, ay = text_rect[0] + text_rect[2] - pad - 3, h - pad - 1
                ImageDraw.Draw(im).polygon([(ax-3, ay-3), (ax+3, ay-3), (ax, ay)], fill=t['title'], outline=t['ink'])
            return im

        frames = c.get('typing_frames', 8)
        states = {f'typing-{i}': page(round(total*(i+1)/frames)) for i in range(frames)}
        states['normal'] = page(total, arrow=not choices, choice=0 if choices else None)
        states['waiting'] = page(total, choice=0 if choices else None)
        for index in range(len(choices)):
            states[f'choice-{index}'] = page(total, choice=index)
        meta.update(speaker=speaker, lines=lines, choices=choices, text_rect=text_rect, layout=c.get('layout', 'panel'),
                    portrait_rect=portrait_rect, name_rect=name_rect, line_height=line_h, typing_frames=frames,
                    duration_ms=c.get('duration_ms', 60), editable_text=True,
                    choice_rects=[[ox, oy+(len(lines)+i)*line_h-2, text_rect[0]+text_rect[2]-ox-pad, line_h] for i in range(len(choices))],
                    nine_slice=[pad-2]*4, slice_source='skin')
        layers = {'skin': skin}
        if portrait:
            layers['portrait'] = fit(portrait, tuple(portrait_rect[2:]))
        return states, layers

    def listing(self, c, w, h, meta):
        """A selectable list: icon, label and right-aligned value per row (shops, quest logs, skills)."""
        t = self.theme
        rows, row_h = c.get('rows', []), c.get('row_height', 20)
        edge = 4 if t['style'] == 'slate' else t['rim'] + 3
        skin = Image.new('RGBA', (w, h))
        box(skin, (0, 0, w, h), t)
        if edge + len(rows)*row_h > h - edge + 2:
            raise ValueError(f"{c['id']}: {len(rows)} rows of {row_h}px do not fit; enlarge the list")
        rects = [[edge, edge + i*row_h, w - 2*edge, row_h - 1] for i in range(len(rows))]
        base = Image.new('RGBA', (w, h))   # row content on a transparent layer, drawn over any highlight
        d = ImageDraw.Draw(base)
        for (x, y, rw, rh), row in zip(rects, rows):
            d.line((x+2, y+rh, x+rw-3, y+rh), fill=t['border'])
            ix = x + 2
            if row.get('source') or row.get('icon'):
                base.alpha_composite(self.item_art(row, (16, 16)), (ix, y + (rh-16)//2))
                ix += 20
            self.label(base, row.get('label', ''), (ix, y + (rh-7)//2), t['muted'] if row.get('disabled') else t['text'])
            if row.get('value') is not None:
                vx = x + rw - 4
                if row.get('value_icon'):
                    art = self.item_art({'source': row['value_icon']}, (10, 10))
                    base.alpha_composite(art, (vx - 10, y + (rh-10)//2))
                    vx -= 13
                self.label(base, str(row['value']), (vx, y + (rh-7)//2), t['title'], 'right')
        states = {}
        for index, (x, y, rw, rh) in enumerate(rects):
            im = skin.copy()
            ImageDraw.Draw(im).rectangle((x, y, x+rw-1, y+rh-1), fill=t['button'] if t['style'] != 'slate' else t['border'])
            im.alpha_composite(base)
            hl = ImageDraw.Draw(im)
            hl.rectangle((x, y, x+rw-1, y+rh-1), outline=t['select'])
            states[f'selected-{index}'] = im
        plain = skin.copy(); plain.alpha_composite(base)
        states['normal'] = states.get(f"selected-{c.get('selected', 0)}", plain).copy()
        meta.update(row_rects=rects, rows=rows, selected=c.get('selected', 0))
        return states, {'skin': skin, 'content': base}


def head_meta(doc):
    """Title and description tags for preview.html."""
    name = html.escape(str(doc['name']), quote=True)
    return (f'<title>{name} - interface playground</title>\n'
            '<meta name="description" content="Interactive pixel UI components, states and screens.">')


def image_inputs(doc):
    """Every image a recipe refers to, as (holder dict, key, file stem, path)."""
    found = []
    for c in doc['components']:
        for key in ('source', 'portrait'):
            if c.get(key):
                found.append((c, key, c['id'] if key == 'source' else f"{c['id']}-{key}", c[key]))
        for listname in ('items', 'rows'):
            for index, entry in enumerate(c.get(listname, [])):
                for key in ('source', 'value_icon'):
                    if entry.get(key):
                        stem = f"{c['id']}-{listname[:-1]}-{index}" + ('' if key == 'source' else '-icon')
                        found.append((entry, key, stem, entry[key]))
    for screen in doc.get('screens', []):
        background = screen.get('background')
        if isinstance(background, str) and not background.startswith('#'):
            found.append((screen, 'background', f"{screen['id']}-background", background))
    return found


def portable_name(holder, key, stem, path):
    # Frame references ("set.json#frame") are saved as PNGs so the copy stands alone.
    suffix = '.png' if '#' in str(path) else (Path(path).suffix or '.png')
    return stem + suffix


def generate(recipe, out, scale=2):
    recipe, out = Path(recipe),Path(out)
    pa.protect_inputs([recipe],[out/'source.json',out/'ui.json',out/'atlas.json'])
    doc = pa.read_json(recipe)
    studio = Studio(doc,recipe.parent)
    for name in studio.specs:
        studio.build(name)
    found = image_inputs(doc)
    inputs = [recipe] + [recipe.parent/str(path).partition('#')[0] for *_, path in found]
    outputs = [out/name for name in ('source.json','ui.json','atlas.json','atlas.png','preview.png','catalog.png','preview.html')]
    for name,(states,_,layers) in studio.built.items():
        outputs.extend(out/'components'/name/f'{state}.png' for state in states)
        outputs.extend(out/'components'/name/f'layer-{layer}.png' for layer in layers)
        outputs.append(out/'components'/name/'preview.gif')
    outputs.extend(out/'screens'/f"{s['id']}.png" for s in doc.get('screens',[]))
    outputs.extend(out/'inputs'/portable_name(*entry) for entry in found)
    if doc.get('font'):
        inputs.append(recipe.parent/doc['font'])
        outputs.append(out/'inputs'/Path(doc['font']).name)
    pa.protect_inputs(inputs,outputs)
    out.mkdir(parents=True,exist_ok=True)
    images, manifest, catalog, labels = {}, {}, [], []
    for name,(states,meta,layers) in studio.built.items():
        dest = out/'components'/name
        dest.mkdir(parents=True,exist_ok=True)
        meta['states'],meta['layers'] = {},{}
        for state,im in states.items():
            im.save(dest/f'{state}.png')
            meta['states'][state] = f'components/{name}/{state}.png'
            images[f'{name}/{state}'] = im
        for layer,im in layers.items():
            im.save(dest/f'layer-{layer}.png')
            meta['layers'][layer] = f'components/{name}/layer-{layer}.png'
        if meta['type']=='floating-text':
            gif(list(states.values()),[meta['duration_ms']]*len(states),dest/'preview.gif',scale=scale)
        if meta['type']=='dialogue':
            frames = [states[f'typing-{i}'] for i in range(meta['typing_frames'])] + [states['normal'], states['waiting']]*2
            gif(frames,[meta['duration_ms']]*meta['typing_frames']+[450]*4,dest/'preview.gif',scale=scale)
        manifest[name] = meta
        if meta['type'] not in ('canvas','hud'):
            catalog.append(states[meta['default']])
            labels.append(name)
    atlas(images,out)
    if catalog:
        pa.make_sheet(catalog,labels,scale=2,columns=4).save(out/'catalog.png')
    screens = []
    (out/'screens').mkdir(exist_ok=True)
    for screen in doc.get('screens',[]):
        safe_name(screen['id'])
        im = studio.compose(screen['size'],screen['children'],screen.get('background',studio.theme['ink']))
        im.save(out/'screens'/f"{screen['id']}.png")
        screens.append(im)
    if screens:
        pa.make_sheet(screens,[s['id'] for s in doc['screens']],scale=scale,columns=2).save(out/'preview.png')
    # Keep the recipe portable by copying every source image and an optional font.
    portable = deepcopy(doc)
    copies = image_inputs(portable)
    for (holder, key, _, path), original in zip(copies, found):
        dest = out/'inputs'/portable_name(*original)
        dest.parent.mkdir(exist_ok=True)
        if '#' in str(path):
            load_image(recipe.parent, path).save(dest)
        else:
            dest.write_bytes((recipe.parent/path).read_bytes())
        holder[key] = f'inputs/{dest.name}'
    for c in portable['components']:
        if c.get('source'):
            manifest[c['id']]['source'] = c['source']
        if c.get('items'):
            manifest[c['id']]['items'] = c['items']
        if c.get('rows'):
            manifest[c['id']]['rows'] = c['rows']
    if doc.get('font'):
        dest = out/'inputs'/Path(doc['font']).name
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes((recipe.parent/doc['font']).read_bytes())
        portable['font'] = f'inputs/{dest.name}'
    pa.write_json(out/'source.json',portable)
    screens_data = portable.get('screens',[])
    data = {'name':doc['name'],'theme':studio.theme,'components':manifest,'screens':screens_data}
    if doc.get('locales'):
        data['locales'] = doc['locales']
    pa.write_json(out/'ui.json',data)
    template = (Path(__file__).resolve().parents[1]/'assets/templates/ui-preview.html').read_text(encoding='utf-8')
    (out/'preview.html').write_text(template.replace('__HEAD_META__',head_meta(doc)).replace('__UI_DATA__',json.dumps(data,ensure_ascii=False).replace('<','\\u003c')),encoding='utf-8')
    return {'components':len(manifest),'states':len(images),'screens':len(screens),'output':str(out)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('recipe',type=Path)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--scale',type=pa.positive,default=2)
    args = parser.parse_args()
    try:
        print(json.dumps(generate(args.recipe,args.out,args.scale),ensure_ascii=False))
    except (OSError,ValueError,KeyError,TypeError) as error:
        parser.exit(2,f'Error: {error}\n')


if __name__=='__main__':
    main()
