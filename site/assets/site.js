// Pixel Art Studio site: language memory, install tabs, copy buttons, crisp image scaling.
(() => {
  const KEY = 'pixel-art-studio-lang';
  const lang = document.documentElement.lang;
  const store = {
    get() { try { return localStorage.getItem(KEY); } catch { return null; } },
    set(value) { try { localStorage.setItem(KEY, value); } catch {} },
  };
  const t = (en, zh) => (lang.startsWith('zh') ? zh : en);

  // Remember an explicit language choice; on a first visit to the English home page, follow the browser.
  for (const link of document.querySelectorAll('.lang a')) link.addEventListener('click', () => store.set(link.hreflang));
  const home = document.documentElement.classList.contains('home');
  if (home && lang === 'en' && !store.get() && /^zh\b/i.test(navigator.language || '')) {
    const zh = document.querySelector('.lang a[hreflang^="zh"]');
    if (zh) location.replace(zh.href);
  }

  // Copy buttons on every code block.
  function addCopy(box) {
    const pre = box.querySelector('pre');
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'btn small copy';
    button.textContent = t('Copy', '复制');
    button.addEventListener('click', async () => {
      const text = box.dataset.code ?? pre.innerText.replace(/^\$ /gm, '');
      try { await navigator.clipboard.writeText(text.trimEnd()); button.textContent = t('Copied!', '已复制！'); }
      catch { button.textContent = t('Select & copy', '请手动复制'); }
      setTimeout(() => { button.textContent = t('Copy', '复制'); }, 1600);
    });
    box.append(button);
  }
  for (const pre of document.querySelectorAll('.doc pre')) {
    const box = document.createElement('div');
    box.className = 'code frame sunken';
    pre.replaceWith(box);
    box.append(pre);
    addCopy(box);
  }

  // Install tabs on the home page.
  const terminal = document.querySelector('.terminal');
  if (terminal) {
    const items = JSON.parse(terminal.querySelector('script[type="application/json"]').textContent);
    const tabs = terminal.querySelector('.term-tabs');
    const box = terminal.querySelector('.code');
    const code = box.querySelector('code');
    const note = terminal.querySelector('.term-note');
    const buttons = [];
    const pick = (i) => {
      buttons.forEach((b, j) => { b.setAttribute('aria-selected', i === j); b.tabIndex = i === j ? 0 : -1; });
      code.replaceChildren();
      items[i].code.split('\n').forEach((line, n) => {
        if (n) code.append('\n');
        if (!items[i].plain && !line.startsWith('/')) { const s = document.createElement('span'); s.className = 'prompt'; s.textContent = '$ '; code.append(s); }
        code.append(line);
      });
      box.dataset.code = items[i].code;
      code.parentElement.style.whiteSpace = items[i].plain ? 'pre-wrap' : 'pre';
      note.textContent = items[i].note || '';
    };
    items.forEach((item, i) => {
      const b = document.createElement('button');
      b.type = 'button'; b.className = 'btn'; b.setAttribute('role', 'tab'); b.textContent = item.label;
      b.addEventListener('click', () => pick(i));
      b.addEventListener('keydown', (e) => {
        if (e.key !== 'ArrowRight' && e.key !== 'ArrowLeft') return;
        e.preventDefault();
        const n = (i + (e.key === 'ArrowRight' ? 1 : -1) + items.length) % items.length;
        pick(n); buttons[n].focus();
      });
      buttons.push(b); tabs.append(b);
    });
    addCopy(box);
    pick(0);
  }

  // Scale pixel art by whole numbers so every pixel stays square; shrink smoothly only when it cannot fit.
  function crisp() {
    for (const img of document.querySelectorAll('.shot img')) {
      if (!img.naturalWidth) continue;
      const box = img.parentElement, style = getComputedStyle(box);
      const w = box.clientWidth - parseFloat(style.paddingLeft) - parseFloat(style.paddingRight);
      const fixed = box.closest('.gallery');
      const h = fixed ? box.clientHeight - parseFloat(style.paddingTop) - parseFloat(style.paddingBottom) : Infinity;
      const s = Math.min(w / img.naturalWidth, h / img.naturalHeight, Number(img.dataset.max || 4));
      img.style.width = (s >= 1 ? Math.floor(s) : s) * img.naturalWidth + 'px';
    }
  }
  for (const img of document.querySelectorAll('.shot img')) img.addEventListener('load', crisp);
  addEventListener('resize', crisp);
  crisp();
})();
