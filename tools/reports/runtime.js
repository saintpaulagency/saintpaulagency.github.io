
(function () {
  const data = window.__DASH_DATA, calcs = {}, cache = {};
  const DEFAULTS = %PARAMS%;
  let params = Object.assign({}, DEFAULTS);
  // a link can carry settings: ?set=program=vfv;range=1y
  const setQ = new URLSearchParams(location.search).get('set');
  if (setQ) setQ.split(';').forEach((kv) => { const [k, v] = kv.split('='); if (k) params[k] = v; });
  const cbs = [];
  window.__calcErrors = [];
  window.dash = {
    calc(id, o) { calcs[id] = o; },
    data(id) {
      if (data[id]) return { status: 'ok', data: data[id] };
      if (calcs[id]) {
        if (!cache[id]) {
          try {
            const ins = calcs[id].inputs.map((i) => { const d = window.dash.data(i); if (d.status !== 'ok') throw new Error('input ' + i + ' ' + d.status); return d.data; });
            cache[id] = { status: 'ok', data: calcs[id].fn(...ins) };
          } catch (e) { window.__calcErrors.push(id + ': ' + e.message); cache[id] = { status: 'error', message: String(e) }; }
        }
        return cache[id];
      }
      return { status: 'error', message: 'missing ' + id };
    },
    params() { return Object.assign({}, params); },
    setParams(o) { Object.assign(params, o); cbs.forEach((f) => f()); },
    resetParams() { params = Object.assign({}, DEFAULTS); cbs.forEach((f) => f()); },
    onData(f) { cbs.push(f); setTimeout(() => { f(); window.__drawn = true; }, 0); },
    setLink(id) { try { history.replaceState(null, '', location.pathname + location.search + '#' + id); } catch (e) { /* a page opened from a file */ } },
    colors: ['#2c7be5', '#e8710a', '#12b886', '#7048e8', '#e64980', '#15aabf', '#fab005'],
    loader() {}, refresh() {},
  };
  window.addEventListener('load', () => { window.__loaded = true; });
})();
