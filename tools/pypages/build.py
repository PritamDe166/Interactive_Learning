"""Build a Python-fundamentals explainer page from a spec module.
usage (from any folder; snippets that write files will write them there, so use a scratch folder):
    python3 tools/pypages/build.py tools/pypages/specs/<slug>.py [more specs...]
The spec module defines SPEC (dict). See variables-objects.html for the format it reproduces.
- traces every snippet with tools/pytrace.py (real runs)
- resolves story steps -> trace indexes
- asserts every puzzle answer and quiz expectation against the real output
"""
import importlib.util, io, json, os, re, subprocess, sys, contextlib, html as H
SITE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PF = SITE + '/python-fundamentals'
sys.path.insert(0, SITE + '/tools')
import pytrace

def run_code(code, inputs=()):
    tr = pytrace.Recorder(code, list(inputs)).run()
    return tr

def out_of(tr):
    last = tr['steps'][-1]
    o = last['out']
    if last.get('exc'):
        o = o.split('Traceback (most recent call last):')[0] + last['exc'] + '\n'
    return o

def norm(s):
    return ' / '.join(l.rstrip() for l in s.strip('\n').split('\n'))

def resolve(steps, spec):
    """spec: 'start' | 'end' | {'after': line, 'n': k} | {'event': 'call'|'return'|'exception', 'n': k} | int"""
    if spec == 'start': return 0
    if spec == 'end': return len(steps) - 1
    if isinstance(spec, int): return spec
    n = spec.get('n', 1); c = 0
    for i, st in enumerate(steps):
        if 'after' in spec and st['ran'] == spec['after'] and st['event'] in ('line', 'end', 'return', 'exception', 'call'):
            # 'ran' == L means line L just finished
            c += 1
            if c == n: return i
        if 'event' in spec and st['event'] == spec['event']:
            c += 1
            if c == n: return i
    raise SystemExit(f'could not resolve {spec}')

def esc(s): return H.escape(s, quote=False)

def build(path):
    m = importlib.util.spec_from_file_location('spec', path); mod = importlib.util.module_from_spec(m); m.loader.exec_module(mod)
    S = mod.SPEC
    slug = S['slug']
    snippets = {'walk': {'code': S['walk']['code'], 'inputs': S['walk'].get('inputs', [])}}
    for p in S.get('puzzles', []):
        snippets[p['id']] = {'code': p['code'], 'inputs': p.get('inputs', [])}
    for x in S.get('extra_traces', {}).items():
        snippets[x[0]] = x[1]
    # write snippet file + traces (via pytrace main for identical output)
    os.makedirs(PF + '/snippets', exist_ok=True)
    json.dump({'page': slug, 'snippets': snippets}, open(f'{PF}/snippets/{slug}.json', 'w'), indent=1)
    subprocess.run([sys.executable, '-I', SITE + '/tools/pytrace.py', f'{PF}/snippets/{slug}.json'], check=True, stdout=subprocess.DEVNULL)
    traces = {k: pytrace.Recorder(v['code'], v.get('inputs', [])).run() for k, v in snippets.items()}
    # story mapping
    wsteps = traces['walk']['steps']
    MAP = [resolve(wsteps, st['at']) for st in S['walk']['steps']]
    assert all(a < b for a, b in zip(MAP, MAP[1:])), (slug, 'story map not strictly increasing', MAP)
    # verify puzzles
    for p in S.get('puzzles', []):
        actual = norm(out_of(traces[p['id']]))
        if p.get('check', True):
            want = p['opts'][p['a']]
            assert actual == want, f"{slug}:{p['id']} answer {want!r} != actual {actual!r}"
            others = [o for i, o in enumerate(p['opts']) if i != p['a']]
            assert actual not in others, f"{slug}:{p['id']} duplicate option"
        else:
            print(f"  (unchecked) {p['id']}: actual = {actual!r}")
    # verify quiz
    for q in S['quiz']:
        if 'code' in q:
            actual = norm(out_of(run_code(q['code'], q.get('inputs', []))))
            assert q['expect'] in actual, f"{slug} quiz {q['code']!r}: expected {q['expect']!r} in {actual!r}"
    # verify walkthrough output mention
    if 'walk_out' in S:
        assert norm(out_of(traces['walk'])) == S['walk_out'], (slug, norm(out_of(traces['walk'])))
    page = render(S, MAP)
    open(f'{PF}/{slug}.html', 'w').write(page)
    print('built', slug, 'walk steps', len(wsteps), 'map', MAP, 'python', traces['walk']['python'])

