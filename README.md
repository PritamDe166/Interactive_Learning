# Interactive Explainers

Animated, clickable explainers for topics I'm learning. Each explainer is one self-contained HTML file.

## Layout

```
Interactive_explainations/
├── index.html                    # hub: links to every subject
├── system-design-explainers/
│   ├── index.html                # 119-day roadmap with links
│   └── load-balancing-algorithms.html
├── aws/                          # add when started
├── python/
└── ai/
```

## Adding an explainer

1. Save the HTML file into its subject folder (lowercase, hyphens, no spaces).
2. Link it from that subject's `index.html`. For System Design, add `file:"name.html"` to the day's entry.
3. In the root `index.html`, bump `done` for the subject and add an entry to `RECENT`.
4. Commit and push. GitHub Pages updates in about a minute.

## Starting a new subject

Create the folder with its own `index.html`, then set `path:"folder-name/index.html"` on the subject in the root `index.html`.
