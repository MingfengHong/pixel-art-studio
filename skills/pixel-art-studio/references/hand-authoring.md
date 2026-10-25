# Hand-authored pixel art

Release-quality game art is placed pixel by pixel. Shape generators, filters and noise produce "programmer art": soft silhouettes, uniform texture, no intent. Author final sprites, tiles and portraits as editable grid sources, and use the tools only to render, assemble and check them.

## The workflow

1. **Set the canvas and grid.** Pick the native size from the target game: 16×16 tiles and icons, 16×16 to 16×32 characters, 32×48 large props, 32–64 px portraits. Never resize finished pixels.
2. **Build the palette before drawing.** Give each material a ramp of 3–5 tones: deep shadow, shadow, base, light, highlight. Shift hue as well as value: shadows lean toward purple or blue, lights toward yellow. Reuse ramps across the set and keep the total small.
3. **Block the silhouette.** Fill the shape in the base tone only and check that it reads at 1×.
4. **Shade by form.** Light comes from the top left. Add the light side, then the shadow side, then the contact or occlusion shadow. Shade each clump separately (leaf clusters, hair locks, cloth folds) instead of one gradient across the whole object.
5. **Outline.** Use a dark outline that is not black, such as `#20161f` or a darkened ramp tone. Outline the outer silhouette; inside the shape, separate materials with the darker ramp tone, not the outline color.
6. **Detail last.** Eyes, highlights, buckles, flowers and specks come after the big forms read. One well-placed pixel beats a cluster of noise.
7. **Review** at 1× and at 3× on light and dark backgrounds, then in the real scene next to the other assets.

Write each set as a grid source: one character per pixel, `.` for transparent, shared palette keys. Frames in one source share a canvas, so keep a separate source per size (tiles, props, large props, characters, portraits, icons).

```json
{"version": 1, "name": "props", "canvas": [16, 16], "pivot": [8, 16],
 "palette": {"o": "#20161f", "L": "#a8ea72", "G": "#62c24c", "D": "#3a9142", "K": "#245e33"},
 "frames": [{"name": "bush", "duration_ms": 100, "rows": ["................", "...", "..oooooooooooo.."]}]}
```

Render a sheet with `scripts/pixel_art.py render SOURCE --out DIR`. Other tools take a single frame as `source.json#frame-name`.

For large organic shapes such as tree canopies, it is fine to block the forms with a short script: clump circles, per-clump light crescent, a checker-dither band between light and mid, a dark underside. Save the result as a grid source and hand-fix the pixels that look mechanical.

## Quality bar

An asset is ready when all of these hold:

- The silhouette reads at 1× with no color.
- Every material has a planned ramp (one base and one shade can be enough at 16 px, three or more tones for larger art), and shadows are hue-shifted rather than only darker.
- The outer outline is continuous, with no single-pixel gaps or stair-step jaggies along curves.
- Light direction is the same on every asset in the scene.
- No orphan pixels or noise. Texture comes from intentional clusters: pebbles, blades, planks, shingles.
- Props sit into the ground by 2–4 px, and cast a shadow where the style uses them.
- Pixel density matches its neighbours: no mixed scales, no smooth gradients, no anti-aliased edges against transparency.

## Tiles and scenes

Backgrounds are assembled from tiles on a grid, not painted as one image. Paths and shores turn at right angles; curves come from tiles drawn with the curve inside them.

A side-view terrain set needs:

| Piece | Role |
|---|---|
| `top` (2–3 variants) | Grass cap with a dark lip, blades and a shadow row on the dirt below |
| `top_left`, `top_right` | Rounded outer corners with the side outline |
| `left`, `right` | Exposed side walls |
| `fill` (with rare variants) | Dirt; a stone or root variant used about one tile in eight |
| `platform` left / mid / right | A one-row floating ledge with a rounded underside |
| water `top` / `fill` | Foam crest and waves, then a calm fill |

Background layers are tiles too: sky bands, cloud left / mid / right, far mountains (slope, peak, fill) in pale cool tones, nearer hills, a tree-line top and fill. Distant layers get lower contrast, cooler color and no outline; foreground props keep the strongest outlines.

