/* =========================================================================
   explainer-kit.js — small helpers shared by explainer pages.
   No colours here: everything is styled through CSS classes.

   Usage pattern for a cancellable animation:
     const run = Kit.newRun('stage');     // a new run on the same channel cancels the older one
     await Kit.move(pill, [x1,y1], [x2,y2], 600, run);
     await Kit.sleep(300, run);
     Kit.safe(promise)                    // swallow the "cancelled" error

   Playback controls (injected into .topbar automatically):
     Kit.speed     0.25–2, remembered per viewer
     Kit.paused    freezes Kit.move / Kit.sleep / Kit.tick
     Kit.stepMode  "slide" mode: waits for Next before every Kit.move and
                   before every Kit.sleep of 500 ms or more
   Continuous simulations should advance time with Kit.tick(dt) so they
   follow speed and pause. Pages without discrete steps set
   <body data-anim="continuous"> to hide the step-by-step option.
   ========================================================================= */
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gens = {};
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch (e) { return d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { /* storage blocked */ } }
  };
  let waiting = null;           // pending step-mode gate

  class Stop extends Error {}

  const K = {
    speed: store.get('ie-speed', 1),
    paused: false,
    stepMode: store.get('ie-step', false),
    reduce,
    Stop,
    $: id => document.getElementById(id),

    /** create an SVG element */
    el(tag, attrs = {}, parent) {
      const e = document.createElementNS(NS, tag);
      for (const k in attrs) e.setAttribute(k, attrs[k]);
      if (parent) parent.appendChild(e);
      return e;
    },

    /** svg <text> helper */
    text(parent, x, y, str, cls) {
      const t = K.el('text', { x, y, class: cls || '' }, parent);
      t.textContent = str;
      return t;
    },

    /** labelled box: returns { g, title, sub } */
    node(parent, x, y, w, h, title, sub, cls) {
      const g = K.el('g', { class: 'node ' + (cls || '') }, parent);
      K.el('rect', { x: x - w / 2, y: y - h / 2, width: w, height: h, rx: 12 }, g);
      const t = K.text(g, x, sub ? y - 3 : y + 5, title, 'n-title');
      const s = sub !== undefined ? K.text(g, x, y + 16, sub, 'n-sub') : null;
      return { g, title: t, sub: s };
    },

    /** arrow line between two points; returns the <line> */
    arrow(parent, a, b, cls, marker = 'arr') {
      return K.el('line', { x1: a[0], y1: a[1], x2: b[0], y2: b[1], class: 'msg ' + (cls || ''), 'marker-end': `url(#${marker})` }, parent);
    },

    /** request "pill" that can be moved with Kit.move */
    pill(parent, label, cls) {
      const g = K.el('g', { class: 'pill ' + (cls || ''), transform: 'translate(-200,-200)' }, parent);
      const w = Math.max(54, label.length * 7.6 + 22);
      K.el('rect', { x: -w / 2, y: -13, width: w, height: 26, rx: 8 }, g);
      const t = K.el('text', { x: 0, y: 5 }, g);
      t.textContent = label;
      return g;
    },

    /** start a run on a channel (default 'main'); starting a new run cancels older runs on the same channel */
    newRun(ch = 'main') { gens[ch] = (gens[ch] || 0) + 1; return { ch, id: gens[ch] }; },
    alive(run) { return run === undefined || gens[run.ch] === run.id; },
    cancel(ch = 'main') { gens[ch] = (gens[ch] || 0) + 1; },

    /** wait for Next in step mode (no-op otherwise) */
    gate(run) {
      if (!K.stepMode) return Promise.resolve();
      return new Promise((res, rej) => {
        const w = { done: false };
        waiting = w; ui();
        const iv = setInterval(() => {
          if (!K.alive(run)) { clearInterval(iv); if (waiting === w) waiting = null; ui(); rej(new Stop()); }
          else if (w.done || !K.stepMode) { clearInterval(iv); if (waiting === w) waiting = null; ui(); res(); }
        }, 50);
      });
    },
    next() { if (waiting) { waiting.done = true; waiting = null; ui(); } },

    /** seconds (or ms) of animation time for a real-time delta: scaled by speed, 0 when paused */
    tick(dt) { return K.paused ? 0 : dt * K.speed; },

    async sleep(ms, run) {
      if (ms >= 500) await K.gate(run);
      const target = reduce ? Math.min(ms, 40) : ms;
      return new Promise((res, rej) => {
        let acc = 0, last = performance.now();
        (function f(t) {
          if (!K.alive(run)) return rej(new Stop());
          acc += K.tick(Math.max(0, t - last)); last = t;
          acc >= target ? res() : requestAnimationFrame(f);
        })(last);
      });
    },

    ease: k => (k < 0.5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2),

    /** move an element (translate) from a to b */
    async move(node, a, b, ms, run) {
      await K.gate(run);
      return new Promise((res, rej) => {
        const d = reduce ? 1 : ms;
        let k = 0, last = performance.now();
        (function f(t) {
          if (!K.alive(run)) return rej(new Stop());
          k = Math.min(1, k + K.tick(Math.max(0, t - last)) / d); last = t;
          const e = K.ease(k);
          node.setAttribute('transform', `translate(${(a[0] + (b[0] - a[0]) * e).toFixed(1)},${(a[1] + (b[1] - a[1]) * e).toFixed(1)})`);
          k < 1 ? requestAnimationFrame(f) : res();
        })(last);
      });
    },

    /** prepend a line to a log <ul>, keep at most `max` */
    log(ul, html, max = 8) {
      if (ul.dataset.empty !== 'no') { ul.innerHTML = ''; ul.dataset.empty = 'no'; }
      ul.insertAdjacentHTML('afterbegin', `<li>${html}</li>`);
      while (ul.children.length > max) ul.lastElementChild.remove();
    },
    resetLog(ul, html) { ul.innerHTML = `<li>${html}</li>`; ul.dataset.empty = 'yes'; },

    /** run an async fn, ignoring cancellation */
    safe(p) { return Promise.resolve(p).catch(e => { if (!(e instanceof Stop)) throw e; }); },

    /** wire a .seg button group; calls onPick(value) */
    seg(groupEl, onPick) {
      const btns = groupEl.querySelectorAll('button[data-v]');
      btns.forEach(b => b.addEventListener('click', () => {
        btns.forEach(x => x.setAttribute('aria-pressed', String(x === b)));
        onPick(b.dataset.v);
      }));
    },

    fmt: n => n.toLocaleString('en-US')
  };

  /* ---------- playback control bar ---------- */
  const SPEEDS = [0.25, 0.5, 0.75, 1, 1.5, 2];
  function ui() {
    const nb = document.getElementById('acNext');
    if (nb) { nb.disabled = !waiting; nb.classList.toggle('ready', !!waiting); }
    const pb = document.getElementById('acPause');
    if (pb) { pb.textContent = K.paused ? 'Resume' : 'Pause'; pb.setAttribute('aria-pressed', String(K.paused)); }
    const nw = document.getElementById('acNextWrap');
    if (nw) nw.hidden = !K.stepMode;
  }
  function mount() {
    const bar = document.querySelector('.topbar');
    if (!bar || document.getElementById('animCtrl')) return;
    const continuous = document.body.dataset.anim === 'continuous';
    const box = document.createElement('div');
    box.className = 'anim-ctrl'; box.id = 'animCtrl';
    box.setAttribute('role', 'group'); box.setAttribute('aria-label', 'Animation playback');
    box.innerHTML = `
      <label class="ac-speed" for="acSpeed"><span>Speed</span>
        <select id="acSpeed">${SPEEDS.map(v => `<option value="${v}"${v === K.speed ? ' selected' : ''}>${v}×</option>`).join('')}</select>
      </label>
      <button class="ac-btn" id="acPause" type="button" aria-pressed="false">Pause</button>
      ${continuous ? '' : `<label class="ac-step" for="acStep"><input type="checkbox" id="acStep"${K.stepMode ? ' checked' : ''}> Step by step</label>
      <span id="acNextWrap"${K.stepMode ? '' : ' hidden'}><button class="ac-btn ac-next" id="acNext" type="button" disabled title="Next step (→ key)">Next ▸</button></span>`}`;
    const toggle = bar.querySelector('.theme-toggle');
    bar.insertBefore(box, toggle || null);
    box.querySelector('#acSpeed').addEventListener('change', e => { K.speed = +e.target.value || 1; store.set('ie-speed', K.speed); });
    box.querySelector('#acPause').addEventListener('click', () => { K.paused = !K.paused; ui(); });
    const st = box.querySelector('#acStep');
    if (st) st.addEventListener('change', () => { K.stepMode = st.checked; store.set('ie-step', K.stepMode); ui(); });
    const nx = box.querySelector('#acNext');
    if (nx) nx.addEventListener('click', K.next);
    document.addEventListener('keydown', e => {
      if (e.key !== 'ArrowRight' || !waiting) return;
      const tag = (e.target.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'select' || tag === 'textarea') return;
      e.preventDefault(); K.next();
    });
    if (continuous) K.stepMode = false;
    ui();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', mount); else mount();

  window.Kit = K;
})();
