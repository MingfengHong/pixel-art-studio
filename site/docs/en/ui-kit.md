# Game UI

The UI tool builds a complete pixel interface from one recipe:
- Every component state, plus text-free nine-slice skins and separate layers.
- Composed screens.
- An interactive browser preview.

@shots examples/interface-kit/screens/battle.png|Battle screen, examples/interface-kit/preview.png|Town HUD, dialogue, inventory, battle and shop screens

Try the RPG kit in the [interface playground]({{root}}playground/index.html?lang={{lang}}).

## Ask your agent

> Use pixel-art-studio to make an RPG interface in a plum-and-gold style: a town HUD with portrait, HP/MP bars and an item belt, an NPC dialogue box with choices, an equipment and inventory screen, a turn-based battle screen, a shop, and a character select screen. Include state PNGs, nine-slice skins and an interactive preview.

## Run it yourself

```bash
python scripts/ui.py assets/examples/interface-kit/recipe.json --out output/interface
```

Open `output/interface/preview.html`. In the preview:
- Belts and lists respond to clicks and number keys.
- The dialogue types itself out; click to finish the line and pick an answer.
- Sliders, switches, dropdowns, scroll views, tooltips, dialogs and floating text all work.

## Themes

`theme.style` picks the frame language, and any color can be overridden on top:

| Style | Look |
|---|---|
| `slate` | Bevelled slate panels |
| `wood` | A warm framed rim with plank grain around a light fill |
| `arcade` | A bold outline, a two-pixel rim and dark fills |

```json
"theme": {"style": "arcade", "frame": "#d9a94a", "frame_light": "#ffe29a", "frame_dark": "#8a5a1e",
          "surface": "#2e2547", "inset": "#1f1933", "title": "#ffd257", "select": "#7fd1c8"}
```

The RPG kit is exactly this: `arcade` recolored into plum and gold. The [side-scroller HUD]({{repo}}/blob/main/skills/pixel-art-studio/assets/examples/side-scroller/hud.json) uses plain `arcade`.

## Components

| Type | Main fields | You get |
|---|---|---|
| `health-bar`, `mana-bar`, `xp-bar`, `stamina-bar`, `bar` | `value`, `color`, `label`, `max` | States and track, fill and text layers |
| `button` | `label`, `icon` or `source`, `layout: "stack"`, `shape: "round"`, `opacity` | Six states and text-free skins |
| `hotbar` | `slots`, `cell`, `items`, `selected` | A selectable item belt |
| `list` | `rows` with `source`, `label`, `value`, `value_icon`, `disabled` | Shops, quest logs, skill and stat lists |
| `dialogue` | `speaker`, `text`, `portrait`, `layout`, `choices` | Typewriter frames, a continue arrow, choice states |
| `dial` | `time`, `label` | A day/night clock face |
| `scroll-view` | `columns`, `cell`, `items`, `slots` | An inventory grid with empty slots |
| `minimap`, `panel`, `slider`, `toggle`, `switch`, `dropdown` | Usual fields | Every state, track and thumb, skins |
| `image`, `sprite`, `icon`, `text`, `label` | `source`, `frame` or `slot`, `outline`, `align` | Framed art and outlined text |
| `modal`, `tooltip`, `floating-text` | `lines`, `buttons`, `frames` | Dialogs, tooltips, rising text |

Every image field accepts a PNG or `set.json#frame`, so hand-drawn icons and portraits plug straight in.

## Dialogue boxes

```json
{"id": "talk", "type": "dialogue", "layout": "inset", "size": [312, 76],
 "speaker": "Bram the Trader", "portrait": "../rpg-kit/merchant.json#down-stand", "portrait_crop": [0, 0, 16, 16],
 "text": "Welcome, traveler! Fresh bread, sturdy boots and a map of the old mines. Care to take a look?",
 "choices": ["Show me your wares.", "Just passing through."]}
```

- **Portrait:** `portrait_crop` cuts the head and shoulders out of the sprite and enlarges them by a whole number, so the portrait always matches the character.
- **Layout:** `"inset"` puts the portrait inside the box with the name as a tab on top. The default `"panel"` layout gives the portrait its own panel with a name plate.
- **Text:** keep two or three lines of 35-50 characters per page. Text wraps automatically, and the tool stops with an error if a page does not fit.
- **Typewriter:** `typing_frames` × `duration_ms` sets the speed. Clicking finishes the line, and a blinking arrow means "continue".

## Text and languages

The built-in 5x7 font has proportional upper and lower case with descenders. For Chinese or other scripts, set a licensed TTF/OTF `font` and its native `font_size`. Add `locales` to translate screen names and descriptions in the preview.

## What it writes

| File | Contents |
|---|---|
| `components/<id>/*.png`, `layer-*.png` | Every state and layer |
| `atlas.png`, `atlas.json` | Named state rectangles |
| `ui.json` | Types, states, labels, layers, slices, slot and row rectangles, layout |
| `screens/*.png`, `preview.png`, `catalog.png` | Composed screens and overviews |
| `preview.html` | Interactive playground |
| `source.json`, `inputs/` | A portable recipe; referenced frames are saved as PNGs |

The full component reference and HUD layout advice are in [ui.md]({{repo}}/blob/main/skills/pixel-art-studio/references/ui.md).