def render(S, MAP):
    slug = S['slug']
    lede = ''.join(f'<li>{b}</li>' for b in S['lede'])
    steps_js = json.dumps([{k: v for k, v in st.items() if k in ('title', 'text', 'tip')} for st in S['walk']['steps']], ensure_ascii=False)
    puzzles = S.get('puzzles', [])
    pz_js = json.dumps([{k: p[k] for k in ('id', 'name', 'q', 'opts', 'a', 'why')} for p in puzzles], ensure_ascii=False)
    starters = [{'label': 'Walkthrough code', 'code': S['walk']['code'], 'inputs': S['walk'].get('inputs', [])}]
    starters += [{'label': f"Puzzle {i+1}: {p['name'].split('·',1)[-1].strip()}", 'code': p['code'], 'inputs': p.get('inputs', [])} for i, p in enumerate(puzzles)]
    starters += S.get('runner_extra', [])
    customs = S.get('custom', [])
    custom_html = ''.join(f'''
  <section aria-labelledby="{c['id']}H">
    <h2 class="stage-title" id="{c['id']}H">{c['title']}</h2>
    <div class="stage-kind">{c['kind']}</div>
{c['html']}
  </section>
''' for c in customs)
    custom_js = '\n'.join(f"  /* ===== {c['title']} ===== */\n  (function () {{\n{c['js']}\n  }})();" for c in customs)
    cheat = ''.join(f'      <li><span class="if">{a}</span><span class="arrow">→</span><span class="then">{b}</span></li>\n' for a, b in S['cheat'])
    notes = ''.join(f'      <div class="note"><span class="flag{"" if f == "Corrected" else " add"}">{f}</span><p>{t}</p></div>\n' for f, t in S.get('notes', []))
    quiz = ''.join(f'''      <details><summary>{q['q']}<span class="go">Show answer</span></summary>
        <div class="ans"><p>{q['a']}</p></div></details>
''' for q in S['quiz'])
    assert len(S['quiz']) in (3, 6), 'quiz must have 3 or 6 cards'
    pz_section = '' if not puzzles else '''
  <section aria-labelledby="predH">
    <h2 class="stage-title" id="predH">Predict the output</h2>
    <div class="stage-kind">Pick a puzzle · choose your answer · then step through it</div>
    <div class="chips" id="pzChips"></div>
    <div class="puzzle-area" id="pzArea"></div>
  </section>
'''
    pz_js_block = '' if not puzzles else '''
  /* ========== Predict the output ========== */
  const PZ = ''' + pz_js + ''';
  $('pzChips').innerHTML = PZ.map((p, i) => `<button class="chip-btn" type="button" data-i="${i}" aria-pressed="false">${p.name}</button>`).join('');
  function puzzle(i) {
    const p = PZ[i], area = $('pzArea');
    area.innerHTML = `<div class="two">
        <div><pre class="codeblock static-code">${T[p.id].code.split('\\n').map(l => `<span class="ln">${K.pyHighlight(l) || ' '}</span>`).join('')}</pre></div>
        <div class="card predict"><div class="q">${p.q}</div><div class="opts">${p.opts.map((o, j) => `<button class="chip-btn" type="button" data-j="${j}">${o.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</button>`).join('')}</div><p class="status-line" style="text-align:left;margin:0" id="pzVerdict">Choose an answer to unlock the step-through.</p></div>
      </div><div id="pzTrace"></div>`;
    area.querySelectorAll('.predict .chip-btn').forEach(b => b.addEventListener('click', () => {
      const j = +b.dataset.j, ok = j === p.a;
      area.querySelectorAll('.predict .chip-btn').forEach((x, xj) => { x.disabled = true; x.classList.toggle('right', xj === p.a); x.classList.toggle('wrong', xj === j && !ok); });
      $('pzVerdict').innerHTML = `<span class="${ok ? 'ok-text' : 'bad-text'}">${ok ? 'Correct.' : 'Not quite.'}</span> ${p.why} <b>Step through below to watch it happen.</b>`;
      K.trace($('pzTrace'), T[p.id], { controls: true });
    }));
  }
  $('pzChips').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
    $('pzChips').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
    puzzle(+b.dataset.i);
  }));
  $('pzChips').querySelector('button').click();
'''
    page_style = S.get('style', '')
    return f'''<!doctype html>
<html lang="en" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(S['title_plain'])}</title>
<meta name="description" content="{H.escape(S['desc'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="../assets/css/theme.css">
<link rel="stylesheet" href="../assets/css/base.css">
<link rel="stylesheet" href="../assets/css/explainer.css">
<script src="../assets/js/theme.js"></script>
<script src="../assets/js/explainer-kit.js"></script>
<script src="traces/{slug}.js"></script>
<style>
  .static-code {{ margin: 0; }}
  .puzzle-area {{ display: grid; gap: 14px; margin-top: 12px; }}
{page_style}
</style>
</head>
<body>
<div class="wrap explainer">
  <div class="topbar">
    <a class="back" href="index.html">← Python Fundamentals</a>
    <button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch theme"></button>
  </div>

  <header>
    <div class="eyebrow">Python · Topic {S['num']} · {S['part']}</div>
    <h1>{S['title']}</h1>
    <ul class="lede">{lede}</ul>
  </header>

  <section aria-labelledby="storyH">
    <h2 class="stage-title" id="storyH">Walkthrough: {S['walk']['title']}</h2>
    <div class="stage-kind">Real trace of real code · Next ▶ moves one idea at a time</div>
    <div class="story wide" id="pageStory">
      <div id="pageTrace"></div>
    </div>
  </section>

  <h2 class="part-title">Try it yourself</h2>
  <p class="sub">Run and change the code, predict before you peek, and try to break things.</p>

  <section aria-labelledby="runH">
    <h2 class="stage-title" id="runH">Edit and run</h2>
    <div class="stage-kind">Change the code · Run ▶ for the output · Step through to watch it run</div>
    <div id="runner"></div>
  </section>
{pz_section}{custom_html}
  <section aria-labelledby="cheatH">
    <h2 id="cheatH">Cheat-sheet</h2>
    <ul class="cheat">
{cheat}    </ul>
  </section>

  <section aria-labelledby="refH">
    <h2 id="refH">{S.get('ref_title', 'Reference')}</h2>
{S.get('ref_html', '')}
    <div class="notes" style="margin-top:14px">
{notes}    </div>
  </section>

  <section aria-labelledby="quizH">
    <h2 id="quizH">Check yourself</h2>
    <p class="sub">Say the answer out loud before you open each card.</p>
    <div class="quiz">
{quiz}    </div>
  </section>

  <footer>Every trace and output on this page was produced by running the code (Python 3.13; the same results on Python 3.15). The edit-and-run box runs real Python 3.14 in your browser with Pyodide. {S['sources']}</footer>
</div>

<script>
(function () {{
  const K = Kit, $ = K.$;
  const T = window.TRACES['{slug}'];

  /* ========== Walkthrough ========== */
  const tr = K.trace($('pageTrace'), T.walk, {{}});
  const MAP = {json.dumps(MAP)};
  const STEPS = {steps_js};
  STEPS.forEach((st, i) => {{
    if (i === 0) return;
    st.play = async run => {{ for (let k = MAP[i - 1] + 1; k <= MAP[i]; k++) {{ tr.show(k); if (k < MAP[i]) await K.sleep(Math.max(150, Math.min(600, 4800 / (MAP[i] - MAP[i - 1]))), run); }} }};
  }});
  K.story({{ root: $('pageStory'), steps: STEPS, show: i => tr.show(MAP[i]), tipLabel: 'Tip' }});

  /* ========== Edit and run ========== */
  K.pyRunner($('runner'), {{ starters: {json.dumps(starters, ensure_ascii=False)} }});
{pz_js_block}
{custom_js}
}})();
</script>
</body>
</html>
'''

if __name__ == '__main__':
    for p in sys.argv[1:]:
        build(p)
