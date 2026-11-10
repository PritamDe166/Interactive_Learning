/* =========================================================================
   caching-flows.js — shared animated cards and walkthrough helper for the
   Week 3 caching pages (system-design/hld/cache-*.html, cdn-http-caching.html,
   caching-patterns-atlas.html). Load after explainer-kit.js.

   CF.cards(['aside', 'lru', …], { links }) → card specs for Kit.atlas; links: true adds a "Deep dive →" to each card's page
   CF.quiz(['aside', …])          → "which one fits?" scenarios whose answer is one of those ids
   CF.story(root, { vb, tone, build(m), steps: [{ title, text, tip?, set?(m), play?(m, run) }] })
       A Kit.story walkthrough drawn with Kit.mini: build(m) draws the fixed diagram once;
       set(m) puts step i's finished state on screen (after a reset); play(m, run) animates it.
   CF.ttlBar(m, x, y, w) → { set(fraction, 'warn'|'gone'|'', text), to(m, run, from, to, ms, state, textFn) }
   Timings shown in the diagrams are illustrative.
   ========================================================================= */
(function () {
  const ttlBar = (m, x, y, w, label) => {
    const g = Kit.el('g', { class: 'cf-ttl' }, m.svg);
    Kit.el('rect', { class: 'cf-track', x, y, width: w, height: 6, rx: 3 }, g);
    const f = Kit.el('rect', { class: 'cf-fill', x, y, width: w, height: 6, rx: 3 }, g);
    const t = Kit.text(g, x + w / 2, y + 18, label || '', 'at-nsub');
    return {
      set(k, s, txt) { f.setAttribute('width', Math.max(0, w * k)); g.setAttribute('class', 'cf-ttl ' + (s || '')); if (txt !== undefined) t.textContent = txt; },
      async to(m, run, from, to, ms, s, txt) { const n = 16; for (let i = 1; i <= n; i++) { const k = from + (to - from) * i / n; this.set(k, s, typeof txt === 'function' ? txt(k) : txt); await m.sleep(ms / n, run); } }
    };
  };
  const trio = m => { m.box('app', 58, 78, 'App', { icon: 'server', w: 84 }); m.box('cache', 195, 34, 'Cache', { icon: 'ram', w: 84 }); m.db('db', 305, 92, 'Database'); m.wire('app', 'cache'); m.wire('app', 'db'); };
  const line3 = m => { m.box('app', 48, 70, 'App', { icon: 'server', w: 78 }); m.box('cache', 180, 70, 'Cache', { icon: 'ram', w: 84 }); m.db('db', 310, 68, 'Database'); m.wire('app', 'cache'); m.wire('cache', 'db'); };
  const all = (arr, f) => Promise.all(arr.map(f));

  /* ---------------- cards ---------------- */
  const CARDS = {
    /* ---- read path ---- */
    aside: { name: 'Cache-aside', tone: 'cyan', tags: ['read path'],
      rule: 'The app checks the cache; on a miss it reads the DB and fills the cache itself. Also called lazy loading.',
      takeaway: 'Only data someone asked for gets cached.',
      use: 'Read-heavy data; the default with Redis and <code>IMemoryCache</code>.', avoid: 'First read is slow; data stale until TTL or delete.',
      build(m) { trio(m); return [
        { cap: 'GET <b>product:12</b> from the cache → <b class="bad-text">miss</b>', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'GET' }); m.badge('cache', 'MISS', 'red'); await m.send(['cache', 'app'], { run: r, tone: 'muted' }); } },
        { cap: 'The app reads the row from the database', go: async r => { m.state('db', 'on'); await m.send(['app', 'db'], { run: r, label: 'SELECT' }); await m.send(['db', 'app'], { run: r, tone: 'yellow' }); } },
        { cap: 'The app writes it into the cache with a TTL', go: async r => { m.state('db', ''); await m.send(['app', 'cache'], { run: r, label: 'SET ttl=5m' }); m.badge('cache', 'stored', 'teal'); } },
        { cap: 'Next read → <b class="ok-text">hit</b>; the database is not touched', go: async r => { m.state('db', 'dim'); await m.send(['app', 'cache'], { run: r, label: 'GET' }); m.badge('cache', 'HIT', 'teal'); m.state('cache', 'ok'); await m.send(['cache', 'app'], { run: r, tone: 'teal' }); } }
      ]; } },

    'through-read': { name: 'Read-through', tone: 'violet', tags: ['read path'],
      rule: 'The app only talks to the cache. On a miss the cache provider loads from the DB, stores it and returns it.',
      takeaway: 'Same flow as cache-aside, but the loading code lives in the cache layer.',
      use: 'You want one place that knows how to load (a library or provider).', avoid: 'The cache layer now depends on your database schema.',
      build(m) { line3(m); return [
        { cap: 'App asks the cache only', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'GET' }); m.badge('cache', 'MISS', 'red'); } },
        { cap: 'The <b>cache</b> loads the row from the database', go: async r => { m.state('db', 'on'); await m.send(['cache', 'db'], { run: r, label: 'load' }); await m.send(['db', 'cache'], { run: r, tone: 'yellow' }); m.badge('cache', 'stored', 'teal'); m.state('db', ''); } },
        { cap: 'Cache returns the value; the app never saw the miss', go: async r => { await m.send(['cache', 'app'], { run: r, tone: 'yellow' }); } },
        { cap: 'Later reads are hits', go: async r => { m.state('db', 'dim'); await m.send(['app', 'cache'], { run: r, label: 'GET' }); m.badge('cache', 'HIT', 'teal'); m.state('cache', 'ok'); await m.send(['cache', 'app'], { run: r, tone: 'teal' }); } }
      ]; } },

    refresh: { name: 'Refresh-ahead', tone: 'teal', tags: ['read path'],
      rule: 'Before a popular entry expires, the cache reloads it in the background, so no reader waits on a miss.',
      takeaway: 'Hot keys never expire in front of a user.',
      use: 'Expensive, predictable, hot data (home page, config, price lists).', avoid: 'Refreshes keys nobody reads again; needs a good guess of what\'s hot.',
      build(m) { line3(m); const bar = ttlBar(m, 120, 118, 120, ''); m._bar = bar; return [
        { cap: 'Reads hit while the entry is fresh', go: async r => { m.badge('cache', 'v1', 'teal'); await m.send(['app', 'cache'], { run: r, label: 'GET' }); await bar.to(m, r, 1, 0.45, 1300, '', k => `TTL left ${Math.round(k * 100)}%`); } },
        { cap: 'At ~80% of the TTL, a read triggers a background reload', go: async r => { await bar.to(m, r, 0.45, 0.2, 700, 'warn', k => `TTL left ${Math.round(k * 100)}% · refresh`); m.state('db', 'on'); await m.send(['cache', 'db'], { run: r, label: 'reload' }); await m.send(['db', 'cache'], { run: r, tone: 'yellow' }); m.state('db', ''); } },
        { cap: 'Entry replaced <b>before</b> it expired: TTL starts again', go: async r => { m.badge('cache', 'v2', 'teal'); m.state('cache', 'ok'); bar.set(1, '', 'TTL left 100%'); await m.send(['app', 'cache'], { run: r, label: 'GET' }); } }
      ]; },
      reset(m) { m._bar && m._bar.set(1, '', 'TTL left 100%'); } },

    /* ---- write path ---- */
    wthrough: { name: 'Write-through', tone: 'blue', tags: ['write path'],
      rule: 'Every write goes to the cache and on to the database in the same request; the client gets its ack only after both.',
      takeaway: 'Cache is never behind the DB; every write pays two hops.',
      use: 'Data read right after it is written (profiles, carts, settings).', avoid: 'Slower writes; fills the cache with data nobody may read.',
      build(m) { line3(m); return [
        { cap: 'App writes <b>cart:7</b> to the cache', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'SET' }); m.badge('cache', 'v2', 'teal'); } },
        { cap: 'The cache writes it to the database <b>synchronously</b>', go: async r => { m.state('db', 'on'); await m.send(['cache', 'db'], { run: r, label: 'write' }); m.badge('db', 'v2', 'teal'); } },
        { cap: 'Only now is the write acknowledged', go: async r => { await m.send(['db', 'cache', 'app'], { run: r, label: 'ACK', tone: 'teal' }); m.state('db', ''); m.state('cache', 'ok'); } }
      ]; } },

    wbehind: { name: 'Write-behind (write-back)', tone: 'orange', tags: ['write path'],
      rule: 'Writes land in the cache and are acknowledged at once; the cache flushes them to the DB later, in batches.',
      takeaway: 'Fastest writes, but the buffer can be lost.',
      use: 'Very high write rates where small loss is acceptable (counters, metrics, likes).', avoid: 'Money, orders, anything you must not lose.',
      vb: [360, 160],
      build(m) { m.box('app', 48, 55, 'App', { icon: 'server', w: 78 }); m.box('cache', 178, 55, 'Cache', { icon: 'ram', w: 84 }); m.db('db', 312, 92, 'Database'); m.wire('app', 'cache'); const s = m.slots('buf', 178, 122, 4, { label: 'write buffer' }); m.wire('buf', 'db');
        return [
          { cap: 'Three writes, each acked straight away', go: async r => { const v = []; for (const w of ['w1', 'w2', 'w3']) { await m.send(['app', 'cache'], { run: r, label: w, ms: 420 }); v.push({ t: w }); s.set(v); } } },
          { cap: 'Later, one batch goes to the database', go: async r => { m.state('db', 'on'); await m.send(['buf', 'db'], { run: r, label: 'batch ×3' }); s.set([]); m.badge('db', '+3', 'teal'); m.state('db', ''); } },
          { cap: 'A new write w4 is buffered… and the cache node <b class="bad-text">crashes</b>', go: async r => { m.badge('db'); await m.send(['app', 'cache'], { run: r, label: 'w4', ms: 420 }); s.set([{ t: 'w4' }]); await m.sleep(500, r); m.state('cache', 'hot'); m.badge('cache', 'crash', 'red'); s.set([{ t: 'w4', tone: 'red' }]); } },
          { cap: '<b class="bad-text">w4 is lost</b>: the client was told it was saved', go: async r => { await m.sleep(400, r); s.set([]); } }
        ]; } },

    waround: { name: 'Write-around', tone: 'yellow', tags: ['write path'],
      rule: 'Writes skip the cache and go straight to the DB; the cache fills only when something is read.',
      takeaway: 'Keeps write-only data from pushing useful entries out.',
      use: 'Logs, audit trails, bulk imports: written a lot, read rarely.', avoid: 'Read-right-after-write always misses.',
      build(m) { trio(m); return [
        { cap: 'INSERT goes straight to the database; cache untouched', go: async r => { m.state('cache', 'dim'); m.state('db', 'on'); await m.send(['app', 'db'], { run: r, label: 'INSERT' }); m.state('db', ''); m.state('cache', ''); } },
        { cap: 'Someone reads it later → miss', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'GET' }); m.badge('cache', 'MISS', 'red'); } },
        { cap: 'Loaded from the DB and cached on the way back (cache-aside)', go: async r => { await m.send(['app', 'db'], { run: r, label: 'SELECT' }); await m.send(['db', 'app'], { run: r, tone: 'yellow' }); await m.send(['app', 'cache'], { run: r, label: 'SET' }); m.badge('cache', 'stored', 'teal'); } }
      ]; } },

    invalidate: { name: 'Invalidate on write', tone: 'red', tags: ['write path'],
      rule: 'When data changes, update the DB, then <b>delete</b> the cache key. The next read loads the new value.',
      takeaway: 'Delete, don\'t overwrite: a late overwrite can put an old value back.',
      use: 'The usual write rule alongside cache-aside.', avoid: 'Brief window where a reader can still see the old value.',
      build(m) { trio(m); return [
        { cap: 'Cache holds <b>price = ₹499</b>', go: async r => { m.badge('cache', '₹499'); await m.sleep(500, r); } },
        { cap: 'UPDATE the price in the database', go: async r => { m.state('db', 'on'); await m.send(['app', 'db'], { run: r, label: 'UPDATE ₹449' }); m.badge('db', '₹449', 'teal'); m.state('db', ''); } },
        { cap: 'DEL the key; don\'t SET it', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'DEL', tone: 'red' }); m.badge('cache', 'gone', 'muted'); } },
        { cap: 'Next read misses and reloads ₹449', go: async r => { m.badge('db'); await m.send(['app', 'cache'], { run: r, label: 'GET' }); await m.send(['app', 'db'], { run: r, label: 'SELECT' }); await m.send(['db', 'app'], { run: r, tone: 'yellow' }); await m.send(['app', 'cache'], { run: r, label: 'SET' }); m.badge('cache', '₹449', 'teal'); } }
      ]; } },

    stale: { name: 'Stale data', tone: 'red', tags: ['failure', 'write path'],
      rule: 'The database changes but the cache still holds the old copy, so readers get yesterday\'s answer until the key goes.',
      takeaway: 'Every cache is a copy; decide how stale is acceptable and how the copy gets fixed.',
      use: '(failure mode) Any write path that forgets the cache.', avoid: 'Fix with delete-on-write, short TTLs, or events that invalidate.',
      build(m) { trio(m); return [
        { cap: 'Cache and DB agree: <b>stock = 5</b>', go: async r => { m.badge('cache', 'stock 5'); m.badge('db', 'stock 5'); await m.sleep(500, r); } },
        { cap: 'An order updates the DB only', go: async r => { m.state('db', 'on'); await m.send(['app', 'db'], { run: r, label: 'UPDATE stock=0' }); m.badge('db', 'stock 0', 'teal'); m.state('db', ''); } },
        { cap: 'Readers still get <b class="bad-text">stock 5</b> from the cache', go: async r => { for (let k = 0; k < 2; k++) { await m.send(['app', 'cache'], { run: r, label: 'GET', ms: 420 }); await m.send(['cache', 'app'], { run: r, tone: 'red', ms: 420 }); } m.state('cache', 'hot'); } },
        { cap: 'Fix: DEL on write (or a short TTL) so the next read reloads 0', go: async r => { m.state('cache', ''); await m.send(['app', 'cache'], { run: r, label: 'DEL', tone: 'red' }); m.badge('cache', 'gone', 'muted'); } }
      ]; } },

    /* ---- eviction ---- */
    lru: { name: 'LRU eviction', tone: 'yellow', tags: ['eviction'],
      rule: 'When the cache is full, evict the key used <b>least recently</b>.',
      takeaway: 'Same reads as the LFU card: LRU throws out A, the popular key.',
      use: 'Recent data is likely to be read again (most workloads, Redis allkeys-lru).', avoid: 'One-off scans push hot keys out.',
      build(m) { const s = m.slots('c', 180, 72, 3, { w: 34, label: '3 slots · least recent ← → most recent' }); const seq = m.label(180, 128, '', 'at-small'); m._seq = seq;
        const show = arr => s.set(arr.map(k => ({ t: k, tone: k === 'D' ? 'yellow' : '' })));
        return [
          { cap: 'Read <b>A</b> three times (it\'s popular)', go: async r => { seq.textContent = 'reads: A A A'; show(['A']); await m.sleep(700, r); } },
          { cap: 'Read B, then C: cache is full', go: async r => { seq.textContent = 'reads: A A A B'; show(['A', 'B']); await m.sleep(500, r); seq.textContent = 'reads: A A A B C'; show(['A', 'B', 'C']); await m.sleep(500, r); } },
          { cap: 'D arrives: A was used longest ago → <b class="bad-text">A evicted</b>', go: async r => { seq.textContent = 'reads: A A A B C D'; s.set([{ t: 'A', tone: 'red' }, { t: 'B' }, { t: 'C' }]); await m.sleep(700, r); show(['B', 'C', 'D']); } }
        ]; },
      reset(m) { m._seq && (m._seq.textContent = ''); } },

    lfu: { name: 'LFU eviction', tone: 'violet', tags: ['eviction'],
      rule: 'When the cache is full, evict the key used <b>least often</b> (ties: the older one).',
      takeaway: 'LFU keeps A; but a once-popular key can squat forever without ageing.',
      use: 'A stable set of hot keys mixed with one-off reads (Redis allkeys-lfu).', avoid: 'Popularity that shifts; needs counter decay.',
      build(m) { const s = m.slots('c', 180, 72, 3, { w: 34, label: '3 slots · read count under each key' }); const seq = m.label(180, 128, '', 'at-small'); const cnt = [0, 1, 2].map(i => m.label(180 - 38 + i * 38, 104, '', 'at-small')); m._seq = seq; m._cnt = cnt;
        const show = arr => { s.set(arr.map(([k, c, tone]) => ({ t: k, tone }))); cnt.forEach((t, i) => t.textContent = arr[i] ? '×' + arr[i][1] : ''); };
        return [
          { cap: 'Read <b>A</b> three times', go: async r => { seq.textContent = 'reads: A A A'; show([['A', 3]]); await m.sleep(700, r); } },
          { cap: 'Read B, then C: cache is full', go: async r => { seq.textContent = 'reads: A A A B C'; show([['A', 3], ['B', 1], ['C', 1]]); await m.sleep(700, r); } },
          { cap: 'D arrives: B and C were read once; B is older → <b class="bad-text">B evicted</b>, A stays', go: async r => { seq.textContent = 'reads: A A A B C D'; show([['A', 3], ['B', 1, 'red'], ['C', 1]]); await m.sleep(700, r); show([['A', 3], ['C', 1], ['D', 1, 'yellow']]); } }
        ]; },
      reset(m) { m._seq && (m._seq.textContent = ''); m._cnt && m._cnt.forEach(t => t.textContent = ''); } },

    fifo: { name: 'FIFO eviction', tone: 'blue', tags: ['eviction'],
      rule: 'When the cache is full, evict the key that was <b>inserted first</b>, however often it is read.',
      takeaway: 'Simplest to build, but blind to use: A goes even though it was just read.',
      use: 'Data that ages out naturally (a queue of recent events).', avoid: 'Hot keys that were cached early get evicted.',
      build(m) { const s = m.slots('c', 180, 72, 3, { w: 34, label: '3 slots · inserted first ← → inserted last' }); const seq = m.label(180, 128, '', 'at-small'); m._seq = seq;
        return [
          { cap: 'Insert A, B, C (cache full)', go: async r => { for (const [i, k] of ['A', 'B', 'C'].entries()) { seq.textContent = 'reads: ' + ['A', 'B', 'C'].slice(0, i + 1).join(' '); s.set(['A', 'B', 'C'].slice(0, i + 1).map(t => ({ t }))); await m.sleep(450, r); } } },
          { cap: 'Read A twice: hits, but FIFO order does not change', go: async r => { seq.textContent = 'reads: A B C A A'; s.set([{ t: 'A', tone: 'yellow' }, { t: 'B' }, { t: 'C' }]); await m.sleep(800, r); } },
          { cap: 'D arrives: A was inserted first → <b class="bad-text">A evicted</b> (LRU would evict B)', go: async r => { seq.textContent = 'reads: A B C A A D'; s.set([{ t: 'A', tone: 'red' }, { t: 'B' }, { t: 'C' }]); await m.sleep(700, r); s.set([{ t: 'B' }, { t: 'C' }, { t: 'D', tone: 'yellow' }]); } }
        ]; },
      reset(m) { m._seq && (m._seq.textContent = ''); } },

    ttl: { name: 'TTL expiry', tone: 'teal', tags: ['eviction'],
      rule: 'Every key gets a time-to-live; when it runs out the key disappears and the next read reloads it.',
      takeaway: 'TTL caps how stale data can get. Add jitter so keys don\'t all expire together.',
      use: 'Any cached copy of data that changes; a safety net even with invalidation.', avoid: 'Too short: few hits. Too long: stale data.',
      build(m) { trio(m); const bar = ttlBar(m, 150, 128, 110, ''); m._bar = bar; return [
        { cap: 'SET <b>doctor:42</b> with TTL 60 s', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'SET ttl=60s' }); bar.set(1, '', '60 s left'); } },
        { cap: 'Time passes; reads hit', go: async r => { m.send(['app', 'cache'], { run: r, label: 'GET' }).catch(() => {}); await bar.to(m, r, 1, 0, 1800, '', k => `${Math.round(k * 60)} s left`); } },
        { cap: 'TTL hits 0: the key <b>expires</b>', go: async r => { bar.set(0, 'gone', 'expired'); m.badge('cache', 'expired', 'muted'); await m.sleep(400, r); } },
        { cap: 'Next read misses and reloads fresh data', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'GET' }); m.badge('cache', 'MISS', 'red'); await m.send(['app', 'db'], { run: r, label: 'SELECT' }); await m.send(['db', 'app'], { run: r, tone: 'yellow' }); await m.send(['app', 'cache'], { run: r, label: 'SET' }); m.badge('cache', 'fresh', 'teal'); bar.set(1, '', '60 s left'); } }
      ]; },
      reset(m) { m._bar && m._bar.set(1, '', ''); } },

    /* ---- failure modes ---- */
    stampede: { name: 'Cache stampede', tone: 'red', tags: ['failure'],
      rule: 'A hot key expires and many requests miss at once; every one of them runs the same expensive DB query.',
      takeaway: 'Fix: single-flight (one loader, others wait), stale-while-revalidate, TTL jitter.',
      use: '(failure mode) Expect it on any hot key with a TTL.', avoid: 'HybridCache single-flight is per server, not cluster-wide.',
      vb: [360, 160],
      build(m) { const ys = [24, 58, 92, 126]; ys.forEach((y, i) => m.box('r' + i, 36, y, 'req ' + (i + 1), { w: 50, h: 22 })); m.box('cache', 190, 30, 'Cache', { icon: 'ram', w: 84 }); m.db('db', 305, 104, 'Database');
        ys.forEach((y, i) => { m.wire('r' + i, 'cache', { dash: true }); m.wire('r' + i, 'db'); });
        return [
          { cap: 'Hot key <b>product:12</b> expires', go: async r => { m.badge('cache', 'expired', 'muted'); await m.sleep(500, r); } },
          { cap: '4 requests miss at the same moment…', go: async r => { await all(ys, (_, i) => m.send(['r' + i, 'cache'], { run: r, tone: 'muted', ms: 600 })); } },
          { cap: '…and all 4 run the same query → <b class="bad-text">DB overloaded</b>', go: async r => { await all(ys, (_, i) => m.send(['r' + i, 'db'], { run: r, tone: 'red', ms: 750 })); m.state('db', 'hot'); m.badge('db', 'CPU 100%', 'red'); await m.sleep(600, r); } },
          { cap: 'Fix · single-flight: req 1 loads, req 2–4 <b>wait</b> for its result', go: async r => { m.state('db', ''); m.badge('db'); ['r1', 'r2', 'r3'].forEach(id => m.state(id, 'dim')); await m.send(['r0', 'db'], { run: r, tone: 'teal' }); await m.send(['db', 'r0'], { run: r, tone: 'yellow' }); m.badge('cache', 'filled', 'teal'); ['r0', 'r1', 'r2', 'r3'].forEach(id => m.state(id, 'ok')); } }
        ]; } },

    swr: { name: 'Stale-while-revalidate', tone: 'teal', tags: ['failure'],
      rule: 'When an entry goes stale, keep serving the old copy instantly while <b>one</b> background refresh fetches the new one.',
      takeaway: 'Nobody waits and only one query reaches the DB.',
      use: 'Data where a few seconds of staleness is fine (catalogues, feeds, dashboards).', avoid: 'Balances, stock at checkout: anything that must be exact.',
      build(m) { trio(m); const bar = ttlBar(m, 150, 128, 110, ''); m._bar = bar; return [
        { cap: 'Entry is fresh for 60 s, then usable-but-stale for 30 s more', go: async r => { m.badge('cache', 'v1', 'teal'); await bar.to(m, r, 1, 0, 1200, '', k => k > 0 ? `fresh ${Math.round(k * 60)} s` : 'stale'); bar.set(1, 'warn', 'stale window'); } },
        { cap: 'A read in the stale window gets <b>v1 instantly</b>…', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'GET' }); await m.send(['cache', 'app'], { run: r, tone: 'yellow', label: 'v1 (stale)' }); } },
        { cap: '…and triggers <b>one</b> background refresh', go: async r => { m.state('db', 'on'); await m.send(['app', 'db'], { run: r, label: 'refresh' }); await m.send(['db', 'app'], { run: r, tone: 'yellow' }); await m.send(['app', 'cache'], { run: r, label: 'SET v2' }); m.state('db', ''); m.badge('cache', 'v2', 'teal'); bar.set(1, '', 'fresh 60 s'); } }
      ]; },
      reset(m) { m._bar && m._bar.set(1, '', ''); } },

    penetration: { name: 'Cache penetration', tone: 'orange', tags: ['failure'],
      rule: 'Requests for keys that don\'t exist anywhere always miss, so every one reaches the database.',
      takeaway: 'Fix: cache the "not found" (short TTL) or check a Bloom filter first.',
      use: '(failure mode) Bots, scrapers, bad client IDs.', avoid: 'Negative entries must expire, or new records stay "missing".',
      build(m) { m.box('app', 58, 78, 'Bot', { icon: 'bug', w: 80 }); m.box('cache', 195, 34, 'Cache', { icon: 'ram', w: 84 }); m.db('db', 305, 92, 'Database'); m.wire('app', 'cache'); m.wire('app', 'db');
        return [
          { cap: 'GET <b>patient:999999</b> → miss', go: async r => { await m.send(['app', 'cache'], { run: r, label: 'GET' }); m.badge('cache', 'MISS', 'red'); } },
          { cap: 'Not in the DB either: nothing to cache', go: async r => { await m.send(['app', 'db'], { run: r, label: 'SELECT' }); m.badge('db', 'no row', 'muted'); await m.send(['db', 'app'], { run: r, tone: 'muted' }); } },
          { cap: 'So every repeat hits the database again', go: async r => { m.badge('db'); for (let k = 0; k < 3; k++) await m.send(['app', 'db'], { run: r, tone: 'red', ms: 380 }); m.state('db', 'hot'); } },
          { cap: 'Fix: store <b>NULL</b> with a short TTL; repeats stop at the cache', go: async r => { m.state('db', 'dim'); m.badge('cache', 'NULL ttl=30s', 'teal'); for (let k = 0; k < 2; k++) await m.send(['app', 'cache'], { run: r, tone: 'teal', ms: 380 }); } }
        ]; } },

    avalanche: { name: 'Cache avalanche', tone: 'red', tags: ['failure'],
      rule: 'Many keys expire at the same moment (or a cache node dies), so a flood of misses hits the DB together.',
      takeaway: 'Fix: add random jitter to TTLs, warm the cache gradually, protect the DB with limits.',
      use: '(failure mode) Bulk loads with one TTL, cache restarts.', avoid: 'Jitter spreads load; it doesn\'t remove it.',
      vb: [360, 160],
      build(m) { m.box('app', 50, 80, 'App', { icon: 'server', w: 78 }); const s = m.slots('keys', 190, 38, 6, { w: 20, label: 'keys loaded at 09:00, TTL 1 h' }); m.db('db', 305, 112, 'Database'); m.wire('app', 'keys', { dash: true }); m.wire('app', 'db'); m._s = s;
        const full = (tone) => s.set(Array.from({ length: 6 }, (_, i) => ({ t: 'k' + (i + 1), tone })));
        return [
          { cap: '6 popular keys all cached at 09:00 with the <b>same</b> TTL', go: async r => { full(''); await m.sleep(700, r); } },
          { cap: 'At 10:00 they all expire together', go: async r => { full('muted'); await m.sleep(400, r); s.set([]); } },
          { cap: 'Every one misses at once → <b class="bad-text">DB flooded</b>', go: async r => { await all([0, 1, 2, 3, 4, 5], i => m.send(['app', 'db'], { run: r, tone: 'red', ms: 500 + i * 60 })); m.state('db', 'hot'); m.badge('db', '6× load', 'red'); } },
          { cap: 'Fix: TTL = 1 h ± random jitter, so expiries spread out', go: async r => { m.state('db', ''); m.badge('db'); for (let i = 0; i < 6; i++) { s.set(Array.from({ length: 6 }, (_, j) => ({ t: 'k' + (j + 1), tone: j === i ? 'muted' : '' }))); await m.send(['app', 'db'], { run: r, tone: 'teal', ms: 300 }); } full(''); } }
        ]; } },

    hotkey: { name: 'Hot key', tone: 'orange', tags: ['failure'],
      rule: 'One key gets most of the traffic, so the one cache node that owns it melts while the others idle.',
      takeaway: 'Fix: a short-lived local (L1) copy in each app server, or replicate that key.',
      use: '(failure mode) Flash sales, viral posts, a celebrity\'s profile.', avoid: 'L1 copies add a staleness window per server.',
      build(m) { m.box('app', 48, 70, 'App ×N', { icon: 'server', w: 80 }); m.box('l1', 48, 128, 'L1 copy', { w: 70, h: 22 }); ['s1', 's2', 's3'].forEach((id, i) => m.box(id, 270, 26 + i * 46, 'node ' + (i + 1), { icon: 'ram', w: 84 })); ['s1', 's2', 's3'].forEach(id => m.wire('app', id)); m.wire('app', 'l1', { dash: true });
        return [
          { cap: 'Keys spread across 3 cache nodes; <b>product:12</b> lives on node 2', go: async r => { m.state('l1', 'dim'); await m.send(['app', 's1'], { run: r, ms: 450 }); await m.send(['app', 's3'], { run: r, ms: 450 }); await m.send(['app', 's2'], { run: r, ms: 450, label: 'product:12' }); } },
          { cap: 'A flash sale: almost every read is for that one key', go: async r => { m.state('l1', 'dim'); for (let k = 0; k < 4; k++) await m.send(['app', 's2'], { run: r, ms: 300, tone: 'red' }); m.state('s2', 'hot'); m.badge('s2', '95% load', 'red'); m.state('s1', 'dim'); m.state('s3', 'dim'); } },
          { cap: 'Fix: each app keeps a 5-second <b>L1 copy</b>; node 2 sees one read per server', go: async r => { m.state('s2', ''); m.badge('s2'); m.state('s1', ''); m.state('s3', ''); m.state('l1', 'ok'); for (let k = 0; k < 3; k++) await m.send(['app', 'l1'], { run: r, ms: 300, tone: 'teal' }); } }
        ]; },
      reset(m) { m.state('l1', 'dim'); } },

    /* ---- distributed caching ---- */
    l1: { name: 'In-process cache (L1)', tone: 'yellow', tags: ['where it lives'],
      rule: 'Each app server keeps its own copy in its own memory (<code>IMemoryCache</code>). Fastest possible read, no network.',
      takeaway: 'N servers = N separate caches that can disagree.',
      use: 'Small, rarely-changing data (config, lookup lists); a short-lived L1 in front of Redis.', avoid: 'Data that changes: server 1 sees the update, servers 2–3 don\'t.',
      vb: [360, 160],
      build(m) { ['a1', 'a2', 'a3'].forEach((id, i) => { m.box(id, 70, 30 + i * 50, 'App ' + (i + 1), { icon: 'server', w: 84 }); m.box('c' + i, 190, 30 + i * 50, 'L1', { w: 44, h: 24 }); m.wire(id, 'c' + i); }); m.db('db', 315, 80, 'Database'); [0, 1, 2].forEach(i => m.wire('c' + i, 'db'));
        return [
          { cap: 'Each server cached <b>price ₹499</b> in its own memory', go: async r => { [0, 1, 2].forEach(i => m.badge('c' + i, '₹499')); await m.sleep(700, r); } },
          { cap: 'Server 2 handles an update: DB and <b>its own</b> L1 change', go: async r => { m.state('db', 'on'); await m.send(['a2', 'c1', 'db'], { run: r, label: 'UPDATE ₹449' }); m.state('db', ''); m.badge('c1', '₹449', 'teal'); } },
          { cap: 'Servers 1 and 3 still answer <b class="bad-text">₹499</b> until their copy expires', go: async r => { m.state('c0', 'hot'); m.state('c2', 'hot'); m.badge('c0', '₹499', 'red'); m.badge('c2', '₹499', 'red'); await m.sleep(900, r); } }
        ]; } },

    redis: { name: 'Distributed cache (Redis)', tone: 'red', tags: ['where it lives'],
      rule: 'All app servers share one cache over the network (<code>IDistributedCache</code>, StackExchange.Redis). One copy, one truth.',
      takeaway: 'Consistent across servers, at the cost of a network hop per read.',
      use: 'Sessions, shared lookups, anything every server must see the same.', avoid: 'Redis becomes a dependency: plan for it being slow or down.',
      vb: [360, 160],
      build(m) { ['a1', 'a2', 'a3'].forEach((id, i) => { m.box(id, 60, 30 + i * 50, 'App ' + (i + 1), { icon: 'server', w: 84 }); }); m.box('redis', 200, 80, 'Redis', { icon: 'ram', w: 84 }); m.db('db', 315, 80, 'Database'); ['a1', 'a2', 'a3'].forEach(id => m.wire(id, 'redis')); m.wire('redis', 'db', { dash: true });
        return [
          { cap: 'All three servers read the same key from Redis', go: async r => { m.badge('redis', '₹499'); await all(['a1', 'a2', 'a3'], id => m.send([id, 'redis'], { run: r, label: 'GET', ms: 650 })); } },
          { cap: 'Server 2 updates the DB and deletes the key', go: async r => { await m.send(['a2', 'redis'], { run: r, label: 'DEL', tone: 'red' }); m.badge('redis', 'gone', 'muted'); } },
          { cap: 'The next read (any server) reloads <b>₹449</b>: everyone sees it', go: async r => { await m.send(['a1', 'redis'], { run: r, label: 'GET' }); m.badge('redis', '₹449', 'teal'); m.state('redis', 'ok'); } }
        ]; } },

    hybrid: { name: 'Two-level cache (L1 + L2)', tone: 'violet', tags: ['where it lives'],
      rule: 'Check a short-lived in-process L1 first, then Redis (L2), then the DB. .NET\'s <code>HybridCache</code> does this for you.',
      takeaway: 'Most reads never leave the process; Redis keeps servers roughly in step.',
      use: 'High read rates on shared data; hot keys.', avoid: 'Keep L1 TTL short: other servers\' L1 copies are not invalidated instantly.',
      build(m) { m.box('app', 44, 70, 'App', { icon: 'server', w: 72 }); m.box('l1', 140, 70, 'L1', { w: 52, h: 28 }); m.box('l2', 236, 70, 'Redis L2', { icon: 'ram', w: 84 }); m.db('db', 325, 68, 'DB', { w: 40 }); m.wire('app', 'l1'); m.wire('l1', 'l2'); m.wire('l2', 'db');
        return [
          { cap: 'Cold start: L1 miss → L2 miss → DB', go: async r => { await m.send(['app', 'l1'], { run: r, ms: 350 }); m.badge('l1', 'miss', 'red'); await m.send(['l1', 'l2'], { run: r, ms: 450 }); m.badge('l2', 'miss', 'red'); m.state('db', 'on'); await m.send(['l2', 'db'], { run: r, ms: 450 }); } },
          { cap: 'The value fills L2 and L1 on the way back', go: async r => { await m.send(['db', 'l2'], { run: r, tone: 'yellow', ms: 450 }); m.state('db', ''); m.badge('l2', 'ttl 10m', 'teal'); await m.send(['l2', 'l1'], { run: r, tone: 'yellow', ms: 450 }); m.badge('l1', 'ttl 30s', 'teal'); } },
          { cap: 'Next read: <b class="ok-text">L1 hit</b>, no network at all', go: async r => { m.state('l2', 'dim'); m.state('db', 'dim'); await m.send(['app', 'l1'], { run: r, label: 'GET', ms: 350 }); m.state('l1', 'ok'); m.badge('l1', 'HIT', 'teal'); } }
        ]; } },

    cluster: { name: 'Sharded cache cluster', tone: 'blue', tags: ['where it lives'],
      rule: 'Spread keys over several cache nodes. Redis Cluster maps each key to one of <b>16,384 hash slots</b>; each node owns a range of slots.',
      takeaway: 'More memory and throughput; adding a node moves only some slots.',
      use: 'Data or traffic bigger than one node can hold.', avoid: 'Multi-key operations must live in one slot (use {hash tags}).',
      vb: [360, 160],
      build(m) { m.box('app', 50, 80, 'App', { icon: 'server', w: 78 }); m.box('hk', 165, 80, 'hash the key', { w: 100, h: 26 }); ['n1', 'n2', 'n3'].forEach((id, i) => m.box(id, 300, 30 + i * 50, ['0–5460', '5461–10922', '10923–16383'][i], { icon: 'ram', w: 96, sub: i === 2 ? 'slot ranges' : '' })); m.wire('app', 'hk'); ['n1', 'n2', 'n3'].forEach(id => m.wire('hk', id));
        return [
          { cap: 'Hash the key to a slot: <b>CRC16(key) mod 16384</b>', go: async r => { await m.send(['app', 'hk'], { run: r, label: 'user:42' }); m.badge('hk', 'slot 8,112', 'teal'); } },
          { cap: 'Slot 8,112 belongs to node 2 → go there', go: async r => { await m.send(['hk', 'n2'], { run: r }); m.state('n2', 'ok'); } },
          { cap: 'Another key lands on another node; load spreads out', go: async r => { m.badge('hk', 'slot 1,203', 'teal'); await m.send(['app', 'hk', 'n1'], { run: r, label: 'cart:9' }); m.state('n1', 'ok'); } }
        ]; } },

    replication: { name: 'Replication & failover', tone: 'teal', tags: ['where it lives'],
      rule: 'A primary takes writes and copies them <b>asynchronously</b> to replicas. If the primary dies, a replica is promoted (Sentinel or Cluster).',
      takeaway: 'Survives a node loss, but the last writes before a crash can be lost.',
      use: 'Any cache you can\'t afford to lose in one go (sessions, rate-limit counters).', avoid: 'Async copy = possible loss of recent writes on failover.',
      build(m) { m.box('app', 50, 75, 'App', { icon: 'server', w: 78 }); m.box('p', 190, 40, 'Primary', { icon: 'ram', w: 90 }); m.box('rp', 190, 115, 'Replica', { icon: 'ram', w: 90 }); m.box('sent', 315, 75, 'Sentinel', { icon: 'eye', w: 80 }); m.wire('app', 'p'); m.wire('p', 'rp'); m.wire('app', 'rp', { dash: true }); m.wire('sent', 'p', { dash: true }); m.wire('sent', 'rp', { dash: true });
        return [
          { cap: 'Writes go to the primary, which copies them to the replica', go: async r => { await m.send(['app', 'p'], { run: r, label: 'SET' }); await m.send(['p', 'rp'], { run: r, tone: 'teal', label: 'async copy' }); } },
          { cap: 'The primary <b class="bad-text">dies</b>; Sentinel notices missed heartbeats', go: async r => { m.state('p', 'hot'); m.badge('p', 'down', 'red'); await m.send(['sent', 'p'], { run: r, tone: 'red', ms: 500 }); } },
          { cap: 'Sentinel promotes the replica; the app writes to the new primary', go: async r => { await m.send(['sent', 'rp'], { run: r, tone: 'teal', label: 'promote', ms: 500 }); m.text('rp', 'New primary'); m.state('rp', 'ok'); await m.send(['app', 'rp'], { run: r, label: 'SET' }); } }
        ]; } },

    persistence: { name: 'Redis persistence: RDB vs AOF', tone: 'orange', tags: ['where it lives'],
      rule: '<b>RDB</b> saves a point-in-time snapshot every few minutes. <b>AOF</b> appends every write to a log (fsync every second by default).',
      takeaway: 'RDB: compact, may lose minutes. AOF: loses about a second, bigger files. Many run both.',
      use: 'When a restart must not mean a fully cold cache.', avoid: 'A cache is still not your source of truth.',
      vb: [360, 160],
      build(m) { m.box('mem', 70, 80, 'Redis memory', { icon: 'ram', w: 110 }); m.box('rdb', 260, 36, 'dump.rdb (snapshot)', { icon: 'disk', w: 150 }); m.box('aof', 260, 124, 'appendonly.aof (log)', { icon: 'doc', w: 150 }); m.wire('mem', 'rdb'); m.wire('mem', 'aof');
        return [
          { cap: '<b>AOF</b>: each write is appended to the log', go: async r => { for (const w of ['SET a', 'INCR b', 'DEL c']) await m.send(['mem', 'aof'], { run: r, label: w, ms: 420, tone: 'yellow' }); m.badge('aof', '+3 lines', 'teal'); } },
          { cap: '<b>RDB</b>: every few minutes, the whole dataset is snapshotted', go: async r => { await m.send(['mem', 'rdb'], { run: r, label: 'snapshot', ms: 800 }); m.badge('rdb', '10:05', 'teal'); } },
          { cap: 'Restart: data is reloaded from disk instead of starting empty', go: async r => { m.state('mem', 'dim'); await m.sleep(300, r); m.state('mem', ''); await m.send(['aof', 'mem'], { run: r, label: 'replay', ms: 600, tone: 'teal' }); m.state('mem', 'ok'); } }
        ]; } },

    /* ---- CDN & HTTP caching ---- */
    cdn: { name: 'CDN: pull vs push', tone: 'blue', tags: ['edge'],
      rule: 'An edge server near the user keeps copies of files. <b>Pull</b>: it fetches from the origin on the first miss. <b>Push</b>: you upload ahead of time.',
      takeaway: 'Pull is the default; push (or pre-warming) for big, predictable launches.',
      use: 'Static assets, images, video, versioned JS/CSS bundles.', avoid: 'Purging after a bad deploy; use versioned file names.',
      vb: [360, 160],
      build(m) { m.tile('user', 34, 62, 'User · Pune', 'users'); m.box('edge', 168, 62, 'Edge · Mumbai', { icon: 'edge', w: 106 }); m.box('origin', 310, 62, 'Origin', { icon: 'server', w: 78 }); m.box('ci', 310, 132, 'CI deploy', { icon: 'branch', w: 82, h: 26 }); m.wire('user', 'edge'); m.wire('edge', 'origin'); m.wire('ci', 'edge', { dash: true });
        return [
          { cap: '<b>Pull</b>: the first user misses at the edge', go: async r => { m.state('ci', 'dim'); await m.send(['user', 'edge'], { run: r, label: 'app.4f2.js' }); m.badge('edge', 'MISS', 'red'); } },
          { cap: 'The edge fetches from the origin and keeps a copy', go: async r => { await m.send(['edge', 'origin'], { run: r }); await m.send(['origin', 'edge', 'user'], { run: r, tone: 'yellow' }); m.badge('edge', 'cached', 'teal'); } },
          { cap: 'Later users nearby are served from the edge', go: async r => { m.state('origin', 'dim'); await m.send(['user', 'edge'], { run: r }); m.badge('edge', 'HIT', 'teal'); await m.send(['edge', 'user'], { run: r, tone: 'teal' }); } },
          { cap: '<b>Push</b>: CI uploads the file to the CDN before anyone asks', go: async r => { m.state('origin', ''); m.state('ci', 'on'); m.badge('edge'); await m.send(['ci', 'edge'], { run: r, label: 'upload' }); m.badge('edge', 'ready', 'teal'); } }
        ]; },
      reset(m) { m.state('ci', 'dim'); } },

    cdnpull: { name: 'Pull CDN', tone: 'blue', tags: ['edge'],
      rule: 'The edge starts empty. On the first request it <b>pulls</b> the file from your origin, keeps it, and serves everyone nearby.',
      takeaway: 'Zero setup per file; the first user in each region pays the trip to the origin.',
      use: 'The default for websites, images and API responses you mark cacheable.', avoid: 'A huge launch: every region misses at the same moment.',
      vb: [360, 150],
      build(m) { m.tile('u1', 34, 40, 'User 1', 'user'); m.tile('u2', 34, 110, 'User 2', 'user'); m.box('edge', 175, 75, 'Edge · Mumbai', { icon: 'edge', w: 110 }); m.box('origin', 312, 75, 'Origin', { icon: 'server', w: 78 }); m.wire('u1', 'edge'); m.wire('u2', 'edge'); m.wire('edge', 'origin');
        return [
          { cap: 'User 1 asks the nearest edge → <b class="bad-text">miss</b>', go: async r => { await m.send(['u1', 'edge'], { run: r, label: 'logo.png' }); m.badge('edge', 'MISS', 'red'); } },
          { cap: 'Edge pulls from the origin (slow, far away) and keeps a copy', go: async r => { m.state('origin', 'on'); await m.send(['edge', 'origin'], { run: r }); await m.send(['origin', 'edge'], { run: r, tone: 'yellow' }); m.state('origin', ''); m.badge('edge', 'cached', 'teal'); await m.send(['edge', 'u1'], { run: r, tone: 'yellow' }); } },
          { cap: 'User 2 nearby: <b class="ok-text">edge hit</b>, origin untouched', go: async r => { m.state('origin', 'dim'); await m.send(['u2', 'edge'], { run: r }); m.badge('edge', 'HIT', 'teal'); await m.send(['edge', 'u2'], { run: r, tone: 'teal' }); } }
        ]; } },

    cdnpush: { name: 'Push CDN', tone: 'violet', tags: ['edge'],
      rule: 'You <b>upload</b> files to the CDN as part of the deploy, so edges have them before the first user asks.',
      takeaway: 'No first-user miss and no origin load at launch; you manage what\'s on the CDN.',
      use: 'Big, predictable releases: game patches, video, installers.', avoid: 'Many small, changing files: you pay to store and keep them in sync.',
      vb: [360, 150],
      build(m) { m.box('ci', 60, 40, 'CI / deploy', { icon: 'branch', w: 96 }); m.tile('u', 50, 112, 'Users', 'users'); m.box('e1', 230, 40, 'Edge · Mumbai', { icon: 'edge', w: 110 }); m.box('e2', 230, 112, 'Edge · Chennai', { icon: 'edge', w: 110 }); m.wire('ci', 'e1'); m.wire('ci', 'e2'); m.wire('u', 'e2');
        return [
          { cap: 'At deploy time, CI uploads the release to every edge', go: async r => { await all(['e1', 'e2'], id => m.send(['ci', id], { run: r, label: 'patch-2.1', ms: 700 })); m.badge('e1', 'ready', 'teal'); m.badge('e2', 'ready', 'teal'); } },
          { cap: 'Launch: the first user is already a <b class="ok-text">hit</b>', go: async r => { await m.send(['u', 'e2'], { run: r }); m.state('e2', 'ok'); await m.send(['e2', 'u'], { run: r, tone: 'teal' }); } }
        ]; } },

    cc: { name: 'Cache-Control header', tone: 'cyan', tags: ['http'],
      rule: 'The response header tells every cache on the way what it may do: <code>max-age</code>, <code>s-maxage</code>, <code>private</code>, <code>no-cache</code>, <code>no-store</code>.',
      takeaway: 'Your server decides who may keep a copy and for how long.',
      use: 'Every cacheable response; set it on purpose, not by default.', avoid: '<code>private</code> or <code>no-store</code> for per-user or sensitive data.',
      vb: [360, 160],
      build(m) { m.tile('br', 40, 70, 'Browser', 'laptop'); m.box('edge', 175, 70, 'CDN edge', { icon: 'edge', w: 96 }); m.box('origin', 310, 70, 'Origin', { icon: 'server', w: 78 }); m.wire('br', 'edge'); m.wire('edge', 'origin'); const h = m.label(180, 140, '', 'at-small'); m._h = h;
        return [
          { cap: '<code>public, max-age=600</code> → browser <b>and</b> CDN keep it for 10 min', go: async r => { h.textContent = 'Cache-Control: public, max-age=600'; await m.send(['origin', 'edge', 'br'], { run: r, tone: 'yellow', ms: 500 }); m.badge('edge', 'stored', 'teal'); m.badge('br', 'stored', 'teal'); } },
          { cap: '<code>private, max-age=600</code> → only the browser keeps it', go: async r => { m.badge('edge'); m.badge('br'); h.textContent = 'Cache-Control: private, max-age=600'; await m.send(['origin', 'edge', 'br'], { run: r, tone: 'yellow', ms: 500 }); m.badge('edge', 'skip', 'muted'); m.badge('br', 'stored', 'teal'); } },
          { cap: '<code>no-store</code> → nobody keeps a copy', go: async r => { m.badge('edge'); m.badge('br'); h.textContent = 'Cache-Control: no-store'; await m.send(['origin', 'edge', 'br'], { run: r, tone: 'yellow', ms: 500 }); m.badge('edge', 'skip', 'muted'); m.badge('br', 'skip', 'muted'); } }
        ]; },
      reset(m) { m._h && (m._h.textContent = ''); } },

    etag: { name: 'ETag & 304 Not Modified', tone: 'teal', tags: ['http'],
      rule: 'The response carries a version tag (<code>ETag: "v7"</code>). Later the browser asks <code>If-None-Match: "v7"</code>; if unchanged the server answers <b>304</b> with no body.',
      takeaway: 'Revalidation costs a round trip but not the download.',
      use: 'HTML, API responses, anything with <code>no-cache</code> or an expired max-age.', avoid: 'Still a request per use; versioned files with long max-age avoid even that.',
      build(m) { m.tile('br', 40, 70, 'Browser', 'laptop'); m.box('origin', 290, 70, 'API / origin', { icon: 'server', w: 96 }); m.wire('br', 'origin'); const h = m.label(165, 128, '', 'at-small'); m._h = h;
        return [
          { cap: 'First request: <b>200</b> with the body and <code>ETag: "v7"</code>', go: async r => { await m.send(['br', 'origin'], { run: r, label: 'GET /doctors' }); h.textContent = '200 OK · 48 KB · ETag: "v7"'; await m.send(['origin', 'br'], { run: r, tone: 'yellow', label: '48 KB' }); m.badge('br', 'v7', 'teal'); } },
          { cap: 'Copy is stale: ask <code>If-None-Match: "v7"</code>', go: async r => { h.textContent = 'If-None-Match: "v7"'; await m.send(['br', 'origin'], { run: r, label: 'v7?' }); } },
          { cap: 'Unchanged → <b>304 Not Modified</b>, no body; reuse the copy', go: async r => { h.textContent = '304 Not Modified · 0 KB'; await m.send(['origin', 'br'], { run: r, tone: 'teal', label: '304' }); m.state('br', 'ok'); } }
        ]; },
      reset(m) { m._h && (m._h.textContent = ''); } },

    busting: { name: 'Versioned file names', tone: 'yellow', tags: ['http'],
      rule: 'Put a content hash in the file name (<code>app.4f2c.js</code>) and cache it for a year with <code>immutable</code>. A new build gets a new name.',
      takeaway: 'Never purge static files: change the URL instead.',
      use: 'All build output: JS, CSS, fonts, images.', avoid: 'The HTML that references them must stay short-cached.',
      build(m) { m.tile('br', 40, 70, 'Browser', 'laptop'); m.box('edge', 175, 70, 'CDN edge', { icon: 'edge', w: 96 }); m.box('origin', 310, 70, 'Origin', { icon: 'server', w: 78 }); m.wire('br', 'edge'); m.wire('edge', 'origin'); const h = m.label(180, 132, '', 'at-small'); m._h = h;
        return [
          { cap: '<code>app.4f2c.js</code> cached everywhere for a year', go: async r => { h.textContent = 'max-age=31536000, immutable'; m.badge('edge', '4f2c', 'teal'); m.badge('br', '4f2c', 'teal'); await m.sleep(700, r); } },
          { cap: 'Deploy: HTML now points to <code>app.9b1e.js</code>, a new URL', go: async r => { h.textContent = '<script src="app.9b1e.js">'; await m.send(['br', 'edge'], { run: r, label: '9b1e?' }); m.badge('edge', 'MISS', 'red'); await m.send(['edge', 'origin'], { run: r }); await m.send(['origin', 'edge', 'br'], { run: r, tone: 'yellow' }); m.badge('edge', '9b1e', 'teal'); m.badge('br', '9b1e', 'teal'); } },
          { cap: 'Nothing purged; old and new versions never mix', go: async r => { m.state('edge', 'ok'); m.state('br', 'ok'); await m.sleep(600, r); } }
        ]; },
      reset(m) { m._h && (m._h.textContent = ''); } },

    purge: { name: 'Purge / invalidation', tone: 'red', tags: ['http'],
      rule: 'Tell the CDN to drop a URL (or a tag) from every edge now, so the next request goes back to the origin.',
      takeaway: 'Your emergency brake for things that can\'t be versioned (HTML, an API response).',
      use: 'A wrong price on a cached page; content taken down.', avoid: 'Purges take time to spread and can stampede the origin.',
      vb: [360, 150],
      build(m) { m.box('ci', 60, 40, 'You / CI', { icon: 'terminal', w: 90 }); m.tile('u', 50, 112, 'User', 'user'); m.box('edge', 200, 75, 'CDN edges', { icon: 'edge', w: 100 }); m.box('origin', 318, 75, 'Origin', { icon: 'server', w: 70 }); m.wire('ci', 'edge'); m.wire('u', 'edge'); m.wire('edge', 'origin');
        return [
          { cap: 'Edges hold <code>/pricing</code> showing the old price', go: async r => { m.badge('edge', 'old page', 'red'); await m.sleep(600, r); } },
          { cap: 'Send a purge for <code>/pricing</code>', go: async r => { await m.send(['ci', 'edge'], { run: r, label: 'PURGE /pricing', tone: 'red' }); m.badge('edge', 'dropped', 'muted'); } },
          { cap: 'Next request misses and fetches the corrected page', go: async r => { await m.send(['u', 'edge', 'origin'], { run: r }); await m.send(['origin', 'edge', 'u'], { run: r, tone: 'yellow' }); m.badge('edge', 'new page', 'teal'); } }
        ]; } },

    /* ---- caching in practice (playbook) ---- */
    pubsub: { name: 'Clear L1 on every server (pub/sub)', tone: 'violet', tags: ['in practice'],
      rule: 'When one server changes data, it deletes the Redis key and <b>publishes</b> "invalidate product:12". Every server is subscribed and drops its own L1 copy.',
      takeaway: 'L1 stays fast, and servers agree within milliseconds instead of waiting for the L1 TTL.',
      use: 'Any L1 + Redis setup where stale prices or permissions matter.', avoid: 'Redis pub/sub is fire-and-forget: a restarting server misses messages, so keep the L1 TTL short too.',
      vb: [360, 160],
      build(m) { m.box('redis', 290, 80, 'Redis', { icon: 'ram', w: 86 }); [0, 1, 2].forEach(i => { m.box('a' + i, 58, 30 + i * 50, 'App ' + (i + 1), { icon: 'server', w: 80 }); m.box('c' + i, 150, 30 + i * 50, 'L1', { w: 40, h: 24 }); m.wire('a' + i, 'c' + i); m.wire('c' + i, 'redis'); });
        return [
          { cap: 'Every server has <b>₹499</b> in its L1', go: async r => { [0, 1, 2].forEach(i => m.badge('c' + i, '₹499')); await m.sleep(600, r); } },
          { cap: 'App 2 updates the DB, then DELs the Redis key and PUBLISHes "invalidate product:12"', go: async r => { await m.send(['a1', 'c1', 'redis'], { run: r, label: 'DEL + PUBLISH', tone: 'red' }); m.badge('c1', 'dropped', 'muted'); m.badge('redis', 'channel: invalidate', 'teal'); } },
          { cap: 'Redis pushes the message to every subscriber; each drops its L1 copy', go: async r => { await Promise.all([m.send(['redis', 'c0', 'a0'], { run: r, tone: 'violet', ms: 600 }), m.send(['redis', 'c2', 'a2'], { run: r, tone: 'violet', ms: 600 })]); m.badge('c0', 'dropped', 'muted'); m.badge('c2', 'dropped', 'muted'); } },
          { cap: 'Next read on any server reloads <b>₹449</b>', go: async r => { await m.send(['a0', 'c0', 'redis'], { run: r, label: 'GET' }); m.badge('c0', '₹449', 'teal'); m.state('c0', 'ok'); } }
        ]; } },

    events: { name: 'Invalidate across services (change events)', tone: 'blue', tags: ['in practice'],
      rule: 'The service that owns the data writes the change and an <b>outbox</b> row in one transaction; a relay publishes "ProductChanged"; every service that cached it deletes its copy.',
      takeaway: 'Each service owns its cache; events tell it when to drop entries.',
      use: 'Microservices that cache another service\'s data (search, pricing, recommendations).', avoid: 'Events can be late or duplicated: keep TTLs and make the delete idempotent.',
      vb: [360, 160],
      build(m) { m.box('a', 60, 40, 'Catalog svc', { icon: 'server', w: 94 }); m.db('db', 60, 118, 'DB + outbox'); m.box('bk', 185, 80, 'Broker', { icon: 'pipe', w: 80 }); m.box('s1', 305, 40, 'Search svc', { icon: 'server', w: 92 }); m.box('s2', 305, 120, 'Pricing svc', { icon: 'server', w: 92 }); m.wire('a', 'db'); m.wire('db', 'bk'); m.wire('bk', 's1'); m.wire('bk', 's2');
        return [
          { cap: 'Search and Pricing each cache product 12', go: async r => { m.badge('s1', 'cached v1'); m.badge('s2', 'cached v1'); await m.sleep(600, r); } },
          { cap: 'Catalog writes the change <b>and</b> an outbox row in one transaction', go: async r => { m.state('db', 'on'); await m.send(['a', 'db'], { run: r, label: 'UPDATE + outbox' }); m.state('db', ''); } },
          { cap: 'A relay publishes <b>ProductChanged 12</b> to the broker', go: async r => { await m.send(['db', 'bk'], { run: r, label: 'event', tone: 'yellow' }); } },
          { cap: 'Each subscriber deletes its cached copy; next read reloads', go: async r => { await Promise.all([m.send(['bk', 's1'], { run: r, tone: 'yellow', ms: 600 }), m.send(['bk', 's2'], { run: r, tone: 'yellow', ms: 600 })]); m.badge('s1', 'dropped', 'muted'); m.badge('s2', 'dropped', 'muted'); } }
        ]; } },

    cdnkey: { name: 'CDN cache key', tone: 'cyan', tags: ['in practice'],
      rule: 'The edge stores one copy per <b>cache key</b> (by default: host + path + full query string). Marketing parameters like <code>utm_source</code> create copies of the same page.',
      takeaway: 'Normalise the key: ignore parameters that don\'t change the response.',
      use: 'Any page shared through campaigns, emails or ads.', avoid: 'Don\'t strip parameters the page really depends on (page=2, sort=price).',
      vb: [360, 160],
      build(m) { m.tile('u', 34, 60, 'Visitors', 'users'); m.box('edge', 180, 60, 'CDN edge', { icon: 'edge', w: 96 }); m.box('origin', 315, 60, 'Origin', { icon: 'server', w: 74 }); m.wire('u', 'edge'); m.wire('edge', 'origin'); const s = m.slots('k', 180, 128, 3, { w: 30, label: 'copies stored at the edge' });
        return [
          { cap: '<code>/p/12?utm_source=mail</code>, <code>…=ads</code>, <code>…=sms</code>: three different keys', go: async r => { for (const [i, t] of ['mail', 'ads', 'sms'].entries()) { await m.send(['u', 'edge', 'origin'], { run: r, label: t, ms: 380 }); s.set(['mail', 'ads', 'sms'].slice(0, i + 1).map(x => ({ t: x.slice(0, 3) }))); } m.badge('edge', '3 misses', 'red'); } },
          { cap: 'Same page, stored 3 times; the origin did 3× the work', go: async r => { m.state('origin', 'hot'); await m.sleep(600, r); } },
          { cap: 'Fix: key ignores <code>utm_*</code> → one copy, the rest are hits', go: async r => { m.state('origin', ''); s.set([{ t: '/p/12', tone: 'yellow' }]); m.badge('edge', 'HIT ×2', 'teal'); await m.send(['u', 'edge'], { run: r, tone: 'teal' }); await m.send(['edge', 'u'], { run: r, tone: 'teal' }); } }
        ]; },
      reset(m) { m.nodes.k.slots.set([]); } },

    vary: { name: 'The Vary header', tone: 'teal', tags: ['in practice'],
      rule: '<code>Vary</code> adds request headers to the cache key. <code>Vary: Accept-Language</code> keeps English and Hindi apart; <code>Vary: Cookie</code> makes a copy per visitor.',
      takeaway: 'Vary only on headers that really change the response.',
      use: 'Language, compression (<code>Accept-Encoding</code>), device-specific pages.', avoid: '<code>Vary: Cookie</code> or <code>User-Agent</code> on public pages: the hit ratio collapses.',
      vb: [360, 160],
      build(m) { m.tile('u', 34, 60, 'Visitors', 'users'); m.box('edge', 180, 60, 'CDN edge', { icon: 'edge', w: 96 }); m.box('origin', 315, 60, 'Origin', { icon: 'server', w: 74 }); m.wire('u', 'edge'); m.wire('edge', 'origin'); const s = m.slots('k', 180, 128, 5, { w: 26, label: 'copies stored at the edge' });
        return [
          { cap: '<code>Vary: Accept-Language</code>: one copy for en, one for hi. Correct.', go: async r => { await m.send(['u', 'edge', 'origin'], { run: r, label: 'en', ms: 380 }); s.set([{ t: 'en' }]); await m.send(['u', 'edge', 'origin'], { run: r, label: 'hi', ms: 380 }); s.set([{ t: 'en' }, { t: 'hi' }]); await m.send(['u', 'edge'], { run: r, label: 'en', tone: 'teal' }); m.badge('edge', 'HIT', 'teal'); } },
          { cap: '<code>Vary: Cookie</code>: every visitor has different analytics cookies…', go: async r => { m.badge('edge'); s.set([]); for (let i = 1; i <= 5; i++) { await m.send(['u', 'edge', 'origin'], { run: r, label: 'c' + i, ms: 300 }); s.set(Array.from({ length: i }, (_, j) => ({ t: 'c' + (j + 1), tone: 'red' }))); } } },
          { cap: '…so every request is a miss: hit ratio ≈ 0%', go: async r => { m.badge('edge', '0% hits', 'red'); m.state('origin', 'hot'); await m.sleep(500, r); } }
        ]; },
      reset(m) { m.nodes.k.slots.set([]); } },

    leak: { name: 'Cache leaks & poisoning', tone: 'red', tags: ['in practice'],
      rule: 'If a personalised response is cacheable, the edge serves <b>Asha\'s page to Ravi</b>. Poisoning is the same idea on purpose: an attacker gets a harmful variant cached for everyone.',
      takeaway: 'Per-user responses: <code>Cache-Control: private</code> or <code>no-store</code>. Cache only on keyed inputs.',
      use: '(failure mode) Logged-in pages, anything with Set-Cookie.', avoid: 'Responses that change with headers you didn\'t put in the key (e.g. <code>X-Forwarded-Host</code>).',
      vb: [360, 160],
      build(m) { m.tile('a', 34, 40, 'Asha', 'user'); m.tile('b', 34, 118, 'Ravi', 'user'); m.box('edge', 180, 80, 'CDN edge', { icon: 'edge', w: 96 }); m.box('origin', 315, 80, 'Origin', { icon: 'server', w: 74 }); m.wire('a', 'edge'); m.wire('b', 'edge'); m.wire('edge', 'origin');
        return [
          { cap: 'Asha (logged in) opens <code>/appointments</code>; no <code>private</code> header', go: async r => { await m.send(['a', 'edge', 'origin'], { run: r, label: 'GET' }); await m.send(['origin', 'edge', 'a'], { run: r, tone: 'yellow', label: 'Hi Asha' }); m.badge('edge', 'cached: Hi Asha', 'red'); } },
          { cap: 'Ravi opens the same URL → <b>edge HIT: Ravi sees Asha\'s appointments</b>', go: async r => { await m.send(['b', 'edge'], { run: r, label: 'GET' }); await m.send(['edge', 'b'], { run: r, tone: 'red', label: 'Hi Asha' }); m.state('b', 'hot'); } },
          { cap: 'Fix: <code>Cache-Control: private</code> → the edge never stores it', go: async r => { m.state('b', ''); m.badge('edge', 'not stored', 'muted'); await m.send(['b', 'edge', 'origin'], { run: r, label: 'GET' }); await m.send(['origin', 'edge', 'b'], { run: r, tone: 'teal', label: 'Hi Ravi' }); } }
        ]; } },

    bigkey: { name: 'Big keys in Redis', tone: 'orange', tags: ['in practice'],
      rule: 'Redis runs commands one at a time. One <b>50 MB value</b> (a whole catalogue in one key) ties it up and every small request queues behind it.',
      takeaway: 'Keep values small (KBs): split into hash fields or pages, compress, fetch only what you need.',
      use: '(failure mode) "Cache the whole list" designs.', avoid: 'Huge sets or hashes deleted in one go: use UNLINK or delete in batches.',
      vb: [360, 150],
      build(m) { m.box('app', 50, 75, 'App', { icon: 'server', w: 74 }); m.box('redis', 200, 75, 'Redis (1 thread)', { icon: 'ram', w: 120 }); m.tile('o', 330, 75, 'Other callers', 'users'); m.wire('app', 'redis'); m.wire('redis', 'o');
        return [
          { cap: 'Small GETs: each takes well under a millisecond', go: async r => { for (let k = 0; k < 3; k++) await m.send(['o', 'redis'], { run: r, ms: 300, tone: 'teal' }); } },
          { cap: 'GET <b>catalog:all</b> (50 MB) occupies Redis while it is copied out…', go: async r => { m.state('redis', 'hot'); m.badge('redis', 'busy: 50 MB', 'red'); await m.send(['redis', 'app'], { run: r, label: '50 MB', ms: 1800, tone: 'red' }); } },
          { cap: '…and every other request waits behind it', go: async r => { m.badge('o', 'p99 ↑', 'red'); await m.sleep(600, r); } },
          { cap: 'Fix: <code>catalog:page:1..N</code> or a hash per product; fetch only what you need', go: async r => { m.state('redis', ''); m.badge('redis', '4 KB values', 'teal'); m.badge('o'); for (let k = 0; k < 3; k++) await m.send(['app', 'redis'], { run: r, ms: 300, tone: 'teal' }); } }
        ]; } },

    warm: { name: 'Cache warming', tone: 'yellow', tags: ['in practice'],
      rule: 'Before sending traffic to a new or empty cache (deploy, new region, failover), load the <b>hottest keys</b> first, taken from logs or yesterday\'s access counts.',
      takeaway: 'The first users get hits, and the database never sees a cold-start flood.',
      use: 'New regions, cache cluster replacements, big launches.', avoid: 'Warming everything: load the top N, let the rest fill lazily.',
      vb: [360, 150],
      build(m) { m.box('job', 60, 40, 'Warm-up job', { icon: 'terminal', w: 104 }); m.tile('u', 50, 115, 'Users', 'users'); m.box('cache', 200, 75, 'New cache', { icon: 'ram', w: 96 }); m.db('db', 320, 75, 'Database'); m.wire('job', 'cache'); m.wire('u', 'cache'); m.wire('cache', 'db'); m.wire('job', 'db', { via: [[200, 20]], dash: true });
        return [
          { cap: 'The new cache is empty: switching traffic now would send every read to the DB', go: async r => { m.badge('cache', 'empty', 'muted'); m.state('u', 'dim'); await m.sleep(600, r); } },
          { cap: 'A job loads the top 1,000 keys (from access logs) in the background', go: async r => { m.state('db', 'on'); await m.send(['job', 'db'], { run: r, label: 'top 1,000', ms: 700 }); await m.send(['job', 'cache'], { run: r, label: 'SET ×1,000', ms: 700, tone: 'yellow' }); m.state('db', ''); m.badge('cache', 'warm', 'teal'); } },
          { cap: 'Then traffic switches over: first requests are already hits', go: async r => { m.state('u', ''); await m.send(['u', 'cache'], { run: r, tone: 'teal' }); m.state('cache', 'ok'); m.state('db', 'dim'); } }
        ]; } },

    redisuses: { name: 'Redis beyond caching', tone: 'red', tags: ['in practice'],
      rule: 'The same Redis often does three other jobs: <b>rate limiting</b> (INCR + EXPIRE), <b>locks</b> (SET NX PX) and <b>leaderboards</b> (sorted sets).',
      takeaway: 'Know the command behind each: interviewers ask "how would you build it with Redis?"',
      use: 'Per-user API limits, "only one worker runs this job", top-N lists.', avoid: 'Mixing these with an LRU cache: eviction can delete your counters and locks.',
      vb: [360, 160],
      build(m) { m.box('app', 60, 80, 'API', { icon: 'server', w: 74 }); m.box('redis', 255, 80, 'Redis', { icon: 'ram', w: 90 }); m.wire('app', 'redis'); const t = m.label(180, 145, '', 'at-small'); m._t = t;
        return [
          { cap: 'Rate limit: <code>INCR rl:user:7:10:42</code> + <code>EXPIRE 60</code>; over 100 → 429', go: async r => { t.textContent = 'INCR rl:user:7:10:42 → 101 (limit 100)'; await m.send(['app', 'redis'], { run: r, label: 'INCR' }); m.badge('redis', '101 > 100', 'red'); await m.send(['redis', 'app'], { run: r, tone: 'red', label: '429' }); } },
          { cap: 'Lock: <code>SET lock:report NX PX 30000</code>; only one worker gets OK', go: async r => { m.badge('redis'); t.textContent = 'SET lock:report <token> NX PX 30000 → OK'; await m.send(['app', 'redis'], { run: r, label: 'SET NX' }); m.badge('redis', 'OK (lock held)', 'teal'); } },
          { cap: 'Leaderboard: <code>ZINCRBY</code> scores, <code>ZREVRANGE 0 9</code> for the top 10', go: async r => { m.badge('redis'); t.textContent = 'ZREVRANGE board 0 9 WITHSCORES'; await m.send(['app', 'redis'], { run: r, label: 'ZREVRANGE' }); await m.send(['redis', 'app'], { run: r, tone: 'yellow', label: 'top 10' }); } }
        ]; },
      reset(m) { m._t && (m._t.textContent = ''); } },

    multiregion: { name: 'Caches in several regions', tone: 'blue', tags: ['in practice'],
      rule: 'Each region keeps its own cache next to its users. A write in one region must <b>invalidate the copies in the others</b>, usually through a replicated event stream.',
      takeaway: 'Reads stay local and fast; cross-region staleness is bounded by event lag (seconds) plus the TTL.',
      use: 'Global products: India, EU and US users.', avoid: 'Synchronous cross-region invalidation on every write: too slow.',
      vb: [360, 160],
      build(m) { m.box('mum', 70, 34, 'Mumbai cache', { icon: 'ram', w: 112 }); m.box('fra', 290, 34, 'Frankfurt cache', { icon: 'ram', w: 118 }); m.box('vir', 250, 112, 'Virginia cache', { icon: 'ram', w: 118 }); m.box('st', 70, 112, 'Event stream', { icon: 'pipe', w: 112 }); m.wire('mum', 'st'); m.wire('st', 'fra'); m.wire('st', 'vir');
        return [
          { cap: 'All three regions cache the same product at <b>₹499</b>', go: async r => { ['mum', 'fra', 'vir'].forEach(id => m.badge(id, '₹499')); await m.sleep(600, r); } },
          { cap: 'A write in Mumbai updates the DB and clears the <b>local</b> cache', go: async r => { m.badge('mum', 'cleared', 'muted'); await m.send(['mum', 'st'], { run: r, label: 'ProductChanged' }); } },
          { cap: 'The event reaches the other regions a second later; they clear theirs', go: async r => { await Promise.all([m.send(['st', 'fra'], { run: r, tone: 'yellow', ms: 800 }), m.send(['st', 'vir'], { run: r, tone: 'yellow', ms: 900 })]); m.badge('fra', 'cleared', 'muted'); m.badge('vir', 'cleared', 'muted'); } }
        ]; } },

    monitor: { name: 'Read the cache dashboard', tone: 'teal', tags: ['in practice'],
      rule: 'Five numbers tell you if a cache is healthy: <b>hit ratio</b>, <b>evictions/s</b>, <b>memory used</b>, <b>p99 latency</b> and the <b>DB load</b> behind it.',
      takeaway: 'They move together: memory full → evictions → hit ratio falls → DB load and p99 rise.',
      use: 'Every cache in production; alert on hit ratio and memory.', avoid: 'Watching averages only: a stampede hides inside a good average.',
      vb: [360, 160],
      build(m) { const names = ['hit ratio', 'evictions/s', 'memory', 'DB queries/s', 'p99']; const vals = names.map((n, i) => { m.box('k' + i, 66 + (i % 3) * 114, 36 + Math.floor(i / 3) * 70, '', { w: 104, h: 38 }); m.label(66 + (i % 3) * 114, 68 + Math.floor(i / 3) * 70, n, 'at-small'); return i; }); m._set = (arr, bad) => arr.forEach((v, i) => { m.text('k' + i, v); m.state('k' + i, bad.includes(i) ? 'hot' : 'ok'); });
        return [
          { cap: 'Healthy: 96% hits, no evictions, memory 62%', go: async r => { m._set(['96%', '0', '62%', '180', '4 ms'], []); await m.sleep(800, r); } },
          { cap: 'Catalogue triples; memory hits 100% and evictions start', go: async r => { m._set(['91%', '1,200', '100%', '900', '6 ms'], [1, 2]); await m.sleep(800, r); } },
          { cap: 'Hit ratio falls, DB load and p99 climb: <b>cache too small</b>', go: async r => { m._set(['72%', '4,000', '100%', '5,600', '38 ms'], [0, 1, 2, 3, 4]); await m.sleep(800, r); } }
        ]; },
      reset(m) { m._set && m._set(['–', '–', '–', '–', '–'], []); } }
  };
  Object.keys(CARDS).forEach(id => CARDS[id].id = id);
  // deep-dive page for each card (used when CF.cards(ids, { links: true }))
  const PAGES = {
    'cache-read-strategies.html': ['aside', 'through-read', 'refresh'],
    'cache-write-strategies.html': ['wthrough', 'wbehind', 'waround', 'invalidate', 'stale'],
    'cache-eviction.html': ['lru', 'lfu', 'fifo', 'ttl'],
    'distributed-caching.html': ['l1', 'redis', 'hybrid', 'cluster', 'replication', 'persistence'],
    'cache-failure-modes.html': ['stampede', 'swr', 'penetration', 'avalanche', 'hotkey'],
    'cdn-http-caching.html': ['cdn', 'cdnpull', 'cdnpush', 'cc', 'etag', 'busting', 'purge'],
    'caching-in-practice.html': ['pubsub', 'events', 'cdnkey', 'vary', 'leak', 'bigkey', 'warm', 'redisuses', 'multiregion', 'monitor']
  };
  const LINK = {}; for (const f in PAGES) PAGES[f].forEach(id => LINK[id] = f);

  /* ---------------- "which one fits?" scenarios ---------------- */
  const QUIZ = [
    { q: 'A product catalogue API in ASP.NET Core reads the same items thousands of times a minute. A slow first request is fine.', a: 'aside', why: 'Read-heavy, tolerant of a first-read miss: the app checks Redis, loads from SQL on a miss and sets a TTL.' },
    { q: 'You want one shared component that knows how to load doctors from the DB, so no controller ever writes loading code.', a: 'through-read', why: 'Read-through puts the loader inside the cache layer; callers only ever ask the cache.' },
    { q: 'The home-page "top doctors" list takes 3 seconds to compute and is read on every visit. No visitor should ever wait for it.', a: 'refresh', why: 'Reload it in the background before it expires so no reader hits the 3-second miss.' },
    { q: 'A clinic\'s appointment slots are edited and must show the new value on the very next read.', a: 'wthrough', why: 'Write-through keeps cache and DB in step on every write, so the next read is fresh (invalidate-on-write also works).' },
    { q: 'You record a page-view counter on every request: 20,000 increments a second. Losing a few seconds of counts is acceptable.', a: 'wbehind', why: 'Buffer in the cache and flush in batches; the loss risk is acceptable for counters.' },
    { q: 'An audit log is written on every API call and almost never read back.', a: 'waround', why: 'Write straight to the store; caching it would only push useful entries out.' },
    { q: 'Two admins edit the same price within milliseconds; afterwards the cache shows the older price.', a: 'invalidate', why: 'Overwriting the cache on write lets the slower request win. Delete the key instead and let the next read load the DB value.' },
    { q: 'A small cache serves a stable set of hot keys, but a nightly job reads every record once.', a: 'lfu', why: 'The scan reads each key once; LFU evicts those first and keeps the hot set.' },
    { q: 'Recently viewed items are likely to be viewed again soon; popularity changes through the day.', a: 'lru', why: 'LRU follows recency and adapts as popularity shifts.' },
    { q: 'Doctor availability changes every few minutes; a little staleness is OK but never more than a minute.', a: 'ttl', why: 'A 60-second TTL caps staleness even if an invalidation is missed.' },
    { q: 'At 00:00 a sale starts, the product key expires, and the database CPU jumps to 100% for a few seconds.', a: 'stampede', why: 'Many concurrent misses on one key: single-flight, stale-while-revalidate or TTL jitter.' },
    { q: 'A dashboard can show numbers a few seconds old, but must never block a user while it refreshes.', a: 'swr', why: 'Serve the stale copy instantly and refresh once in the background.' },
    { q: 'A scraper requests random patient IDs; none exist, and every request reaches SQL Server.', a: 'penetration', why: 'Cache the "not found" briefly or keep a Bloom filter of valid IDs; also rate-limit the client.' },
    { q: 'A nightly import caches 2 million rows with a 24-hour TTL; the next night the database falls over at the same minute.', a: 'avalanche', why: 'Everything expires together. Add random jitter to the TTL and warm gradually.' },
    { q: 'A viral post sends 95% of reads to one Redis node in a cluster of six.', a: 'hotkey', why: 'One key, one node: add a short local L1 copy or replicate the key.' },
    { q: 'Country and currency lists change twice a year and are read on every request.', a: 'l1', why: 'Tiny, near-static data: keep it in each server\'s memory, no network hop.' },
    { q: 'User sessions must be visible to whichever of 8 app servers gets the next request.', a: 'redis', why: 'A shared distributed cache gives every server the same copy.' },
    { q: 'Your Redis cluster is at 85% memory and still growing.', a: 'cluster', why: 'Shard keys across more nodes (hash slots); adding a node moves only some slots.' },
    { q: 'If the Redis node holding rate-limit counters dies, you want a copy to take over within seconds.', a: 'replication', why: 'Primary + replica with automatic promotion (Sentinel or Cluster).' },
    { q: 'After a Redis restart the app is slow for 20 minutes while the cache refills.', a: 'persistence', why: 'Turn on RDB and/or AOF so Redis reloads its data on restart.' },
    { q: 'You ship versioned JavaScript bundles to users across India.', a: 'busting', why: 'Hash in the file name + a one-year immutable max-age: new builds get new URLs, nothing to purge.' },
    { q: 'A 2 GB game patch goes live at 9:00 for millions of players.', a: 'cdnpush', why: 'Upload to the CDN ahead of time so no edge has to pull from the origin at launch.' },
    { q: 'A per-user account page must be cached by the browser but never by the CDN.', a: 'cc', why: '<code>Cache-Control: private, max-age=…</code> keeps shared caches out.' },
    { q: 'A doctors list rarely changes; you want clients to check freshness cheaply instead of re-downloading 48 KB.', a: 'etag', why: 'ETag + If-None-Match returns 304 with no body when nothing changed.' },
    { q: 'A pricing page went out with a wrong price and is cached at the edges.', a: 'purge', why: 'Purge that URL so every edge refetches the corrected page.' },
    { q: 'You run L1 caches on 12 API servers in front of Redis; after a price change some servers keep the old price for 30 s.', a: 'pubsub', why: 'Publish an invalidation message so every server drops its L1 copy at once (keep the short L1 TTL as a backstop).' },
    { q: 'The search service caches product data owned by the catalog service and shows old names after edits.', a: 'events', why: 'The owner publishes change events (outbox → broker); subscribers delete their cached copies.' },
    { q: 'An email campaign links to /p/12?utm_source=mail&utm_campaign=diwali and the CDN hit ratio for that page drops.', a: 'cdnkey', why: 'Each parameter combination is a new cache key. Ignore utm_* in the key.' },
    { q: 'Someone added Vary: User-Agent to the home page and the CDN hit ratio fell to almost zero.', a: 'vary', why: 'Every browser version becomes its own copy. Vary only on headers that change the response.' },
    { q: 'A patient reports seeing another patient\'s appointments; CDN logs show a cache HIT.', a: 'leak', why: 'A personalised response was cacheable at the edge. Mark it private or no-store.' },
    { q: 'p99 latency for all Redis calls jumps whenever the "export all products" endpoint runs.', a: 'bigkey', why: 'One huge value blocks Redis\'s single command thread. Split or page the data.' },
    { q: 'You are moving to a new Redis cluster tonight and don\'t want a cold-start flood on SQL Server.', a: 'warm', why: 'Pre-load the hottest keys before switching traffic.' },
    { q: 'You need "max 100 requests per minute per API key" across 10 API servers.', a: 'redisuses', why: 'A shared Redis counter with INCR + EXPIRE (or a token bucket script) works across all servers.' },
    { q: 'Users in Frankfurt see an old product description for a few seconds after an edit made in Mumbai.', a: 'multiregion', why: 'Cross-region invalidation travels by event; staleness = event lag (+ TTL). That is the normal trade-off.' },
    { q: 'After the catalogue tripled, hit ratio dropped from 96% to 72% and evictions jumped.', a: 'monitor', why: 'Memory is full and keys are being evicted: the cache is too small for the working set.' }
  ];

  /* ---------------- walkthrough built on Kit.mini + Kit.story ---------------- */
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

  /* ---------------- Week 3 series, drill and page setup ---------------- */
  const SERIES = [
    ['caching-overview.html', 'H15 Why cache', 'Why caching exists'],
    ['cache-read-strategies.html', 'H16 Read', 'Read strategies'],
    ['cache-write-strategies.html', 'H17 Write', 'Write strategies & invalidation'],
    ['cache-eviction.html', 'H18 Eviction', 'Eviction policies'],
    ['distributed-caching.html', 'H19 Distributed', 'Distributed caching'],
    ['cache-failure-modes.html', 'H20 Failures', 'Caching failure modes'],
    ['cdn-http-caching.html', 'H21 CDN & HTTP', 'CDN & HTTP caching'],
    ['caching-in-practice.html', 'Playbook', 'Caching in practice: the interview playbook'],
    ['caching-patterns-atlas.html', 'All patterns', 'All caching patterns at a glance']
  ];
  function series(el, file) {
    if (window.SD) return SD.series(el, file, 'hld');
    el.classList.add('series'); el.setAttribute('aria-label', 'Week 3: caching topics');
    el.innerHTML = '<span class="lbl">Week 3 · Caching</span>' + SERIES.map(([f, short]) => `<a href="${f}"${f === file ? ' aria-current="page"' : ''}>${short}</a>`).join('');
  }
  function prevNext(el, file) {
    if (window.SD) return SD.prevNext(el, file, 'hld');
    const i = SERIES.findIndex(x => x[0] === file); el.classList.add('prevnext');
    const p = SERIES[i - 1], n = SERIES[i + 1];
    el.innerHTML = (p ? `<a class="prev" href="${p[0]}"><small>← Previous</small>${p[2]}</a>` : '') + (n ? `<a class="next" href="${n[0]}"><small>Next →</small>${n[2]}</a>` : '');
  }
  /** one-question-at-a-time "which pattern fits?" drill; options are the page's card names */
  function drill(el, ids, extra) {
    const names = ids.map(id => CARDS[id].name);
    const items = QUIZ.filter(q => ids.includes(q.a)).map(q => ({ q: q.q, a: CARDS[q.a].name, why: q.why })).concat(extra || []);
    Kit.pick(el, items, names);
  }
  /** wires a standard caching page: cards, series strip, page nav, drill, previous/next */
  function page(o) {
    const $ = id => document.getElementById(id);
    if ($('atlas')) Kit.atlas($('atlas'), { cards: CF.cards(o.ids, { links: o.links }), filters: o.filters });
    if ($('series')) series($('series'), o.file);
    if ($('pageNav')) Kit.pageNav($('pageNav'));
    if ($('drill')) drill($('drill'), o.drillIds || o.ids, o.extraDrill);
    if ($('prevnext')) prevNext($('prevnext'), o.file);
  }

  window.CF = {
    CARDS, QUIZ, SERIES, ttlBar, story, series, prevNext, drill, page,
    cards: (ids, o = {}) => ids.map(id => Object.assign({}, CARDS[id], { href: o.links ? LINK[id] : undefined })),
    quiz: ids => QUIZ.filter(q => ids.includes(q.a))
  };
})();
