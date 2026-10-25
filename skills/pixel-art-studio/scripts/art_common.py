"""Pixel text, atlas export and animation playback shared by the art tools."""
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont
import pixel_art as pa


# Original 5x7 bitmap alphabet; each hexadecimal digit pair is one five-bit row.
GLYPHS = {
    'A':'0E11111F111111', 'B':'1E11111E11111E', 'C':'0F10101010100F',
    'D':'1E11111111111E', 'E':'1F10101E10101F', 'F':'1F10101E101010',
    'G':'0F10101711110F', 'H':'1111111F111111', 'I':'0E04040404040E',
    'J':'0702020212120C', 'K':'11121418141211', 'L':'1010101010101F',
    'M':'111B1515111111', 'N':'11191513111111', 'O':'0E11111111110E',
    'P':'1E11111E101010', 'Q':'0E11111115120D', 'R':'1E11111E141211',
    'S':'0F10100E01011E', 'T':'1F040404040404', 'U':'1111111111110E',
    'V':'11111111110A04', 'W':'11111115151B11', 'X':'11110A040A1111',
    'Y':'11110A04040404', 'Z':'1F01020408101F',
    '0':'0E11131519110E', '1':'040C040404040E', '2':'0E11010204081F',
    '3':'1E01010E01011E', '4':'02060A121F0202', '5':'1F10101E01011E',
    '6':'0E10101E11110E', '7':'1F010204080808', '8':'0E11110E11110E',
    '9':'0E11110F01010E', '.':'00000000000004',
    ':':'00000400000400', '/':'01010204081010', '-':'0000000E000000',
    '+':'0004041F040400', '%':'19190204081313', '!':'04040404040004',
    '?':'0E110102040004', '(':'02040808080402', ')':'08040202020408',
    '[':'0E08080808080E', ']':'0E02020202020E', "'":'04040000000000',
    '=':'00001F001F0000', '<':'02040810080402', '>':'08040201020408',
    '_':'0000000000001F', '#':'0A1F0A0A1F0A00', '"':'0A0A0000000000',
    '*':'00150E1F0E1500', '&':'0C12140815120D', '~':'00000D16000000',
}
# Lowercase and descenders on the same 7-row body; rows 7 and 8 hang below the baseline.
LOWER = {
    'a':['.....','.....','.###.','....#','.####','#...#','.####'],
    'b':['#....','#....','####.','#...#','#...#','#...#','####.'],
    'c':['.....','.....','.####','#....','#....','#....','.####'],
    'd':['....#','....#','.####','#...#','#...#','#...#','.####'],
    'e':['.....','.....','.###.','#...#','#####','#....','.####'],
    'f':['..##','.#..','####','.#..','.#..','.#..','.#..'],
    'g':['.....','.....','.####','#...#','#...#','#...#','.####','....#','####.'],
    'h':['#....','#....','####.','#...#','#...#','#...#','#...#'],
    'i':['#','.','#','#','#','#','#'],
    'j':['..#','...','..#','..#','..#','..#','..#','..#','##.'],
    'k':['#...','#...','#..#','#.#.','##..','#.#.','#..#'],
    'l':['#.','#.','#.','#.','#.','#.','.#'],
    'm':['.....','.....','##.#.','#.#.#','#.#.#','#.#.#','#.#.#'],
    'n':['.....','.....','####.','#...#','#...#','#...#','#...#'],
    'o':['.....','.....','.###.','#...#','#...#','#...#','.###.'],
    'p':['.....','.....','####.','#...#','#...#','#...#','####.','#....','#....'],
    'q':['.....','.....','.####','#...#','#...#','#...#','.####','....#','....#'],
    'r':['....','....','#.##','##..','#...','#...','#...'],
    's':['.....','.....','.####','#....','.###.','....#','####.'],
    't':['.#..','.#..','####','.#..','.#..','.#..','..##'],
    'u':['.....','.....','#...#','#...#','#...#','#...#','.####'],
    'v':['.....','.....','#...#','#...#','#...#','.#.#.','..#..'],
    'w':['.....','.....','#...#','#...#','#.#.#','#.#.#','.#.#.'],
    'x':['.....','.....','#...#','.#.#.','..#..','.#.#.','#...#'],
    'y':['.....','.....','#...#','#...#','#...#','#...#','.####','....#','####.'],
    'z':['.....','.....','#####','...#.','..#..','.#...','#####'],
    ',':['.','.','.','.','.','#','#','#'],
    ';':['.','.','#','.','.','#','#','#'],
}


def _glyph(char):
    """Rows of '#' and '.', trimmed to the columns the character uses."""
    if char in LOWER:
        rows = LOWER[char]
    elif char == ' ':
        return ['..'] * 7
    else:
        rows = [format(b, '05b').replace('1', '#').replace('0', '.') for b in bytes.fromhex(GLYPHS[char])]
    used = [x for x in range(len(rows[0])) if any(row[x] == '#' for row in rows)]
    return [row[used[0]:used[-1]+1] for row in rows] if used else rows


def unknown_characters(text):
    return set(text) - (GLYPHS.keys() | LOWER.keys() | {' '})


def text_width(text):
    """Width in pixels of text in the built-in font at scale 1."""
    return max(1, sum(len(_glyph(ch)[0]) + 1 for ch in text) - 1) if text else 1


def wrap_text(text, width, font=None, font_size=12):
    """Split text into lines no wider than `width` pixels at scale 1; explicit newlines are kept."""
    lines = []
    for paragraph in str(text).split('\n'):
        line = ''
        for word in paragraph.split(' '):
            trial = f'{line} {word}' if line else word
            measured = text_image(trial, font=font, font_size=font_size).width if font else text_width(trial)
            if line and measured > width:
                lines.append(line)
                line = word
            else:
                line = trial
        lines.append(line)
    return lines


