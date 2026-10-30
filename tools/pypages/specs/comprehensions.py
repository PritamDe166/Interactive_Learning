import json
SRC = [450, 1200, 300, 800, 950]
EXPRS = [("f", lambda f: f), ("f * 2", lambda f: f * 2), ("f // 100", lambda f: f // 100), ('f"Rs {f}"', lambda f: f"Rs {f}")]
CONDS = [("", lambda f: True), ("if f >= 500", lambda f: f >= 500), ("if f % 100 == 0", lambda f: f % 100 == 0), ("if f < 400", lambda f: f < 400)]
PIPE = {}
for ei, (e, ef) in enumerate(EXPRS):
    for ci, (c, cf) in enumerate(CONDS):
        code = f"[{e} for f in fees{(' ' + c) if c else ''}]"
        real = eval(code, {"fees": SRC})
        sim = [ef(f) for f in SRC if cf(f)]
        assert real == sim
        PIPE[f"{ei}|{ci}"] = {"code": code, "items": [{"in": f, "pass": cf(f), "out": repr(ef(f)) if cf(f) else None} for f in SRC], "res": repr(real)}

SPEC = {
 "slug": "comprehensions", "num": 6, "part": "Control flow and data",
 "title": "Comprehensions", "title_plain": "Comprehensions",
 "desc": "Python fundamentals: list, dict and set comprehensions and generator expressions, shown side by side with the loop they replace.",
 "lede": [
  "A <b>comprehension</b> builds a new list from an existing sequence in one expression: <span class=\"mono\">[f * 2 for f in fees]</span>.",
  "Read it as <b>what to keep</b> · <b>for each item</b> · <b>optional filter</b>: <span class=\"mono\">[expr for x in items if cond]</span>.",
  "Same idea for <b>dicts</b> <span class=\"mono\">{k: v for ...}</span> and <b>sets</b> <span class=\"mono\">{x for ...}</span>; with round brackets it becomes a lazy <b>generator expression</b>.",
  "Use one when the loop only builds a collection. If it needs several statements, keep the normal loop."
 ],
 "walk": {"title": "the same list, two ways", "code":
'''fees = [450, 1200, 300, 800]
doubled = []
for f in fees:
    doubled.append(f * 2)
doubled2 = [f * 2 for f in fees]
big = [f for f in fees if f >= 500]
labels = ["high" if f >= 500 else "low" for f in fees]
lengths = {n: len(n) for n in ["Asha", "Ravi"]}
units = {f % 3 for f in fees}
total = sum(f for f in fees if f >= 500)
print(doubled == doubled2, big)
print(labels)
print(lengths, units, total)''',
 "steps": [
  {"at": {"after": 2}, "title": "The loop way: start empty", "text": "The classic pattern: make an empty list, then append to it inside a loop. Three lines for one idea."},
  {"at": {"after": 4, "n": 4}, "title": "…append on every round", "text": "After four rounds <span class=\"mono\">doubled</span> holds the four results. Note that the loop variable <span class=\"mono\">f</span> is still around afterwards."},
  {"at": {"after": 5}, "title": "The comprehension way", "text": "<span class=\"mono\">[f * 2 for f in fees]</span> says the same thing in one line and builds a <b>new list</b> object. Read it left to right: <i>f times 2, for each f in fees</i>."},
  {"at": {"after": 6}, "title": "Add a filter with if", "text": "An <span class=\"mono\">if</span> at the end <b>drops</b> items: only fees ≥ 500 are kept. The result can be shorter than the input."},
  {"at": {"after": 7}, "title": "if/else goes at the front", "text": "To <b>choose a value</b> for every item, put a conditional expression in the expression part: <span class=\"mono\">\"high\" if f &gt;= 500 else \"low\"</span>. Every item produces an output, so the length stays 4.", "tip": "Filter: <span class=\"mono\">[x for x in xs if c]</span>. Choose: <span class=\"mono\">[a if c else b for x in xs]</span>. Mixing them up is the most common syntax error here."},
  {"at": {"after": 8}, "title": "Dict comprehension", "text": "Curly braces with <span class=\"mono\">key: value</span> build a dict. Here each name maps to its length."},
  {"at": {"after": 9}, "title": "Set comprehension", "text": "Curly braces <b>without</b> a colon make a set, so duplicates collapse: four fees, but only the distinct remainders survive."},
  {"at": {"after": 10}, "title": "Generator expression", "text": "Inside <span class=\"mono\">sum(...)</span> the brackets disappear: this is a <b>generator expression</b>. It hands values to sum() one at a time without building a list first. Great for big data."},
  {"at": "end", "title": "Same results", "text": "<span class=\"mono\">doubled == doubled2</span> is True: same contents, different objects. Comprehensions are usually a little faster and much easier to read once you know the shape."}
 ]},
 "walk_out": "True [1200, 800] / ['low', 'high', 'low', 'high'] / {'Asha': 4, 'Ravi': 4} {0, 2} 2000",
 "puzzles": [
  {"id": "p1", "name": "1 · filter", "code": "nums = [1, 2, 3, 4, 5, 6]\nprint([n * n for n in nums if n % 2 == 0])", "q": "What's printed?", "opts": ["[4, 16, 36]", "[1, 9, 25]", "[2, 4, 6]"], "a": 0,
   "why": "Keep the even numbers (2, 4, 6), then square them."},
  {"id": "p2", "name": "2 · else in the wrong place", "code": "nums = [1, 2, 3]\nprint([n for n in nums if n > 1 else 0])", "q": "What happens?", "opts": ["[0, 2, 3]", "SyntaxError: invalid syntax", "[2, 3]"], "a": 1, "check": False,
   "why": "A trailing <span class=\"mono\">if</span> is a filter and can't have an <span class=\"mono\">else</span>. Move it to the front: <span class=\"mono\">[n if n &gt; 1 else 0 for n in nums]</span> → <span class=\"mono\">[0, 2, 3]</span>."},
  {"id": "p3", "name": "3 · nested loops", "code": "pairs = [(d, t) for d in [\"Mon\", \"Tue\"] for t in [9, 10]]\nprint(pairs)", "q": "What's printed?", "opts": ["[('Mon', 9), ('Mon', 10), ('Tue', 9), ('Tue', 10)]", "[('Mon', 9), ('Tue', 10)]", "[('Mon', 9), ('Tue', 9), ('Mon', 10), ('Tue', 10)]"], "a": 0,
   "why": "Multiple <span class=\"mono\">for</span> clauses nest in the order written: the first is the outer loop."},
  {"id": "p4", "name": "4 · set or dict?", "code": "a = {x % 2 for x in range(5)}\nb = {x: x % 2 for x in range(3)}\nprint(a, b)", "q": "What's printed?", "opts": ["{0, 1} {0: 0, 1: 1, 2: 0}", "{0, 1, 0, 1, 0} {0: 0, 1: 1, 2: 0}", "[0, 1] {0, 1, 2}"], "a": 0,
   "why": "No colon → set (duplicates collapse). Colon → dict."},
  {"id": "p5", "name": "5 · a generator is used once", "code": "g = (n * 10 for n in range(3))\nprint(sum(g))\nprint(sum(g))", "q": "What's printed?", "opts": ["30 / 30", "30 / 0", "30 / TypeError"], "a": 1,
   "why": "A generator produces each value once. The first sum() used them all up; the second sees nothing and returns 0. More in Iterators &amp; generators."},
  {"id": "p6", "name": "6 · flatten", "code": "rows = [[1, 2], [3], [4, 5]]\nprint([x for row in rows for x in row])", "q": "What's printed?", "opts": ["[1, 2, 3, 4, 5]", "[[1, 2], [3], [4, 5]]", "[1, 3, 4]"], "a": 0,
   "why": "Outer loop over rows, inner loop over the items in each row: a flat list."}
 ],
 "runner_extra": [{"label": "Your turn: clean a CSV line", "code": 'line = " asha , 35 , PUNE ,  "\nparts = [p.strip() for p in line.split(",") if p.strip()]\nprint(parts)\nclean = [p.title() if not p.isdigit() else int(p) for p in parts]\nprint(clean)\n# Try: build {"name": ..., "age": ..., "city": ...} with zip and a dict comprehension'}],
 "custom": [
  {"id": "pipe", "title": "Comprehension pipeline", "kind": "Pick an expression and a filter · watch each fee go through",
   "html": '''    <div class="two">
      <div class="chip-group" style="margin:0"><div class="label">Expression (what to keep)</div><div class="chips" id="cpE" style="margin:0"></div></div>
      <div class="chip-group" style="margin:0"><div class="label">Filter (which items)</div><div class="chips" id="cpC" style="margin:0"></div></div>
    </div>
    <pre class="codeblock" id="cpCode" style="min-height:0;margin-top:12px"></pre>
    <div class="cp-grid" id="cpGrid"></div>
    <div class="card" style="margin-top:10px"><div class="label">Result</div><div class="mono" id="cpRes" style="font-size:16px;overflow-wrap:anywhere">[]</div></div>
    <p class="status-line" id="cpStatus"></p>''',
   "js": '''    const PIPE = __PIPE__, E = __E__, C = __C__;
    let ei = 1, ci = 1;
    $('cpE').innerHTML = E.map((e, i) => `<button class="chip-btn mono" type="button" data-i="${i}" aria-pressed="${i === ei}">${e.replace(/</g, '&lt;')}</button>`).join('');
    $('cpC').innerHTML = C.map((c, i) => `<button class="chip-btn mono" type="button" data-i="${i}" aria-pressed="${i === ci}">${c ? c.replace(/</g, '&lt;') : '(none)'}</button>`).join('');
    async function go() {
      const run = K.newRun('cp'); const P = PIPE[ei + '|' + ci];
      const code = P.code.replace('[', '').replace(/\\]$/, '');
      $('cpCode').innerHTML = `<span class="ln">${K.pyHighlight('result = ' + P.code)}</span>`;
      $('cpGrid').innerHTML = '<div class="cp-h">fee</div><div class="cp-h">filter</div><div class="cp-h">expression</div>' + P.items.map(it => `<div class="cp-in">${it.in}</div><div class="cp-f"></div><div class="cp-o"></div>`).join('');
      $('cpRes').textContent = '[]'; const got = [];
      const cells = [...$('cpGrid').children].slice(3);
      try {
        for (let k = 0; k < P.items.length; k++) {
          const it = P.items[k], [a, f, o] = cells.slice(k * 3, k * 3 + 3);
          a.classList.add('cur'); await K.sleep(300, run);
          f.textContent = C[ci] ? (it.pass ? 'pass ✓' : 'dropped ✗') : 'no filter'; f.classList.add(it.pass ? 'ok' : 'bad'); await K.sleep(300, run);
          if (it.pass) { o.textContent = '→ ' + it.out; o.classList.add('ok'); got.push(it.out); $('cpRes').textContent = '[' + got.join(', ') + ']'; }
          a.classList.remove('cur'); await K.sleep(250, run);
        }
        $('cpRes').textContent = P.res;
        $('cpStatus').innerHTML = `${got.length} of ${P.items.length} items kept. Same as the loop: <span class="mono">for f in fees: ${C[ci] ? C[ci].replace(/</g, '&lt;') + ': ' : ''}result.append(${E[ei].replace(/</g, '&lt;')})</span>`;
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    ['cpE', 'cpC'].forEach(id => $(id).querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      $(id).querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      if (id === 'cpE') ei = +b.dataset.i; else ci = +b.dataset.i; go();
    })));
    go();'''.replace('__PIPE__', json.dumps(PIPE)).replace('__E__', json.dumps([e for e, _ in EXPRS])).replace('__C__', json.dumps([c for c, _ in CONDS]))}
 ],
 "style": '''  .cp-grid { display: grid; grid-template-columns: minmax(60px, 1fr) minmax(90px, 1.2fr) minmax(100px, 1.5fr); gap: 6px; margin-top: 12px; font-family: var(--mono); font-size: 14px; }
  .cp-h { font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
  .cp-in, .cp-f, .cp-o { padding: 6px 10px; border-radius: 8px; background: var(--panel-2); border: 1px solid var(--line); min-height: 32px; transition: all .2s; }
  .cp-in.cur { border-color: var(--cyan); box-shadow: 0 0 0 3px var(--teal-wash); }
  .cp-f.ok, .cp-o.ok { color: var(--good-text); border-color: var(--teal); }
  .cp-f.bad { color: var(--bad-text); border-style: dashed; }''',
 "cheat": [
  ["Transform every item", "<span class=\"mono\">[f(x) for x in xs]</span>"],
  ["Keep only some items", "<span class=\"mono\">[x for x in xs if cond]</span>"],
  ["Choose between two values per item", "<span class=\"mono\">[a if cond else b for x in xs]</span>"],
  ["Build a lookup table", "<span class=\"mono\">{x.id: x for x in items}</span>"],
  ["Distinct values", "<span class=\"mono\">{x.city for x in items}</span>"],
  ["Feeding sum / max / any / all", "Generator expression: <span class=\"mono\">sum(x.fee for x in items)</span>"],
  ["Loop body needs several statements or side effects", "Keep the normal <span class=\"mono\">for</span> loop"]
 ],
 "ref_title": "Reference: the four shapes",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Shape</th><th>Brackets</th><th>Result</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>List comprehension</td><td class="mono">[ ]</td><td>list</td><td class="mono">[n * 2 for n in nums]</td></tr>
          <tr><td>Dict comprehension</td><td class="mono">{k: v}</td><td>dict</td><td class="mono">{p["id"]: p for p in rows}</td></tr>
          <tr><td>Set comprehension</td><td class="mono">{ }</td><td>set</td><td class="mono">{p["city"] for p in rows}</td></tr>
          <tr><td>Generator expression</td><td class="mono">( )</td><td>generator (lazy)</td><td class="mono">sum(n * 2 for n in nums)</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Added", "<b>Gap topic:</b> the repo builds lists with <span class=\"mono\">append</span> in loops (Loops.py, Lists_exercises.py) but never uses comprehensions, which are everywhere in real Python code and in the Notion learning plan (Week 1)."],
  ["Added", "<b>Own scope:</b> the loop variable of a comprehension does <b>not</b> leak out (unlike a for loop). Since Python 3.12 list/dict/set comprehensions are inlined for speed (PEP 709), but this rule hasn't changed."],
  ["Added", "<b>Readability rule:</b> one <span class=\"mono\">for</span> and one <span class=\"mono\">if</span> is easy to read. Two nested <span class=\"mono\">for</span>s is the usual limit; beyond that, write a loop or a helper function."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">print([c.upper() for c in \"abc\"])</span>", "code": 'print([c.upper() for c in "abc"])', "expect": "['A', 'B', 'C']", "a": "<b class=\"mono\">['A', 'B', 'C']</b>. Any iterable works, including a string."},
  {"q": "<span class=\"mono\">print(len([x for x in range(10) if x % 3 == 0]))</span>", "code": "print(len([x for x in range(10) if x % 3 == 0]))", "expect": "4", "a": "<b class=\"mono\">4</b>. 0, 3, 6 and 9."},
  {"q": "<span class=\"mono\">print({k: v for k, v in [(\"a\", 1), (\"a\", 2)]})</span>", "code": 'print({k: v for k, v in [("a", 1), ("a", 2)]})', "expect": "{'a': 2}", "a": "<b class=\"mono\">{'a': 2}</b>. The later value for the same key wins."},
  {"q": "<span class=\"mono\">x = 5; y = [x for x in range(3)]; print(x)</span>", "code": "x = 5; y = [x for x in range(3)]; print(x)", "expect": "5", "a": "<b class=\"mono\">5</b>. The comprehension's x is separate and doesn't overwrite the outer one."},
  {"q": "<span class=\"mono\">print(any(n &gt; 3 for n in [1, 5, 2]))</span>", "code": "print(any(n > 3 for n in [1, 5, 2]))", "expect": "True", "a": "<b class=\"mono\">True</b>. A generator expression straight into any()."},
  {"q": "<span class=\"mono\">print(type((n for n in [1])).__name__)</span>", "code": "print(type((n for n in [1])).__name__)", "expect": "generator", "a": "<b class=\"mono\">generator</b>. Round brackets don't make a \"tuple comprehension\"."}
 ],
 "sources": "Gap topic: not in the Python_Fundamentals repo; listed in the Notion plans (Roadmap: data structures with comprehensions; 8-week plan, Week 1)."
}
