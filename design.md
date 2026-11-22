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

## Layout: the learning workbench
Every page is a workbench: a dark sidebar (field) on the left, the page on paper to its right. Designed in Figma first: https://www.figma.com/design/c6fwa4Y7qqp8cvVByJalon (frames "Home / Learning workbench", "Diagram kit", "Explainer / Cache eviction").
- Home (`index.html`, `assets/css/site/workbench.css`): page head with the tally, the caching lab (one request through client, cache and database, hit or miss), "Choose your rabbit hole" subject tabs, "Fresh from the lab", the lime close band. About (`about.html`) uses the same shell and stylesheet. `site/home.css` is the earlier home design, no longer linked; it can be deleted.
- Subject pages: the sidebar is written into every page under the subject folders by `python3 tools/build_shell.py` (between `<!-- shell:start -->` and `<!-- shell:end -->`). It lists the subject's pages in the same groups as its roadmap, from `sd-series.js`, `aws-cloud-practitioner/topics.js` and the `PARTS` lists in the Python and Angular roadmaps. Styles: the "Workbench shell" block at the end of `assets/css/base.css`. Below 72rem it folds into a "pages" menu above the page.
- Explainers (`explainer.css`, "Workbench layer" at the end): sections on paper, numbered with a blue display numeral; tabs underline in blue; the walkthrough is a diagram well with the narration on a dark panel; previous / next are two wells.
- Diagrams: square nodes with a hairline. Blue fill = happening now (`.on`), lime = the answer or a hit (`.solid`, `.hit`, `.ok`), red only for errors, faded = out of play (`.dim`). Wires are grey, blue while a request travels them. Request pills are ink with paper text.

## Buttons
Two kinds, by job:
- **Actions** (primary buttons, the walkthrough's Back / Next / Play all, the home lab's controls): offset style, square, a 2px outline and a hard 3px shadow (ink on paper; lime on dark panels and in dark mode). Hover lifts a pixel, press sinks into the shadow. Primary is blue; one primary per group, the rest outline or a text link.
- **Chips** (keys, presets, quiz answers, filters, Reset, playback controls): flat, a 1px hairline that turns ink on hover, no shadow.
- **Chosen toggle**: one style everywhere, a flat lime fill with ink text.
- **Disabled**: the same button, faded; on dark panels a faint outline, never a grey block.
Styles: "Pass 2" block at the end of `explainer.css`, and `site/workbench.css`.

## Colour discipline
- Lime is for the logo, the close band, chosen toggles and "hit" states in diagrams. Bullets, takeaways, notes and cheat-sheet answers are ink.
- Red only for errors and "watch out". Exam-domain tags and map phases are neutral or blue, never one colour per item.

## Counts
One number per subject: explainers = pages its roadmap lists as ready. `tools/build_shell.py` computes it for the sidebars; keep `SUBJECTS` in `index.html`, the sidebar in `about.html` and `TRACKS` in `system-design/index.html` in step.

## Logo
`assets/img/logo.svg`: a lime square with an ink S drawn as a request route, from an outlined start node to a filled end node. It is the tab icon on every page (added by `tools/build_shell.py`), the square in the sidebar wordmark, and stands beside the name on the home page. Ink on lime only; never recoloured.

## Adding or changing pages
- After adding, renaming or reordering any page: update its roadmap list (above), then run `python3 tools/build_shell.py` and `python3 tools/build_search_index.py`. Both are safe to run again.
- A new explainer copied from `_template/explainer.html` gets its sidebar from `build_shell.py`.
- Stylesheets and scripts are linked with `?v=<date>` so browsers fetch new styles after a deploy. When you change a CSS or JS file, bump the date on every link (one find-and-replace across the repo) and on the `@import` lines in `theme.css`, `site/home.css` and `site/workbench.css`.
- After the explainers change look, recapture `assets/img/home/*.webp` if a page still shows them (About does not; the home page draws its own lab).

## Exports
`assets/css/site/tokens.css` in this project. Tailwind, DTCG or shadcn blocks are added here on request.
