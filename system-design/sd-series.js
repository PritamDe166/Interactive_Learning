/* System Design shared page wiring (HLD + LLD).
   One list of every explainer in learning order. Each page calls SD.page({ track, file }) and gets:
     #series   → strip of the pages in the same week / phase (current one highlighted)
     #pageNav  → numbered section menu pinned in the top bar (Kit.pageNav, built from section[data-nav])
     #prevnext → previous / next page across the whole track
   SD.story(root, o) is the step-by-step walkthrough on a Kit.mini stage (same as CF.story).
   SD.drill(el, items, opts) is a one-at-a-time "which one fits?" drill (Kit.pick). */
(function () {
  const HLD = [
    { g: 'Week 1 · Networking', pages: [
      ['client-server-dns.html', 'H1 DNS', 'Client-server & DNS'],
      ['http.html', 'H2 HTTP', 'HTTP'],
      ['tcp-udp.html', 'H3 TCP/UDP', 'TCP & UDP'],
      ['https-tls.html', 'H4 TLS', 'HTTPS & TLS'],
      ['latency-throughput.html', 'H5 Latency', 'Latency & throughput'],
      ['availability-slos.html', 'H6 Availability', 'Availability, SLOs & recovery'],
      ['week-1-review.html', 'H7 Review', 'Review: journey of a request']] },
    { g: 'Week 2 · Scaling', pages: [
      ['scaling.html', 'H8 Scaling', 'Vertical vs horizontal scaling'],
      ['stateless.html', 'H9 Stateless', 'Stateless applications'],
      ['proxy-lb-gateway.html', 'H10–12 Proxy · Gateway · LB', 'Reverse proxy, API gateway & load balancers'],
      ['load-balancing-algorithms.html', 'H13 LB algorithms', 'Load-balancing algorithms'],
      ['scale-web-app.html', 'H14 Design', 'Design: scale a web app to millions']] },
    { g: 'Week 3 · Caching', pages: [
      ['caching-overview.html', 'H15 Why cache', 'Why caching exists'],
      ['cache-read-strategies.html', 'H16 Read', 'Read strategies'],
      ['cache-write-strategies.html', 'H17 Write', 'Write strategies & invalidation'],
      ['cache-eviction.html', 'H18 Eviction', 'Eviction policies'],
      ['distributed-caching.html', 'H19 Distributed', 'Distributed caching'],
      ['cache-failure-modes.html', 'H20 Failures', 'Caching failure modes'],
      ['cdn-http-caching.html', 'H21 CDN & HTTP', 'CDN & HTTP caching'],
      ['caching-in-practice.html', 'Playbook', 'Caching in practice: the interview playbook'],
      ['caching-patterns-atlas.html', 'All patterns', 'All caching patterns at a glance']] }
  ];
  const LLD = [
    { g: 'Phase 2 · SOLID', pages: [
      ['solid.html', 'L6 Overview', 'SOLID overview'],
      ['solid-srp.html', 'L7 S', 'S · Single responsibility'],
      ['solid-ocp.html', 'L8 O', 'O · Open-closed'],
      ['solid-lsp.html', 'L9 L', 'L · Liskov substitution'],
      ['solid-isp.html', 'L10 I', 'I · Interface segregation'],
      ['solid-dip.html', 'L11 D', 'D · Dependency inversion']] },
    { g: 'Phase 3 · Creational patterns', pages: [
      ['singleton.html', 'L12 Singleton', 'Singleton'],
      ['factory-method.html', 'L13 Factory', 'Simple factory & factory method'],
      ['abstract-factory.html', 'L14 Abstract factory', 'Abstract factory'],
      ['builder.html', 'L15 Builder', 'Builder'],
      ['prototype.html', 'L16 Prototype', 'Prototype']] }
  ];
  const TRACKS = { hld: HLD, lld: LLD };
  const flat = t => TRACKS[t].flatMap(g => g.pages.map(p => p.concat(g.g)));
  const guess = () => location.pathname.includes('/lld/') ? 'lld' : 'hld';
  const here = () => decodeURIComponent(location.pathname.split('/').pop() || 'index.html');

  function series(el, file, track) {
    track = track || guess(); file = file || here();
    const grp = TRACKS[track].find(g => g.pages.some(p => p[0] === file));
    if (!grp) return;
    el.classList.add('series'); el.setAttribute('aria-label', grp.g + ' pages');
    el.innerHTML = `<span class="lbl">${grp.g}</span>` + grp.pages.map(([f, s, t]) => `<a href="${f}" title="${t}"${f === file ? ' aria-current="page"' : ''}>${s}</a>`).join('');
  }
  function prevNext(el, file, track) {
    track = track || guess(); file = file || here();
    const all = flat(track), i = all.findIndex(x => x[0] === file);
    el.classList.add('prevnext');
    const p = all[i - 1], n = all[i + 1], idx = 'index.html', road = track === 'lld' ? 'LLD roadmap' : 'HLD roadmap';
    el.innerHTML = (p ? `<a class="prev" href="${p[0]}"><small>← Previous</small>${p[2]}</a>` : `<a class="prev" href="${idx}"><small>← Back to</small>${road}</a>`)
      + (n ? `<a class="next" href="${n[0]}"><small>Next →</small>${n[2]}</a>` : `<a class="next" href="${idx}"><small>Done · back to</small>${road}</a>`);
  }
  function story(root, o) {
    root = typeof root === 'string' ? document.getElementById(root) : root;
    const wrap = document.createElement('div'); wrap.className = 'at-stage' + (o.tone ? ' tone-' + o.tone : '');
    const [w, h] = o.vb || [420, 220];
    wrap.innerHTML = `<svg viewBox="0 0 ${w} ${h}" role="img" aria-label="${(o.alt || 'Animated diagram').replace(/"/g, '')}"></svg>`;
    root.appendChild(wrap);
    const m = Kit.mini(wrap.querySelector('svg'));
    o.build(m);
    const show = i => { m.reset(); if (o.reset) o.reset(m); const st = o.steps[i]; if (st.set) st.set(m); };
    const steps = o.steps.map(st => ({ title: st.title, text: st.text, tip: st.tip, play: st.play ? (run => st.play(m, run)) : undefined }));
    Kit.story({ root, steps, show, tipLabel: o.tipLabel || 'Interview tip' });
    return m;
  }
  /** items: [{ q, a, why, opts? }]; opts: default option list */
  function drill(el, items, opts) { Kit.pick(el, items, opts); }
  /** wire the standard page furniture; extra: { atlas: cards, drill: { items, opts } } */
  function page(o = {}) {
    const $ = id => document.getElementById(id);
    if ($('series')) series($('series'), o.file, o.track);
    if ($('pageNav')) Kit.pageNav($('pageNav'));
    if (o.atlas && $('atlas')) Kit.atlas($('atlas'), { cards: o.atlas });
    if (o.drill && $('drill')) drill($('drill'), o.drill.items, o.drill.opts);
    if ($('prevnext')) prevNext($('prevnext'), o.file, o.track);
  }
  window.SD = { HLD, LLD, series, prevNext, story, drill, page, pages: flat };
})();
