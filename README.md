# See How It Works

Animated, clickable explainers for topics I'm learning. Live at
https://seehowitworks.dev

Hosted on S3 + CloudFront (Terraform in `infra/`), deployed by `.github/workflows/deploy.yml` on every push to `main`. DNS for `seehowitworks.dev` is a Route 53 hosted zone; the domain is registered at Hostinger with its nameservers pointing to Route 53.

## Layout

```
Interactive_explainations/
├── index.html                      # hub: links to every subject
├── assets/
│   ├── css/
│   │   ├── theme.css               # ALL colours + fonts, dark (default) and light
│   │   ├── base.css                # shared layout: top bar, toggle, type, footer
│   │   ├── hub.css                 # home pages: root hub + subject roadmaps
│   │   └── explainer.css           # explainer building blocks: stage, controls, cards, quiz
│   └── js/
│       ├── theme.js                # light/dark toggle, remembers the choice
│       └── explainer-kit.js        # shared animation helpers (move packets, cancel runs, logs)
├── _template/
│   └── explainer.html              # copy this to start a new explainer
├── system-design/
│   ├── index.html                  # picks a track: HLD or LLD
│   ├── sd-series.js                # every HLD/LLD page in order: week strip, page nav, previous/next, SD.story, SD.drill
│   ├── hld/                        # high-level design
│   │   ├── index.html              # H1–H147 roadmap (same numbering as Notion), weeks fold away
│   │   ├── client-server-dns.html … (one file per explainer; H10–H12 share proxy-lb-gateway.html#h10/#h11/#h12)
│   │   ├── scale-web-app.html      # H14 design: one app from 1 user to millions, scale-ladder calculator
│   │   ├── foundations-flows.js    # Weeks 1–2 pattern cards + drills (DNS routing, HTTP versions, TLS, DR, state, gateway/HA, P2C)
│   │   ├── caching-patterns-atlas.html  (week-level pattern atlas, Kit.atlas)
│   │   ├── caching-in-practice.html  (Week 3 playbook: worked design, sizing calculator, CDN cache-key lab, dashboard drill)
│   │   ├── cache-*.html, distributed-caching.html, cdn-http-caching.html  (Week 3 topic pages)
│   │   └── caching-flows.js  (shared caching cards and quiz scenarios)
│   └── lld/                        # low-level design
│       ├── index.html              # L1–L67 roadmap (same numbering as Notion)
│       ├── solid*.html             # L6–L11
│       └── singleton.html, factory-method.html, abstract-factory.html, builder.html, prototype.html  # L12–L16 creational patterns
├── aws-cloud-practitioner/         # CLF-C02, one page per topic (topics.js holds the map)
├── python-fundamentals/            # Python topics (code stepper + edit-and-run)
└── angular/                        # Modern Angular (v22): data flow and control flow, 15 topics
```

## Rules of the road

- **Colours live only in `theme.css`.** Pages and other CSS files use tokens such as `var(--fg)`, `var(--cyan)`, `var(--accent-text)`, so both themes work automatically.
- **Shared look and helpers go in `assets/`; page-specific animation code stays in the page.** Explainers load `theme.js` and `explainer-kit.js`.
- **Links point at files explicitly** (`folder/index.html`, not `folder/`), so pages work from disk, GitHub Pages and S3/CloudFront alike.
- **AWS pages** are one page per topic, in the same order as the course notes. `aws-cloud-practitioner/topics.js` lists every section and topic (`live: true` once built); the roadmap and the per-page strip (`<div class="aws-trail"></div>`) are drawn from it. Walkthroughs use `Kit.net`, a request-path diagram: icon tiles, dashed Region/AZ boxes and a glowing dot that travels the path (`net.send([...])`), with failures shown as a red ✕ and re-routing. Every topic page has a **Points to remember** list (`.remember`) and folds the course hands-on into an **In the console** box (`.console-steps`); every section ends with a review page holding a section summary (`.sum-grid`) and original exam-style questions (`Kit.mcq`). `Kit.pick` runs quick-fire drills.
- **Angular pages** use the same colour key everywhere: cyan = data down (`input()`, `[prop]`), orange = events up (`output()`, `(event)`), violet = two-way (`model()`, `[(x)]`). Kit helpers: `codeCard`, `compBox`, `ngWire`, `tsHighlight`, `ngHighlight`. All 15 pages build one running example, **CareDesk** (a clinic portal); `angular/caredesk.js` holds the step list and draws the "Building CareDesk" strip (`<div class="cd-trail" data-stage="N">`). Every snippet is built and run in a real Angular project before it goes on a page.
- **Pattern atlas pages** (`Kit.atlas`): cards styled after "N patterns" infographics. Each card has a numbered colour badge, a one-line rule, a mini diagram, its phases as a numbered list (readable without playing), a bold takeaway and Use when / Watch out lines. Nothing moves until the learner presses **▶ Play** on a card; it plays once (the current phase is highlighted) and offers ↺ Replay. Tag filter chips appear only with `filters: true`. Mini diagrams use the `m` helper (`box`, `db`, `tile`, `wire`, `send`, `slots`, `badge`, `state`, `link`, `text`, `label`); see the Kit header. Link an atlas or playbook from the HLD roadmap with `atlas:{file, t, s?}` (or an array) on the week; it shows as a dashed card and does not count as a day. Example: `system-design/hld/caching-patterns-atlas.html`.
- **System Design page layout** (every HLD and LLD page): header lede → week strip (`#series`) → numbered section menu pinned in the top bar (`#pageNav`, `Kit.pageNav`, built from `section[data-nav]`) → **1 Learn** → **2 Compare** → **3 Try it** → **4 Revise** (cheat-sheet, reference) → **5 Test** (drill + quiz cards) → previous / next. Sections a page doesn't need are left out, but the order never changes. Pages call `SD.page({ track: 'hld' | 'lld', drill? })`; caching pages call `CF.page(...)`, which uses the same strip and links. Pattern cards for Weeks 1–2 live in `foundations-flows.js` (`FF.cards`, `FF.drill`), for Week 3 in `caching-flows.js`.
- Pages one folder deep reference assets as `../assets/...`; pages two deep (`system-design/hld/`, `system-design/lld/`) use `../../assets/...`; the root hub uses `assets/...`.

## Adding an explainer

1. Copy `_template/explainer.html` into the subject folder and rename it (lowercase, hyphens).
2. Fill in the content and the page's own script.
3. Link it from the subject's `index.html` (for System Design HLD, add `file:"name.html"` to its H-session in `system-design/hld/index.html`; for LLD, add `file` to its L-topic in `PARTS` in `system-design/lld/index.html`). System Design pages also go into `system-design/sd-series.js` so they get the week strip and previous / next links.
4. In the root `index.html`, bump `done` (days covered) and `pages` (explainer files) for the subject, and add an entry to `RECENT`.
5. Commit and push. GitHub Pages updates in about a minute.

## Starting a new subject

Create the folder (e.g. `aws/`) with an `index.html` that loads `theme`, `base` and `hub` CSS from `../assets/css/`, then set `path:"aws/index.html"` on the subject in the root `index.html`.
