# Pixel UI production

Define the palette, frame language, spacing, icon size and typography from the user's reference. Learn the reference's qualities (readability, hierarchy, polish) and design an original look rather than copying its layout, frames or wording. Keep labels and interaction regions editable.

## Generate the interface kit

From the installed skill folder:

```sh
python scripts/ui.py assets/examples/interface-kit/recipe.json --out output/interface
```

Open `output/interface/preview.html` directly in a browser. The [RPG recipe](../assets/examples/interface-kit/recipe.json) has six screens:

- **Town HUD:** portrait, HP/MP/XP bars, gold, minimap, quest tracker and an item belt.
- **Dialogue:** a portrait inside the box, a name tab, typewriter text and choices.
- **Inventory and equipment:** equipment slots around the character, a stat list and a scrolling bag.
- **Shop:** a merchant portrait, a price list and buy/leave actions.
- **Battle:** party and enemies at 2× over a tile-assembled field, with slash and hit effects, a command list and a party list with portraits and HP bars.
- **Character select:** the stand frame enlarged in a framed showcase, stat changes, a skill slot, prev/select/next buttons, and the cast in the scene with emote bubbles.

The [side-scroller HUD](../assets/examples/side-scroller/hud.json) shows a mobile-style layout instead: big icon buttons, a day/night dial, on-screen arrows and round action buttons.

`preview.html` is a self-contained page styled with the recipe's own `theme` colors:
- It fills the browser window and scales each screen to fit.
- Belts and lists respond to clicks and number keys, dialogue types itself out, and sliders, switches, dropdowns, scroll views, tooltips, dialogs and floating text all work.
- `?embed=1` shows only the playground window, and `?lang=` picks English or Chinese for the built-in text.
- An optional `locales` object translates screen names and descriptions:

```json
"locales": {"zh-CN": {"label": "中文", "name": "RPG 界面套件", "screens": {"hud": {"title": "小镇 HUD"}}}}
```

## Themes

`theme.style` picks the frame language. Any color role can be overridden on top of it.

| Style | Look |
|---|---|
| `slate` (default) | Bevelled slate panels with a single outline |
| `wood` | A warm framed rim with plank grain around a light fill |
| `arcade` | A bold outline, a two-pixel rim and dark fills, for mobile and action HUDs |

Color roles:
- **General:** `ink`, `border`, `light`, `surface`, `inset`, `text`, `muted`, `accent`, `health`, `mana`, `xp`, `shadow`.
- **Framed styles:** `frame`, `frame_light`, `frame_dark`, `button`, `title`, `select`, `bar_bg`, plus `rim` and `corner` in pixels.

The RPG kit is `arcade` recolored into a plum-and-gold theme. One theme and three overrides give a different identity.

## Components

| Type | Main recipe fields | Artwork and metadata |
|---|---|---|
| `hud`, `canvas` | `children`, `background` (color with alpha, or an image path) | Composite and child placements |
| `health-bar`, `mana-bar`, `xp-bar`, `stamina-bar`, `bar` | `value` 0-1, `color`, `label`, `max` | Empty/half/full/current, track/fill/text layers, `fill_rect`, `value_text` |
| `minimap` | `tiles`, `colors`, `markers[].at` | Map, viewport mask, markers |
| `button` | `label`, `icon` or `source`, `layout: "stack"`, `shape: "round"`, `opacity`, `outline` | Six states, text-free skins |
| `toggle`, `switch` | `value` | Off/on/disabled |
| `slider` | `value` 0-1, `range` | Min/half/max/current/disabled, track/thumb |
| `dropdown` | `options`, `selected` | Selection variants, expanded menu |
| `panel` | `label`, `align` | Panel, skin, nine-slice insets |
| `scroll-view` | `columns`, `cell`, `items` (`source` or `icon`, `count`), `slots` | Top/middle/bottom, full content, viewport |
| `hotbar` | `slots`, `cell`, `gap`, `items`, `selected`, `numbers` | `selected-N` states, slot rectangles |
| `list` | `rows` (`source`, `label`, `value`, `value_icon`, `disabled`), `row_height`, `selected` | `selected-N` states, row rectangles; shops, quest logs, skills, stats |
| `dialogue` | `speaker`, `text` or `lines`, `portrait`, `layout`, `choices`, `typing_frames`, `duration_ms` | Typing frames, waiting/continue, `choice-N`, text/portrait/name rectangles, GIF |
| `dial` | `time` 0-1, `label`, `day`, `night` | Day/night face with a hand; quarter states |
| `text`, `label` | `label`, `color`, `scale`, `outline`, `align` | Transparent raster and editable string |
| `image`, `sprite` | `source`, `crop`, `frame` or `slot` | Fitted art, optionally framed or in a sunken slot |
| `icon` | `icon`, `color` | Built-in 7×7 symbol |
| `modal`, `tooltip` | `label`, `lines`, `buttons` | Dialog or pointer box |
| `floating-text` | `label`, `color`, `outline`, `frames`, `rise`, `scale` | Rising, fading frames and a GIF |

