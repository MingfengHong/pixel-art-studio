# Getting started

Pixel Art Studio is an Agent Skill: a folder of instructions, guides and local tools that your coding agent loads when you ask for pixel art. Install it once, then describe what you want in plain language.

## Install

The skill is the folder `skills/pixel-art-studio` in the repository. Every method below puts that whole folder where your agent looks for skills.

### Let your agent do it

Paste this into your coding agent:

```text
Please read the install instructions at https://github.com/MingfengHong/pixel-art-studio/blob/main/INSTALL.md and install Pixel Art Studio for me.
```

[INSTALL.md]({{repo}}/blob/main/INSTALL.md) tells the agent how to find the right folder for itself, install, verify with a smoke test, and report back. It asks before installing Python packages or replacing an existing copy.

### Any agent

The community [skills CLI](https://github.com/vercel-labs/skills) (Node.js 22.20+) detects your agents and installs into the right folder:

```bash
npx skills add MingfengHong/pixel-art-studio
```

Add `-g` to install for your user, or `-a claude-code`, `-a codex`, `-a gemini-cli` and so on to pick a target.

### Claude Code

Inside Claude Code:

```text
/plugin marketplace add MingfengHong/pixel-art-studio
/plugin install pixel-art-studio@pixel-art-studio
```

Or copy the folder into `~/.claude/skills/` (all projects) or `.claude/skills/` (one project).

### Codex, Gemini CLI and GitHub Copilot

All three read `~/.agents/skills/`:

```bash
git clone https://github.com/MingfengHong/pixel-art-studio.git
cp -R pixel-art-studio/skills/pixel-art-studio ~/.agents/skills/
```

Gemini CLI can also install straight from Git:

```bash
gemini skills install https://github.com/MingfengHong/pixel-art-studio.git --path skills/pixel-art-studio
```

### Claude.ai and Claude Desktop

Download [pixel-art-studio.skill]({{url}}pixel-art-studio.skill), turn on code execution, and upload the file under **Customize → Skills**.

### Other agents

| Agent | User folder | Project folder |
|---|---|---|
| Cursor | `~/.cursor/skills/` | `.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |

## Ask for art

Most agents load the skill automatically when you ask for pixel art. You can also call it by name: `/pixel-art-studio` in Claude Code, `$pixel-art-studio` in Codex, or mention "pixel-art-studio" elsewhere.

> Use pixel-art-studio to create six 24×24 inventory icons: a lantern, key, potion, bread, compass and pouch. Use my palette and a one-pixel outline. Deliver editable sources and a PNG atlas.

> Here is a screenshot of my game. Use pixel-art-studio to draw three new enemies that match its palette, outline and proportions.

The agent sets the visual direction, makes one representative sample, extends the set, and checks it at native size and integer zoom.

## What you get back

- **Editable sources**: a pixel grid, recipe, or portable `source.json` with its inputs.
- **Native PNGs or an atlas**, plus a zoomed preview.
- **Metadata**: frame timing and pivots for animation, placement and layers for maps, slice insets and states for UI.

## Local tools

The bundled tools need Python 3.10+ and Pillow. Install once from the skill folder:

```bash
python -m pip install -r requirements.txt
```

They run offline and never need an account. Without Python, the agent can still work with its own image tools and will say which checks it skipped. Connecting [PixelLab](generation.html) is optional.

## Next steps

Pick a workflow: [characters](characters.html), [game UI](ui-kit.html), [worlds](worlds.html), [animation](animation.html), [image editing](image-editing.html) or [pixel grids and export](pixel-grids.html).
