# Install Pixel Art Studio: instructions for AI agents

> **For people:** you don't need to follow these steps yourself. Paste one line into your coding agent:
>
> ```text
> Please read the install instructions at https://github.com/MingfengHong/pixel-art-studio/blob/main/INSTALL.md and install Pixel Art Studio for me.
> ```
>
> 中文：`请阅读以下安装说明并帮我安装 Pixel Art Studio：https://github.com/MingfengHong/pixel-art-studio/blob/main/INSTALL.md`

You are an AI coding agent. The user asked you to install **Pixel Art Studio**, an Agent Skill for making pixel art sprites, tilesets, scenes, game UI and animation. Follow this runbook from top to bottom.

## What this request covers

The user's request authorizes you to:

- Copy the skill folder `skills/pixel-art-studio` from `https://github.com/MingfengHong/pixel-art-studio` into the skills directory of **the agent you are running in**.
- Download the repository into a temporary folder to do that, and delete the temporary folder afterwards.
- Run the read-only checks and the smoke test in step 5.

It does **not** cover the following. Ask first, or leave them out:

- Installing for other agents on this machine. Mention them if you see them; install only if the user says so.
- Installing Python packages. Step 4 says when to ask.
- Overwriting an existing `pixel-art-studio` folder that the user didn't ask you to update.
- Using `sudo`, changing permissions, editing agent settings, or touching shell profiles.
- Anything related to PixelLab. It is optional; never install `requirements-pixellab.txt` or ask for a PixelLab token as part of installation.

## Language

Reply in the language the user wrote in. Keep commands, paths and identifiers unchanged.

## Step 1: Identify your host and the target folder

Install for the agent that is reading this file. Use the **user** folder unless the user asked for this project only, in which case use the **project** folder at the repository root of the current workspace.

| You are running in | User folder | Project folder |
|---|---|---|
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| Codex | `~/.agents/skills/` | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/` | `.gemini/skills/` or `.agents/skills/` |
| GitHub Copilot (CLI, VS Code, cloud agent) | `~/.copilot/skills/` or `~/.agents/skills/` | `.github/skills/` or `.agents/skills/` |
| Cursor | `~/.cursor/skills/` | `.agents/skills/` |
| OpenCode | `~/.config/opencode/skills/` | `.opencode/skills/` or `.agents/skills/` |
| Windsurf | `~/.codeium/windsurf/skills/` | `.windsurf/skills/` |
| Cline | `~/.agents/skills/` | `.agents/skills/` |

- `~` is the user's home directory (`$HOME`, or `%USERPROFILE%` on Windows).
- If you are sure of your host but it isn't listed, use the skills directory from your own documentation.
- If you cannot tell which host you are, or the table and your documentation disagree, ask the user before writing anything.
- **Claude.ai or Claude Desktop chat** cannot install from a shell. Tell the user to download `https://mingfenghong.github.io/pixel-art-studio/pixel-art-studio.skill`, turn on code execution, and upload the file under **Customize → Skills**. Then stop.

The final layout must be `<skills folder>/pixel-art-studio/SKILL.md`, with the whole folder (scripts, references, assets) next to it.

## Step 2: Check for an existing install

If `<skills folder>/pixel-art-studio/SKILL.md` already exists, Pixel Art Studio is already installed there.

- If the user asked to install or update, say that you will replace the existing copy with the latest one, then continue.
- Otherwise tell the user it is already installed and ask whether to replace it with the latest copy. Stop until they answer.

When updating, replace the folder as a whole rather than merging, so removed files do not linger.

## Step 3: Install

Pick the variant that matches the user's shell. Replace `TARGET` with the folder from step 1. Each variant downloads into a temporary folder, copies the skill, and cleans up.

**macOS, Linux, WSL, Git Bash (needs `git`):**

```bash
TARGET="$HOME/.claude/skills"   # replace with the folder from step 1
TMP="$(mktemp -d)"
git clone --depth 1 https://github.com/MingfengHong/pixel-art-studio.git "$TMP/pixel-art-studio"
mkdir -p "$TARGET"
rm -rf "$TARGET/pixel-art-studio"
cp -R "$TMP/pixel-art-studio/skills/pixel-art-studio" "$TARGET/"
rm -rf "$TMP"
```

**Windows PowerShell (needs `git`):**

```powershell
$Target = Join-Path $HOME '.claude\skills'   # replace with the folder from step 1
$Tmp = Join-Path ([IO.Path]::GetTempPath()) ("pixel-art-studio-" + [guid]::NewGuid())
git clone --depth 1 https://github.com/MingfengHong/pixel-art-studio.git (Join-Path $Tmp 'repo')
New-Item -ItemType Directory -Force -Path $Target | Out-Null
$Dest = Join-Path $Target 'pixel-art-studio'
if (Test-Path $Dest) { Remove-Item -LiteralPath $Dest -Recurse -Force }
Copy-Item -LiteralPath (Join-Path $Tmp 'repo\skills\pixel-art-studio') -Destination $Target -Recurse
Remove-Item -LiteralPath $Tmp -Recurse -Force
```

**Without `git`:** download `https://github.com/MingfengHong/pixel-art-studio/archive/refs/heads/main.zip` into the temporary folder (`curl -L -o` or `Invoke-WebRequest -OutFile`), extract it, and copy `pixel-art-studio-main/skills/pixel-art-studio` the same way.

Only remove `"$TARGET/pixel-art-studio"` (or `$Dest`), never the parent skills folder. Do not modify the copied files.

## Step 4: Python helpers (optional)

The skill's local tools need Python 3.10+ and Pillow. Check without changing anything:

```bash
python --version
python -c "import PIL; print(PIL.__version__)"
```

Use `python3` if `python` is missing or older.

- **Both present:** nothing to do.
- **Pillow missing:** ask the user whether to install it, unless they already asked for a full install. If they agree, run `python -m pip install -r "<skills folder>/pixel-art-studio/requirements.txt"`. If pip refuses because the environment is externally managed, report that and suggest a virtual environment or `pipx`; do not add `--break-system-packages` on your own.
- **Python missing or older than 3.10:** tell the user. The skill still works through the agent's own image tools, without the local renderer and checks.

## Step 5: Verify

1. Confirm that `<skills folder>/pixel-art-studio/SKILL.md` exists and that its front matter contains `name: pixel-art-studio`.
2. If Python and Pillow are available, render a bundled example into a temporary folder, check that `atlas.png` was written, then delete the temporary folder:

   ```bash
   python "<skills folder>/pixel-art-studio/scripts/pixel_art.py" render "<skills folder>/pixel-art-studio/assets/examples/beacon/source.json" --out "<temporary folder>/beacon"
   ```

3. Most hosts load new skills only in a new session. Do not claim the skill is active in the current session unless your host shows that it is.

## Step 6: Report to the user

Keep the report short:

- Where the skill was installed.
- Python status: ready, Pillow missing, or Python unavailable.
- Whether a new session or restart is needed.
- How to use it: ask for pixel art in plain language, or invoke it by name (`/pixel-art-studio` in Claude Code, `$pixel-art-studio` in Codex). One example prompt: "Use pixel-art-studio to make six 24×24 inventory icons with a one-pixel outline."
- Docs: `https://mingfenghong.github.io/pixel-art-studio/`

If any step failed, report the exact command and error, say what is left undone, and do not describe the installation as complete.

## Update and uninstall

- **Update:** run step 3 again; it replaces the folder.
- **Uninstall:** delete `<skills folder>/pixel-art-studio`, and nothing else.
