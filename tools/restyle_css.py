#!/usr/bin/env python3
"""One-off restyle pass for the Grid system (see design.md).

Rewrites CSS in assets/css/explainer.css, assets/css/hub.css and every page's
inline <style> blocks:
  * border-radius -> 0 (circles at 50% stay)
  * padding, margin and gap lengths snap to the --space-* scale
  * label rules (uppercase or letter-spaced) lose the capitals and tracking,
    move from mono to the body face, and grow to at least 13px
Mono stays everywhere else (code, logs, figures).

Usage: python3 tools/restyle_css.py [--dry]
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRY = "--dry" in sys.argv

RULE = re.compile(r"([^{}]+)\{([^{}]*)\}")
RADIUS = re.compile(r"border-radius\s*:\s*([^;}]+)")
UPPER = re.compile(r"\s*text-transform\s*:\s*uppercase\s*;?", re.I)
TRACK = re.compile(r"\s*letter-spacing\s*:\s*(\.\d+|0?\.\d+|\d+(?:\.\d+)?)(em|px)\s*;?")
SMALL = re.compile(r"font-size\s*:\s*(\d+(?:\.\d+)?)px")
MONO = re.compile(r"font-family\s*:\s*var\(--mono\)\s*(!important)?")

stats = {"radius": 0, "labels": 0}

SCALE = [(2, "3xs"), (4, "2xs"), (8, "xs"), (12, "sm"), (16, "md"), (24, "lg"), (40, "xl"), (64, "2xl"), (96, "3xl"), (144, "4xl")]
SPACING = re.compile(r"((?:padding|margin|gap|row-gap|column-gap)(?:-(?:top|right|bottom|left|block|inline)(?:-(?:start|end))?)?\s*:\s*)([^;}]+)")
PX = re.compile(r"(-?)(\d+(?:\.\d+)?)px")


def snap(m):
    sign, n = m.group(1), float(m.group(2))
    if n <= 1:
        return m.group(0)
    name = min(SCALE, key=lambda t: (abs(t[0] - n), t[0]))[1]
    stats["spacing"] = stats.get("spacing", 0) + 1
    return f"calc(-1 * var(--space-{name}))" if sign else f"var(--space-{name})"


def fix_spacing(m):
    value = m.group(2)
    if "max(" in value or "env(" in value:
        return m.group(0)
    return m.group(1) + PX.sub(snap, value)



def fix_radius(m):
    v = m.group(1).strip()
    if "50%" in v or v in ("0", "inherit"):
        return m.group(0)
    stats["radius"] += 1
    return "border-radius: 0"


def is_tracked(body):
    for m in TRACK.finditer(body):
        n, unit = float(m.group(1)), m.group(2)
        if (unit == "em" and n >= 0.04) or (unit == "px" and n >= 0.6):
            return True
    return False


def fix_rule(m):
    sel, body = m.group(1), m.group(2)
    if sel.strip().startswith("@"):
        return m.group(0)
    if not (UPPER.search(body) or is_tracked(body)):
        return m.group(0)
    stats["labels"] += 1
    body = UPPER.sub("", body)

    def track(t):
        n, unit = float(t.group(1)), t.group(2)
        return "" if (unit == "em" and n >= 0.04) or (unit == "px" and n >= 0.6) else t.group(0)

    body = TRACK.sub(track, body)
    body = MONO.sub(lambda f: "font-family: var(--display)" + (" !important" if f.group(1) else ""), body)
    body = SMALL.sub(lambda f: "font-size: 13px" if float(f.group(1)) < 13 else f.group(0), body)
    body = re.sub(r";\s*;", ";", body)
    return f"{sel}{{{body}}}"


def restyle(css):
    css = RADIUS.sub(fix_radius, css)
    css = RULE.sub(fix_rule, css)
    css = SPACING.sub(fix_spacing, css)
    return css


def main():
    changed = []
    for rel in ("assets/css/explainer.css", "assets/css/hub.css"):
        p = ROOT / rel
        old = p.read_text(encoding="utf-8")
        new = restyle(old)
        if new != old:
            changed.append(rel)
            if not DRY:
                p.write_text(new, encoding="utf-8")
    style = re.compile(r"(<style[^>]*>)(.*?)(</style>)", re.S | re.I)
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith((".git", ".hallmark", "infra")) or rel in ("index.html", "about.html"):
            continue
        old = p.read_text(encoding="utf-8")
        new = style.sub(lambda m: m.group(1) + restyle(m.group(2)) + m.group(3), old)
        if new != old:
            changed.append(rel)
            if not DRY:
                p.write_text(new, encoding="utf-8")
    print(f"{len(changed)} files, {stats['radius']} radii squared, {stats['labels']} label rules reset, {stats.get('spacing', 0)} spacings snapped" + (" (dry run)" if DRY else ""))


if __name__ == "__main__":
    main()
