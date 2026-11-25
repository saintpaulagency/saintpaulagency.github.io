// node check.js page.html name : load at 1440 light and 390 dark, report errors, calc errors, blank figures, overflow; screenshot
const { chromium } = require('playwright');
(async () => {
  const [file, name] = process.argv.slice(2);
  const b = await chromium.launch(); let bad = 0;
  for (const [w, scheme] of [[1440, 'light'], [390, 'dark']]) {
    const p = await b.newPage({ viewport: { width: w, height: 900 }, colorScheme: scheme });
    const errs = []; p.on('pageerror', e => errs.push(e.message)); p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    await p.goto('file://' + require('path').resolve(file)); await p.waitForTimeout(3500);
    const r = await p.evaluate(() => {
      const blanks = [...document.querySelectorAll('[data-source]')].filter(e => e.offsetParent && /^\s*[—–-]\s*$/.test(e.textContent)).map(e => e.dataset.source + '.' + (e.dataset.field || ''));
      const tabs = [...document.querySelectorAll('[role=tab],.tab,button[data-tab]')].map(t => t.textContent.trim()).filter(Boolean).slice(0, 12);
      return { drawn: !!window.__drawn, calc: window.__calcErrors || [], blanks: blanks.slice(0, 10), nBlank: blanks.length, figures: document.querySelectorAll('[data-source]').length,
        overflow: document.documentElement.scrollWidth - innerWidth, tabs, through: (window.__DASH_BUILT || {}).through };
    });
    await p.screenshot({ path: `out/${name}-${w}.png` });
    const ok = r.drawn && !r.calc.length && !errs.length && r.overflow <= 1;
    if (!ok) bad++;
    console.log(`${ok ? 'OK  ' : 'FAIL'} ${name} ${w}/${scheme} drawn=${r.drawn} figures=${r.figures} blanks=${r.nBlank} ${r.blanks.join(',')} overflow=${r.overflow} calc=${r.calc.join('|')} errs=${errs.slice(0,3).join('|')} through=${r.through} tabs=${r.tabs.join('/')}`);
    await p.close();
  }
  await b.close(); process.exit(bad ? 1 : 0);
})();
