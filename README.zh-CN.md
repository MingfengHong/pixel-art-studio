<div align="center">
  <h1>
    <img src="site/assets/logo.png" width="420" alt="Pixel Art Studio">
  </h1>
  <p><strong>让你的编程助手制作像素角色、瓦片场景与游戏界面。</strong></p>
  <h3><a href="https://mingfenghong.github.io/pixel-art-studio/">🌐 项目主页：文档与在线演示 →</a></h3>
  <p>
    <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
    <a href="https://agentskills.io/specification"><img alt="Agent Skills" src="https://img.shields.io/badge/format-Agent%20Skills-8a2be2.svg"></a>
    <a href="skills/pixel-art-studio/requirements.txt"><img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776ab.svg"></a>
    <a href="THIRD_PARTY_NOTICES.md"><img alt="References: CC0" src="https://img.shields.io/badge/references-CC0-lightgrey.svg"></a>
    <a href="https://mingfenghong.github.io/pixel-art-studio/"><img alt="Live demo" src="https://img.shields.io/badge/demo-live-79ceb3.svg"></a>
  </p>
  <p>
    <a href="https://mingfenghong.github.io/pixel-art-studio/">项目主页</a> ·
    <a href="#安装">安装</a> ·
    <a href="#使用">使用</a> ·
    <a href="skills/pixel-art-studio/references/few-shots.md">示例</a> ·
    <a href="skills/pixel-art-studio/SKILL.md">SKILL.md</a> ·
    <a href="README.md">English</a>
  </p>
</div>

---

