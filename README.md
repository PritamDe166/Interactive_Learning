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
│       └── theme.js                # light/dark toggle, remembers the choice
├── _template/
│   └── explainer.html              # copy this to start a new explainer
└── system-design-explainers/
    ├── index.html                  # 119-day roadmap with links
    └── load-balancing-algorithms.html
```

## Rules of the road

- **Colours live only in `theme.css`.** Pages and other CSS files use tokens such as `var(--fg)`, `var(--cyan)`, `var(--accent-text)`, so both themes work automatically.
- **Shared look goes in `assets/`; page-specific animation code stays in the page.**
- **Links point at files explicitly** (`folder/index.html`, not `folder/`), so pages work from disk, GitHub Pages and S3/CloudFront alike.
- Pages one folder deep reference assets as `../assets/...`; the root hub uses `assets/...`.

## Adding an explainer

1. Copy `_template/explainer.html` into the subject folder and rename it (lowercase, hyphens).
2. Fill in the content and the page's own script.
3. Link it from the subject's `index.html` (for System Design, add `file:"name.html"` to that day).
4. In the root `index.html`, bump `done` for the subject and add an entry to `RECENT`.
5. Commit and push. GitHub Pages updates in about a minute.

## Starting a new subject

Create the folder (e.g. `aws/`) with an `index.html` that loads `theme`, `base` and `hub` CSS from `../assets/css/`, then set `path:"aws/index.html"` on the subject in the root `index.html`.
