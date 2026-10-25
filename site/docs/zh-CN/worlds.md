# 地图与地形

有两种工具可以搭建游戏世界。`tilemap.py` 把手绘瓦片集按网格拼起来，用于最终美术；`world.py` 程序化生成俯视地形，用于快速布局和背景。

@shots examples/world-workshop/scene.png|俯视小镇：程序地形、手绘房屋树木与角色, examples/side-scroller/scene/scene.png|由手绘瓦片拼成的横版场景

## 向助手提需求

> 用 pixel-art-studio 在 16 px 网格上搭一个俯视小镇：一条主路、两栋房子、一片草药田和一个池塘。放上主角和三个村民，并给我地图数据。

## 手绘瓦片集：tilemap.py

```bash
python scripts/tilemap.py assets/examples/side-scroller/scene.json --out output/meadow
```

| 配方字段 | 用途 |
|---|---|
| `tilesets` | 网格源、图集 JSON 或 PNG，其中的帧会成为可按名字引用的瓦片和精灵 |
| `size`、`tile_size` | 地图的格数和瓦片的像素尺寸 |
| `background` | 一种颜色，或分段色带（天空渐变） |
| `layers[].rows` + `legend` | 每格一个字符，对应一个瓦片、一组变体，或 `{"tile", "flip"}` |
| `layers[].terrain` | 自动拼边：横版规则选顶面、拐角、侧壁和填充；`"rule": "mask"` 按四邻接选，用于俯视瓦片 |
| `layers[].objects`、`parallax` | 位于该图层深度的精灵，以及该层的视差系数 |
| `objects` | 道具和角色：`tile`、`seat`、`dx`、`z`、`shadow` |

输出 `scene.png`、每层一张 PNG、记录每层瓦片名和物件位置的 `map.json`，以及可移植的 `source.json`。一套瓦片需要哪些部件，见[手绘像素](hand-drawn.html)。

## 程序地形：world.py

```bash
python scripts/world.py assets/examples/world-workshop/recipe.json --out output/town
```

```json
{
  "name": "river-town",
  "tile_size": 16,
  "seed": 5,
  "map": [
    "gggggggggggggggggggg",
    "pppppppppppppppppppp",
    "ggfffgggggppgggwwwgg"
  ],
  "objects": [
    {"source": "town.json#house-red", "at": [176, 32], "depth": -8},
    {"source": "../rpg-kit/warrior.json#down-stand", "at": [144, 88], "shadow": true}
  ],
  "scatter": [{"source": "../side-scroller/props.json#flowers", "count": 6, "on": "g"}]
}
```

| 格子 | 地形 |
|---|---|
| `g` | 草地，四种变体：草簇、草丛、小花、卵石 |
| `p` | 泥土小路，草会长到它开放的边上 |
| `f` | 带垄沟的耕地 |
| `w` | 水面：北侧是泥土岸，其他岸边有波纹 |

- **瓦片命名：** `grass-0` 到 `grass-3`，以及 `path-NN`、`farm-NN`、`water-NN`。`NN` 是邻接掩码：北 1、东 2、南 4、西 8。
- **外观与复现：** `palette` 可覆盖材质色阶，`seed` 让结果可复现。
- **物件：** 支持 PNG 或 `set.json#frame`，按底边排序，可投射 `shadow`。`scatter` 会把副本随机撒到格子上。
- **附加：** 可选的 `platform` 和 `isometric` 行分别生成横版地形和等距地块。

## 输出文件

| 文件 | 内容 |
|---|---|
| `scene.png`、`ground.png` | 合成后的地图，以及单独的地面层 |
| `tiles/*.png`、`atlas.png`、`atlas.json` | 所有生成的瓦片 |
| `map.json` | 瓦片名、图层和物件位置 |
| `source.json`、`inputs/` | 附带图片副本的可移植配方 |

瓦片规则、建筑与视差背景见 [environments.md]({{repo}}/blob/main/skills/pixel-art-studio/references/environments.md)。
