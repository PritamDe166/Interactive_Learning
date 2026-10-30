# Interactive Explainers

Animated, clickable explainers for topics I'm learning. Live at
https://pritamde166.github.io/Interactive_Learning/

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
│   ├── hld/                        # high-level design
│   │   ├── index.html              # 119-day roadmap with links
│   │   └── client-server-dns.html … (one file per explainer)
│   └── lld/                        # low-level design
│       └── index.html              # LLD topics, added as they're learned
├── aws-cloud-practitioner/         # CLF-C02 sections
└── python-fundamentals/            # Python topics (code stepper + edit-and-run)
```

## Rules of the road

- **Colours live only in `theme.css`.** Pages and other CSS files use tokens such as `var(--fg)`, `var(--cyan)`, `var(--accent-text)`, so both themes work automatically.
- **Shared look and helpers go in `assets/`; page-specific animation code stays in the page.** Explainers load `theme.js` and `explainer-kit.js`.
- **Links point at files explicitly** (`folder/index.html`, not `folder/`), so pages work from disk, GitHub Pages and S3/CloudFront alike.
- Pages one folder deep reference assets as `../assets/...`; pages two deep (`system-design/hld/`, `system-design/lld/`) use `../../assets/...`; the root hub uses `assets/...`.

## Adding an explainer

1. Copy `_template/explainer.html` into the subject folder and rename it (lowercase, hyphens).
2. Fill in the content and the page's own script.
3. Link it from the subject's `index.html` (for System Design HLD, add `file:"name.html"` to that day in `system-design/hld/index.html`; for LLD, add the topic to `PARTS` in `system-design/lld/index.html`).
4. In the root `index.html`, bump `done` (days covered) and `pages` (explainer files) for the subject, and add an entry to `RECENT`.
5. Commit and push. GitHub Pages updates in about a minute.

## Starting a new subject

Create the folder (e.g. `aws/`) with an `index.html` that loads `theme`, `base` and `hub` CSS from `../assets/css/`, then set `path:"aws/index.html"` on the subject in the root `index.html`.