def safe_name(value):
    if not isinstance(value, str) or not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_-]*', value):
        raise ValueError(f'Use letters, digits, hyphens or underscores for file IDs: {value!r}')
    return value


def _outlined(image, color):
    """Pad by one pixel and draw a one-pixel outline around every visible pixel."""
    padded = Image.new('RGBA', (image.width+2, image.height+2))
    mask = Image.new('L', padded.size)
    alpha = image.getchannel('A').point(lambda v: 255 if v else 0)
    for dx, dy in [(-1,-1),(0,-1),(1,-1),(-1,0),(1,0),(-1,1),(0,1),(1,1)]:
        mask.paste(255, (1+dx, 1+dy), alpha)
    padded.paste(Image.new('RGBA', padded.size, color), (0, 0), mask)
    padded.alpha_composite(image, (1, 1))
    return padded


def text_image(text, color='#edf1df', scale=1, font=None, font_size=12, outline=None):
    text = str(text)
    if font:
        face = ImageFont.truetype(str(font), font_size)
        box = face.getbbox(text)
        mask = Image.new('L', (max(1, box[2]-box[0]), max(1, box[3]-box[1])))
        ImageDraw.Draw(mask).text((-box[0], -box[1]), text, font=face, fill=255)
        mask = mask.point(lambda value: 255 if value >= 128 else 0)
        out = Image.new('RGBA', mask.size, color)
        out.putalpha(mask)
    else:
        unknown = unknown_characters(text)
        if unknown:
            raise ValueError(f'Provide a font file for these characters: {"".join(sorted(unknown))}')
        glyphs = [_glyph(ch) for ch in text]
        out = Image.new('RGBA', (text_width(text), 9 if any(len(g) > 7 for g in glyphs) else 7))
        px, x, ink = out.load(), 0, pa.rgba(color) if isinstance(color, str) else color
        for rows in glyphs:
            for y, row in enumerate(rows):
                for dx, cell in enumerate(row):
                    if cell == '#':
                        px[x+dx, y] = ink
            x += len(rows[0]) + 1
    if outline:
        out = _outlined(out, outline)
    return out.resize((out.width*scale, out.height*scale), Image.Resampling.NEAREST)


def put_text(image, text, xy, color, align='left', outline=None, **options):
    """Draw text with its top-left glyph pixel at xy; an outline grows outward by one pixel."""
    label = text_image(text, color, outline=outline, **options)
    x, y = xy
    if outline:
        x, y = x - options.get('scale', 1), y - options.get('scale', 1)
    if align == 'center':
        x -= label.width//2
    elif align == 'right':
        x -= label.width
    image.alpha_composite(label, (int(x), int(y)))


def load_frames(path):
    """Named images from a grid source, an atlas JSON, or a single PNG (named after the file)."""
    path = Path(path)
    if path.suffix.lower() == '.png':
        with Image.open(path) as im:
            return {path.stem: im.convert('RGBA')}
    doc = pa.read_json(path)
    if isinstance(doc.get('frames'), list) and doc['frames'] and 'rows' in doc['frames'][0]:
        _, images, _ = pa.load_sprite(path)
        return {f['name']: im for f, im in zip(doc['frames'], images)}
    with Image.open(path.parent / doc['image']) as sheet:
        sheet = sheet.convert('RGBA')
    frames = doc['frames'].items() if isinstance(doc['frames'], dict) else ((f['name'], f) for f in doc['frames'])
    return {name: sheet.crop((r[0], r[1], r[0]+r[2], r[1]+r[3])) for name, f in frames for r in [f['rect']]}


def load_image(base, source):
    """An image path, or "frames.json#name" for one frame of a grid source or atlas."""
    path, _, frame = str(source).partition('#')
    if frame:
        frames = load_frames(Path(base) / path)
        if frame not in frames:
            raise ValueError(f'{path} has no frame named {frame!r}')
        return frames[frame]
    with Image.open(Path(base) / path) as im:
        return im.convert('RGBA')


def atlas(images, out, width=512, padding=1):
    """Pack named, variable-sized images into an untrimmed shelf atlas."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    width = max(width, max(im.width for im in images.values()))
    x = y = row_h = 0
    records = {}
    for name, im in images.items():
        if x and x + im.width > width:
            x, y, row_h = 0, y + row_h + padding, 0
        records[name] = {'rect': [x, y, im.width, im.height], 'pivot': [im.width//2, im.height]}
        x += im.width + padding
        row_h = max(row_h, im.height)
    sheet = Image.new('RGBA', (width, y + row_h))
    for name, im in images.items():
        sheet.paste(im, records[name]['rect'][:2])
    sheet.save(out / 'atlas.png')
    pa.write_json(out / 'atlas.json', {'format':'pixel-art-studio-packed-v1', 'image':'atlas.png',
                                      'size':list(sheet.size), 'padding':padding, 'frames':records})
    return records


def gif(images, durations, path, scale=3, loop=0):
    frames = []
    for image in images:
        frame = pa.checker(image.size)
        frame.alpha_composite(image)
        frames.append(frame.resize((image.width*scale, image.height*scale), Image.Resampling.NEAREST).convert('RGB'))
    strip = Image.new('RGB', (frames[0].width, sum(im.height for im in frames)))
    offset = 0
    for frame in frames:
        strip.paste(frame, (0, offset))
        offset += frame.height
    palette = strip.quantize(colors=256, dither=Image.Dither.NONE)
    frames = [im.quantize(palette=palette, dither=Image.Dither.NONE) for im in frames]
    options = {'loop': loop} if loop is not None else {}
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=durations,
                   disposal=2, optimize=False, **options)
