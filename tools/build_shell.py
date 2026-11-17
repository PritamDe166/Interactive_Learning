#!/usr/bin/env python3
"""Add (or refresh) the workbench sidebar on every subject page.

The sidebar lists the pages of the current subject, grouped the same way as each
subject's own roadmap, with the current page marked. It is plain HTML, so it works
with JavaScript off and is the same on every visit.

Sources (edit these, then re-run this script):
  system-design/sd-series.js      HLD and LLD pages, in weeks / phases
  aws-cloud-practitioner/topics.js AWS sections; topics with  live: true
  python-fundamentals/index.html   PARTS, topics with  file:"..."
  angular/index.html               PARTS, topics with  file:"..."

Run from the repo root:  python3 tools/build_shell.py
The sidebar sits between <!-- shell:start --> and <!-- shell:end --> right after <body>.
"""
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START, END = '<!-- shell:start -->', '<!-- shell:end -->'
SUBJECTS = [
    ('system-design', 'System Design', 'system-design/index.html'),
    ('aws-cloud-practitioner', 'AWS', 'aws-cloud-practitioner/index.html'),
    ('python-fundamentals', 'Python', 'python-fundamentals/index.html'),
    ('angular', 'Angular', 'angular/index.html'),
]


def read(rel):
    with open(os.path.join(ROOT, rel), encoding='utf-8') as f:
        return f.read()


def tidy(s):
    """Group names: 'Week 3 · Caching' reads as 'Week 3: Caching'."""
    return s.replace(' · ', ': ').replace('&amp;', '&')


def sd_tracks():
    src = read('system-design/sd-series.js')
    tracks = []
    for name, label in (('HLD', 'HLD'), ('LLD', 'LLD')):
        block = re.search(r'const %s = \[(.*?)\n  \];' % name, src, re.S).group(1)
        groups = []
        for g, body in re.findall(r"\{ g: '([^']+)', pages: \[(.*?)\]\s*\}", block, re.S):
            pages = []
            for f, short, title in re.findall(r"\['([^']+)', '([^']+)', '([^']+)'\]", body):
                code = short.split(' ')[0]
                code = code if re.match(r'^[HL]\d', code) else ''
                pages.append(('system-design/%s/%s' % (name.lower(), f), title.replace(' · ', ': '), code))
            groups.append((tidy(g), pages))
        tracks.append((label, 'system-design/%s/index.html' % name.lower(), '%s roadmap' % label, groups))
    return tracks


def aws_tracks():
    src = read('aws-cloud-practitioner/topics.js')
    groups = []
    for t, body in re.findall(r"\{ id: '[^']+', t: '([^']+)'.*?topics: \[(.*?)\n    \]\s*\}", src, re.S):
        pages = []
        for line in body.split('\n'):
            m = re.search(r"file: '([^']+)', t: '([^']+)'", line)
            if m and 'live: true' in line:
                pages.append(('aws-cloud-practitioner/' + m.group(1), m.group(2), ''))
        if pages:
            groups.append((tidy(t), pages))
    return [('', 'aws-cloud-practitioner/index.html', 'AWS roadmap', groups)]


def parts_tracks(folder, road):
    src = read(folder + '/index.html')
    block = re.search(r'const PARTS = \[(.*?)\n\];', src, re.S).group(1)
    groups = []
    for part, name, body in re.findall(r'\{part:"([^"]+)", name:"([^"]+)", sections:\[(.*?)\n \]\}', block, re.S):
        pages = []
        for line in body.split('\n'):
            m = re.search(r'\{t:"([^"]+)".*?file:"([^"]+)"', line)
            if m:
                pages.append(('%s/%s' % (folder, m.group(2)), m.group(1), ''))
        if pages:
            groups.append(('%s: %s' % (part, name), pages))
    return [('', folder + '/index.html', road, groups)]


def site():
    return {
        'system-design': sd_tracks(),
        'aws-cloud-practitioner': aws_tracks(),
        'python-fundamentals': parts_tracks('python-fundamentals', 'Python roadmap'),
        'angular': parts_tracks('angular', 'Angular roadmap'),
    }


def rel(target, page):
    return os.path.relpath(target, os.path.dirname(page)).replace(os.sep, '/')


def sidebar(page, subject, tracks, counts):
    e = lambda s: html.escape(s, quote=True)
    name = next(n for k, n, _ in SUBJECTS if k == subject)
    home = rel('index.html', page)
    out = ['<aside class="wb-side" aria-label="Site">',
           '<a class="wb-mark" href="%s" aria-label="See How It Works, home"><span>See How</span><span>It Works</span></a>' % home,
           '<details class="wb-pages" open data-wb-pages>',
           '<summary>%s pages</summary>' % e(name),
           '<nav aria-label="%s pages">' % e(name)]
    for label, road, road_name, groups in tracks:
        if label:
            out.append('<h2 class="wb-track">%s</h2>' % e(label))
        cur = ' aria-current="page"' if road == page else ''
        out.append('<a class="wb-road" href="%s"%s>%s</a>' % (rel(road, page), cur, e(road_name)))
        for g, pages in groups:
            here = any(p[0] == page for p in pages)
            out.append('<details class="wb-g"%s><summary>%s</summary><ul>' % (' open' if here else '', e(g)))
            for f, title, code in pages:
                cur = ' aria-current="page"' if f == page else ''
                n = '<span class="n">%s</span>' % e(code) if code else ''
                out.append('<li><a href="%s"%s><span class="t">%s</span>%s</a></li>' % (rel(f, page), cur, e(title), n))
            out.append('</ul></details>')
    out.append('</nav></details>')
    out.append('<nav class="wb-subjects" aria-label="Subjects"><h2>Subjects</h2><ul>')
    for k, n, idx in SUBJECTS:
        cur = ' aria-current="true"' if k == subject else ''
        out.append('<li><a href="%s"%s>%s<span class="n">%d</span></a></li>' % (rel(idx, page), cur, e(n), counts[k]))
    out.append('<li><span class="soon">AI<span class="n">Soon</span></span></li></ul></nav>')
    out.append('</aside>')
    return '\n'.join(out)


def main():
    data = site()
    # explainer files per subject (roadmaps and the map are not counted), the same figure the home page shows
    counts = {}
    for k, _, _ in SUBJECTS:
        counts[k] = sum(1 for d, _, fs in os.walk(os.path.join(ROOT, k)) for f in fs
                        if f.endswith('.html') and f not in ('index.html', 'map.html'))
    done = 0
    for subject, _, _ in SUBJECTS:
        for dirpath, _, files in os.walk(os.path.join(ROOT, subject)):
            for fn in sorted(files):
                if not fn.endswith('.html'):
                    continue
                path = os.path.join(dirpath, fn)
                page = os.path.relpath(path, ROOT).replace(os.sep, '/')
                src = open(path, encoding='utf-8').read()
                src = re.sub(r'\n?%s.*?%s' % (re.escape(START), re.escape(END)), '', src, flags=re.S)
                block = '%s\n%s\n%s' % (START, sidebar(page, subject, data[subject], counts), END)
                m = re.search(r'<body([^>]*)>', src)
                attrs = m.group(1)
                if 'class="' in attrs:
                    if not re.search(r'class="[^"]*\bwb\b', attrs):
                        attrs = attrs.replace('class="', 'class="wb ', 1)
                else:
                    attrs += ' class="wb"'
                src = src[:m.start()] + '<body%s>\n%s' % (attrs, block) + src[m.end():]
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(src)
                done += 1
    print('sidebar written to %d pages; pages per subject: %s' % (done, counts))


if __name__ == '__main__':
    main()
