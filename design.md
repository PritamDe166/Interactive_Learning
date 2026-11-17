# Design: See How It Works

The locked system. Every Hallmark run reads this first and pages share it. Change it on purpose; the file is the rule.

## System
- Genre: editorial
- Shape of the first page: Narrative Workflow (home), Banner hero (About)
- Theme: Grid (Swiss column system, no strokes, fields that run off the page), recoloured to the owner's Figma reference
- Axes: light/grotesk-sans/cool · posture: full-palette · modes: light (default) + dark, toggled by `assets/js/theme.js`

## Tokens
`assets/css/site/tokens.css` is the source of truth. The roles:
```css
:root {
  --color-paper: oklch(98.6% 0.005 265);  --color-paper-2: oklch(95.8% 0.006 265);  --color-paper-3: oklch(92.4% 0.007 265);
  --color-ink: oklch(18% 0.009 265);  --color-ink-2: oklch(32% 0.009 265);  --color-muted: oklch(48% 0.012 265);  --color-rule: oklch(89% 0.006 265);
  --color-accent: oklch(53% 0.215 264);  --color-accent-ink: oklch(98.6% 0.005 265);  --color-focus: oklch(53% 0.215 264);
  --color-field: oklch(18.5% 0.009 265);  --color-field-ink: oklch(97% 0.005 265);
  --color-mark: oklch(91% 0.18 115);  --color-mark-ink: oklch(18% 0.009 265);
  --font-display: "Radio Canada Big", ui-sans-serif, system-ui, sans-serif;  --font-body: "Radio Canada", ui-sans-serif, system-ui, sans-serif;
  --radius-card: 0;  --radius-pill: 0;  --rule-hair: 1px;  --shadow-card: none;
}
```
The spacing scale, the type scale, the easings and the durations are the scaffold's and live in `tokens.css`. Fonts are self-hosted in `assets/fonts/` (SIL OFL).

Three colour roles, one job each:
- **Field** (near-black): a flood from a column line to the page edge. Type crossing onto it turns field-ink (the overprint). Two or three per page, never touching.
- **Accent** (electric blue): the primary button, link and row hovers, focus rings, the one chosen state.
- **Mark** (acid lime): a fill only (the wordmark square, one band per page, text selection). Never text on paper.

## Controls
- Primary: accent fill, accent-ink text · radius 0 · 52px tall · one per page
- Secondary: text with a 1px underline that turns accent on hover
- Inputs on a field: display type at text-3xl over a hairline, no box

## Type
- Display: Radio Canada Big 700, sentence case, tracking -0.035em (-0.045em at poster size). One weight and one colour per head.
- Body: Radio Canada 400 at 17px; labels Radio Canada 500 a step smaller, sentence case, never tracked capitals, never mono.

## Motion
- Character: still. State changes only (colour on hover, 220ms ease-out). No scroll reveals. Under reduced motion everything ends at once.

## Rollout to the rest of the site
Done: `index.html`, `about.html` (stylesheet `assets/css/site/home.css`).
Next, in this order: the five subject roadmaps (`*/index.html`, today on `hub.css`), then the explainers (`explainer.css`).
- Map the old tokens in `assets/css/theme.css` onto these roles rather than rewriting each page: `--bg` to paper, `--panel` to paper-2, `--fg` to ink, `--yellow`/`--accent-text` to accent, `--teal` stays as the "good/hit" state colour.
- Explainers drop the tracked-caps mono eyebrows (`WEEK 3 · H18 · CACHING & CDN`), the rounded pills and the yellow numbered circles; section numbers become display numerals as on the home page.
- After the explainers change, recapture `assets/img/home/*.webp` so the home page shows them in the new look.
- Run `python3 tools/build_search_index.py` after adding or renaming any page.

## Exports
`assets/css/site/tokens.css` in this project. Tailwind, DTCG or shadcn blocks are added here on request.
