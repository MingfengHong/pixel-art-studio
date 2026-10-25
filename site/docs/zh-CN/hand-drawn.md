# 手绘像素

发布级的游戏美术要逐像素绘制。这个 Skill 让助手把每个最终用到的精灵、瓦片、头像和图标都写成可编辑的网格，再用工具渲染、拼装和检查。

@shots examples/side-scroller/hud/screens/hud.png|由手绘瓦片拼成的横版场景，带完整 HUD

## 向助手提需求

> 用 pixel-art-studio 画一套 16x16 横版草地平台瓦片：草地顶面、拐角、侧壁、带石块变体的泥土填充、浮空平台、水面、云和远山。再拼一个带道具和主角的示例关卡。

## 工作流程

1. **画布：** 瓦片和图标 16x16，角色 16x16 到 16x32，大型道具 32x48，头像 32-64 px。
2. **先定调色板：** 每种材质 3-5 个色阶，阴影偏紫或偏蓝，亮部偏黄。
3. **剪影：** 先用基础色填满形状，确认原尺寸下能看清。
4. **按体块上色：** 光从左上方来，每一团（叶团、发绺、衣褶）分别打亮和压暗。
5. **描边：** 外轮廓用深色但不纯黑的描边，材质之间用更深的色阶区分。
6. **最后加细节**，再在原尺寸和 3 倍、浅色和深色背景以及场景里检查。

每组素材是一个网格源：一个字符一个像素，`.` 表示透明。

```json
{"version": 1, "name": "props", "canvas": [16, 16],
 "palette": {"o": "#20161f", "L": "#a8ea72", "G": "#62c24c", "D": "#3a9142"},
 "frames": [{"name": "bush", "duration_ms": 100, "rows": ["................", "..."]}]}
```

其他工具用 `props.json#bush` 引用其中一帧。

## 用瓦片拼，而不是整张画

背景由瓦片在网格上拼成。一套横版瓦片需要：草地顶面（2-3 个变体）、外拐角、侧壁、带少量石块变体的泥土填充、浮空平台和水面。背景也是瓦片：云、冷色远山、暖色山丘和远景树线。

@shots examples/side-scroller/sheets/tiles/preview.png|手绘瓦片集

`tilemap.py` 负责拼场景。每一层是若干行字符加一个图例，地形字符会自己选边角瓦片：

```bash
python scripts/tilemap.py assets/examples/side-scroller/scene.json --out output/meadow
```

```json
"terrain": {"#": {"top": ["ground-top", "ground-top-flowers"], "top_left": "ground-top-left",
  "top_right": {"tile": "ground-top-left", "flip": "x"}, "left": "ground-left",
  "right": {"tile": "ground-left", "flip": "x"}, "fill": ["ground-fill", "ground-fill-stone"]}}
```

道具用 `"tile": [x, y]` 站在某个格子上，用 `"seat": 3` 嵌进草里。图层上的 `objects` 让远处的精灵留在近景层后面，`parallax` 会记录下来给引擎用。

## 质量标准

- 不看颜色，原尺寸下剪影也能认出来。
- 每种材质至少三个色阶，阴影有色相偏移。
- 描边连续，没有孤立像素和噪点。
- 整个场景只有一个光源方向。
- 道具嵌入地面 2-4 px。
- 不混用像素尺寸，不用渐变，透明边缘不抗锯齿。

## 学习参考，而不是照抄

研究参考图为什么好看：剪影清楚、层次分明、色阶协调、道具密集但有用意。然后设计自己的瓦片、布局、配色和文字。这里的示例学习了明亮的手机平台游戏和经典 RPG，但没有复用它们的边框、布局或文字。

包括角色、头像和图标在内的完整方法见 [hand-authoring.md]({{repo}}/blob/main/skills/pixel-art-studio/references/hand-authoring.md)。
