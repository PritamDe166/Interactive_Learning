/* Weeks 1–2 (networking + scaling) shared pattern cards for Kit.atlas, plus "which one fits?" drills.
   Same card shape as caching-flows.js: { name, tone, tags, rule, takeaway, use, avoid, vb, build(m) → [{ cap, go }], reset? }
   Usage on a page:  Kit.atlas($('atlas'), { cards: FF.cards([...ids]) });  FF.drill($('drill'), [...ids], extraItems) */
(function () {
  /* common little layouts */
  const dns3 = (m, a, b) => { m.tile('u', 36, 75, 'User', 'user'); m.box('dns', 150, 75, 'DNS', { icon: 'dns', w: 76 }); m.box('a', 296, 35, a, { icon: 'server', w: 112 }); m.box('b', 296, 118, b, { icon: 'server', w: 112 }); m.wire('u', 'dns'); m.wire('dns', 'a'); m.wire('dns', 'b'); };
  const C = {
    /* ---------- H1 · DNS routing policies ---------- */
    dnssimple: { name: 'Simple (one answer)', tone: 'cyan', tags: ['DNS routing'],
      rule: 'The name has one record (or a fixed list). Every resolver gets the <b>same answer</b>, whatever the user\'s location or the server\'s health.',
      takeaway: 'Fine for one server or one load balancer in one region.', use: 'Small sites; a name that points at a load balancer or CDN.', avoid: 'Several regions, or anything that needs DNS to route around failures.',
      build(m) { dns3(m, 'Mumbai', 'Virginia'); m.state('b', 'dim');
        return [
          { cap: 'User asks for <code>shop.example.com</code>', go: async r => { await m.send(['u', 'dns'], { run: r, label: 'A?' }); } },
          { cap: 'DNS always answers the same IP: <b>Mumbai</b>', go: async r => { await m.send(['dns', 'a'], { run: r, tone: 'teal', label: '203.0.113.10' }); m.state('a', 'ok'); } },
          { cap: 'A user in New York also goes to Mumbai: slow, but simple', go: async r => { m.badge('u', 'NY user', 'muted'); await m.send(['u', 'dns', 'a'], { run: r, tone: 'yellow' }); m.badge('a', '+220 ms', 'red'); } }
        ]; } },
    dnsweighted: { name: 'Weighted', tone: 'teal', tags: ['DNS routing'],
      rule: 'Each answer has a <b>weight</b>: e.g. 90% of lookups get the current version, 10% get the new one.',
      takeaway: 'A cheap canary or gradual migration, but resolvers cache answers, so the split is approximate.', use: 'Canary releases, moving traffic between data centres step by step.', avoid: 'Instant rollback: cached answers keep flowing until the TTL ends.',
      build(m) { dns3(m, 'v1 (weight 90)', 'v2 (weight 10)');
        return [
          { cap: 'Ten users look up the same name', go: async r => { for (let i = 0; i < 3; i++) await m.send(['u', 'dns'], { run: r, ms: 260 }); } },
          { cap: 'Nine get <b>v1</b>…', go: async r => { await m.send(['dns', 'a'], { run: r, tone: 'teal', label: '×9' }); m.badge('a', '90%', 'teal'); } },
          { cap: '…one gets <b>v2</b>. Raise its weight as confidence grows', go: async r => { await m.send(['dns', 'b'], { run: r, tone: 'yellow', label: '×1' }); m.badge('b', '10%', 'yellow'); } }
        ]; } },
    dnsgeo: { name: 'Geolocation (GeoDNS)', tone: 'blue', tags: ['DNS routing'],
      rule: 'DNS looks at <b>where the request comes from</b> (the resolver\'s IP, or the user\'s subnet if the resolver sends it) and answers with that region\'s IP.',
      takeaway: 'Users in India get Mumbai, users in the US get Virginia.', use: 'Multi-region apps; data-residency rules ("EU users stay in the EU").', avoid: 'Users on a far-away public resolver can be placed in the wrong region.',
      build(m) { m.tile('u', 36, 35, 'India', 'user'); m.tile('v', 36, 118, 'USA', 'user'); m.box('dns', 150, 75, 'GeoDNS', { icon: 'dns', w: 86 }); m.box('a', 296, 35, 'Mumbai', { icon: 'server', w: 100 }); m.box('b', 296, 118, 'Virginia', { icon: 'server', w: 100 }); m.wire('u', 'dns'); m.wire('v', 'dns'); m.wire('dns', 'a'); m.wire('dns', 'b');
        return [
          { cap: 'A lookup from India…', go: async r => { await m.send(['u', 'dns'], { run: r, label: 'from IN' }); } },
          { cap: '…gets the <b>Mumbai</b> IP', go: async r => { await m.send(['dns', 'a'], { run: r, tone: 'teal' }); m.badge('a', 'IN users', 'teal'); } },
          { cap: 'A lookup from the USA gets <b>Virginia</b>', go: async r => { await m.send(['v', 'dns'], { run: r, label: 'from US' }); await m.send(['dns', 'b'], { run: r, tone: 'teal' }); m.badge('b', 'US users', 'teal'); } }
        ]; } },
    dnslatency: { name: 'Latency-based', tone: 'violet', tags: ['DNS routing'],
      rule: 'The DNS provider keeps <b>measured network latency</b> from each user network to each region, and answers with the fastest region, not the nearest on a map.',
      takeaway: 'Usually the best default for global apps: it follows real network paths.', use: 'Global APIs where speed matters more than borders.', avoid: 'Compliance rules that require a fixed region: use geolocation for those.',
      build(m) { dns3(m, 'Singapore', 'Mumbai'); m.badge('u', 'Dubai user', 'muted');
        return [
          { cap: 'User in Dubai looks up the API', go: async r => { await m.send(['u', 'dns'], { run: r, label: 'A?' }); } },
          { cap: 'Measured: Singapore 95 ms, Mumbai 40 ms', go: async r => { m.badge('a', '95 ms', 'red'); m.badge('b', '40 ms', 'teal'); await m.sleep(700, r); } },
          { cap: 'Answer: <b>Mumbai</b>, the faster one', go: async r => { await m.send(['dns', 'b'], { run: r, tone: 'teal' }); m.state('b', 'ok'); m.state('a', 'dim'); } }
        ]; } },
    dnsfailover: { name: 'Failover (health-checked)', tone: 'red', tags: ['DNS routing'],
      rule: 'The DNS provider <b>health-checks</b> the primary. While it passes, DNS answers primary; when it fails, DNS answers the secondary.',
      takeaway: 'Keep the TTL low (30–60 s): clients keep using the cached dead IP until it expires.', use: 'Active-passive across regions; a static "sorry" site as a last resort.', avoid: 'Expecting instant failover: detection time + TTL is the real outage.',
      build(m) { dns3(m, 'Primary', 'Secondary'); m.state('b', 'dim');
        return [
          { cap: 'Health checks pass: DNS answers <b>Primary</b>', go: async r => { m.badge('a', 'healthy', 'teal'); await m.send(['u', 'dns', 'a'], { run: r, tone: 'teal' }); } },
          { cap: 'Primary goes down; three checks in a row fail', go: async r => { m.state('a', 'hot'); m.badge('a', 'down', 'red'); await m.sleep(700, r); } },
          { cap: 'DNS now answers <b>Secondary</b>; clients switch as their cached answer (TTL 60 s) expires', go: async r => { m.state('b', ''); m.badge('dns', 'TTL 60 s', 'yellow'); await m.send(['u', 'dns', 'b'], { run: r, tone: 'teal' }); m.state('b', 'ok'); } }
        ]; } },

    /* ---------- H2 · HTTP versions ---------- */
    h11: { name: 'HTTP/1.1 + keep-alive', tone: 'yellow', tags: ['HTTP versions'],
      rule: '<b>Keep-alive</b> reuses one TCP connection for many requests, but one at a time: a slow response blocks the ones behind it. Browsers open about <b>6 connections</b> per host to work around it.',
      takeaway: 'Reuse saves handshakes; ordering still blocks.', use: 'Everywhere as a fallback; simple internal calls.', avoid: 'Many small requests from a browser: they queue.',
      vb: [360, 150],
      build(m) { m.box('c', 50, 75, 'Browser', { icon: 'laptop', w: 84 }); m.box('s', 300, 75, 'Server', { icon: 'server', w: 84 }); m.wire('c', 's', { label: '1 connection' });
        return [
          { cap: 'Request 1 goes out on the connection…', go: async r => { await m.send(['c', 's'], { run: r, label: 'GET /a' }); } },
          { cap: '…requests 2 and 3 <b>wait</b> until response 1 is back', go: async r => { m.badge('c', '2 waiting', 'red'); await m.send(['s', 'c'], { run: r, tone: 'teal', label: '/a', ms: 1200 }); } },
          { cap: 'Then 2, then 3: one at a time on this connection', go: async r => { m.badge('c'); for (const p of ['/b', '/c']) { await m.send(['c', 's'], { run: r, label: p, ms: 360 }); await m.send(['s', 'c'], { run: r, tone: 'teal', ms: 360 }); } } }
        ]; } },
    h2: { name: 'HTTP/2 multiplexing', tone: 'cyan', tags: ['HTTP versions'],
      rule: 'Many requests travel <b>at the same time</b> as interleaved streams on one TCP connection, with compressed headers (HPACK).',
      takeaway: 'One connection, no queueing at the HTTP level. But one lost TCP packet still stalls every stream.', use: 'Browsers and gRPC: the default today.', avoid: 'Lossy mobile networks, where TCP head-of-line blocking hurts.',
      build(m) { m.box('c', 50, 75, 'Browser', { icon: 'laptop', w: 84 }); m.box('s', 300, 75, 'Server', { icon: 'server', w: 84 }); m.wire('c', 's', { label: '1 TCP connection' });
        return [
          { cap: 'Three requests leave together as streams 1, 3, 5', go: async r => { await Promise.all(['/a', '/b', '/c'].map((p, i) => m.send(['c', 's'], { run: r, label: p, ms: 500 + i * 120 }))); } },
          { cap: 'Responses come back interleaved, whichever is ready first', go: async r => { await Promise.all(['/c', '/a', '/b'].map((p, i) => m.send(['s', 'c'], { run: r, tone: 'teal', label: p, ms: 500 + i * 160 }))); } },
          { cap: 'A lost TCP packet: <b>all</b> streams wait for the resend', go: async r => { m.badge('s', 'packet lost', 'red'); m.state('c', 'hot'); await m.sleep(800, r); } }
        ]; } },
    h3: { name: 'HTTP/3 over QUIC', tone: 'teal', tags: ['HTTP versions'],
      rule: 'QUIC runs on <b>UDP</b> and does reliability <b>per stream</b>, so a lost packet only stalls its own stream. The TLS 1.3 handshake is built in.',
      takeaway: 'Faster setup (1 round trip, 0 on resume) and survives a network change (Wi-Fi → 4G).', use: 'Mobile users, video, global sites behind a CDN.', avoid: 'Networks that block UDP: clients fall back to HTTP/2.',
      build(m) { m.box('c', 50, 75, 'Phone', { icon: 'phone', w: 80 }); m.box('s', 300, 75, 'Server', { icon: 'server', w: 84 }); m.wire('c', 's', { label: 'QUIC (UDP)' });
        return [
          { cap: 'One round trip sets up the connection <b>and</b> encryption', go: async r => { await m.send(['c', 's'], { run: r, label: 'hello + keys' }); await m.send(['s', 'c'], { run: r, tone: 'teal' }); } },
          { cap: 'A packet for stream /b is lost: only /b waits', go: async r => { m.badge('s', '/b resend', 'yellow'); await Promise.all(['/a', '/c'].map((p, i) => m.send(['s', 'c'], { run: r, tone: 'teal', label: p, ms: 500 + i * 120 }))); } },
          { cap: 'Phone switches Wi-Fi → 4G: same connection ID, no new handshake', go: async r => { m.badge('c', 'new IP, same conn', 'teal'); await m.send(['c', 's'], { run: r, label: 'GET /d' }); } }
        ]; } },

    /* ---------- H4 · where TLS ends ---------- */
    tlsterm: { name: 'TLS termination at the LB', tone: 'cyan', tags: ['TLS at the edge'],
      rule: 'The load balancer holds the certificate, <b>decrypts</b> traffic and forwards plain HTTP to the app servers on the private network.',
      takeaway: 'One place for certificates; the LB can read paths and cookies to route.', use: 'The common default behind a cloud load balancer.', avoid: 'Rules that require encryption on every hop (health data, PCI): re-encrypt instead.',
      build(m) { m.tile('u', 36, 75, 'Client', 'user'); m.box('lb', 170, 75, 'Load balancer', { icon: 'lb', w: 116 }); m.box('s', 312, 75, 'App', { icon: 'server', w: 76 }); m.wire('u', 'lb'); m.wire('lb', 's');
        return [
          { cap: 'Client → LB over <b>HTTPS</b>', go: async r => { await m.send(['u', 'lb'], { run: r, label: 'TLS', tone: 'teal' }); m.badge('lb', 'cert here', 'teal'); } },
          { cap: 'LB decrypts, reads <code>/api/orders</code>, picks a server', go: async r => { await m.sleep(500, r); } },
          { cap: 'LB → app over <b>plain HTTP</b> inside the private network', go: async r => { await m.send(['lb', 's'], { run: r, label: 'http', tone: 'yellow' }); } }
        ]; } },
    tlspass: { name: 'TLS passthrough', tone: 'blue', tags: ['TLS at the edge'],
      rule: 'The load balancer works at L4 and forwards the <b>encrypted bytes untouched</b>; the app server holds the certificate and decrypts.',
      takeaway: 'End-to-end encryption, but the LB can\'t see URLs, headers or cookies.', use: 'When only the app may see plaintext, or for non-HTTP protocols.', avoid: 'Path-based routing, WAF rules or header-based stickiness.',
      build(m) { m.tile('u', 36, 75, 'Client', 'user'); m.box('lb', 170, 75, 'L4 LB', { icon: 'lb', w: 96 }); m.box('s', 312, 75, 'App', { icon: 'server', w: 76 }); m.wire('u', 'lb'); m.wire('lb', 's');
        return [
          { cap: 'Encrypted bytes reach the LB', go: async r => { await m.send(['u', 'lb'], { run: r, label: 'TLS', tone: 'teal' }); } },
          { cap: 'LB can\'t read them; it just picks a server by IP/port', go: async r => { m.badge('lb', 'sees only IP:port', 'muted'); await m.sleep(500, r); } },
          { cap: 'App decrypts with its own certificate', go: async r => { await m.send(['lb', 's'], { run: r, label: 'TLS', tone: 'teal' }); m.badge('s', 'cert here', 'teal'); } }
        ]; } },
    tlsreenc: { name: 'Re-encryption (TLS bridging)', tone: 'violet', tags: ['TLS at the edge'],
      rule: 'The LB decrypts to inspect and route, then opens a <b>new TLS connection</b> to the app server.',
      takeaway: 'Smart routing and encryption on every hop, at the cost of a second handshake and more certificates.', use: 'Regulated data with L7 routing or a WAF.', avoid: 'Very latency-sensitive internal hops where the network is already trusted.',
      build(m) { m.tile('u', 36, 75, 'Client', 'user'); m.box('lb', 170, 75, 'Load balancer', { icon: 'lb', w: 116 }); m.box('s', 312, 75, 'App', { icon: 'server', w: 76 }); m.wire('u', 'lb'); m.wire('lb', 's');
        return [
          { cap: 'HTTPS to the LB; it decrypts and inspects', go: async r => { await m.send(['u', 'lb'], { run: r, label: 'TLS', tone: 'teal' }); m.badge('lb', 'inspect + route', 'violet'); } },
          { cap: 'A <b>second</b> TLS session to the app', go: async r => { await m.send(['lb', 's'], { run: r, label: 'TLS #2', tone: 'teal' }); } }
        ]; } },
    mtls: { name: 'Mutual TLS (mTLS)', tone: 'teal', tags: ['TLS at the edge'],
      rule: 'Normally only the server proves who it is. In mTLS <b>both sides present certificates</b>, so the server also knows exactly which client is calling.',
      takeaway: 'Service-to-service identity without passwords or API keys.', use: 'Internal microservice calls (a service mesh automates it), partner/bank APIs.', avoid: 'Public browser traffic: users don\'t have client certificates.',
      build(m) { m.box('a', 60, 75, 'Orders svc', { icon: 'server', w: 96 }); m.box('b', 300, 75, 'Payments svc', { icon: 'server', w: 106 }); m.wire('a', 'b');
        return [
          { cap: 'Payments shows its certificate', go: async r => { await m.send(['b', 'a'], { run: r, label: 'cert: payments', tone: 'teal' }); m.badge('a', 'verified ✓', 'teal'); } },
          { cap: 'Orders shows <b>its</b> certificate too', go: async r => { await m.send(['a', 'b'], { run: r, label: 'cert: orders', tone: 'yellow' }); m.badge('b', 'caller = orders ✓', 'teal'); } },
          { cap: 'An unknown caller without a valid cert is refused', go: async r => { m.badge('b', 'no cert → reject', 'red'); await m.sleep(500, r); } }
        ]; } },
    hsts: { name: 'HSTS', tone: 'orange', tags: ['TLS at the edge'],
      rule: 'The response header <code>Strict-Transport-Security: max-age=31536000</code> tells the browser: <b>only ever use HTTPS</b> for this site, even if someone types http://.',
      takeaway: 'Stops downgrade attacks where someone on the Wi-Fi keeps you on plain HTTP.', use: 'Every HTTPS site; add the domain to the browser preload list.', avoid: 'Turning it on before every subdomain supports HTTPS (with includeSubDomains).',
      build(m) { m.tile('u', 36, 75, 'Browser', 'laptop'); m.tile('x', 170, 30, 'Café Wi-Fi', 'router'); m.box('s', 312, 75, 'bank.com', { icon: 'server', w: 90 }); m.wire('u', 'x'); m.wire('x', 's'); m.wire('u', 's');
        return [
          { cap: 'Without HSTS: typing <code>bank.com</code> starts on <b>http://</b>; an attacker on the Wi-Fi can keep you there', go: async r => { await m.send(['u', 'x'], { run: r, label: 'http://', tone: 'red' }); m.state('x', 'hot'); } },
          { cap: 'With HSTS (remembered from an earlier visit): the browser upgrades to https:// <b>before</b> sending anything', go: async r => { m.state('x', 'dim'); await m.send(['u', 's'], { run: r, label: 'https://', tone: 'teal' }); m.badge('s', 'HSTS 1 year', 'teal'); } }
        ]; } },

    /* ---------- H6 · disaster recovery ---------- */
    drbackup: { name: 'Backup & restore', tone: 'orange', tags: ['disaster recovery'],
      rule: 'Take regular backups and copy them to another region. After a disaster, <b>build everything again</b> and restore the latest backup.',
      takeaway: 'Cheapest. RPO = time since last backup (hours); RTO = hours to a day.', use: 'Internal tools, reporting, anything that can be down for a while.', avoid: 'Customer-facing systems with tight recovery targets.',
      build(m) { m.box('p', 70, 75, 'Primary region', { icon: 'cloud', w: 124 }); m.box('d', 290, 75, 'DR region', { icon: 'cloud', w: 110 }); m.wire('p', 'd', { dash: true }); m.state('d', 'dim');
        return [
          { cap: 'Nightly backup copied to the DR region', go: async r => { await m.send(['p', 'd'], { run: r, label: 'backup', tone: 'yellow' }); m.badge('d', 'backups only', 'muted'); } },
          { cap: 'Primary region lost at 18:00: last backup was 02:00', go: async r => { m.state('p', 'hot'); m.badge('p', 'down', 'red'); await m.sleep(500, r); } },
          { cap: 'Build servers, restore data: back by tomorrow. <b>RPO 16 h · RTO ~1 day</b>', go: async r => { m.state('d', 'ok'); m.badge('d', 'RPO 16 h · RTO 1 day', 'red'); await m.sleep(500, r); } }
        ]; } },
    drpilot: { name: 'Pilot light', tone: 'yellow', tags: ['disaster recovery'],
      rule: 'The <b>data</b> is replicated continuously to the DR region, but app servers there are off (or minimal). On disaster, start them and scale up.',
      takeaway: 'RPO minutes or less; RTO tens of minutes. Low running cost.', use: 'Important systems that can tolerate a short outage.', avoid: 'When you can\'t afford the time to boot and warm the servers.',
      build(m) { m.box('p', 70, 75, 'Primary region', { icon: 'cloud', w: 124 }); m.db('d', 290, 75, 'DR: DB replica'); m.wire('p', 'd');
        return [
          { cap: 'Database changes stream to the DR replica', go: async r => { await m.send(['p', 'd'], { run: r, label: 'replication', tone: 'teal' }); m.badge('d', 'servers off', 'muted'); } },
          { cap: 'Disaster: promote the replica, start the app servers', go: async r => { m.state('p', 'hot'); m.badge('p', 'down', 'red'); await m.sleep(500, r); m.state('d', 'ok'); } },
          { cap: '<b>RPO ~minutes · RTO ~30 min</b>', go: async r => { m.badge('d', 'RPO min · RTO 30 min', 'yellow'); await m.sleep(300, r); } }
        ]; } },
    drwarm: { name: 'Warm standby', tone: 'teal', tags: ['disaster recovery'],
      rule: 'A <b>smaller full copy</b> of the system runs all the time in the DR region, with live data. On disaster, switch DNS and scale it up.',
      takeaway: 'RPO seconds; RTO minutes. You pay for the always-on copy.', use: 'Customer-facing systems that need recovery in minutes.', avoid: 'Forgetting to test it: an untested standby is a guess.',
      build(m) { m.box('p', 70, 75, 'Primary (100%)', { icon: 'cloud', w: 124 }); m.box('d', 290, 75, 'Standby (20%)', { icon: 'cloud', w: 118 }); m.wire('p', 'd');
        return [
          { cap: 'Standby runs at small size with replicated data', go: async r => { await m.send(['p', 'd'], { run: r, label: 'live data', tone: 'teal' }); } },
          { cap: 'Disaster: DNS points to the standby, autoscaling grows it', go: async r => { m.state('p', 'hot'); m.badge('p', 'down', 'red'); m.text('d', 'Standby → 100%'); m.state('d', 'ok'); await m.sleep(500, r); } },
          { cap: '<b>RPO seconds · RTO minutes</b>', go: async r => { m.badge('d', 'RPO s · RTO min', 'teal'); await m.sleep(300, r); } }
        ]; },
      reset(m) { m.text('d', 'Standby (20%)'); } },
    dractive: { name: 'Active-active (multi-site)', tone: 'blue', tags: ['disaster recovery'],
      rule: 'Two or more regions <b>serve real traffic all the time</b>. If one fails, the others already have the users and the data.',
      takeaway: 'RPO near zero, RTO near zero, at the highest cost and complexity (data conflicts).', use: 'Payments, global consumer apps, anything that "must never be down".', avoid: 'Apps whose database can\'t handle writes in two regions.',
      build(m) { m.tile('u', 180, 22, 'Users', 'users'); m.box('p', 80, 110, 'Region A', { icon: 'cloud', w: 100 }); m.box('d', 280, 110, 'Region B', { icon: 'cloud', w: 100 }); m.wire('u', 'p'); m.wire('u', 'd'); m.wire('p', 'd', { dash: true });
        return [
          { cap: 'Both regions serve users and replicate to each other', go: async r => { await Promise.all([m.send(['u', 'p'], { run: r, tone: 'teal' }), m.send(['u', 'd'], { run: r, tone: 'teal' })]); } },
          { cap: 'Region A fails: B already has the traffic', go: async r => { m.state('p', 'hot'); m.badge('p', 'down', 'red'); await m.send(['u', 'd'], { run: r, tone: 'teal', label: 'all users' }); } },
          { cap: '<b>RPO ≈ 0 · RTO ≈ seconds</b>', go: async r => { m.badge('d', 'RPO≈0 · RTO≈0', 'teal'); m.state('d', 'ok'); await m.sleep(300, r); } }
        ]; } },

    /* ---------- H9 · where state lives ---------- */
    sticky: { name: 'Sticky sessions', tone: 'orange', tags: ['where state lives'],
      rule: 'The session stays in one server\'s memory; the load balancer sets an <b>affinity cookie</b> so the same user always returns to that server.',
      takeaway: 'Quick fix for legacy apps; uneven load, and the session dies with the server.', use: 'Legacy apps you can\'t change this quarter.', avoid: 'Autoscaling and rolling deploys: users get logged out.',
      build(m) { m.tile('u', 36, 75, 'Asha', 'user'); m.box('lb', 150, 75, 'LB', { icon: 'lb', w: 70 }); m.box('a', 296, 35, 'Server 1', { icon: 'server', w: 96 }); m.box('b', 296, 118, 'Server 2', { icon: 'server', w: 96 }); m.wire('u', 'lb'); m.wire('lb', 'a'); m.wire('lb', 'b');
        return [
          { cap: 'Login lands on Server 1; session stored in its memory', go: async r => { await m.send(['u', 'lb', 'a'], { run: r, label: 'login' }); m.badge('a', 'session: Asha', 'teal'); } },
          { cap: 'Cookie <code>AFFINITY=s1</code> sends every request back to Server 1', go: async r => { await m.send(['u', 'lb', 'a'], { run: r, label: 'cookie s1', tone: 'yellow' }); } },
          { cap: 'Server 1 restarts: session gone, Asha is logged out', go: async r => { m.state('a', 'hot'); m.badge('a', 'restarted', 'red'); await m.send(['u', 'lb', 'b'], { run: r, tone: 'red', label: 'who are you?' }); } }
        ]; } },
    sessionstore: { name: 'Shared session store', tone: 'red', tags: ['where state lives'],
      rule: 'Servers keep only a <b>session ID</b> in a cookie; the session data lives in a shared store like Redis that every server reads.',
      takeaway: 'Any server can serve any request; logout and revocation are instant.', use: 'Classic web apps with server-side sessions (ASP.NET Core distributed session).', avoid: 'Forgetting the store is now critical: make Redis highly available.',
      build(m) { m.tile('u', 36, 75, 'Asha', 'user'); m.box('lb', 124, 75, 'LB', { icon: 'lb', w: 62 }); m.box('a', 222, 35, 'Server 1', { icon: 'server', w: 88 }); m.box('b', 222, 118, 'Server 2', { icon: 'server', w: 88 }); m.box('r', 316, 75, 'Redis', { icon: 'ram', w: 70, h: 30 }); m.wire('u', 'lb'); m.wire('lb', 'a'); m.wire('lb', 'b'); m.wire('a', 'r'); m.wire('b', 'r');
        return [
          { cap: 'Login on Server 1 writes the session to Redis', go: async r => { await m.send(['u', 'lb', 'a', 'r'], { run: r, label: 'sid=7f' }); m.badge('r', '7f → Asha', 'teal'); } },
          { cap: 'Next request goes to Server 2; it reads the same session', go: async r => { await m.send(['u', 'lb', 'b', 'r'], { run: r, label: 'sid=7f', tone: 'teal' }); m.badge('b', 'Hi Asha', 'teal'); } }
        ]; } },
    jwt: { name: 'Token on the client (JWT)', tone: 'violet', tags: ['where state lives'],
      rule: 'After login the client holds a <b>signed token</b> with the user\'s claims and sends it on each call (<code>Authorization: Bearer …</code>). Any server checks the signature, no lookup.',
      takeaway: 'No session store at all; but a token stays valid until it expires, so keep it short and add refresh tokens.', use: 'APIs, mobile apps, service-to-service calls.', avoid: 'Needing instant logout or big claims (the token travels on every request).',
      build(m) { m.tile('u', 36, 75, 'App', 'phone'); m.box('lb', 150, 75, 'LB', { icon: 'lb', w: 70 }); m.box('a', 296, 35, 'Server 1', { icon: 'server', w: 96 }); m.box('b', 296, 118, 'Server 2', { icon: 'server', w: 96 }); m.wire('u', 'lb'); m.wire('lb', 'a'); m.wire('lb', 'b');
        return [
          { cap: 'Login returns a signed token (expires in 15 min)', go: async r => { await m.send(['a', 'lb', 'u'], { run: r, label: 'JWT', tone: 'yellow' }); m.badge('u', 'holds JWT', 'violet'); } },
          { cap: 'Any server verifies the signature and reads the claims', go: async r => { await m.send(['u', 'lb', 'b'], { run: r, label: 'Bearer JWT', tone: 'teal' }); m.badge('b', 'sig ✓ user=Asha', 'teal'); } }
        ]; } },
    blob: { name: 'Files in object storage', tone: 'blue', tags: ['where state lives'],
      rule: 'Uploads and generated files go to <b>blob/object storage</b> (Azure Blob, S3), not the server\'s disk. The app stores only the file\'s key.',
      takeaway: 'Servers stay disposable; files survive restarts and every server can serve them.', use: 'Profile photos, reports, invoices, exports.', avoid: 'Saving to <code>C:\\uploads</code> on one VM: the file is missing on every other server.',
      build(m) { m.tile('u', 36, 75, 'User', 'user'); m.box('a', 160, 35, 'Server 1', { icon: 'server', w: 90 }); m.box('b', 160, 118, 'Server 2', { icon: 'server', w: 90 }); m.box('s', 310, 75, 'Blob storage', { icon: 'bucket', w: 100 }); m.wire('u', 'a'); m.wire('u', 'b'); m.wire('a', 's'); m.wire('b', 's');
        return [
          { cap: 'Upload hits Server 1; it writes the file to blob storage', go: async r => { await m.send(['u', 'a', 's'], { run: r, label: 'photo.jpg' }); m.badge('s', 'photo.jpg', 'teal'); } },
          { cap: 'Later, Server 2 serves it (or hands out a short-lived download URL)', go: async r => { await m.send(['s', 'b', 'u'], { run: r, tone: 'teal', label: 'photo' }); } }
        ]; } },

    /* ---------- H10–12 · fronting and spreading traffic ---------- */
    bff: { name: 'Backend for frontend (BFF)', tone: 'violet', tags: ['gateway'],
      rule: 'One gateway <b>per client type</b>: the mobile BFF returns small, phone-shaped responses; the web BFF returns richer ones. Each is owned by that client\'s team.',
      takeaway: 'Clients get exactly what their screens need without the services changing.', use: 'Web and mobile apps with different screens and release cycles.', avoid: 'Copying business logic into each BFF: they should only shape and combine.',
      build(m) { m.tile('w', 36, 35, 'Web', 'laptop'); m.tile('p', 36, 118, 'Mobile', 'phone'); m.box('bw', 160, 35, 'Web BFF', { icon: 'shield', w: 90 }); m.box('bp', 160, 118, 'Mobile BFF', { icon: 'shield', w: 96 }); m.box('s', 310, 75, 'Services', { icon: 'server', w: 90 }); m.wire('w', 'bw'); m.wire('p', 'bp'); m.wire('bw', 's'); m.wire('bp', 's');
        return [
          { cap: 'Web asks its BFF: full product page', go: async r => { await m.send(['w', 'bw', 's'], { run: r, label: 'page' }); await m.send(['s', 'bw', 'w'], { run: r, tone: 'teal', label: '40 KB' }); } },
          { cap: 'Mobile asks its BFF: same data, trimmed for a phone', go: async r => { await m.send(['p', 'bp', 's'], { run: r, label: 'page' }); await m.send(['s', 'bp', 'p'], { run: r, tone: 'teal', label: '6 KB' }); } }
        ]; } },
    aggregate: { name: 'Request aggregation', tone: 'cyan', tags: ['gateway'],
      rule: 'The client makes <b>one call</b>; the gateway calls several services <b>in parallel</b> and merges the answers into one response.',
      takeaway: 'Fewer round trips from slow mobile networks; the gateway pays the fan-out on a fast internal network.', use: 'Dashboards and detail pages that need data from many services.', avoid: 'Long chains: one slow service delays the whole response. Set timeouts and return partial data.',
      build(m) { m.tile('u', 36, 75, 'App', 'phone'); m.box('g', 150, 75, 'Gateway', { icon: 'shield', w: 86 }); ['Orders', 'Profile', 'Offers'].forEach((n, i) => { m.box('s' + i, 300, 28 + i * 47, n, { w: 90, h: 30 }); m.wire('g', 's' + i); }); m.wire('u', 'g');
        return [
          { cap: 'One request: <code>GET /home</code>', go: async r => { await m.send(['u', 'g'], { run: r, label: '/home' }); } },
          { cap: 'Gateway calls three services at the same time', go: async r => { await Promise.all([0, 1, 2].map(i => m.send(['g', 's' + i], { run: r, ms: 500 }))); await Promise.all([0, 1, 2].map(i => m.send(['s' + i, 'g'], { run: r, tone: 'teal', ms: 500 + i * 100 }))); } },
          { cap: 'One merged response back to the phone', go: async r => { await m.send(['g', 'u'], { run: r, tone: 'teal', label: '1 response' }); } }
        ]; } },
    dnslb: { name: 'DNS load balancing', tone: 'yellow', tags: ['spreading traffic'],
      rule: 'The name returns <b>several IPs</b> (or a different one per lookup), so clients spread themselves across servers or regions.',
      takeaway: 'Free and global, but slow to react: cached answers ignore failures until the TTL expires.', use: 'Spreading users across regions or several load balancers.', avoid: 'Fine-grained balancing inside one data centre: use a real load balancer.',
      build(m) { dns3(m, 'LB · region A', 'LB · region B');
        return [
          { cap: 'DNS returns both IPs, rotating the order', go: async r => { await m.send(['u', 'dns'], { run: r, label: 'A?' }); m.badge('dns', 'A, B', 'yellow'); } },
          { cap: 'Clients mostly take the first one: traffic splits roughly in half', go: async r => { await m.send(['dns', 'a'], { run: r, tone: 'teal' }); await m.send(['dns', 'b'], { run: r, tone: 'teal' }); } },
          { cap: 'A fails: clients with a cached "A" keep trying it until the TTL ends', go: async r => { m.state('a', 'hot'); m.badge('a', 'down · still cached', 'red'); await m.sleep(500, r); } }
        ]; } },
    activepassive: { name: 'Active-passive', tone: 'orange', tags: ['spreading traffic'],
      rule: 'One node serves; a <b>standby</b> watches it with heartbeats and takes over its address (a floating/virtual IP) when it stops answering.',
      takeaway: 'Simple and safe for things that can only have one leader; the standby\'s capacity sits idle.', use: 'Load balancer pairs, primary/standby databases.', avoid: 'Thinking it\'s instant: detection plus takeover takes seconds.',
      build(m) { m.tile('u', 36, 75, 'Clients', 'users'); m.box('a', 250, 35, 'Active', { icon: 'lb', w: 92 }); m.box('b', 250, 118, 'Passive', { icon: 'lb', w: 92 }); m.wire('u', 'a'); m.wire('u', 'b'); m.wire('a', 'b', { dash: true }); m.state('b', 'dim');
        return [
          { cap: 'All traffic to the active node; heartbeats every second', go: async r => { m.badge('a', 'VIP 10.0.0.5', 'teal'); await m.send(['u', 'a'], { run: r, tone: 'teal' }); await m.send(['a', 'b'], { run: r, label: '♥', ms: 400 }); } },
          { cap: 'Heartbeats stop: active has failed', go: async r => { m.state('a', 'hot'); m.badge('a', 'down', 'red'); await m.sleep(600, r); } },
          { cap: 'Passive claims the virtual IP and serves', go: async r => { m.state('b', 'ok'); m.badge('b', 'VIP 10.0.0.5', 'teal'); await m.send(['u', 'b'], { run: r, tone: 'teal' }); } }
        ]; } },
    activeactive: { name: 'Active-active', tone: 'teal', tags: ['spreading traffic'],
      rule: 'All nodes <b>serve at the same time</b>. If one fails, the rest absorb its share.',
      takeaway: 'No idle hardware, but each node must have room: two nodes should each run below ~50% so one can carry everything.', use: 'Stateless app tiers, load-balancer fleets, multi-region apps.', avoid: 'Running each node at 80%: after a failure the survivor is overloaded.',
      build(m) { m.tile('u', 36, 75, 'Clients', 'users'); m.box('a', 250, 35, 'Node A', { icon: 'server', w: 92 }); m.box('b', 250, 118, 'Node B', { icon: 'server', w: 92 }); m.wire('u', 'a'); m.wire('u', 'b');
        return [
          { cap: 'Traffic splits across both: 45% load each', go: async r => { m.badge('a', '45%', 'teal'); m.badge('b', '45%', 'teal'); await Promise.all([m.send(['u', 'a'], { run: r, tone: 'teal' }), m.send(['u', 'b'], { run: r, tone: 'teal' })]); } },
          { cap: 'Node A fails: B takes everything at 90%, still OK', go: async r => { m.state('a', 'hot'); m.badge('a', 'down', 'red'); m.badge('b', '90%', 'yellow'); await m.send(['u', 'b'], { run: r, tone: 'teal', label: 'all' }); } }
        ]; } },

    /* ---------- H13 · power of two choices ---------- */
    p2c: { name: 'Power of two choices', tone: 'violet', tags: ['LB algorithms'],
      rule: 'Pick <b>two servers at random</b> and send the request to the one with fewer active requests.',
      takeaway: 'Almost as good as checking every server, much cheaper, and avoids every balancer piling onto the same "least loaded" server.', use: 'Large fleets and many independent balancers (Envoy, NGINX, HAProxy offer it).', avoid: 'Two or three servers: just use least connections.',
      build(m) { m.box('lb', 60, 75, 'Balancer', { icon: 'lb', w: 90 }); const L = [3, 7, 2, 5]; L.forEach((n, i) => { m.box('s' + i, 290, 22 + i * 36, 'S' + (i + 1) + ' · ' + n + ' active', { w: 120, h: 26 }); m.wire('lb', 's' + i); });
        return [
          { cap: 'Randomly sample two: <b>S2</b> (7) and <b>S3</b> (2)', go: async r => { m.state('s1', 'on'); m.state('s2', 'on'); m.state('s0', 'dim'); m.state('s3', 'dim'); await m.sleep(700, r); } },
          { cap: 'Send to the less busy one: <b>S3</b>', go: async r => { await m.send(['lb', 's2'], { run: r, tone: 'teal' }); m.text('s2', 'S3 · 3 active'); m.state('s2', 'ok'); m.state('s1', ''); } }
        ]; },
      reset(m) { m.text('s2', 'S3 · 2 active'); } }
  };
  Object.keys(C).forEach(id => { C[id].id = id; C[id].vb = C[id].vb || [360, 150]; });

  /* scenario drills: a = card id */
  const Q = [
    { q: 'You are launching a new checkout version and want 5% of users on it for a day.', a: 'dnsweighted', why: 'Weighted records split lookups by percentage (approximately, because of caching).' },
    { q: 'EU users\' data must be served from the Frankfurt region.', a: 'dnsgeo', why: 'Geolocation routing answers by where the user is; latency-based might pick another region.' },
    { q: 'A global API should send each user to whichever region answers fastest.', a: 'dnslatency', why: 'Latency-based routing uses measured network latency, not distance.' },
    { q: 'If the Mumbai region goes down, users should be sent to Singapore automatically.', a: 'dnsfailover', why: 'Health-checked failover records switch the answer; keep the TTL low.' },
    { q: 'A single-region intranet app behind one load balancer.', a: 'dnssimple', why: 'One record pointing at the load balancer is all you need.' },
    { q: 'A product page makes 60 small requests and they queue behind each other.', a: 'h2', why: 'HTTP/2 multiplexes them on one connection.' },
    { q: 'Mobile users on patchy networks see whole pages stall when one packet is lost.', a: 'h3', why: 'QUIC recovers loss per stream, so one loss stalls only its stream.' },
    { q: 'The load balancer must route by URL path and you want one place to renew certificates.', a: 'tlsterm', why: 'Terminate TLS at the LB; it can read the path.' },
    { q: 'Compliance says traffic must be encrypted on every hop, and you still need path routing.', a: 'tlsreenc', why: 'Decrypt at the LB to route, then re-encrypt to the servers.' },
    { q: 'The payments service must accept calls only from the orders service.', a: 'mtls', why: 'Mutual TLS gives the caller a certificate identity the server can check.' },
    { q: 'You want browsers to never even try plain HTTP on your bank site.', a: 'hsts', why: 'HSTS makes the browser upgrade to HTTPS before sending anything.' },
    { q: 'An internal reporting app can be down for a day, and losing a day of data is acceptable.', a: 'drbackup', why: 'Backup & restore is the cheapest strategy that meets RPO/RTO of about a day.' },
    { q: 'Online booking must be back within minutes after a region failure, with almost no lost bookings.', a: 'drwarm', why: 'Warm standby: replicated data plus a running scaled-down copy.' },
    { q: 'Payments must keep working through a region failure with no visible outage.', a: 'dractive', why: 'Active-active: other regions already serve the traffic.' },
    { q: 'A legacy WebForms app keeps sessions in memory and you can\'t change it this quarter.', a: 'sticky', why: 'Sticky sessions keep each user on one server, at the cost of uneven load.' },
    { q: 'Users must be logged out everywhere the moment an admin disables them.', a: 'sessionstore', why: 'Delete the session from the shared store: revocation is instant.' },
    { q: 'Patients upload lab reports; any of 8 servers may later serve the download.', a: 'blob', why: 'Put files in object storage, not on one server\'s disk.' },
    { q: 'The mobile app needs smaller responses than the website from the same services.', a: 'bff', why: 'A mobile BFF shapes responses for the phone.' },
    { q: 'The home screen needs data from 5 services and the phone is on a slow network.', a: 'aggregate', why: 'Let the gateway fan out and return one combined response.' },
    { q: 'A pair of load balancers where only one should own the public IP at a time.', a: 'activepassive', why: 'Active-passive with a floating IP and heartbeats.' },
    { q: 'Ten stateless API servers; you want every one of them working all the time.', a: 'activeactive', why: 'Active-active; keep enough headroom to lose one.' },
    { q: '40 independent balancers each pick the "least loaded" server and all hit the same one.', a: 'p2c', why: 'Power of two choices spreads choices randomly while still avoiding busy servers.' }
  ];
  window.FF = {
    CARDS: C, QUIZ: Q,
    cards: ids => ids.map(id => C[id]),
    drill(el, ids, extra) { Kit.pick(el, Q.filter(q => ids.includes(q.a)).map(q => ({ q: q.q, a: C[q.a].name, why: q.why })).concat(extra || []), ids.map(id => C[id].name)); }
  };
})();
