# 像素网格与导出

对于小而精确的精灵和图标，助手会直接把像素写成文本网格。`pixel_art.py` 负责渲染网格、把 PNG 转回网格、制作参考拼图，以及自动检查图片。

@shots examples/beacon/preview.png|两种姿态的 8×8 信标, examples/ui-components/preview.png|小型界面控件, examples/tile-scene/preview.png|用瓦片拼成的小屋

## 网格格式

```json
{
  "version": 1,
  "name": "outline-free-beacon",
  "canvas": [8, 8],
  "pivot": [4, 8],
  "palette": {"a": "#f2edd7", "b": "#8fb9a8", "c": "#3a6b73"},
  "frames": [
    {"name": "rest", "duration_ms": 400, "rows": [
      "........", "...bb...", "..baab..", ".baaaab.",
      "..baab..", "...cc...", "..cccc..", "........"]}
  ]
}
```

调色板的每个键是一个字符；`.` 表示透明。每帧都有唯一的 `name`、正数 `duration_ms`，以及与像素行数一致的行。`pivot` 默认为底部中点。

## 命令

在 Skill 文件夹中运行：

```bash
python scripts/pixel_art.py render assets/examples/beacon/source.json --out output/beacon --scale 8
```

| 目标 | 命令 |
|---|---|
| 把网格渲染为图集、元数据和预览 | `pixel_art.py render SOURCE --out DIR [--scale] [--columns] [--padding]` |
| 把 PNG 转为可编辑网格 | `pixel_art.py from-png IMAGE.png OUT.json` |
| 制作带标注的参考拼图 | `pixel_art.py sheet A.png B.png --out SHEET.png` |
| 检查尺寸、颜色、透明度或放大倍数 | `pixel_art.py inspect IMAGE.png [--size W H] [--max-colors N] [--binary-alpha] [--palette FILE] [--scale N]` |

`inspect` 匹配时返回 0，不匹配返回 1，输入错误返回 2，助手可以把它当作自动检查。

## 图集元数据

`atlas.json`（格式 `pixel-art-studio-atlas-v1`）列出图片、原生画布、间距和按顺序排列的帧。每帧包含 `name`、`rect: [x, y, width, height]`、`duration_ms` 和 `pivot`。UI、地图与动画工具使用以帧名为键的打包变体。

导入引擎时，把每个 `rect` 和 `pivot` 映射到引擎的精灵导入器，使用最近邻过滤和整数缩放。如果渲染器会对纹理做过滤，请给图集加间距或外扩。

## 像素规范

- 只用一套逻辑网格，不要混用像素密度，也不要按小数倍缩放。
- 在原生尺寸和整数倍放大下，分别在深浅背景上检查每个素材。
- 色块要干净，避免噪点；作为眼睛、高光或星星的单个像素没有问题。

制作要点见 [style-and-quality.md]({{repo}}/blob/main/skills/pixel-art-studio/references/style-and-quality.md)；全部命令与格式细节见 [tools-and-export.md]({{repo}}/blob/main/skills/pixel-art-studio/references/tools-and-export.md)。