Assemble with `scripts/tilemap.py` (see [environments.md](environments.md#assemble-hand-made-tilesets)). Mirror pieces with `flip` rather than drawing both sides. List several variants for `top` and `fill` so repeats break up.

## Characters

Match the character style to the brief and the tile size: the figure should sit on the same grid and use the same outline and palette as the world. Draw in this order: silhouette, line, color, face last.

- **Canvas:** pick it from the tiles. A 16×16 figure fills one tile; a 16×24 or 16×32 figure stands taller than a tile. Keep the head large enough to read at 1×.
- **Silhouette:** check the shape in one flat color before adding detail. Headgear, hair and a held item are what make figures tell apart; give each character something that changes the outline, not just the colors.
- **Line:** one outline color for the whole set. Curves step in steady runs (3-2-1), with no stray single pixels.
- **Color:** a small shared palette with one light direction. Flat fills with one shade read best at small sizes; add a highlight only where it helps the form.
- **Face:** the smaller the sprite, the less face. At 16 px tall two eye dots are enough; add a mouth or brows only when the size allows and an expression needs them.
- **Symmetry:** type front and back views as the left half and mirror them, then place the asymmetric pixels by hand.
- **Directions:** down, up and right; left mirrors right unless something is held in one hand.
- **Walk cycle:** stand, then one foot forward, then the other. Long robes can sway instead, shifting only the bottom row.

### Variants from one body

Character generators layer parts on one base body whose frames line up. Do the same by hand:

- **Palette:** change hair, cloth and skin ramps without changing keys.
- **Parts:** a hat, hood, helmet or held item drawn for every view and frame, aligned to the base, so any combination animates.

The [rpg-kit](../assets/examples/rpg-kit) example has four class figures and a merchant at 16×16.

## Enemies and actions

- **Enemy reads:** each enemy needs a silhouette that reads at a glance: the slime's dome, the bat's wing span, the goblin's ears and club, the mushroom's spotted cap, the ghost's wavy hem, the skeleton's skull and ribs. Give it one accent color for the eyes or mouth that pops against its body ramp.
- **Idle:** two frames are enough. Squash and stretch the slime, flap the bat's wings up and down, lift the goblin's club, drop the mushroom's cap one row, float the ghost one pixel up and swap its hem.
- **Hurt:** flash every non-outline pixel to one light tone and knock the body back one pixel. It is the same rule for every enemy, so it can be a transform of the idle frame.
- **Attack (three beats):**
  - Anticipation: the weapon pulls back, often one pixel higher.
  - Contact: the weapon at full reach, the body leaning in.
  - Follow-through: the weapon low and past the target.
  - Keep the feet planted so the pivot does not jump.
- **Weapons:** draw them two pixels wide, with a bright edge and a shaded side, outlined as one shape. Single-pixel diagonals with per-pixel outlines turn into a dotted line.
- **Hurt:** push the body or head back one pixel, close or squeeze the eyes, and raise the ramp one step lighter for a flash frame.
- **Canvas size:** give attack frames a wider canvas than idle frames, for example 24×16 for a 16×16 figure, and keep the body at the same position in every frame.
- **Short attacks:** at small sizes two beats can be enough: a wind-up that pulls the weapon back and a release that pushes it out. Draw the weapon behind the body on the wind-up and in front on the release.
- **Projectiles:** give fireballs, arrows and spells their own frames with a centered pivot and move them in the game, not inside the attacker's sprite. See [class-actions.json](../assets/examples/rpg-kit/class-actions.json) and [projectiles.json](../assets/examples/rpg-kit/projectiles.json).

## Buildings and large props

Draw buildings like tiles: a structure you can read, then hand-placed details.

- **Size:** a cottage fits 3×3 tiles (48×48). Place it on the grid so the door lines up with a path tile.
- **Roof:** in a 3/4 top-down view the roof is most of the height. A hip roof widens one pixel every course toward the eave. Shingle courses are three rows of fill and one darker line, with seams staggered between courses. The top course is the sunlit tone, and the right slope sits one step darker.
- **Eave:** a dark outline row, then one row of shadow color on the wall under it. This one row is what makes the roof overhang.
- **Wall:** a top beam, timber posts at the corners and centre, plaster fill shaded on the right, and a stone footing with staggered joints.
- **Details last:** door, window with a cross bar and a glint, flower box, chimney on the right slope. Keep them on whole pixels, not centred by arithmetic.
- **Variants:** a second roof color is the same rows with other roof keys. A new building type reuses the body and changes the front: an awning and a sign turn the cottage into a shop. Trees and props that stand beside a house share its outline color and light.

See [town.json](../assets/examples/world-workshop/town.json): one cottage with red and blue roofs, a shop made from the same cottage with a green roof, a striped awning and a coin sign, a well and a round tree, used by the [town map](../assets/examples/world-workshop/recipe.json).

## Effects

- Effects use few colors: white for the hot core, one or two tints for the body, and a warm or cool accent. Effects drawn over sprites usually have no outline.
- Plan three beats: appear, peak, dissipate. A slash grows along its arc, fills to full thickness, then thins from the start. A hit spark is a cross, then a starburst, then scattered particles. A heal is rising plus-shaped sparkles.
- Keep each effect on its own canvas with a centered pivot, and place it over the target.

## Portraits and expressions

Choose how to show a character up close from the brief:

- **Sprite crop:** crop the head and shoulders of a stand frame and show it at a whole zoom (2× or 3×) in a framed slot. Set `portrait_crop` on a dialogue box, or `crop` on an image, slot or list row. It always matches the sprite.
- **Enlarged sprite:** show the whole stand frame at a whole zoom in a framed panel, for a character select or equipment screen.
- **Emote bubbles:** a small speech bubble with one symbol (`!`, `?`, a heart, an anger mark, `...`) above the head shows a mood without redrawing the face.
- **Drawn portrait:** a separate bust at 32–64 px when the brief asks for one. Keep it in the sprite's palette and outline, block the forms by region, and keep the face as simple as the size allows. Repaint only the eyes, brows and mouth for expressions so the rest of the portrait does not shift. Check it at 1× next to the sprite.

## Icons

Keep 16×16 icons centred with one pixel of margin. Choose the feature that makes the object recognizable (a sword's guard, a potion's neck, a key's teeth), outline it, and give each icon a top-left highlight. Keep the light direction and outline color shared across the whole set.

## Examples

- [side-scroller](../assets/examples/side-scroller): terrain, background and prop tiles, two large trees, a hero, item and UI icons, a tile-assembled scene and a full HUD.
- [rpg-kit](../assets/examples/rpg-kit): four characters from one grid, hero attack and hurt frames, a slime, bat, goblin, mushroom, ghost and skeleton with idle, attack and hurt frames, slash, hit and heal effects, emote bubbles, and 24 icons. They are used by the [RPG interface kit](../assets/examples/interface-kit/recipe.json), including its battle screen, and by the [town map](../assets/examples/world-workshop/recipe.json).
