# 动画

动画工具有两种用法：导入已有的帧序列，或用关键帧驱动分层剪纸动画。位置会对齐到整像素，动作始终清晰。

@shots examples/layered-animation/preview.gif|由两个图层组成的挥剑动作, examples/rpg-kit/sheets/slash.gif|手绘刀光特效, examples/rpg-kit/sheets/spark.gif|命中火花

## 向助手提需求

> 用 pixel-art-studio 为我的 16×16 冒险者做一段挥剑动作。剑保持为独立图层，循环播放，导出帧、时序和 GIF。

## 自己运行

```bash
python scripts/animate.py assets/examples/layered-animation/recipe.json --out output/attack
```

## 分层关键帧

```json
{
  "name": "layered-attack",
  "canvas": [48, 48],
  "pivot": [24, 38],
  "frame_count": 12,
  "duration_ms": 80,
  "loop": true,
  "layers": [
    {"id": "body", "source": "atlas.png", "rect": [0, 17, 16, 16], "pivot": [8, 16],
     "keys": [{"time": 0, "x": 24, "y": 34}, {"time": 0.4, "x": 24, "y": 32}, {"time": 1, "x": 24, "y": 34}]},
    {"id": "blade", "parent": "body", "source": "weapon.png", "pivot": [3, 13],
     "keys": [{"time": 0, "x": 5, "y": -5, "angle": -15}, {"time": 0.55, "x": 7, "y": -5, "angle": -70}, {"time": 1, "x": 5, "y": -5, "angle": -15}]}
  ]
}
```

| 字段 | 用途 |
|---|---|
| `id`、`source`、`rect` | 图层及其图片区域 |
| `pivot` | 裁剪后图片内的旋转锚点 |
| `parent` | 前面的某个图层；子图层随它移动和旋转 |
| `keys` | `time`（0–1）以及 `x`、`y`、`angle`（角度）和 `opacity`（0–1） |
| `keys[].source` | 从该关键帧起把图层换成另一张图或 `set.json#frame` |
| `hold` | 在关键帧上设为 `true`，保持到下一个关键帧 |

关键帧之间线性插值。循环动画的首尾姿态应一致，并在画布上为挥动的肢体留出空间。

## 播放一个技能

图层可以在任意关键帧换帧，所以一份配方就能用手绘帧演出完整技能：法师切换到施法姿势，火球飞过去，然后在史莱姆身上依次播放闪光、火环和烟雾。

@shots examples/skill-cast/preview.gif|火球术：施法、飞行、爆炸

```bash
python scripts/animate.py assets/examples/skill-cast/recipe.json --out output/fireball
```

## 导入帧序列

序列配方列出帧而不是图层。每帧包含图片 `source`、可选 `rect`、目标位置 `at` 和 `duration_ms`，以及共用的 `canvas`、`pivot`、`loop`。可用于导入现有精灵图或生成的帧。

## 输出文件

@shots examples/layered-animation/preview.png|挥剑动作全部帧的拼图

| 文件 | 内容 |
|---|---|
| `frames/*.png` | 按顺序排列、带透明度的原生帧 |
| `atlas.png`、`atlas.json` | 打包后的帧 |
| `animation.json` | 时序、锚点和循环设置 |
| `preview.png`、`preview.gif` | 拼图与播放预览 |
| `source.json`、`inputs/` | 可移植配方 |

帧规划、特效与节奏建议见 [animation-and-fx.md]({{repo}}/blob/main/skills/pixel-art-studio/references/animation-and-fx.md)。
