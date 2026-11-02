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

   Guided story (narrated walkthrough with Back / Next):
     Kit.story({ root, steps, show })
       root  : an element with class "story"; Kit fills the caption + nav
       steps : [{ title, text, tip?, play?: async run => {} }]
       tipLabel: label before each step's tip (default 'Exam tip')
       show(i): draw the finished state of step i instantly (used for Back,
                dot jumps and after each play). Keep it declarative.
     Forward moves call steps[i].play(run) (Kit.move / Kit.sleep), then show(i).

   Code stepper (Python Tutor style), fed by traces from tools/pytrace.py:
     const tr = Kit.trace(el, trace, { controls: true, onStep: (i, step) => {} })
       tr.show(i)  render step i (line markers, frames, objects, arrows, output)
       tr.n        number of steps; tr.steps the raw trace steps
     Scalars inside containers are drawn inline; names in frames point to objects.
   UML class diagrams: Kit.umlDefs(svg); Kit.classBox(svg, x, y, w, {name, stereo, fields, methods});
   Kit.umlLink(svg, fromPt, toPt, 'uses'|'implements'|'inherits'|'creates', bends, label).
   Kit.pyHighlight(line) / Kit.csHighlight(line) return HTML with .k/.s/.n/.c/.b token spans
   (C#: .b marks type names). Kit.codeBlock(pre, code, 'cs'|'py'|'ts'|'ng') fills a .codeblock.
   Angular: Kit.tsHighlight / Kit.ngHighlight (templates: .bd [prop], .ev (event), .tw [(model)], .ip {{ }}).
   Kit.codeCard(el, { file, lang, code, marks: { 3: 'hot', 5: ['bad', 'note'] }, dim, out: [...], caption })
     renders a file card with numbered, marked lines and an optional console.
   Kit.compBox(svg, x, y, w, { name, role, rows }) draws a component; .set(i, text) updates a row.
   Kit.ngWire(svg, a, b, 'down'|'up'|'two', label, bends) draws a data-flow wire
     (down = inputs, cyan · up = outputs, orange · two = model(), violet).

   Exam-style questions: Kit.mcq(el, [{ q, o: [...], a: [index, ...], why }]).
   Quick-fire drill: Kit.pick(el, [{ q, a, why, opts? }], options).
   Request-path diagrams (AWS style): Kit.net(svg, { zones, nodes, links }) → node/state/link/badge/focus,
     await net.send(['user','edge','app'], { run, label, tone }) moves a glowing dot along the path.
     Icon tiles come from Kit.ICONS (users, globe, accel, dns, edge, lb, server, chip, db, bucket, …).

   Edit-and-run box (real Python via Pyodide, loaded on first Run):
     Kit.pyRunner(el, { starters: [{ label, code, inputs? }] })
       Run shows output; Step through renders Kit.trace from the same tracer
       (assets/js/pytrace-src.js, generated from tools/pytrace.py).
   ========================================================================= */
(function () {
  const NS = 'http://www.w3.org/2000/svg';
  const reduce = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
  const gens = {};
  const scriptBase = (document.currentScript && document.currentScript.src) ? document.currentScript.src.replace(/[^/]*$/, '') : '';
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
    assetBase: scriptBase,

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

    /** UML markers for class diagrams; call once per <svg> before umlLink */
    umlDefs(svg) {
      if (svg.querySelector('#uml-tri')) return;
      const d = K.el('defs', {}, svg);
      d.innerHTML = '<marker id="uml-tri" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path class="uml-tri" d="M1 1 L11 6 L1 11 z"/></marker>'
        + '<marker id="uml-open" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="11" markerHeight="11" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path class="uml-open" d="M1 1 L11 6 L1 11"/></marker>';
    },

    /** UML class box. x,y = top-left. spec: { name, stereo?, fields?: [], methods?: [] }.
        Returns { g, h, rows: [<g> per field/method], top, bottom, left, right, cx, cy } */
    classBox(parent, x, y, w, spec, cls) {
      const g = K.el('g', { class: 'uml ' + (cls || '') }, parent);
      const RH = 19, head = spec.stereo ? 40 : 28;
      const fields = spec.fields || [], methods = spec.methods || [];
      const h = head + (fields.length ? fields.length * RH + 8 : 0) + (methods.length ? methods.length * RH + 8 : 0) + (fields.length || methods.length ? 0 : 0);
      K.el('rect', { x, y, width: w, height: h, rx: 8, class: 'uml-box' }, g);
      if (spec.stereo) K.text(g, x + w / 2, y + 15, '«' + spec.stereo + '»', 'uml-stereo');
      K.text(g, x + w / 2, y + head - 9, spec.name, 'uml-name');
      const rows = []; let yy = y + head;
      [[fields, 'f'], [methods, 'm']].forEach(([list, kind]) => {
        if (!list.length) return;
        K.el('line', { x1: x, y1: yy, x2: x + w, y2: yy, class: 'uml-sep' }, g);
        yy += 4;
        list.forEach(t => {
          const r = K.el('g', { class: 'uml-row uml-' + kind }, g);
          K.el('rect', { x: x + 3, y: yy, width: w - 6, height: RH - 1, rx: 4, class: 'uml-hl' }, r);
          const tx = K.text(r, x + 10, yy + 13, t, 'uml-txt'); tx.style.textAnchor = 'start';
          rows.push(r); yy += RH;
        });
        yy += 4;
      });
      return { g, h, rows, top: [x + w / 2, y], bottom: [x + w / 2, y + h], left: [x, y + h / 2], right: [x + w, y + h / 2], cx: x + w / 2, cy: y + h / 2 };
    },

    /** UML relationship from point a to b. kind: 'uses' (dashed, open arrow), 'implements' (dashed, hollow triangle),
        'inherits' (solid, hollow triangle), 'creates' (solid, open arrow). pts: optional bend points. */
    umlLink(parent, a, b, kind = 'uses', pts = [], label) {
      const all = [a, ...pts, b];
      const g = K.el('g', { class: 'uml-link ' + kind }, parent);
      K.el('path', { d: 'M' + all.map(p => p.join(' ')).join(' L'), 'marker-end': `url(#${kind === 'implements' || kind === 'inherits' ? 'uml-tri' : 'uml-open'})` }, g);
      if (label) { const m = all[Math.floor((all.length - 1) / 2)], n = all[Math.floor((all.length - 1) / 2) + 1]; K.text(g, (m[0] + n[0]) / 2, (m[1] + n[1]) / 2 - 6, label, 'mlabel halo'); }
      return g;
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

    fmt: n => n.toLocaleString('en-US'),

    /** Python syntax highlighting (small, good enough for teaching snippets) */
    pyHighlight(src) {
      const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const KW = new Set('False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield'.split(' '));
      const BI = new Set('print len range type int float str bool list dict set tuple input isinstance id sorted sum min max abs round enumerate zip open super any all reversed map filter next iter repr'.split(' '));
      const re = /(#.*$)|([rbfRBF]{0,2}(?:"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'))|(\b\d+(?:\.\d+)?\b)|([A-Za-z_]\w*)|([^\w#'"]+|['"])/g;
      let out = '', m;
      while ((m = re.exec(src))) {
        if (m[1]) out += `<span class="c">${esc(m[1])}</span>`;
        else if (m[2]) out += `<span class="s">${esc(m[2])}</span>`;
        else if (m[3]) out += `<span class="n">${esc(m[3])}</span>`;
        else if (m[4]) out += KW.has(m[4]) ? `<span class="k">${m[4]}</span>` : (BI.has(m[4]) && src[re.lastIndex] === '(' ? `<span class="b">${m[4]}</span>` : esc(m[4]));
        else out += esc(m[0]);
      }
      return out;
    },

    /** C# line highlighter: same token classes as pyHighlight (.k keyword, .s string, .n number, .c comment, .b type name) */
    csHighlight(src) {
      const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const KW = new Set('abstract as base bool break case catch class const continue decimal default do double else enum false finally float for foreach get if in init int interface internal is long namespace new null object override private protected public readonly record return sealed set static string this throw true try using var virtual void while async await required'.split(' '));
      const re = /(\/\/.*$)|(\$?@?"(?:\\.|[^"\\])*")|(\b\d+(?:\.\d+)?m?\b)|([A-Za-z_]\w*)|([^\w"/$@]+|[/"$@])/g;
      let out = '', m;
      while ((m = re.exec(src))) {
        if (m[1]) out += `<span class="c">${esc(m[1])}</span>`;
        else if (m[2]) out += `<span class="s">${esc(m[2])}</span>`;
        else if (m[3]) out += `<span class="n">${esc(m[3])}</span>`;
        else if (m[4]) out += KW.has(m[4]) ? `<span class="k">${m[4]}</span>` : (/^[A-Z]/.test(m[4]) ? `<span class="b">${m[4]}</span>` : esc(m[4]));
        else out += esc(m[0]);
      }
      return out;
    },

    /** TypeScript line highlighter (Angular class files): .k keyword/decorator, .s string, .n Angular signal API or number, .c comment, .b type name */
    tsHighlight(src) {
      const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const KW = new Set('import from export default class interface type extends implements const let var new return this if else for of in typeof keyof readonly private public protected static constructor async await true false null undefined void string number boolean any never unknown as'.split(' '));
      const NG = new Set('signal computed effect input model output linkedSignal resource httpResource inject viewChild contentChild'.split(' '));
      const re = /(\/\/.*$)|(\/\*.*?\*\/)|('(?:\\.|[^'\\])*'|"(?:\\.|[^"\\])*"|`(?:\\.|[^`\\])*`)|(@[A-Za-z]\w*)|(\b\d+(?:\.\d+)?\b)|([A-Za-z_$][\w$]*)|([\s\S])/g;
      let out = '', m;
      while ((m = re.exec(src))) {
        if (m[1] || m[2]) out += `<span class="c">${esc(m[1] || m[2])}</span>`;
        else if (m[3]) out += `<span class="s">${esc(m[3])}</span>`;
        else if (m[4]) out += `<span class="k">${m[4]}</span>`;
        else if (m[5]) out += `<span class="n">${m[5]}</span>`;
        else if (m[6]) {
          const w = m[6], nx = src[re.lastIndex];
          out += KW.has(w) ? `<span class="k">${w}</span>` : (NG.has(w) && (nx === '(' || nx === '.' || nx === '<') ? `<span class="n">${w}</span>` : (/^[A-Z]/.test(w) ? `<span class="b">${w}</span>` : w));
        } else out += esc(m[0]);
      }
      return out;
    },

    /** Angular template line highlighter: .bd [property], .ev (event), .tw [(two-way)], .ip {{ interpolation }},
        .k @if/@for blocks and #refs, .b tag names, .s plain attribute values, .c comments */
    ngHighlight(src) {
      const esc = t => t.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const re = /(<!--.*?-->)|(\{\{.*?\}\})|(@(?:else if|if|else|for|switch|case|default|empty|let|defer)\b)|(<\/?[\w-]+)|(\/?>)|(\[\([\w.-]+\)\]|\[[\w.@-]+\](?==)|\([\w.-]+\)(?==))(="[^"]*")?|(#[\w-]+)|([\w-]+)(="[^"]*")|([\s\S])/g;
      let out = '', m;
      while ((m = re.exec(src))) {
        if (m[1]) out += `<span class="c">${esc(m[1])}</span>`;
        else if (m[2]) out += `<span class="ip">${esc(m[2])}</span>`;
        else if (m[3]) out += `<span class="k">${m[3]}</span>`;
        else if (m[4]) out += `${esc(m[4].startsWith('</') ? '</' : '<')}<span class="b">${m[4].replace(/^<\/?/, '')}</span>`;
        else if (m[5]) out += esc(m[5]);
        else if (m[6]) { const c = m[6].startsWith('[(') ? 'tw' : m[6][0] === '[' ? 'bd' : 'ev'; out += `<span class="${c}">${esc(m[6])}</span>${m[7] ? `<span class="ex">${esc(m[7])}</span>` : ''}`; }
        else if (m[8]) out += `<span class="k">${m[8]}</span>`;
        else if (m[9]) out += `${m[9]}<span class="s">${esc(m[10])}</span>`;
        else out += esc(m[0]);
      }
      return out;
    },

    /** code card (filename bar, numbered lines, per-line marks, optional console and caption).
        opts: { file, lang: 'ts'|'ng'|'cs'|'py', code, marks: { lineNo: 'hot'|'bad'|'ok'|['bad', 'note'] }, dim: bool (dim unmarked lines),
                out: ['console line', ...], outLabel, caption } */
    codeCard(el, o) {
      const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const hl = { cs: K.csHighlight, ts: K.tsHighlight, ng: K.ngHighlight, txt: esc }[o.lang] || K.pyHighlight;
      const marks = o.marks || {};
      const lines = o.code.replace(/\n$/, '').split('\n').map((l, i) => {
        let mk = marks[i + 1], note = '';
        if (Array.isArray(mk)) { note = mk[1]; mk = mk[0]; }
        const cls = mk ? ' mk-' + mk : (o.dim && Object.keys(marks).length ? ' mk-dim' : '');
        return `<span class="ln${cls}"><span class="cc-gut">${i + 1}</span>${hl(l) || ' '}${note ? `<span class="cc-note mk-${mk}">◀ ${esc(note)}</span>` : ''}</span>`;
      }).join('');
      el.classList.add('cc');
      el.innerHTML = `<div class="cc-head"><span class="cc-dots" aria-hidden="true"><i></i><i></i><i></i></span><span class="cc-file">${esc(o.file || '')}</span></div>`
        + `<pre class="cc-code">${lines}</pre>`
        + (o.out ? `<div class="cc-out"><div class="cc-out-h">${esc(o.outLabel || 'Console')}</div><pre>${o.out.length ? o.out.map(esc).join('\n') : '<span class="muted">(nothing logged)</span>'}</pre></div>` : '')
        + (o.caption ? `<div class="cc-cap"><span>${o.caption}</span></div>` : '');
      return el;
    },

    /** Angular component box for component trees. x,y = top-left. spec: { name, role?, rows: [] }.
        Returns { g, h, rows: [{ g, t }], set(i, text), top, bottom, left, right } */
    compBox(parent, x, y, w, spec, cls) {
      const g = K.el('g', { class: 'cbox ' + (cls || '') }, parent);
      const RH = 22, head = 34, rows = spec.rows || [];
      const h = head + rows.length * RH + (rows.length ? 10 : 0);
      K.el('rect', { x, y, width: w, height: h, rx: 12, class: 'cb-box' }, g);
      const n = K.text(g, x + 14, y + 22, spec.name, 'cb-name'); n.style.textAnchor = 'start';
      if (spec.role) { const r = K.text(g, x + w - 14, y + 22, spec.role, 'cb-role'); r.style.textAnchor = 'end'; }
      if (rows.length) K.el('line', { x1: x, y1: y + head, x2: x + w, y2: y + head, class: 'cb-sep' }, g);
      const out = rows.map((t, i) => {
        const rg = K.el('g', { class: 'cb-row' }, g);
        K.el('rect', { x: x + 4, y: y + head + 5 + i * RH, width: w - 8, height: RH - 2, rx: 5, class: 'cb-hl' }, rg);
        const tx = K.text(rg, x + 14, y + head + 20 + i * RH, t, 'cb-txt'); tx.style.textAnchor = 'start';
        return { g: rg, t: tx };
      });
      return { g, h, rows: out, set(i, text) { out[i].t.textContent = text; }, top: [x + w / 2, y], bottom: [x + w / 2, y + h], left: [x, y + h / 2], right: [x + w, y + h / 2] };
    },

    /** data-flow wire between components. kind: 'down' (inputs, cyan), 'up' (outputs/events, orange), 'two' (model, violet).
        Arrowheads are created per <svg> on first use. Returns <g> holding the path (and label). */
    ngWire(parent, a, b, kind = 'down', label, pts = []) {
      const svg = parent.ownerSVGElement || parent, pre = (svg.id || 'ngsvg') + '-ng-';
      if (!svg.querySelector('#' + pre + 'down')) {
        const d = K.el('defs', {}, svg);
        d.innerHTML = ['down', 'up', 'two', 'bad'].map(k => `<marker id="${pre}${k}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse" markerUnits="userSpaceOnUse"><path class="ng-ah ${k}" d="M0 0 L10 5 L0 10 z"/></marker>`).join('');
        svg.insertBefore(d, svg.firstChild);
      }
      const all = [a, ...pts, b];
      const g = K.el('g', { class: 'ngw-g ' + kind }, parent);
      const p = K.el('path', { d: 'M' + all.map(q => q.join(' ')).join(' L'), class: 'ngw ' + kind, 'marker-end': `url(#${pre}${kind})` }, g);
      if (kind === 'two') p.setAttribute('marker-start', `url(#${pre}two)`);
      if (label) { const m = all[Math.floor((all.length - 1) / 2)], n = all[Math.floor((all.length - 1) / 2) + 1]; const t = K.text(g, (m[0] + n[0]) / 2 + 10, (m[1] + n[1]) / 2 + 4, label, 'mlabel halo ' + kind); t.style.textAnchor = 'start'; }
      return g;
    },

    /** fill a <pre class="codeblock"> with highlighted lines; lang 'cs', 'py', 'ts' or 'ng'; returns the line elements */
    codeBlock(pre, code, lang = 'py') {
      const hl = { cs: K.csHighlight, ts: K.tsHighlight, ng: K.ngHighlight }[lang] || K.pyHighlight;
      pre.innerHTML = code.replace(/\n$/, '').split('\n').map(l => `<span class="ln">${hl(l) || ' '}</span>`).join('');
      return [...pre.children];
    },

    /** code stepper; see header */
    trace(root, data, opts = {}) {
      const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const lines = data.code.split('\n');
      const uid = (root.id || 'tr') + '-ah';
      root.classList.add('tr');
      root.innerHTML = `
        <div class="tr-left">
          <div class="tr-legend"><span class="lg next">▶ next line to run</span><span class="lg ran">■ line that just ran</span></div>
          <div class="tr-code">${lines.map((l, i) => `<div class="tr-ln" data-n="${i + 1}"><span class="tr-gut">${i + 1}</span><code>${K.pyHighlight(l) || ' '}</code></div>`).join('')}</div>
          <div class="tr-out"><div class="tr-h">Output</div><pre></pre></div>
        </div>
        <div class="tr-mem">
          <div class="tr-col tr-frames"><div class="tr-h">Names (frames)</div><div class="tr-fbody"></div></div>
          <div class="tr-col tr-heap"><div class="tr-h">Objects</div><div class="tr-hbody"></div></div>
          <svg class="tr-arrows" aria-hidden="true"><defs><marker id="${uid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" class="tr-ah"/></marker></defs><g></g></svg>
        </div>
        ${opts.controls ? `<div class="tr-ctl"><button class="btn" type="button" data-t="prev">◀ Back</button><input type="range" min="0" value="0" aria-label="Step"><button class="btn primary" type="button" data-t="next">Next ▶</button><span class="tr-count"></span></div>` : ''}`;
      const q = sel => root.querySelector(sel);
      const fbody = q('.tr-fbody'), hbody = q('.tr-hbody'), outPre = q('.tr-out pre'), svgG = q('.tr-arrows g'), mem = q('.tr-mem');
      const steps = data.steps;
      let cur = 0;
      const isScalar = o => o && o.v !== undefined && !['function', 'class', 'generator'].includes(o.t);
      const scalarText = o => o.v;
      function cell(v, heap) {
        if (!v) return '';
        if (v.p !== undefined) return `<span class="tr-prim">${esc(v.p)}</span>`;
        const o = heap[v.ref];
        if (o && isScalar(o)) return `<span class="tr-prim">${esc(scalarText(o))}</span>`;
        return `<span class="tr-ptr" data-ref="${v.ref}"></span>`;
      }
      function objHtml(id, o, heap, cls) {
        let body = '';
        if (isScalar(o)) body = `<div class="tr-val">${esc(o.v)}</div>`;
        else if (['list', 'tuple', 'set', 'frozenset'].includes(o.t)) body = o.items.length ? `<div class="tr-seq">${o.items.map((it, i) => `<div class="tr-cell"><div class="tr-cv">${cell(it, heap)}</div>${o.t === 'set' || o.t === 'frozenset' ? '' : `<div class="tr-ix">${i}</div>`}</div>`).join('')}</div>` : '<div class="tr-val muted">empty</div>';
        else if (o.t === 'dict') body = o.items.length ? `<div class="tr-kv">${o.items.map(([k, v]) => `<div class="tr-k">${cell(k, heap)}</div><div class="tr-v">${cell(v, heap)}</div>`).join('')}</div>` : '<div class="tr-val muted">empty</div>';
        else if (o.t === 'instance' || o.t === 'class' || o.t === 'generator') body = `${o.t !== 'instance' ? `<div class="tr-val">${esc(o.v)}</div>` : ''}${(o.attrs || []).length ? `<div class="tr-kv">${o.attrs.map(([k, v]) => `<div class="tr-k">${esc(k)}</div><div class="tr-v">${cell(v, heap)}</div>`).join('')}</div>` : ''}`;
        else body = `<div class="tr-val">${esc(o.v)}</div>`;
        const tag = o.t === 'instance' ? `${o.cls} object` : o.t;
        return `<div class="tr-obj ${cls}" data-id="${id}"><div class="tr-tag">${esc(tag)}</div>${body}</div>`;
      }
      function visibleIds(st) {
        const seen = new Set(), order = [];
        const visit = (v, fromContainer) => {
          if (!v || v.ref === undefined) return;
          const o = st.heap[v.ref]; if (!o) return;
          if (fromContainer && isScalar(o)) return;
          if (seen.has(v.ref)) return; seen.add(v.ref); order.push(v.ref);
          (o.items || []).forEach(it => Array.isArray(it) ? it.forEach(x => visit(x, true)) : visit(it, true));
          (o.attrs || []).forEach(([, x]) => visit(x, true));
        };
        st.frames.forEach(f => { f.vars.forEach(([, v]) => visit(v, false)); if (f.ret) visit(f.ret, false); if (f.yield) visit(f.yield, false); });
        return order.sort((a, b) => a - b);
      }
      function draw() {
        svgG.textContent = '';
        const box = mem.getBoundingClientRect();
        const svg = q('.tr-arrows'); svg.setAttribute('width', box.width); svg.setAttribute('height', box.height);
        mem.querySelectorAll('.tr-ptr').forEach(p => {
          const t = hbody.querySelector(`.tr-obj[data-id="${p.dataset.ref}"]`);
          if (!t) return;
          const a = p.getBoundingClientRect(), b = t.getBoundingClientRect();
          const x1 = a.left + a.width / 2 - box.left, y1 = a.top + a.height / 2 - box.top;
          const yT = Math.min(b.top + 15, b.bottom - 6) - box.top;
          let d;
          if (b.left - box.left > x1 + 12) { const x2 = b.left - box.left - 1; const mx = (x1 + x2) / 2; d = `M${x1} ${y1} C ${mx} ${y1}, ${mx} ${yT}, ${x2} ${yT}`; }
          else { const x2 = b.right - box.left + 1; const bend = Math.max(x2, x1) + 30; d = `M${x1} ${y1} C ${bend} ${y1}, ${bend} ${yT}, ${x2} ${yT}`; }
          K.el('path', { d, class: 'tr-arrow' + (p.classList.contains('chg') ? ' chg' : ''), 'marker-end': `url(#${uid})` }, svgG);
        });
      }
      function show(i) {
        cur = Math.max(0, Math.min(steps.length - 1, i));
        const st = steps[cur], prev = steps[cur - 1];
        root.querySelectorAll('.tr-ln').forEach(el => {
          const n = +el.dataset.n;
          el.classList.toggle('next', st.line === n);
          el.classList.toggle('ran', st.ran === n && st.line !== n);
        });
        const nextEl = root.querySelector('.tr-ln.next');
        const codeBox = q('.tr-code');
        if (nextEl && (nextEl.offsetTop < codeBox.scrollTop || nextEl.offsetTop > codeBox.scrollTop + codeBox.clientHeight - 30)) codeBox.scrollTop = nextEl.offsetTop - 40;
        const prevVar = {};
        if (prev) prev.frames.forEach((f, fi) => f.vars.forEach(([k, v]) => { prevVar[f.name + fi + ':' + k] = JSON.stringify(v); }));
        fbody.innerHTML = st.frames.map((f, fi) => `<div class="tr-frame${fi === st.frames.length - 1 ? ' active' : ''}"><div class="tr-fname">${esc(f.name)}</div>${f.vars.length || f.ret || f.yield || f.raising ? '' : '<div class="tr-empty">no names yet</div>'}${f.vars.map(([k, v]) => {
          const chg = !!prev && prevVar[f.name + fi + ':' + k] !== JSON.stringify(v);
          const c = v.p !== undefined ? `<span class="tr-prim">${esc(v.p)}</span>` : `<span class="tr-ptr${chg ? ' chg' : ''}" data-ref="${v.ref}"></span>`;
          return `<div class="tr-var${chg ? ' chg' : ''}"><span class="tr-name">${esc(k)}</span>${c}</div>`;
        }).join('')}${[['ret', 'return value'], ['yield', 'yielded value']].map(([key, label]) => f[key] ? `<div class="tr-var ret"><span class="tr-name">${label}</span>${f[key].p !== undefined ? `<span class="tr-prim">${esc(f[key].p)}</span>` : `<span class="tr-ptr chg" data-ref="${f[key].ref}"></span>`}</div>` : '').join('')}${f.raising ? '<div class="tr-var ret raising"><span class="tr-name">no return value: exception passing up ↑</span></div>' : ''}</div>`).join('');
        const ids = visibleIds(st);
        const prevIds = prev ? visibleIds(prev) : [];
        const ghosts = prevIds.filter(id => !ids.includes(id) && prev.heap[id]);
        hbody.innerHTML = ids.map(id => objHtml(id, st.heap[id], st.heap, prev && !prevIds.includes(id) ? 'new' : (prev && JSON.stringify(prev.heap[id]) !== JSON.stringify(st.heap[id]) ? 'chg' : ''))).join('')
          + ghosts.map(id => objHtml('g' + id, prev.heap[id], prev.heap, 'ghost')).join('')
          + (ids.length || ghosts.length ? '' : '<div class="tr-empty">no objects yet</div>');
        hbody.querySelectorAll('.tr-obj.ghost .tr-ptr').forEach(p => p.remove());
        hbody.querySelectorAll('.tr-obj.ghost').forEach(g => g.insertAdjacentHTML('beforeend', '<div class="tr-gnote">no names point here → freed</div>'));
        let out = esc(st.out || '');
        if (st.exc) out = st.event === 'end' ? out.replace(esc(st.exc), `<span class="tr-exc">${esc(st.exc)}</span>`) : out + `<span class="tr-exc">${esc(st.exc)} raised here</span>`;
        outPre.innerHTML = out;
        outPre.parentElement.classList.toggle('empty', !st.out && !st.exc);
        if (opts.controls) {
          const r = q('.tr-ctl input'); r.max = steps.length - 1; r.value = cur;
          q('.tr-count').textContent = `Step ${cur + 1} / ${steps.length}`;
          q('[data-t=prev]').disabled = cur === 0; q('[data-t=next]').disabled = cur === steps.length - 1;
        }
        requestAnimationFrame(draw);
        if (opts.onStep) opts.onStep(cur, st);
      }
      if (opts.controls) {
        q('[data-t=prev]').addEventListener('click', () => show(cur - 1));
        q('[data-t=next]').addEventListener('click', () => show(cur + 1));
        q('.tr-ctl input').addEventListener('input', e => show(+e.target.value));
      }
      if (window.ResizeObserver) new ResizeObserver(() => requestAnimationFrame(draw)).observe(root);
      show(0);
      return { show, steps, get n() { return steps.length; }, get cur() { return cur; } };
    },

    /** load Pyodide + the tracer once (on demand); resolves to the pyodide instance */
    loadPython(onStatus) {
      if (K._py) return K._py;
      const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/';
      const add = src => new Promise((res, rej) => { const s = document.createElement('script'); s.src = src; s.onload = res; s.onerror = () => rej(new Error('Could not load ' + src)); document.head.appendChild(s); });
      K._py = (async () => {
        onStatus && onStatus('Loading Python in your browser (about 10 MB, first time only)…');
        if (!window.PYTRACE_SRC) await add(K.assetBase + 'pytrace-src.js');
        if (!window.loadPyodide) await add(PYODIDE + 'pyodide.js');
        const py = await window.loadPyodide({ indexURL: PYODIDE });
        py.runPython(window.PYTRACE_SRC.replace(/\nif __name__ == "__main__":[\s\S]*$/, '\n'));
        return py;
      })();
      K._py.catch(() => { K._py = null; });
      return K._py;
    },

    /** "Edit and run" box: textarea + Run / Step through, executed with Pyodide */
    pyRunner(root, opts = {}) {
      const esc = t => String(t).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      const starters = opts.starters || [{ label: 'Example', code: opts.code || 'print("Hello")' }];
      root.classList.add('runner');
      root.innerHTML = `
        <div class="rn-bar">
          <label class="rn-pick">Start from <select>${starters.map((s, i) => `<option value="${i}">${esc(s.label)}</option>`).join('')}</select></label>
          <div class="rn-btns"><button class="btn primary" type="button" data-r="run">Run ▶</button><button class="btn" type="button" data-r="step">Step through</button><button class="btn" type="button" data-r="reset">Reset</button></div>
        </div>
        <textarea class="rn-code" spellcheck="false" autocapitalize="off" autocomplete="off" aria-label="Python code"></textarea>
        <details class="rn-inputs"><summary>Values for input() (one per line)</summary><textarea class="rn-in" rows="3" spellcheck="false" aria-label="Input values"></textarea></details>
        <div class="rn-status" aria-live="polite">Edit the code, then Run. Python runs in your browser; nothing is sent anywhere.</div>
        <pre class="rn-out" hidden></pre>
        <div class="rn-trace"></div>`;
      const q = s => root.querySelector(s);
      const ta = q('.rn-code'), sel = q('select'), status = q('.rn-status'), out = q('.rn-out'), trBox = q('.rn-trace');
      const load = i => { ta.value = starters[i].code; q('.rn-in').value = (starters[i].inputs || []).join('\n'); out.hidden = true; trBox.innerHTML = ''; fit(); };
      const fit = () => { ta.style.height = 'auto'; ta.style.height = Math.min(520, ta.scrollHeight + 4) + 'px'; };
      ta.addEventListener('input', fit);
      ta.addEventListener('keydown', e => {
        if (e.key === 'Tab' && !e.shiftKey) { e.preventDefault(); const s = ta.selectionStart; ta.setRangeText('    ', s, ta.selectionEnd, 'end'); fit(); }
        if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); go(false); }
      });
      sel.addEventListener('change', () => load(+sel.value));
      async function go(step) {
        root.querySelectorAll('.rn-btns button').forEach(b => b.disabled = true);
        try {
          const py = await K.loadPython(m => { status.textContent = m; });
          status.textContent = 'Running…';
          await new Promise(r => setTimeout(r, 20));
          py.globals.set('RN_CODE', ta.value.replace(/\t/g, '    '));
          py.globals.set('RN_IN', q('.rn-in').value);
          const json = py.runPython('import json\njson.dumps(Recorder(RN_CODE, [x for x in RN_IN.split("\\n")] if RN_IN else [], max_steps=2000).run())');
          const tr = JSON.parse(json);
          const last = tr.steps[tr.steps.length - 1];
          out.hidden = false;
          out.innerHTML = last.out ? esc(last.out).replace(last.exc ? esc(last.exc) : '\u0000', m => `<span class="tr-exc">${m}</span>`) : '<span class="muted">(no output)</span>';
          status.innerHTML = (last.exc ? `<span class="bad-text">Stopped with an error.</span> ` : `<span class="ok-text">Done.</span> `) + `Python ${esc(tr.python)} · ${tr.steps.length} steps` + (step ? '' : ' · press <b>Step through</b> to watch it run line by line');
          trBox.innerHTML = '';
          if (step) { const d = document.createElement('div'); trBox.appendChild(d); K.trace(d, tr, { controls: true }); }
        } catch (e) {
          status.innerHTML = `<span class="bad-text">Couldn't start Python.</span> ${esc(e.message || e)}. Check your internet connection; the rest of the page works without it.`;
        } finally {
          root.querySelectorAll('.rn-btns button').forEach(b => b.disabled = false);
        }
      }
      root.addEventListener('click', e => {
        const b = e.target.closest('[data-r]'); if (!b) return;
        if (b.dataset.r === 'run') go(false);
        if (b.dataset.r === 'step') go(true);
        if (b.dataset.r === 'reset') load(+sel.value);
      });
      load(0);
      return { load, run: () => go(false), step: () => go(true) };
    },

    /** narrated walkthrough; see header */
    story({ root, steps, show, tipLabel = 'Exam tip' }) {
      const ch = 'story-' + (root.id || Math.random().toString(36).slice(2));
      const cap = document.createElement('div');
      cap.className = 'story-cap';
      cap.innerHTML = `<div class="count"></div><h3></h3><p class="txt"></p><p class="tip" hidden></p>
        <div class="story-nav"><button class="btn" type="button" data-a="back">◀ Back</button><button class="btn primary" type="button" data-a="next">Next ▶</button><button class="btn" type="button" data-a="auto">Play all</button></div>
        <div class="story-dots" role="group" aria-label="Steps"></div>`;
      root.appendChild(cap);
      const $c = sel => cap.querySelector(sel);
      const dots = $c('.story-dots');
      dots.innerHTML = steps.map((st, i) => `<button type="button" aria-label="Step ${i + 1}: ${st.title.replace(/"/g, '')}"></button>`).join('');
      let cur = -1, auto = false, seen = new Set();
      function paint() {
        const st = steps[cur];
        $c('.count').textContent = `Step ${cur + 1} of ${steps.length}`;
        $c('h3').innerHTML = st.title;
        $c('.txt').innerHTML = st.text;
        const tip = $c('.tip'); tip.hidden = !st.tip; tip.innerHTML = st.tip ? `<b>${tipLabel}:</b> ` + st.tip : '';
        $c('[data-a=back]').disabled = cur === 0;
        $c('[data-a=next]').textContent = cur === steps.length - 1 ? 'Start again ↺' : 'Next ▶';
        $c('[data-a=auto]').textContent = auto ? 'Stop' : 'Play all';
        dots.querySelectorAll('button').forEach((b, i) => { b.classList.toggle('on', i === cur); b.classList.toggle('seen', seen.has(i)); });
      }
      async function go(i, animate) {
        const run = K.newRun(ch);
        cur = i; seen.add(i); paint();
        if (animate && steps[i].play) {
          if (i > 0) show(i - 1);
          try { await steps[i].play(run); } catch (e) { if (!(e instanceof Stop)) throw e; return; }
        }
        if (K.alive(run)) show(i);
        if (auto && K.alive(run)) {
          try { await K.sleep(2600, run); } catch (e) { return; }
          if (!auto) return;
          if (cur < steps.length - 1) go(cur + 1, true); else { auto = false; paint(); }
        }
      }
      cap.addEventListener('click', e => {
        const a = e.target.closest('[data-a]'); if (!a) return;
        if (a.dataset.a === 'back' && cur > 0) { auto = false; go(cur - 1, false); }
        if (a.dataset.a === 'next') { auto = false; cur === steps.length - 1 ? go(0, false) : go(cur + 1, true); }
        if (a.dataset.a === 'auto') { auto = !auto; if (auto) go(cur === steps.length - 1 ? 0 : cur + 1, true); else { K.cancel(ch); show(cur); paint(); } }
      });
      dots.addEventListener('click', e => { const b = e.target.closest('button'); if (!b) return; auto = false; go([...dots.children].indexOf(b), false); });
      go(0, false);
      return { go };
    }
  };

  /* ---------- exam-style multiple choice ----------
     Kit.mcq(el, [{ q, o: ['A text', 'B text', ...], a: [0] or [1, 3], why }])
     Click an option (or two for "select TWO") to lock in; shows right/wrong and the reason. */
  K.mcq = function (el, qs) {
    el.classList.add('mcq');
    let score = 0, done = 0;
    el.innerHTML = qs.map((x, i) => `<div class="mcq-q" data-i="${i}"><p class="mcq-t"><span class="mcq-n">Q${i + 1}</span> ${x.q}${x.a.length > 1 ? ` <em>(Select ${['', '', 'TWO', 'THREE'][x.a.length]}.)</em>` : ''}</p>
      <ol class="mcq-o" type="A">${x.o.map((t, j) => `<li><button type="button" data-j="${j}">${t}</button></li>`).join('')}</ol><p class="mcq-why" hidden></p></div>`).join('')
      + `<p class="mcq-score">Answered 0 of ${qs.length}</p>`;
    const picked = {};
    el.addEventListener('click', e => {
      const b = e.target.closest('button[data-j]'); if (!b) return;
      const box = b.closest('.mcq-q'), i = +box.dataset.i, x = qs[i];
      if (box.classList.contains('done')) return;
      const set = picked[i] = picked[i] || new Set();
      const j = +b.dataset.j;
      set.has(j) ? set.delete(j) : set.add(j); b.classList.toggle('sel', set.has(j));
      if (set.size < x.a.length) return;
      box.classList.add('done');
      const ok = x.a.every(k => set.has(k)) && set.size === x.a.length;
      box.querySelectorAll('button[data-j]').forEach(btn => { const k = +btn.dataset.j; if (x.a.includes(k)) btn.classList.add('right'); else if (set.has(k)) btn.classList.add('wrong'); });
      const w = box.querySelector('.mcq-why'); w.hidden = false;
      w.innerHTML = (ok ? '<span class="ok-text">Correct.</span> ' : `<span class="bad-text">Answer: ${x.a.map(k => 'ABCDE'[k]).join(', ')}.</span> `) + x.why;
      done++; if (ok) score++;
      el.querySelector('.mcq-score').textContent = `Answered ${done} of ${qs.length} · ${score} correct`;
    });
  };

  /* ---------- quick-fire choice drill ----------
     Kit.pick(el, [{ q, a, why }], ['Option A', 'Option B', ...])
     One question at a time, buttons for every option, score, explanation, Next. */
  K.pick = function (el, items, opts) {
    el.classList.add('pick');
    let i = 0, score = 0, answered = false;
    const optsOf = it => it.opts || opts;
    function render() {
      const it = items[i];
      el.innerHTML = `<div class="count">${i + 1} of ${items.length} · score ${score}</div><div class="q">${it.q}</div>
        <div class="opts">${optsOf(it).map(o => `<button class="btn" type="button" data-o="${o.replace(/"/g, '&quot;')}">${o}</button>`).join('')}</div><p class="fb"></p>
        <div><button class="btn primary" type="button" data-next hidden>${i === items.length - 1 ? 'Start again' : 'Next ▶'}</button></div>`;
      answered = false;
    }
    el.addEventListener('click', e => {
      const b = e.target.closest('button'); if (!b) return;
      if (b.dataset.next !== undefined) { i = (i + 1) % items.length; if (i === 0) score = 0; render(); return; }
      if (answered) return; answered = true;
      const it = items[i], ok = b.dataset.o === it.a; if (ok) score++;
      b.classList.add(ok ? 'right' : 'wrong');
      [...el.querySelectorAll('[data-o]')].find(x => x.dataset.o === it.a).classList.add('right');
      el.querySelector('.fb').innerHTML = (ok ? '<span class="ok-text">Right.</span> ' : `<span class="bad-text">It's ${it.a}.</span> `) + it.why;
      el.querySelector('.count').textContent = `${i + 1} of ${items.length} · score ${score}`;
      el.querySelector('[data-next]').hidden = false;
    });
    render();
  };

  /* ---------- request-path diagrams (AWS-style network flows) ----------
     const net = Kit.net(svg, {
       zones: [{ id, x, y, w, h, label, kind: 'region'|'az'|'aws'|'vpc'|'onprem'|'net' }],
       nodes: { id: { x, y, icon, label, sub, kind: 'net'|'compute'|'storage'|'db'|'sec'|'mgmt'|'user'|'plain', badge: 'right'? } },
       links: [{ a, b, via: [[x,y]], kind: 'pub'|'aws'|'priv'|'dash', label }]
     });
     net.node(id) → { g, label(t), sub(t) }      net.state(id, 'on'|'down'|'dim'|'ok'|'')
     net.link(a, b, 'hot'|'cut'|'dim'|'hide'|'')       net.badge(id, text, 'ok'|'bad'|'') / net.badge(id) clears
     await net.send(['user','dns','edge'], { run, label, tone: 'orange'|'cyan'|'green'|'red', speed })
       a glowing dot travels the links in order (constant speed, follows Kit speed / pause / step mode).
     net.focus(ids|null) dims every node, zone and link not listed.  Icons: see Kit.ICONS. */
  K.ICONS = {
    users: '<circle cx="9" cy="8" r="3"/><path d="M3.5 19c0-3.2 2.4-5.5 5.5-5.5s5.5 2.3 5.5 5.5"/><circle cx="16.5" cy="9" r="2.4"/><path d="M15 13.8c3 0 5.5 2 5.5 5"/>',
    user: '<circle cx="12" cy="8" r="3.6"/><path d="M5 20c0-3.9 3.1-6.5 7-6.5s7 2.6 7 6.5"/>',
    laptop: '<rect x="5" y="5" width="14" height="10" rx="1.5"/><path d="M3 18.5h18"/>',
    globe: '<circle cx="12" cy="12" r="8"/><path d="M4 12h16M12 4c2.4 2.3 3.5 5 3.5 8s-1.1 5.7-3.5 8c-2.4-2.3-3.5-5-3.5-8s1.1-5.7 3.5-8z"/>',
    accel: '<circle cx="12" cy="10" r="6.5"/><path d="M5.5 10h13M12 3.5c1.9 1.8 2.7 4 2.7 6.5s-.8 4.7-2.7 6.5c-1.9-1.8-2.7-4-2.7-6.5s.8-4.7 2.7-6.5zM12 16.5v3M7 21h10"/><circle cx="7" cy="21" r=".8"/><circle cx="17" cy="21" r=".8"/>',
    dns: '<path d="M12 3v18M6 6h11l2.5 2.5L17 11H6zM18 13H7l-2.5 2.5L7 18h11z"/>',
    edge: '<rect x="4.5" y="6.5" width="15" height="11" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/><path d="M4.5 12H2M22 12h-2.5"/>',
    lb: '<circle cx="12" cy="5.5" r="2.3"/><circle cx="5" cy="18.5" r="2.3"/><circle cx="12" cy="18.5" r="2.3"/><circle cx="19" cy="18.5" r="2.3"/><path d="M12 7.8v8.4M10.5 7.3 6.2 16.4M13.5 7.3l4.3 9.1"/>',
    server: '<rect x="4.5" y="4" width="15" height="5.5" rx="1.2"/><rect x="4.5" y="11" width="15" height="5.5" rx="1.2"/><path d="M8 6.8h.01M8 13.8h.01M7 20h10"/>',
    chip: '<rect x="7" y="7" width="10" height="10" rx="1.5"/><path d="M10 7V4M14 7V4M10 20v-3M14 20v-3M7 10H4M7 14H4M20 10h-3M20 14h-3"/>',
    db: '<ellipse cx="12" cy="6" rx="7" ry="2.6"/><path d="M5 6v12c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6V6M5 12c0 1.4 3.1 2.6 7 2.6s7-1.2 7-2.6"/>',
    bucket: '<path d="M4.5 6.5h15l-1.8 12.2c-.2 1.2-2.7 2-5.7 2s-5.5-.8-5.7-2z"/><ellipse cx="12" cy="6.5" rx="7.5" ry="2.2"/>',
    disk: '<rect x="5" y="4" width="14" height="16" rx="2"/><circle cx="12" cy="11" r="3.2"/><path d="M8 17.5h8"/>',
    folder: '<path d="M3.5 7.5c0-1 .8-1.8 1.8-1.8h4.2l2 2h7.2c1 0 1.8.8 1.8 1.8v8c0 1-.8 1.8-1.8 1.8H5.3c-1 0-1.8-.8-1.8-1.8z"/>',
    lambda: '<path d="M6 20 11.2 9.5 9 4.5H6.5M11.2 9.5 15.5 19.5H19"/>',
    box: '<path d="m12 3 8 4.5v9L12 21l-8-4.5v-9z"/><path d="m4 7.5 8 4.5 8-4.5M12 12v9"/>',
    shield: '<path d="M12 3 19 6v5.5c0 4.5-3 8-7 9.5-4-1.5-7-5-7-9.5V6z"/>',
    lock: '<rect x="5.5" y="10.5" width="13" height="9.5" rx="2"/><path d="M8.5 10.5V8a3.5 3.5 0 0 1 7 0v2.5"/>',
    key: '<circle cx="8" cy="12" r="3.5"/><path d="M11.5 12H20M17 12v3M20 12v2"/>',
    idcard: '<rect x="3.5" y="5.5" width="17" height="13" rx="2"/><circle cx="9" cy="11" r="2.2"/><path d="M5.8 16c.5-1.6 1.7-2.4 3.2-2.4s2.7.8 3.2 2.4M14.5 10h3.5M14.5 13.5h3.5"/>',
    cloud: '<path d="M7 18.5a4.5 4.5 0 0 1-.6-9 6 6 0 0 1 11.5 1.6A3.8 3.8 0 0 1 17.2 18.5z"/>',
    building: '<path d="M5 21V4.5h9V21M14 9h5v12M3 21h18M8 8h3M8 11.5h3M8 15h3"/>',
    router: '<circle cx="12" cy="12" r="8"/><path d="M12 6v5M9.8 8.2 12 6l2.2 2.2M12 18v-5M9.8 15.8 12 18l2.2-2.2M6 12h5M18 12h-5"/>',
    switch: '<rect x="3" y="8" width="18" height="8" rx="1.5"/><path d="M6.5 12h.01M9.5 12h.01M12.5 12h.01M15.5 12h.01M18 12h.01"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M5.6 18.4l1.8-1.8M16.6 7.4l1.8-1.8"/>',
    chart: '<path d="M4 20h16M7 16.5V11M11 16.5V6.5M15 16.5v-4M19 16.5V9"/>',
    bolt: '<path d="M13 3 5.5 13.5H12L11 21l7.5-10.5H12z"/>',
    flag: '<path d="M6 21V4M6 4.5h11l-2 3.5 2 3.5H6"/>',
    code: '<path d="m8.5 7.5-5 4.5 5 4.5M15.5 7.5l5 4.5-5 4.5M13.5 5l-3 14"/>',
    branch: '<circle cx="6.5" cy="5.5" r="2"/><circle cx="6.5" cy="18.5" r="2"/><circle cx="17.5" cy="8.5" r="2"/><path d="M6.5 7.5v9M17.5 10.5c0 4-5 3-9.5 6.5"/>',
    pipe: '<rect x="2.5" y="9" width="5" height="6" rx="1"/><rect x="9.5" y="9" width="5" height="6" rx="1"/><rect x="16.5" y="9" width="5" height="6" rx="1"/><path d="M7.5 12h2M14.5 12h2"/>',
    dollar: '<circle cx="12" cy="12" r="8.5"/><path d="M14.8 9c-.5-1-1.5-1.6-2.8-1.6-1.6 0-2.8.9-2.8 2.2 0 3 5.8 1.6 5.8 4.6 0 1.3-1.3 2.2-3 2.2-1.4 0-2.5-.6-3-1.7M12 5.8v1.6M12 16.6v1.6"/>',
    eye: '<path d="M2.5 12S6 6 12 6s9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6z"/><circle cx="12" cy="12" r="2.6"/>',
    cpu: '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9.5" y="9.5" width="5" height="5" rx=".8"/><path d="M9.5 6V3.5M14.5 6V3.5M9.5 20.5V18M14.5 20.5V18M6 9.5H3.5M6 14.5H3.5M20.5 9.5H18M20.5 14.5H18"/>',
    ram: '<rect x="3" y="7.5" width="18" height="8" rx="1.2"/><path d="M6.5 10.5v2M10 10.5v2M14 10.5v2M17.5 10.5v2M5 15.5v2M19 15.5v2"/>',
    phone: '<rect x="7" y="3" width="10" height="18" rx="2"/><path d="M11 18h2"/>',
    doc: '<path d="M6.5 3.5h7.5l4 4v13h-11.5z"/><path d="M14 3.5v4h4M9 11.5h6M9 14.5h6M9 17.5h4"/>',
    terminal: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m7 10 3 2-3 2M12.5 15h4"/>',
    crown: '<path d="M4 17.5 3 8l5 4 4-6 4 6 5-4-1 9.5z"/><path d="M4.5 20.5h15"/>',
    ticket: '<path d="M4 7.5h16v3a1.8 1.8 0 0 0 0 3.5v3H4v-3a1.8 1.8 0 0 0 0-3.5z"/><path d="M14 8v8" stroke-dasharray="1.5 2"/>',
    clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v5l3.5 2"/>',
    bug: '<rect x="8" y="8" width="8" height="11" rx="4"/><path d="M12 8V6M9.5 5.5l1.5 1.5M14.5 5.5 13 7M8 12H4.5M19.5 12H16M8 16H5M19 16h-3M8.5 9 6 6.5M15.5 9 18 6.5"/>',
    camera: '<path d="M4 8.5h3.5L9 6h6l1.5 2.5H20v10H4z"/><circle cx="12" cy="13" r="3.4"/>',
    trash: '<path d="M5 7h14M9.5 7V4.5h5V7M7 7l1 13h8l1-13M10.5 10.5v6.5M13.5 10.5v6.5"/>',
    archive: '<rect x="3.5" y="4.5" width="17" height="4.5" rx="1"/><path d="M5 9v10.5h14V9M10 12.5h4"/>',
    layers: '<path d="M12 4 3.5 8.5 12 13l8.5-4.5zM3.5 12.5 12 17l8.5-4.5M3.5 16.5 12 21l8.5-4.5"/>',
  };
  const NET_SPEED = 0.32;                         // px per ms of animation time at 1×
  K.net = function (svg, spec) {
    const zl = K.el('g', { class: 'nf-zones' }, svg), ll = K.el('g', { class: 'nf-links' }, svg);
    const nl = K.el('g', { class: 'nf-nodes' }, svg), dl = K.el('g', { class: 'nf-dots' }, svg);
    const Z = {}, N = {}, L = [];
    (spec.zones || []).forEach(z => {
      const g = K.el('g', { class: 'nf-zone ' + (z.kind || 'region') }, zl);
      K.el('rect', { x: z.x, y: z.y, width: z.w, height: z.h, rx: 12 }, g);
      if (z.label) {
        const flag = z.kind === 'region' || z.kind === 'az';
        if (flag) { K.el('rect', { x: z.x, y: z.y, width: 26, height: 26, rx: 0, class: 'nf-ztab' }, g); const ic = K.el('g', { class: 'nf-zic', transform: `translate(${z.x + 4},${z.y + 4}) scale(.75)` }, g); ic.innerHTML = K.ICONS.flag; }
        const t = K.text(g, z.x + (flag ? 34 : 12), z.y + 18, z.label, 'nf-zlabel'); t.style.textAnchor = 'start';
      }
      Z[z.id || z.label] = g;
    });
    const TILE = 52;
    for (const id in spec.nodes) {
      const n = spec.nodes[id], g = K.el('g', { class: 'nf-node k-' + (n.kind || 'net') }, nl);
      g.dataset.id = id;
      if (n.icon) {
        K.el('rect', { x: n.x - TILE / 2, y: n.y - TILE / 2, width: TILE, height: TILE, rx: 11, class: 'nf-tile' }, g);
        const ic = K.el('g', { class: 'nf-ic', transform: `translate(${n.x - 15},${n.y - 15}) scale(1.25)` }, g);
        ic.innerHTML = K.ICONS[n.icon] || '';
      } else {
        K.el('rect', { x: n.x - (n.w || 110) / 2, y: n.y - 20, width: n.w || 110, height: 40, rx: 10, class: 'nf-chip' }, g);
      }
      const ly = n.icon ? n.y + TILE / 2 + 18 : n.y + 5;
      const lab = K.text(g, n.x, ly, n.label || '', 'nf-label');
      const sub = K.text(g, n.x, ly + 16, n.sub || '', 'nf-sub');
      const x = K.el('g', { class: 'nf-x', transform: `translate(${n.x + TILE / 2 - 4},${n.y - TILE / 2 + 4})` }, g);
      K.el('circle', { r: 11 }, x); K.el('path', { d: 'M-5-5 5 5M5-5-5 5' }, x);
      const badge = K.el('g', { class: 'nf-badge', transform: `translate(${n.x},${n.y - TILE / 2 - 14})` }, g);
      K.el('rect', { x: -30, y: -11, width: 60, height: 22, rx: 11 }, badge); K.text(badge, 0, 4, '', '');
      N[id] = { g, x: n.x, y: n.y, r: n.icon ? TILE / 2 : (n.w || 110) / 2, badge, side: n.badge === 'right',
        label(t) { lab.textContent = t; }, sub(t) { sub.textContent = t; } };
    }
    (spec.links || []).forEach(l => {
      const a = N[l.a], b = N[l.b];
      const pts = [[a.x, a.y], ...(l.via || []), [b.x, b.y]];
      const d = 'M' + pts.map(p => p.join(' ')).join(' L');
      const g = K.el('g', { class: 'nf-link ' + (l.kind || 'pub') }, ll);
      const p = K.el('path', { d }, g);
      if (l.label) {
        const m = l.at || [(pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2 - 8];
        K.text(g, m[0], m[1], l.label, 'nf-llabel');
      }
      L.push({ a: l.a, b: l.b, g, p, len: 0 });
    });
    const findLink = (a, b) => L.find(l => (l.a === a && l.b === b) || (l.a === b && l.b === a));
    const api = {
      nodes: N, zones: Z,
      node: id => N[id],
      state(id, s) { const n = N[id]; ['on', 'down', 'dim', 'ok'].forEach(c => n.g.classList.toggle(c, c === s)); },
      link(a, b, s) { const l = findLink(a, b); if (!l) return; ['hot', 'cut', 'dim', 'hide'].forEach(c => l.g.classList.toggle(c, c === s)); },
      badge(id, text, cls) {
        const bg = N[id].badge; bg.setAttribute('class', 'nf-badge' + (text ? ' show ' + (cls || '') : ''));
        if (text) { bg.querySelector('text').textContent = text; const w = Math.max(44, text.length * 7.4 + 18); const r = bg.querySelector('rect'); r.setAttribute('x', -w / 2); r.setAttribute('width', w);
          const n = N[id]; if (n.side) bg.setAttribute('transform', `translate(${n.x + n.r + 8 + w / 2},${n.y})`); }
      },
      focus(ids) {
        const on = ids ? new Set(ids) : null;
        for (const id in N) N[id].g.classList.toggle('nf-off', !!on && !on.has(id));
        L.forEach(l => l.g.classList.toggle('nf-off', !!on && !(on.has(l.a) && on.has(l.b))));
      },
      reset() { for (const id in N) { api.state(id, ''); api.badge(id); N[id].g.classList.remove('nf-off'); } L.forEach(l => l.g.setAttribute('class', l.g.getAttribute('class').replace(/ (hot|cut|dim|hide|nf-off)/g, ''))); dl.textContent = ''; },
      clearDots() { dl.textContent = ''; },
      /** dot travels node → node along the links; trims the part hidden under the tiles */
      async send(route, o = {}) {
        const run = o.run, tone = o.tone || 'orange', speed = (o.speed || 1) * NET_SPEED;
        const dot = K.el('g', { class: 'nf-dot ' + tone }, dl);
        K.el('circle', { r: 15, class: 'halo' }, dot); K.el('circle', { r: 7, class: 'core' }, dot);
        let tag = null;
        if (o.label) { tag = K.el('g', { class: 'nf-dtag', transform: 'translate(0,-22)' }, dot); const w = o.label.length * 7 + 16; K.el('rect', { x: -w / 2, y: -10, width: w, height: 20, rx: 10 }, tag); K.text(tag, 0, 4, o.label, ''); }
        dot.setAttribute('transform', 'translate(-99,-99)');
        try {
          await K.gate(run);
          for (let i = 0; i < route.length - 1; i++) {
            const l = findLink(route[i], route[i + 1]);
            if (!l) throw new Error('Kit.net: no link ' + route[i] + '→' + route[i + 1]);
            const fwd = l.a === route[i], len = l.p.getTotalLength();
            const r0 = N[route[i]].r * (i === 0 ? 0.55 : 0.55), r1 = N[route[i + 1]].r * 0.55;
            const s0 = Math.min(r0, len / 3), s1 = Math.max(len - r1, len * 2 / 3);
            const span = s1 - s0, ms = (K.reduce ? 1 : span / speed);
            l.g.classList.add('live');
            await new Promise((res, rej) => {
              let k = 0, last = performance.now();
              (function f(t) {
                if (!K.alive(run)) return rej(new Stop());
                k = Math.min(1, k + K.tick(Math.max(0, t - last)) / ms); last = t;
                const at = fwd ? s0 + span * k : len - (s0 + span * k);
                const pt = l.p.getPointAtLength(at);
                dot.setAttribute('transform', `translate(${pt.x.toFixed(1)},${pt.y.toFixed(1)})`);
                k < 1 ? requestAnimationFrame(f) : res();
              })(last);
            });
            l.g.classList.remove('live');
            if (o.onHop) o.onHop(route[i + 1], i + 1);
          }
        } finally { if (!o.keep) dot.remove(); L.forEach(l => l.g.classList.remove('live')); }
        return dot;
      }
    };
    return api;
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
