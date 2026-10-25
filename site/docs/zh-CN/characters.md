# 角色

角色生成器根据一份简短配方生成小型动画角色：四或八个方向、站立／待机／行走姿态、可编辑像素网格、PNG 图集和 GIF 预览。

@shots examples/characters/adventurer/walk.gif|冒险者的八方向行走, examples/characters/researcher/walk.gif|研究员的四方向行走

## 手绘 RPG 角色

最终美术里的角色要手绘成网格源。RPG 套件包含四个 16x16 职业角色：[战士]({{repo}}/blob/main/skills/pixel-art-studio/assets/examples/rpg-kit/warrior.json)、法师、召唤师和射手，另有一个商人。每个角色有朝下、朝上、朝右三个方向（朝左由朝右镜像），各含站立和两帧行走。

@shots examples/rpg-kit/sheets/warrior/walk.gif|战士, examples/rpg-kit/sheets/mage/walk.gif|法师, examples/rpg-kit/sheets/summoner/walk.gif|召唤师, examples/rpg-kit/sheets/archer/walk.gif|射手

每个职业都有两拍攻击动作，法术和箭是单独的投射物帧：

@shots examples/rpg-kit/sheets/warrior-attack.gif|战士突刺, examples/rpg-kit/sheets/archer-shoot.gif|射手放箭, examples/rpg-kit/sheets/mage-cast.gif|法师施法, examples/rpg-kit/sheets/summoner-cast.gif|召唤师施法, examples/rpg-kit/sheets/fireball.gif|火球, examples/rpg-kit/sheets/wisp.gif|灵火

界面直接复用精灵：头像是头肩部分的裁切，角色选择界面把站立帧放大展示。

@shots examples/interface-kit/screens/select.png|角色选择

## 敌人、动作与特效

RPG 套件还手绘了战斗素材：
- **敌人：** 史莱姆、蝙蝠、哥布林、蘑菇、幽灵和骷髅，各有待机循环、攻击或受击闪白。
- **特效：** 刀光、命中火花和治疗。

@shots examples/rpg-kit/sheets/goblin-attack.gif|哥布林挥棒, examples/rpg-kit/sheets/slime.gif|史莱姆待机, examples/rpg-kit/sheets/bat.gif|蝙蝠振翅, examples/rpg-kit/sheets/enemies/preview.png|蘑菇、幽灵和骷髅

表情气泡（感叹、疑问、爱心、生气、省略号、音符、灵感）可以放在任意角色头顶。

@shots examples/rpg-kit/sheets/emotes/preview.png|表情气泡

本页其余部分介绍角色生成器：用配方快速生成风格统一的 16×16 角色。

## 向助手提需求

> 用 pixel-art-studio 制作一个 16×16 的店主，长发、围裙、戴眼镜。四个方向，包含待机和行走动画，交付可编辑帧与 PNG 图集。

助手会复制一份初始配方，设置配色和部件，运行生成器，再在生成的网格中细化表情或装备。

## 自己运行

在 Skill 文件夹中：

```bash
python scripts/character.py assets/examples/characters/researcher/recipe.json --out output/researcher
```

`--scale` 设置预览放大倍数（默认 6）。图集始终保留原生 16×16 帧。

## 配方

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

| 字段 | 用途 |
|---|---|
| `name` | 源文件和图集中的角色名 |
| `directions` | `4`（默认）或 `8` |
| `parts` | 有序列表，可选 `long-hair`、`glasses`、`beard`、`cap`、`coat`、`apron`；靠后的部件画在上层 |
| `colors` | 按材质角色设置的十六进制颜色；未设置的角色沿用模板配色 |
| `timing_ms` | `stand`、`idle`、`step` 的时长 |
| `template` | 可选的自定义模板，路径相对于配方 |

配色角色：`ink`、`hair`、`hair_shadow`、`skin`、`skin_shadow`、`eyes`、`top`、`top_shadow`、`pants`、`pants_shadow`、`shoes`、`glint`、`cap`、`cap_shadow`、`apron`、`apron_shadow`。外套使用 top 的颜色。眼镜应排在头发和帽子之后。

## 输出文件

@shots examples/characters/researcher/preview.png|研究员全部姿态的拼图

| 文件 | 内容 |
|---|---|
| `source.json` | 每个姿态的可编辑像素网格 |
| `atlas.png`、`atlas.json` | 透明原生帧，含矩形、时长和 `[8,16]` 脚底锚点 |
| `animations.json` | 循环动画；行走顺序为 `walk-a → stand → walk-b → stand` |
| `preview.png` | 带标注的拼图 |
| `idle.gif`、`walk.gif` | 各方向在棋盘格背景上的播放预览 |

## 八方向

设置 `"directions": 8` 可得到 32 个姿态，顺序为正面、右前、右、右后、背面、左后、左、左前。斜向视角有独立绘制的网格；朝左的视角镜像自朝右。参见[冒险者配方]({{repo}}/blob/main/skills/pixel-art-studio/assets/examples/characters/adventurer/recipe.json)。

## 技巧

- 镜像会翻转持械方向、徽章和不对称服装。在生成的 `source.json` 中修正后，用 `scripts/pixel_art.py render` 重新渲染。
- 每次迭代使用单独的输出目录；重新生成会覆盖文件。
- 如需其他比例，请同时修改模板的网格、叠加层、动作和锚点。完整说明见 [sprites.md]({{repo}}/blob/main/skills/pixel-art-studio/references/sprites.md)。
