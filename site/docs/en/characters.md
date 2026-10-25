# Characters

The character generator turns a short recipe into a small animated character: four or eight directions, standing, idle and walk poses, an editable pixel grid, a PNG atlas and GIF previews.

@shots examples/characters/adventurer/walk.gif|Adventurer walking in eight directions, examples/characters/researcher/walk.gif|Researcher walking in four directions

## Hand-drawn RPG characters

For final art, draw characters by hand as grid sources. The RPG kit has four 16x16 class figures, a [warrior]({{repo}}/blob/main/skills/pixel-art-studio/assets/examples/rpg-kit/warrior.json), a mage, a summoner and an archer, plus a merchant. Each has down, up and right views (left mirrors right) with a stand and two walk frames.

@shots examples/rpg-kit/sheets/warrior/walk.gif|Warrior, examples/rpg-kit/sheets/mage/walk.gif|Mage, examples/rpg-kit/sheets/summoner/walk.gif|Summoner, examples/rpg-kit/sheets/archer/walk.gif|Archer

Each class has a two-beat attack, and the spells and arrows are separate projectile frames:

@shots examples/rpg-kit/sheets/warrior-attack.gif|Warrior thrust, examples/rpg-kit/sheets/archer-shoot.gif|Archer shot, examples/rpg-kit/sheets/mage-cast.gif|Mage cast, examples/rpg-kit/sheets/summoner-cast.gif|Summoner cast, examples/rpg-kit/sheets/fireball.gif|Fireball, examples/rpg-kit/sheets/wisp.gif|Spirit wisp

The interface reuses the sprites: portraits are head-and-shoulder crops, and the character select screen shows the stand frame enlarged.

@shots examples/interface-kit/screens/select.png|Character select

## Enemies, actions and effects

The RPG kit also hand-draws battle art:
- **Enemies:** a slime, a bat, a goblin, a mushroom, a ghost and a skeleton, each with an idle loop, an attack or a hurt flash.
- **Effects:** a slash, a hit spark and a heal.

@shots examples/rpg-kit/sheets/goblin-attack.gif|Goblin club attack, examples/rpg-kit/sheets/slime.gif|Slime idle, examples/rpg-kit/sheets/bat.gif|Bat flap, examples/rpg-kit/sheets/enemies/preview.png|Mushroom, ghost and skeleton

Emote bubbles (alert, question, heart, anger, dots, note, idea) sit above any character's head.

@shots examples/rpg-kit/sheets/emotes/preview.png|Emote bubbles

The rest of this page covers the generator, which builds quick, consistent 16×16 casts from a recipe.

## Ask your agent

> Use pixel-art-studio to make a 16×16 shopkeeper with long hair, an apron and glasses. Four directions, idle and walk animations, editable frames and a PNG atlas.

The agent copies a starter recipe, sets the colors and parts, runs the generator, then refines expressions or equipment in the generated grid.

## Run it yourself

From the skill folder:

```bash
python scripts/character.py assets/examples/characters/researcher/recipe.json --out output/researcher
```

`--scale` sets the preview zoom (default 6). The atlas always keeps the native 16×16 frames.

## The recipe

```json
{
  "name": "shopkeeper",
  "directions": 4,
  "parts": ["long-hair", "apron", "glasses"],
  "colors": {
    "hair": "#8d5138",
    "hair_shadow": "#573529",
    "top": "#708fa2",
    "top_shadow": "#465d78",
    "apron": "#e6d6a9"
  },
  "timing_ms": {"stand": 700, "idle": 180, "step": 160}
}
```

| Field | Use |
|---|---|
| `name` | Character name in the source and atlas |
| `directions` | `4` (default) or `8` |
| `parts` | Ordered list from `long-hair`, `glasses`, `beard`, `cap`, `coat`, `apron`; later parts draw on top |
| `colors` | Hex colors by material role; roles you leave out keep the template palette |
| `timing_ms` | `stand`, `idle` and `step` durations |
| `template` | Optional custom template, relative to the recipe |

Color roles: `ink`, `hair`, `hair_shadow`, `skin`, `skin_shadow`, `eyes`, `top`, `top_shadow`, `pants`, `pants_shadow`, `shoes`, `glint`, `cap`, `cap_shadow`, `apron`, `apron_shadow`. Coats use the top colors. Put glasses after hair and headwear.

## What it writes

@shots examples/characters/researcher/preview.png|Every researcher pose on a contact sheet

| File | Contents |
|---|---|
| `source.json` | Editable pixel grids for every pose |
| `atlas.png`, `atlas.json` | Transparent native frames with rectangles, durations and the `[8,16]` foot pivot |
| `animations.json` | Looping clips; a walk plays `walk-a → stand → walk-b → stand` |
| `preview.png` | Labeled contact sheet |
| `idle.gif`, `walk.gif` | Playback of every direction on a checkerboard |

## Eight directions

Set `"directions": 8` for 32 poses ordered front, front-right, right, back-right, back, back-left, left, front-left. Diagonals use their own drawn grids; left-facing views mirror the right. See the [adventurer recipe]({{repo}}/blob/main/skills/pixel-art-studio/assets/examples/characters/adventurer/recipe.json).

## Tips

- Mirroring flips handed tools, badges and asymmetric clothing. Fix those in the generated `source.json`, then re-render it with `scripts/pixel_art.py render`.
- Keep each iteration in its own output folder; regenerating replaces the files.
- For other proportions, edit the template's grids, overlays, motion and pivot together. The full reference is in [sprites.md]({{repo}}/blob/main/skills/pixel-art-studio/references/sprites.md).
