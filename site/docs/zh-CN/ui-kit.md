# 游戏界面

UI 工具根据一份配方生成完整的像素界面：
- 每个组件的全部状态，以及不含文字的九宫格皮肤和独立图层。
- 拼好的界面。
- 可交互的浏览器预览。

@shots examples/interface-kit/screens/battle.png|战斗界面, examples/interface-kit/preview.png|小镇 HUD、对话、背包、战斗与商店界面

可以在[界面演示]({{root}}playground/index.html?lang={{lang}})中直接试用这套 RPG 界面。

## 向助手提需求

> 用 pixel-art-studio 做一套紫底金边风格的 RPG 界面：带头像、HP/MP 条和物品腰带的小镇 HUD，带选项的 NPC 对话框，装备与背包界面、回合制战斗界面、商店，以及角色选择界面。交付各状态 PNG、九宫格皮肤和可交互预览。

## 自己运行

```bash
python scripts/ui.py assets/examples/interface-kit/recipe.json --out output/interface
```

打开 `output/interface/preview.html`。在预览页里：
- 腰带和列表可以点击，也可以按数字键选择。
- 对话框会逐字显示，点击可以显示整句并选择回答。
- 滑块、开关、下拉菜单、滚动视图、提示框、弹窗和飘字都能交互。

## 主题

`theme.style` 选择边框风格，在它之上可以覆盖任意颜色：

| 风格 | 外观 |
|---|---|
| `slate` | 斜面石板面板 |
| `wood` | 带木纹的暖色边框，内衬浅色底 |
| `arcade` | 粗描边、两像素边框、深色底 |

```json
"theme": {"style": "arcade", "frame": "#d9a94a", "frame_light": "#ffe29a", "frame_dark": "#8a5a1e",
          "surface": "#2e2547", "inset": "#1f1933", "title": "#ffd257", "select": "#7fd1c8"}
```

RPG 套件就是把 `arcade` 重新配成紫金色；[横版 HUD]({{repo}}/blob/main/skills/pixel-art-studio/assets/examples/side-scroller/hud.json) 用的是原版 `arcade`。

## 组件

| 类型 | 主要字段 | 产出 |
|---|---|---|
| `health-bar`、`mana-bar`、`xp-bar`、`stamina-bar`、`bar` | `value`、`color`、`label`、`max` | 各状态，以及轨道、填充和文字图层 |
| `button` | `label`、`icon` 或 `source`、`layout: "stack"`、`shape: "round"`、`opacity` | 六种状态和无文字皮肤 |
| `hotbar` | `slots`、`cell`、`items`、`selected` | 可选择的物品腰带 |
| `list` | `rows`：`source`、`label`、`value`、`value_icon`、`disabled` | 商店、任务日志、技能和属性列表 |
| `dialogue` | `speaker`、`text`、`portrait`、`layout`、`choices` | 打字机帧、继续箭头、选项状态 |
| `dial` | `time`、`label` | 昼夜表盘 |
| `scroll-view` | `columns`、`cell`、`items`、`slots` | 带空格的背包网格 |
| `minimap`、`panel`、`slider`、`toggle`、`switch`、`dropdown` | 常规字段 | 各状态、轨道与滑块、皮肤 |
| `image`、`sprite`、`icon`、`text`、`label` | `source`、`frame` 或 `slot`、`outline`、`align` | 带框的美术和描边文字 |
| `modal`、`tooltip`、`floating-text` | `lines`、`buttons`、`frames` | 弹窗、提示框、上浮文字 |

所有图片字段都接受 PNG 或 `set.json#frame`，手绘图标和头像可以直接接入。

## 对话框

```json
{"id": "talk", "type": "dialogue", "layout": "inset", "size": [312, 76],
 "speaker": "Bram the Trader", "portrait": "../rpg-kit/merchant.json#down-stand", "portrait_crop": [0, 0, 16, 16],
 "text": "Welcome, traveler! Fresh bread, sturdy boots and a map of the old mines. Care to take a look?",
 "choices": ["Show me your wares.", "Just passing through."]}
```

- **头像：** `portrait_crop` 从精灵中裁出头肩部分并按整数倍放大，头像永远和角色一致。
- **版式：** `"inset"` 把头像放在框内左侧，名字做成框顶上方的标签；默认的 `"panel"` 版式让头像单独一个面板，下方带名牌。
- **文字：** 每页两到三行，每行 35-50 个字符。文字会自动换行；一页放不下时工具会报错提示。
- **打字机：** 速度由 `typing_frames` × `duration_ms` 决定。点击会显示整句，闪烁的箭头表示“继续”。

## 文字与多语言

内置 5x7 字体有比例宽度的大小写和下行字母。中文或其他文字请设置有授权的 TTF/OTF `font` 及其原生 `font_size`。添加 `locales` 可以在预览中翻译界面名称和说明。

## 输出文件

| 文件 | 内容 |
|---|---|
| `components/<id>/*.png`、`layer-*.png` | 每个状态和图层 |
| `atlas.png`、`atlas.json` | 带名称的状态矩形 |
| `ui.json` | 类型、状态、标签、图层、九宫格、格子和行矩形、布局 |
| `screens/*.png`、`preview.png`、`catalog.png` | 拼好的界面与总览 |
| `preview.html` | 可交互演示 |
| `source.json`、`inputs/` | 可移植配方；引用的帧会存成 PNG |

完整组件说明和 HUD 布局建议见 [ui.md]({{repo}}/blob/main/skills/pixel-art-studio/references/ui.md)。
