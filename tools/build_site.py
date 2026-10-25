"""Build the bilingual project site into _site/: home page, docs, the UI playground and the packaged skill."""
import html
import json
from pathlib import Path
import re
import shutil
import sys

import markdown
from markdown.extensions.toc import slugify_unicode
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "pixel-art-studio"
SRC = ROOT / "site"
OUT = ROOT / "_site"
sys.path.insert(0, str(SKILL / "scripts"))
sys.path.insert(0, str(ROOT / "tools"))
import ui
import art_common
import package_skill

CONFIG = json.loads((SRC / "site.json").read_text(encoding="utf-8"))
LANGS = CONFIG["languages"]
FONTS = ["https://cdn.jsdelivr.net/npm/@fontsource/fusion-pixel-12px-proportional-sc@5.3.0/index.css",
         "https://cdn.jsdelivr.net/npm/@fontsource/fusion-pixel-12px-monospaced-sc@5.3.0/index.css"]


def esc(value):
    return html.escape(str(value), quote=True)


def expand(value):
    return value.replace("{repo}", CONFIG["repo"]).replace("{url}", CONFIG["url"])


def href(value, root):
    """Config links: absolute and anchor links stay as they are; others are relative to the language root."""
    value = expand(value)
    return value if value.startswith(("http://", "https://", "#")) else root + value


def link(item, root, cls=""):
    target = href(item["href"], root)
    external = ' target="_blank" rel="noopener"' if target.startswith("http") else ""
    return f'<a{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} href="{esc(target)}"{external}>{esc(item["label"])}</a>'


class Page:
    """One output file: knows its language, its path inside the language, and the relative way back to the site root."""

    def __init__(self, lang, rel):
        self.lang, self.rel = lang, rel
        self.path = LANGS[lang]["prefix"] + rel
        self.root = "../" * self.path.count("/")          # to the site root
        self.home = self.root + LANGS[lang]["prefix"]     # to this language's root
        self.text = CONFIG["text"][lang]

    def url(self):
        return CONFIG["url"] + self.path.removesuffix("index.html")

    def layout(self, title, description, body, kind, current=""):
        t, nav = self.text, self.text["nav"]
        on_home = kind == "home"
        anchor = lambda name: f"#{name}" if on_home else f"{self.home}index.html#{name}"
        items = [(anchor("playground"), nav["playground"], ""), (anchor("features"), nav["features"], ""),
                 (anchor("examples"), nav["examples"], ""),
                 (f"{self.home}docs/getting-started.html", nav["docs"], "docs" if kind == "docs" else ""),
                 (CONFIG["repo"], nav["github"], "")]
        nav_html = "".join(
            f'<a href="{esc(h)}"{" aria-current=" + chr(34) + "page" + chr(34) if c else ""}'
            f'{" target=" + chr(34) + "_blank" + chr(34) + " rel=" + chr(34) + "noopener" + chr(34) if h.startswith("http") else ""}>{esc(label)}</a>'
            for h, label, c in items)
        switch = "".join(
            f'<a class="btn small" hreflang="{lang}" lang="{lang}" href="{esc(self.root + info["prefix"] + self.rel)}"'
            f'{" aria-current=" + chr(34) + "true" + chr(34) if lang == self.lang else ""}>{esc(info["label"])}</a>'
            for lang, info in LANGS.items())
        alternates = "".join(
            f'<link rel="alternate" hreflang="{lang}" href="{esc(CONFIG["url"] + info["prefix"] + self.rel.removesuffix("index.html"))}">'
            for lang, info in LANGS.items())
        footer = t["footer"]
        favicon = f"{self.root}assets/favicon.png"
        return f"""<!doctype html>
<html lang="{self.lang}"{' class="home"' if on_home else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(self.url())}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{esc(self.url())}">
<meta property="og:image" content="{esc(CONFIG['url'])}examples/interface-kit/preview.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{favicon}">
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
{"".join(f'<link rel="stylesheet" href="{font}">' for font in FONTS)}
<link rel="stylesheet" href="{self.root}assets/style.css">
</head>
<body>
<a class="skip" href="#main">{esc(t['skip'])}</a>
<header class="topbar"><div class="wrap">
<a class="brand" href="{self.home}index.html"><img src="{favicon}" width="32" height="32" alt=""><span>{esc(t['site_title'])}</span></a>
<nav class="nav" aria-label="Site">{nav_html}</nav>
<div class="lang" role="group" aria-label="Language">{switch}</div>
</div></header>
<main id="main">
{body}
</main>
<footer><div class="wrap">
<div class="about"><a class="brand" href="{self.home}index.html"><img src="{favicon}" width="32" height="32" alt=""><span>{esc(t['site_title'])}</span></a><p>{esc(footer['about'])}</p></div>
<nav class="links" aria-label="Footer">{''.join(link(l, self.home) for l in footer['links'])}</nav>
<p class="fine">{esc(footer['fine'])}</p>
</div></footer>
<script src="{self.root}assets/site.js"></script>
</body>
</html>
"""


