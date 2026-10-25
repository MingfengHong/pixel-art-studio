# 快速上手

Pixel Art Studio 是一个 Agent Skill：一个包含说明、指南和本地工具的文件夹，当你提出像素画需求时，编程助手会自动加载它。安装一次，之后用自然语言描述想要的素材即可。

## 安装

Skill 本体是仓库中的 `skills/pixel-art-studio` 文件夹。以下每种方式都会把整个文件夹放到助手读取技能的位置。

### 让助手帮你安装

把这句话发给你的编程助手：

```text
请阅读以下安装说明并帮我安装 Pixel Art Studio：https://github.com/MingfengHong/pixel-art-studio/blob/main/INSTALL.md
```

[INSTALL.md]({{repo}}/blob/main/INSTALL.md) 会告诉助手如何找到自己对应的目录、完成安装、用冒烟测试验证并汇报结果。安装 Python 依赖或替换已有安装前会先询问。

### 任意助手

社区工具 [skills CLI](https://github.com/vercel-labs/skills)（需要 Node.js 22.20+）会识别本机的助手并安装到对应目录：

```bash
npx skills add MingfengHong/pixel-art-studio
```

加 `-g` 安装到用户级目录；加 `-a claude-code`、`-a codex`、`-a gemini-cli` 等指定目标。

### Claude Code

在 Claude Code 中运行：

```text
/plugin marketplace add MingfengHong/pixel-art-studio
/plugin install pixel-art-studio@pixel-art-studio
```

也可以把文件夹复制到 `~/.claude/skills/`（所有项目）或 `.claude/skills/`（单个项目）。

### Codex、Gemini CLI 与 GitHub Copilot

三者都会读取 `~/.agents/skills/`：

```bash
git clone https://github.com/MingfengHong/pixel-art-studio.git
cp -R pixel-art-studio/skills/pixel-art-studio ~/.agents/skills/
```

Gemini CLI 也可以直接从 Git 安装：

```bash
gemini skills install https://github.com/MingfengHong/pixel-art-studio.git --path skills/pixel-art-studio
```

### Claude.ai 与 Claude Desktop

下载 [pixel-art-studio.skill]({{url}}pixel-art-studio.skill)，开启代码执行，然后在 **Customize → Skills** 中上传。

### 其他助手

| 助手 | 用户级目录 | 项目级目录 |
|---|---|---|
| Cursor | `~/.cursor/skills/` | `.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |

## 提出需求

大多数助手在你提出像素画需求时会自动加载 Skill。也可以显式调用：Claude Code 中用 `/pixel-art-studio`，Codex 中用 `$pixel-art-studio`，其他助手在请求中提到 "pixel-art-studio" 即可。

> 用 pixel-art-studio 做六个 24×24 背包图标：提灯、钥匙、药水、面包、指南针和钱袋。采用我提供的调色板和一像素描边，交付可编辑源文件与 PNG 图集。

> 这是我游戏的截图。用 pixel-art-studio 画三个新敌人，配色、描边和比例与截图保持一致。

助手会先确定视觉方向，完成一个代表性小样，再扩展成组素材，并在原生尺寸和整数倍放大下检查。

## 交付内容

- **可编辑源文件**：像素网格、配方，或附带输入文件的可移植 `source.json`。
- **原生 PNG 或图集**，以及放大预览。
- **元数据**：动画的帧时长与锚点、地图的摆放与图层、界面的九宫格边距与状态。

## 本地工具

附带的工具需要 Python 3.10+ 和 Pillow。在 Skill 文件夹中安装一次：

```bash
python -m pip install -r requirements.txt
```

这些工具离线运行，不需要任何账号。没有 Python 时，助手仍可用自身的图像工具制作，并说明跳过了哪些检查。接入 [PixelLab](generation.html) 是可选的。

## 下一步

选择一个工作流：[角色](characters.html)、[游戏界面](ui-kit.html)、[地图与地形](worlds.html)、[动画](animation.html)、[图像编辑](image-editing.html)或[像素网格与导出](pixel-grids.html)。
