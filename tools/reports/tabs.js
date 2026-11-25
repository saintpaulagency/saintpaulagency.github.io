const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  for (const name of process.argv.slice(2)) {
    const p = await b.newPage({ viewport: { width: 1280, height: 900 } }); const errs = [];
    p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + require('path').resolve('out/' + name + '.html')); await p.waitForTimeout(2500);
    const tabs = await p.$$('[role=tab]'); const seen = [];
    for (const t of tabs) { seen.push((await t.textContent()).trim()); await t.click(); await p.waitForTimeout(900); }
    const r = await p.evaluate(() => ({ calc: window.__calcErrors || [], blanks: [...document.querySelectorAll('[data-source]')].filter(e => e.offsetParent && /^\s*[—–-]\s*$/.test(e.textContent)).length, svg: document.querySelectorAll('svg').length }));
    console.log((errs.length || r.calc.length ? 'FAIL ' : 'OK   ') + name, 'tabs:', seen.join('/'), 'svgs', r.svg, 'blanks(last tab)', r.blanks, errs.slice(0, 3).join('|'), r.calc.join('|'));
    await p.close();
  }
  await b.close();
})();