Every image field (`source`, `portrait`, item `source`) accepts a PNG or `set.json#frame`, one frame of a hand-drawn grid source or atlas. Built-in icons: `heart`, `drop`, `star`, `coin`, `sword`, `shield`, `bag`, `gear`, `close`, `check`, `arrow`, `sun`, `moon`, `music`. Use hand-drawn icons for anything shipped.

## Dialogue boxes

A dialogue box is the most-read UI in an RPG. Design it for reading first:

- **Size:** about one quarter to one third of the screen height. Leave the speaker and the scene visible above it.
- **Speaker:** a name tab or plate in the title color. Use one consistent place per game.
- **Portrait:** 40–64 px, framed, the same side every time. Use a drawn portrait, or crop the sprite with `portrait_crop`. `layout: "inset"` places it inside the box with the name as a tab on top. The default `panel` layout gives it a separate panel with a name plate.
- **Text:**
  - Keep each page to two or three lines of about 35–50 characters; split longer speech into pages.
  - Leave 8–10 px of padding and about 4 px of line gap.
  - Use high contrast against the panel: light text on dark, or dark on light, never mid on mid.
- **Typewriter:** about 30–60 ms per character (`typing_frames` × `duration_ms` for the whole line). Clicking finishes the line, and a blinking arrow means "continue".
- **Choices:** list them under the text, with a cursor on the selected one and the others dimmed. Keep two to four short options.
- **Localization:** keep strings editable (`ui.json` stores `lines` and `choices`). Use `font` for scripts the built-in font lacks, and size the box for the longest language.

## HUD layout

- Put vitals (portrait, HP/MP or stamina/hunger, level) in the top left, currency and map or time in the top right, and the hotbar or belt at the bottom centre. On mobile, put touch controls in the bottom corners at 70–85 % opacity.
- Keep the middle of the screen and the character's surroundings clear.
- Give each bar a label and a value when the number matters (`label`, `max`).
- Text drawn over the game scene needs an outline (`outline` on labels, buttons and floating text).

## Recipe

Every component has a unique file-safe `id`, a `type`, and a native `size: [width,height]`.

```json
{
  "name": "compact-hud",
  "theme": {"style": "arcade", "frame": "#d9a94a", "surface": "#2e2547"},
  "components": [
    {"id": "life", "type": "health-bar", "size": [96, 10], "value": 0.75, "label": "HP", "max": 120},
    {"id": "belt", "type": "hotbar", "size": [134, 26], "cell": 18, "slots": 6,
     "items": [{"source": "items.json#sword"}, {"source": "items.json#potion", "count": 5}]}
  ],
  "screens": [{"id": "hud", "size": [320, 180], "children": [
    {"component": "life", "at": [8, 8]}, {"component": "belt", "at": [93, 150]}]}]
}
```

Child placements use `component`, `at: [x,y]` and an optional `state`. Browser behaviors use `tooltip: "item-tip"`, `action: "open:dialog"`, `action: "float:damage"`, or `bind: "health"` on a slider. An optional `label` supplies an accessible name. Place bound bars before sliders, and containers behind controls.

## Text, sizing and export

The built-in 5×7 font has proportional upper and lower case Latin letters, digits and punctuation, and lowercase descenders hang two pixels below. For Chinese or another script, set the recipe-level `font` to a licensed TTF/OTF file and `font_size` to its native size; the tool rasterizes it with hard edges and copies the font into `inputs/`. Keep text-free skins for engine text and localization.

| Output | Use |
|---|---|
| `source.json`, `inputs/` | Portable recipe; referenced frames are saved as PNGs |
| `components/<id>/*.png` | Individual native states |
| `components/<id>/layer-*.png` | Skins, fill, track, thumb, content, text, portrait or mask |
| `atlas.png`, `atlas.json` | Named, untrimmed state rectangles |
| `ui.json` | Types, states, labels, layers, slices, rectangles and layout |
| `screens/*.png`, `preview.png`, `catalog.png` | Native screens and enlarged overviews |
| `preview.html` | Interactive playground that fits the window |

To map the output onto an engine's widgets:
- Apply `nine_slice` to the layer named by `slice_source`, and draw labels separately.
- Clip bar fills to `fill_rect` and scroll content to `viewport`.
- Use `slot_rects`, `row_rects` and `choice_rects` for hit testing.
