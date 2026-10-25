# 图像编辑

图像工具对源图按顺序执行一组像素级精确的操作：去背景、换色、调色板、描边、蒙版补图、缩放和画布调整。

@shots examples/image-editing/preview.png|药水编辑前后对比, examples/potion-variants/preview.png|同一药水的三种配色

## 向助手提需求

> 用 pixel-art-studio 把这瓶灰色药水改成紫色魔法药水：去掉纯色背景，加深色描边和一个小闪光。

## 自己运行

```bash
python scripts/image_ops.py assets/examples/image-editing/recipe.json --out output/potion-edit
```

## 配方

```json
{
  "name": "enchanted-potion",
  "source": "input.png",
  "operations": [
    {"op": "remove-background", "color": "#efe3c8"},
    {"op": "recolor", "map": {"#c0cbdc": "#e1a1ef", "#8b9bb4": "#9f61c1"}},
    {"op": "outline", "color": "#3d244f", "width": 1},
    {"op": "extend", "size": [32, 32], "at": [4, 4]},
    {"op": "patch", "source": "spark.png", "at": [24, 3]},
    {"op": "reduce-colors", "colors": 12}
  ]
}
```

## 操作

| 操作 | 字段 | 作用 |
|---|---|---|
| `resize` | `size` 或整数 `factor` | 最近邻缩放 |
| `pixelate` | 原生 `size`，可选 `keep_size` | 平均到较粗的网格 |
| `crop` | `rect` | 裁出一个区域 |
| `mirror` | `axis` 为 `x` 或 `y` | 翻转 |
| `rotate` | `degrees` | 在扩大的画布上旋转 |
| `remove-background` | `color`、`tolerance`、`connected` | 去除与边缘相连的匹配色，或全部匹配色 |
| `recolor` | `map` | 精确替换颜色 |
| `palette` | `colors` | 匹配到调色板，保留透明度 |
| `reduce-colors` | `colors` | 量化到指定颜色数 |
| `outline` | `width`、`color` | 在画布内描边 |
| `patch` | `source`、`at`、`mask`、`replace` | 合成补丁；蒙版亮度决定透明度 |
| `extend` | `size`、`at`、`color` 或 `tile` | 扩展画布 |

## 输出文件

`image.png`、编辑前后对比的 `preview.png`，以及附带输入文件的可移植 `source.json`。把该源文件输出到新目录即可保留之前的版本。

## 技巧

- 描边前先扩展画布，给描边留出空间。
- 按材质换色：全局替换可能误伤颜色相同的其他像素。
- 换装、局部重绘等语义编辑请参考[参考图与生成](generation.html)，再用 `patch` 合成结果。

完整说明见 [image-editing.md]({{repo}}/blob/main/skills/pixel-art-studio/references/image-editing.md)。