def sprite(path, root, box):
    """An <img> for a small sprite, enlarged by the largest whole number that fits a box of this size.

    `path` is a PNG under the skill's assets or "set.json#frame"; frames are exported to assets/icons/.
    """
    im = art_common.load_image(SKILL / "assets", path)
    if "#" in path:
        name = path.replace("/", "-").replace(".json#", "-").replace("#", "-") + ".png"
        (OUT / "assets" / "icons").mkdir(parents=True, exist_ok=True)
        im.save(OUT / "assets" / "icons" / name)
        path = f"assets/icons/{name}"
    else:
        path = path
    w, h = im.size
    k = max(1, box // max(w, h))
    return f'<img src="{root}{path}" alt="" width="{w * k}" height="{h * k}">'


def home(lang):
    page = Page(lang, "index.html")
    t = page.text
    hero, pg, feats, ex = t["hero"], t["playground"], t["features"], t["examples"]
    icons = "".join(sprite(f"examples/rpg-kit/items.json#{name}", page.root, 48)
                    for name in ("sword", "shield", "potion", "mana", "key", "coin"))
    words = hero["title"].split(" ")
    title = esc(" ".join(words[:-1])) + f' <span class="hi">{esc(words[-1])}</span>'
    actions = "".join(link(a, page.home, "btn primary" if a.get("primary") else "btn") for a in hero["actions"])
    install = json.dumps([{**i, "code": expand(i["code"])} for i in t["install"]], ensure_ascii=False).replace("<", "\\u003c")
    playground = f"{page.root}playground/index.html"
    features = "".join(
        f'<a class="card frame" href="{page.home}docs/{f["doc"]}.html"><div class="art">{sprite(f["icon"], page.root, 48)}</div>'
        f'<h3>{esc(f["title"])}</h3><p>{esc(f["text"])}</p><span class="more">{esc(feats["more"])} &rarr;</span></a>'
        for f in feats["items"])
    examples = "".join(
        f'<a class="frame" href="{page.home}docs/{e["doc"]}.html"><div class="shot"><img src="{page.root}{e["src"]}" alt="{esc(e["title"])}" loading="lazy"></div>'
        f'<div class="cap"><h3>{esc(e["title"])}</h3><p>{esc(e["text"])}</p></div></a>'
        for e in ex["items"])
    body = f"""<section class="screen" id="top"><div class="wrap hero">
  <div>
    <div class="icons" aria-hidden="true">{icons}</div>
    <span class="eyebrow">{esc(hero['eyebrow'])}</span>
    <h1>{title}</h1>
    <p class="tagline">{esc(hero['tagline'])}</p>
    <p class="lede">{esc(hero['lede'])}</p>
    <div class="actions">{actions}</div>
  </div>
  <div class="frame terminal" id="install">
    <div class="bar"><i></i><i></i><i></i><span>{esc(t['install_title'])}</span></div>
    <div class="term-tabs" role="tablist" aria-label="{esc(t['install_title'])}"></div>
    <div class="code sunken"><pre><code></code></pre></div>
    <p class="term-note"></p>
    <script type="application/json">{install}</script>
  </div>
</div></section>
<section class="screen" id="playground"><div class="wrap fill">
  <div class="head"><h2>{esc(pg['title'])}</h2><p>{esc(pg['intro'])}</p></div>
  <div class="frame embed"><iframe src="{playground}?embed=1&amp;lang={lang}" title="{esc(pg['title'])}" loading="lazy"></iframe></div>
  <div class="under"><a href="{playground}?lang={lang}" target="_blank" rel="noopener">{esc(pg['open'])}</a><a href="{page.home}docs/ui-kit.html">{esc(pg['learn'])}</a><a href="{CONFIG['repo']}/blob/main/skills/pixel-art-studio/assets/examples/interface-kit/recipe.json" target="_blank" rel="noopener">{esc(pg['recipe'])}</a></div>
</div></section>
<section class="screen" id="features"><div class="wrap">
  <div class="head"><h2>{esc(feats['title'])}</h2><p>{esc(feats['intro'])}</p></div>
  <div class="grid">{features}</div>
</div></section>
<section class="screen" id="examples"><div class="wrap fill">
  <div class="head"><h2>{esc(ex['title'])}</h2><p>{esc(ex['intro'])}</p></div>
  <div class="grid gallery">{examples}</div>
</div></section>"""
    title_text = f"{hero['title']} - {hero['tagline']}"
    return page, page.layout(title_text, t["description"], body, "home")


def shots(match, root):
    items = []
    # Items are "path|alt" pairs; split only before the next path so alt text may contain commas.
    for item in re.split(r",\s*(?=examples/)", match.group(1)):
        path, _, alt = item.partition("|")
        items.append(f'<div class="shot frame sunken"><img src="{root}{path.strip()}" alt="{esc(alt.strip())}" loading="lazy"></div>')
    return '\n<div class="shotrow">' + "".join(items) + "</div>\n"


def doc(lang, slug, index):
    page = Page(lang, f"docs/{slug}.html")
    t = page.text
    source = (SRC / "docs" / lang / f"{slug}.md").read_text(encoding="utf-8")
    title, _, text = source.partition("\n")
    title = title.removeprefix("# ").strip()
    text = (text.replace("{{root}}", page.root).replace("{{lang}}", lang)
                .replace("{{repo}}", CONFIG["repo"]).replace("{{url}}", CONFIG["url"]))
    text = re.sub(r"^@shots (.+)$", lambda m: shots(m, page.root), text, flags=re.M)
    content = markdown.markdown(text, extensions=["tables", "fenced_code", "toc"],
                                extension_configs={"toc": {"slugify": slugify_unicode}})
    content = content.replace("<p>", '<p class="lead">', 1)
    titles = [doc_title(lang, s) for s in CONFIG["docs"]]
    sidebar = "".join(
        f'<li><a href="{s}.html"{" aria-current=" + chr(34) + "page" + chr(34) if s == slug else ""}>{esc(titles[i])}</a></li>'
        for i, s in enumerate(CONFIG["docs"]))
    pager = ""
    if index > 0:
        prev = CONFIG["docs"][index - 1]
        pager += f'<a class="btn" href="{prev}.html">&larr; {esc(titles[index - 1])}</a>'
    if index < len(CONFIG["docs"]) - 1:
        nxt = CONFIG["docs"][index + 1]
        pager += f'<a class="btn" href="{nxt}.html" style="margin-left:auto">{esc(titles[index + 1])} &rarr;</a>'
    edit = f'{CONFIG["repo"]}/blob/main/site/docs/{lang}/{slug}.md'
    body = f"""<div class="wrap docs">
<aside class="sidebar frame"><h2>{esc(t['docs_heading'])}</h2><ol>{sidebar}</ol></aside>
<article class="doc"><h1>{esc(title)}</h1>
{content}
<nav class="pager" aria-label="{esc(t['docs_title'])}">{pager}</nav>
<p class="edit"><a href="{edit}" target="_blank" rel="noopener">{esc(t['edit'])}</a></p>
</article>
</div>"""
    lead = re.sub(r"<[^>]+>", "", content.split("</p>", 1)[0])
    return page, page.layout(f"{title} - {t['site_title']}", html.unescape(lead)[:300], body, "docs", slug)


def doc_title(lang, slug):
    return (SRC / "docs" / lang / f"{slug}.md").read_text(encoding="utf-8").partition("\n")[0].removeprefix("# ").strip()


def write(page, content):
    dest = OUT / page.path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


def main():
    # Empty the folder rather than deleting it, so a local server running inside it keeps working.
    OUT.mkdir(exist_ok=True)
    for path in OUT.iterdir():
        shutil.rmtree(path) if path.is_dir() else path.unlink()
    shutil.copytree(SKILL / "assets" / "examples", OUT / "examples")
    shutil.copytree(SRC / "assets", OUT / "assets")
    # Favicon: the hand-drawn hero's head.
    art_common.load_image(SKILL / "assets", "examples/rpg-kit/mage.json#down-stand").resize((32, 32), 0).save(OUT / "assets" / "favicon.png")
    ui.generate(SKILL / "assets" / "examples" / "interface-kit" / "recipe.json", OUT / "playground")
    shutil.copy2(OUT / "playground" / "preview.html", OUT / "playground" / "index.html")
    for lang in LANGS:
        write(*home(lang))
        for index, slug in enumerate(CONFIG["docs"]):
            write(*doc(lang, slug, index))
        redirect = Page(lang, "docs/index.html")
        write(redirect, f'<!doctype html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=getting-started.html">'
                        f'<link rel="canonical" href="{CONFIG["url"]}{redirect.path.removesuffix("index.html")}getting-started.html">')
    (OUT / ".nojekyll").touch()
    package_skill.main()
    shutil.copy2(ROOT / "dist" / "pixel-art-studio.skill", OUT / "pixel-art-studio.skill")
    pages = sum(1 for _ in OUT.rglob("*.html"))
    print(f"Site written to {OUT} ({pages} HTML files)")


if __name__ == "__main__":
    main()
