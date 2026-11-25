(function () {
  // Stand-in for the Claude dashboard runtime: connector loaders (answers embedded), file datasets, calcs, draw targets.
  const files = window.__DASH_FILES, answers = window.__DASH_ANSWERS, loaders = {}, calcs = {}, draws = {}, cache = {}, cbs = [];
  window.__calcErrors = [];
  const run = (id, f) => { try { cache[id] = { status: 'ok', data: f() }; } catch (e) { window.__calcErrors.push(id + ': ' + e.message); cache[id] = { status: 'error', message: String(e) }; } return cache[id]; };
  function render() {
    Object.keys(draws).forEach((n) => document.querySelectorAll('[data-draw="' + n + '"]').forEach((el) => { try { draws[n](el); } catch (e) { window.__calcErrors.push('draw ' + n + ': ' + e.message); } }));
    cbs.forEach((f) => { try { f(); } catch (e) { window.__calcErrors.push('onData: ' + e.message); } });
    window.__drawn = true;
  }
  window.dash = {
    loader(id, o) { loaders[id] = o; },
    calc(id, o) { calcs[id] = o; },
    draw(name, fn) { draws[name] = fn; },
    data(id) {
      if (cache[id]) return cache[id];
      if (files[id] !== undefined) return (cache[id] = { status: 'ok', data: files[id] });
      if (loaders[id]) return run(id, () => { const r = loaders[id].fn({ answer: answers[id] }); return r && Array.isArray(r.rows) ? r.rows : r; });
      if (calcs[id]) return run(id, () => calcs[id].fn(...calcs[id].inputs.map((i) => { const d = window.dash.data(i); if (d.status !== 'ok') throw new Error('input ' + i + ' ' + d.status); return d.data; })));
      return { status: 'error', message: 'missing ' + id };
    },
    onData(f) { cbs.push(f); },
    params() { return {}; }, setParams() {}, setLink() {},
    colors: ['#2c7be5', '#e8710a', '#12b886', '#7048e8', '#e64980', '#15aabf', '#fab005'],
  };
  const go = () => setTimeout(render, 0);
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', go); else go();
  let t; window.addEventListener('resize', () => { clearTimeout(t); t = setTimeout(render, 150); });
})();