描述想制作的素材，提供参考图或调色板，即可获得可编辑源文件和清晰的 PNG 产物。Pixel Art Studio 是一个 [Agent Skill](https://agentskills.io)，它把剪影、配色、构图、动画帧和导出串成一套制作流程，让整组素材风格统一。支持 Claude Code、Codex、Gemini CLI、GitHub Copilot、Cursor、OpenCode，以及其他能读取 `SKILL.md` 文件夹的助手。

![带完整 HUD 的手绘横版场景](skills/pixel-art-studio/assets/examples/side-scroller/hud/screens/hud.png)

## 目录

- [可以制作什么](#可以制作什么)
- [安装](#安装)
- [使用](#使用)
- [手绘像素](#手绘像素)
- [制作 UI 套件](#制作-ui-套件)
- [生成角色](#生成角色)
- [地图、图像编辑与动画](#地图图像编辑与动画)
- [示例](#示例)
- [工作原理](#工作原理)
- [仓库结构](#仓库结构)
- [参与贡献](#参与贡献)
- [致谢与许可](#致谢与许可)

## 可以制作什么

| 类型 | 素材 |
|---|---|
| 角色 | 带行走与攻击动作的手绘职业角色、敌人、头像、表情气泡，以及四／八方向生成角色 |
| 道具与图标 | 工具、食物、家具、任务物品、背包图标 |
| 场景 | 按网格拼接的手绘瓦片集（自动选边角、视差分层）、程序生成的俯视地形、等距地块 |
| 游戏界面 | HUD、状态条、快捷栏、列表、商店、NPC 对话框、昼夜表盘、菜单与提示，三种边框风格 |
| 动画与特效 | 帧序列导入、父子图层、关键帧、剪纸式姿态、飘字与 GIF |
| 图像编辑 | 换色、减色、去除纯色背景、蒙版补图、缩放、扩展画布 |
| 参考驱动制作 | 通过助手自带的图像工具完成文字／风格／概念参考、语义编辑、角色转向与动作生成（PixelLab 可选） |

可以指定参考图、调色板、画布尺寸和绘画风格。Skill 会结合像素网格、现有素材、像素编辑器以及助手自带的图像工具完成制作。全部功能均在本地运行，无需注册账号、API 密钥或联网。

## 安装

Skill 本体是 [`skills/pixel-art-studio`](skills/pixel-art-studio) 文件夹。以下每种方式都是把**整个文件夹**（而不仅是 `SKILL.md`）放到助手读取技能的位置。

### 让助手帮你安装

把下面这句话发给 Claude Code、Codex、Gemini CLI、Copilot、Cursor 或其他编程助手：

```text
请阅读以下安装说明并帮我安装 Pixel Art Studio：https://github.com/MingfengHong/pixel-art-studio/blob/main/INSTALL.md
```

[INSTALL.md](INSTALL.md) 是写给助手的安装手册：它会识别当前助手、把 Skill 复制到正确目录、检查 Python、运行冒烟测试并汇报结果。安装 Python 依赖或覆盖已有安装前会先询问，也不会配置 PixelLab。

### 快速安装（适用于各类助手）

社区工具 [`skills` CLI](https://github.com/vercel-labs/skills)（需要 Node.js 22.20+）会识别本机的助手并安装到对应目录：

```bash
npx skills add MingfengHong/pixel-art-studio
```

加 `-g` 安装到用户级目录（默认安装到当前项目），加 `-a <agent>` 指定目标，例如 `-a claude-code`、`-a codex`、`-a gemini-cli`、`-a github-copilot`、`-a cursor`、`-a opencode`。

### Claude Code

**方式 A：插件市场。** 在 Claude Code 中运行：

```text
/plugin marketplace add MingfengHong/pixel-art-studio
/plugin install pixel-art-studio@pixel-art-studio
```

之后可用 `/plugin marketplace update pixel-art-studio` 更新。

**方式 B：复制文件夹。** 放入 `~/.claude/skills/` 对所有项目生效；放入项目内的 `.claude/skills/` 可随仓库共享给团队：

```bash
git clone https://github.com/MingfengHong/pixel-art-studio.git
mkdir -p ~/.claude/skills
cp -R pixel-art-studio/skills/pixel-art-studio ~/.claude/skills/
```

新开一个会话，问一句"有哪些可用的 Skill？"确认已加载。

### Claude.ai 与 Claude Desktop

1. 从[最新 Release](https://github.com/MingfengHong/pixel-art-studio/releases/latest) 下载 `pixel-art-studio.skill`，或运行 `python tools/package_skill.py` 自行打包。该文件就是 ZIP 压缩包，如上传界面要求 `.zip`，改扩展名即可。
2. 确认已开启代码执行，然后打开 **Customize → Skills**（部分版本为 **Settings → Capabilities**）上传文件。

Claude.ai 的自定义 Skill 仅对上传者本人生效，且需要支持代码执行的套餐。

### Codex

Codex 读取用户级目录 `~/.agents/skills/` 和仓库内的 `.agents/skills/`：

```bash
git clone https://github.com/MingfengHong/pixel-art-studio.git
mkdir -p ~/.agents/skills
cp -R pixel-art-studio/skills/pixel-art-studio ~/.agents/skills/
```

也可以让 Codex 通过内置的安装 Skill 完成：

```text
$skill-installer install https://github.com/MingfengHong/pixel-art-studio/tree/main/skills/pixel-art-studio
```

如果没有出现，重启 Codex 即可。

### Gemini CLI

```bash
gemini skills install https://github.com/MingfengHong/pixel-art-studio.git --path skills/pixel-art-studio
```

加 `--scope workspace` 安装到当前项目。Gemini CLI 也会读取 `~/.gemini/skills/` 和 `~/.agents/skills/`，所以为 Codex 复制的那份同样可用。用 `/skills list` 检查。

### GitHub Copilot

复制到 `~/.copilot/skills/`（或 `~/.agents/skills/`）对当前用户生效，或复制到仓库的 `.github/skills/`。Copilot CLI、VS Code 智能体模式和 Copilot 云端智能体都会读取这些位置。

### Cursor、OpenCode、Windsurf 及其他助手

将文件夹复制到对应助手的技能目录。常见位置如下：

| 助手 | 用户级目录 | 项目级目录 |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` 或 `~/.agents/skills/` | `.gemini/skills/` 或 `.agents/skills/` |
| GitHub Copilot | `~/.copilot/skills/` 或 `~/.agents/skills/` | `.github/skills/` 或 `.agents/skills/` |
| Cursor | `~/.cursor/skills/` | `.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` 或 `.agents/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |

各助手的目录约定可能随版本变化；如果某个路径无效，请查阅该助手的文档，或改用 `npx skills add`。

**Windows（PowerShell）**：将目标目录替换为所用助手的目录：

```powershell
git clone https://github.com/MingfengHong/pixel-art-studio.git
$dest = Join-Path $HOME '.claude/skills'
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Copy-Item -LiteralPath 'pixel-art-studio/skills/pixel-art-studio' -Destination $dest -Recurse -Force
```

### Python 辅助工具（可选）

本地制作工具需要 Python 3.10+ 和 [Pillow](https://python-pillow.org)。在已安装的 Skill 文件夹中执行一次：

```bash
python -m pip install -r requirements.txt
```

没有 Python 时，助手仍可用自身的图像工具制作素材，并会说明跳过了哪些检查。

### PixelLab（可选）

PixelLab 不是必需的。以上所有功能都无需 PixelLab 即可使用；除非你主动要求，Skill 不会连接 PixelLab，也不会向你索要令牌。

如果你本身在用 [PixelLab](https://www.pixellab.ai)，希望助手调用它来生成素材，可以在助手中接入 PixelLab 的 MCP 服务，或者安装附带客户端的额外依赖，并在环境变量中设置令牌：

```bash
python -m pip install -r requirements-pixellab.txt
export PIXELLAB_API_KEY=...   # PowerShell：$env:PIXELLAB_API_KEY = '...'
```

之后在请求中明确提到 PixelLab，例如"用 PixelLab 生成……"。助手在发起会消耗额度的调用前会先向你确认。详见 [PixelLab 说明](skills/pixel-art-studio/references/production-workflows.md#optional-pixellab-connection)。

### 更新与卸载

复制安装的：删除技能目录下的 `pixel-art-studio` 文件夹，再复制最新的文件夹。用 `skills` CLI 安装的：重新运行 `npx skills add MingfengHong/pixel-art-studio`。Claude Code 插件：使用 `/plugin marketplace update pixel-art-studio` 或 `/plugin uninstall pixel-art-studio@pixel-art-studio`。

## 使用

大多数助手在你提出像素画需求时会自动加载这个 Skill。如需显式调用：

| 助手 | 调用方式 |
|---|---|
| Claude Code | `/pixel-art-studio`（复制安装）或 `/pixel-art-studio:pixel-art-studio`（插件安装） |
| Codex | `$pixel-art-studio` |
| Gemini CLI、Copilot 等 | 在请求中提到 "pixel-art-studio" |

**背包图标**

> 用 pixel-art-studio 做六个 24×24 背包图标：提灯、钥匙、药水、面包、指南针和钱袋。采用我提供的调色板和一像素描边，交付可编辑源文件与 PNG 图集。

**多方向角色**

> 用 pixel-art-studio 制作一个 16×16 研究员，戴眼镜、留长发、穿浅色外套。包含正面、背面、左侧、右侧，以及待机和行走动画，交付可编辑帧与 PNG 图集。

**村落场景**

> 用 pixel-art-studio 制作一个河边小村落，包含两栋房屋、一座桥和土路。交付可编辑的分层布局与 PNG 预览。

**游戏界面**

> 用 pixel-art-studio 制作一套暗黑奇幻风格的 HUD，包含血条、蓝条、经验条和小地图，以及带滑块和开关的设置菜单。交付各状态 PNG、九宫格皮肤和可交互预览。

**匹配现有风格**

> 这是我游戏的截图。用 pixel-art-studio 画三个新敌人，配色、描边和比例与截图保持一致。

助手会先确定视觉方向，完成一个代表性小样，再扩展成组素材，并在原生尺寸和整数倍放大下打磨细节。常见交付包括可编辑源文件、PNG 或精灵图集、预览，以及帧信息或布局数据。

## 手绘像素

最终的游戏美术要逐像素绘制。这个 Skill 让助手把瓦片、精灵、头像和图标写成可编辑的网格源，再用工具拼装和检查。背景由瓦片在网格上拼成，而不是整张画出来。

![带完整 HUD 的横版场景](skills/pixel-art-studio/assets/examples/side-scroller/hud/screens/hud.png)

```bash
python skills/pixel-art-studio/scripts/tilemap.py skills/pixel-art-studio/assets/examples/side-scroller/scene.json --out output/meadow
```

- **[横版示例](skills/pixel-art-studio/assets/examples/side-scroller)：** 手绘的地形与背景瓦片、大树、道具、主角和图标。`tilemap.py` 自动选边角并分视差层拼出场景，`ui.py` 再叠上完整 HUD。
- **[RPG 套件](skills/pixel-art-studio/assets/examples/rpg-kit)：** 战士、法师、召唤师、射手四个 16×16 职业角色和一个商人，带行走循环；职业攻击动作与火球、箭、灵火投射物，一段火球术技能动画；带攻击或受击帧的史莱姆、蝙蝠、哥布林、蘑菇、幽灵和骷髅；刀光、命中和治疗特效，表情气泡，以及 24 个道具图标。头像直接裁切角色精灵。
- **[手绘指南](skills/pixel-art-studio/references/hand-authoring.md)：** 工作流程、质量标准、瓦片结构、角色、头像与图标。

![小镇里的 RPG 对话](skills/pixel-art-studio/assets/examples/interface-kit/screens/dialogue.png)

## 制作 UI 套件

在仓库根目录运行，即可生成一套 RPG 界面（小镇 HUD、对话、背包与装备、战斗、商店、角色选择）：

```bash
python skills/pixel-art-studio/scripts/ui.py skills/pixel-art-studio/assets/examples/interface-kit/recipe.json --out output/interface
```

用浏览器打开 `output/interface/preview.html`，或直接体验[在线演示](https://mingfenghong.github.io/pixel-art-studio/zh/#playground)。[文档站](https://mingfenghong.github.io/pixel-art-studio/zh/docs/ui-kit.html)逐一介绍了每个组件。可以选择腰带格子和商品，阅读逐字显示的对话并选择回答，滚动背包，悬停查看物品说明。

| 类别 | 包含组件 |
|---|---|
| HUD | 带标签的血条／蓝条／经验条／体力条、小地图、昼夜表盘、快捷栏 |
| 控件 | 图标按钮、上下排布按钮、圆形按钮、开关、滑块、下拉菜单 |
| 菜单 | 面板、画布、带空格的滚动视图、列表（商店、任务、属性） |
| 剧情 | 带头像、名字、打字机帧和选项的 NPC 对话框 |
| 文本与媒体 | 描边文字、带框或带格子的图片，可通过 `set.json#frame` 引用手绘帧 |
| 反馈与提示 | 弹窗、提示框、飘字 |

输出包括原生尺寸状态 PNG、独立的九宫格背景皮肤、填充层／轨道／滑块／滚动内容层、图集、布局数据和完整界面预览。修改配置中的配色、切角、尺寸、文字、数值与位置即可制作其他视觉风格。[UI 指南](skills/pixel-art-studio/references/ui.md)包含全部组件参数；中文标签可通过 `font` 指定具有相应字形和许可的字体。

## 生成角色

附带的角色生成器可以组合发型、眼镜、帽子、胡须、外套与围裙，并按材质设置配色。在仓库根目录从研究员示例开始：

```bash
python skills/pixel-art-studio/scripts/character.py skills/pixel-art-studio/assets/examples/characters/researcher/recipe.json --out output/researcher
```

一次生成**四方向共 16 个姿态帧**，并输出可编辑像素网格、透明 PNG 图集、帧与动画数据、静态预览，以及待机和行走 GIF。

设置 `"directions": 8` 可生成 32 帧，也可以使用[冒险者配置](skills/pixel-art-studio/assets/examples/characters/adventurer/recipe.json)。斜向视图采用独立绘制的网格。[查看八方向行走动画](skills/pixel-art-studio/assets/examples/characters/adventurer/walk.gif)。

![研究员的四方向行走动画](skills/pixel-art-studio/assets/examples/characters/researcher/walk.gif)

制作自己的角色时，可以将下面的配置保存为 `my-character.json`：

```json
{
  "name": "shopkeeper",
  "parts": ["long-hair", "apron", "glasses"],
  "colors": {
    "hair": "#8d5138",
    "hair_shadow": "#573529",
    "top": "#708fa2",
    "top_shadow": "#465d78",
    "apron": "#e6d6a9"
  }
}
```

将该文件传给 `character.py` 并指定输出目录即可。[角色制作指南](skills/pixel-art-studio/references/sprites.md#generate-a-directional-character)介绍了全部配色角色、部件、动作时长与模板格式。初始模板采用 16×16 画布，可以编辑网格和部件，制作其他人物比例。

## 地图、图像编辑与动画

在仓库根目录运行以下完整示例：

```bash
python skills/pixel-art-studio/scripts/world.py skills/pixel-art-studio/assets/examples/world-workshop/recipe.json --out output/world
python skills/pixel-art-studio/scripts/image_ops.py skills/pixel-art-studio/assets/examples/image-editing/recipe.json --out output/potion-edit
python skills/pixel-art-studio/scripts/animate.py skills/pixel-art-studio/assets/examples/layered-animation/recipe.json --out output/attack
```

- **地图工坊**：程序生成地面（草地变体、小路、耕地、带岸的池塘）上的俯视小镇，配手绘房屋、树木、道具和 RPG 角色。
- **图像编辑**：去除纯色背景、换色、描边、扩画布和补图；同时支持蒙版、像素化、调色板匹配、裁切与缩放。
- **动画制作**：导入现有帧序列，或用位置、旋转、透明度关键帧驱动父子图层；输出原生帧、时序与锚点、图集及 GIF。

这些工具通过 Pillow 在本地运行。自由图像生成、风格／概念参考、语义局部重绘、参考角色转向、服装迁移和动作生成，按[生成工作流](skills/pixel-art-studio/references/production-workflows.md)使用助手自带的图像工具，或在原生网格上重绘完成。这些任务也可以接入 PixelLab，但并非必需。

## 示例

[示例文件夹](skills/pixel-art-studio/assets/examples)包含源文件和渲染结果：

- **横版示例**：手绘瓦片、道具、大树和主角拼成的视差场景，带完整的手机风格 HUD。
- **RPG 套件**：四个手绘职业角色和一个商人（含行走与攻击帧）、六种敌人、投射物与特效、表情气泡和 24 个道具图标。
- **UI 套件**：RPG 小镇 HUD、对话、背包与装备、回合制战斗、商店和角色选择，带交互预览。
- **角色**：四方向研究员／巡林员与八方向冒险者，包含配色、部件和待机／行走。
- **地图工坊**：带分层物件和阴影的俯视小镇地图。
- **图像编辑**：透明背景、换色、描边与闪光补图的魔法药水。
- **分层动画**：通过父子关键帧制作可编辑的人物持剑动作。
- **技能演出**：用手绘帧在关键帧图层上演出一段火球术。
- **药水变体**：同一轮廓的三种配色。
- **瓦片场景**：使用地形、建筑与树木模块拼装的小屋场景。
- **UI 组件**：同一视觉体系的小型控件与面板。
- **信标**：三色、两帧的 8×8 发光图标。

![使用模块化像素瓦片搭建的小屋场景](skills/pixel-art-studio/assets/examples/tile-scene/preview.png)

[示例说明](skills/pixel-art-studio/references/few-shots.md)介绍了每组需求与绘制思路。也可以直接渲染附带的源文件：

```bash
python skills/pixel-art-studio/scripts/pixel_art.py render skills/pixel-art-studio/assets/examples/potion-variants/source.json --out output/potions
```

输出包含 `atlas.png`、`atlas.json` 和 `preview.png`。全部命令见[工具与文件格式](skills/pixel-art-studio/references/tools-and-export.md)。

## 工作原理

Skill 遵循 Agent Skills 的[渐进式加载](https://agentskills.io/specification#progressive-disclosure)机制：助手平时只看到简短的描述；当你提出像素画需求时才读取 [`SKILL.md`](skills/pixel-art-studio/SKILL.md)；只有任务需要时才打开对应的专题指南（角色、场景、界面、动画、图像编辑、导出）。配置式工具输出确定，通过 Pillow 在本地运行，不需要联网。自由生成使用助手自带的图像工具；可选的 PixelLab 客户端只在你配置并明确要求时使用。

## 仓库结构

```text
pixel-art-studio/
├── INSTALL.md                        写给助手的安装手册
├── .claude-plugin/marketplace.json   Claude Code 插件市场配置
├── skills/pixel-art-studio/          Skill 本体（安装这个文件夹）
│   ├── SKILL.md                      入口：工作流程与命令
│   ├── references/                   按需加载的专题指南
│   ├── scripts/                      网格、瓦片拼接、UI、角色、地图、图像与动画工具
│   │   └── pixellab.py               可选 PixelLab 客户端（其他工具不依赖它）
│   ├── assets/examples/              示例源文件与渲染结果
│   ├── assets/templates/             角色网格、交互预览模板与风格简报
│   ├── assets/kenney/                精选 CC0 参考图块
│   ├── agents/openai.yaml            Codex 展示信息
│   ├── requirements.txt              Pillow（全部本地工具）
│   └── requirements-pixellab.txt     可选 PixelLab 客户端依赖
├── .github/workflows/pages.yml      构建并部署项目主页
├── site/                             文档站源文件（首页文案、双语指南、样式）
└── tools/                            维护脚本（重建示例、打包、构建主页）
```

## 参与贡献

欢迎分享新的示例、改进绘制指南或完善制作工具。较大的改动请先提 Issue 讨论。

- 提交美术示例时，请附上简短说明、可编辑源文件和预览，并注明参考作者与素材许可。
- 保持 `SKILL.md` 简短，详细内容放在 `references/`。
- 修改脚本或源文件后，运行 `python tools/rebuild_examples.py` 重新生成示例。
- 运行 `python tools/package_skill.py` 打包可上传的归档，输出位于 `dist/pixel-art-studio.skill`。

## 致谢与许可

仓库精选了 [Kenney](https://kenney.nl/assets) 的 Tiny Dungeon、Tiny Town 和 UI Pack – Pixel Adventure 素材包中的 33 张图块。示例主要参考其紧凑剪影、清晰色块和模块化拼装方式。素材采用 **CC0**，详见[作者与来源](skills/pixel-art-studio/assets/kenney/ATTRIBUTION.md)。

Skill 遵循 [Agent Skills 规范](https://agentskills.io/specification)，组织方式参考了 [Anthropic Skills](https://github.com/anthropics/skills)、[Superpowers](https://github.com/obra/superpowers) 和 [pixel-art](https://github.com/wan-huiyan/pixel-art)。

代码与文档采用 [MIT](LICENSE) 许可。附带美术素材的许可见[第三方声明](THIRD_PARTY_NOTICES.md)。
