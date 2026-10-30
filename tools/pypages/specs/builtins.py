import json
FEES = [800, 450, 1200, 450]
NAMES = ["Asha", "Ravi", "Meera"]
MACH = [
 ("len(fees)", "len", "counts items", "int"),
 ("sum(fees)", "sum", "adds them up", "int"),
 ("min(fees), max(fees)", "min/max", "smallest / largest", "tuple"),
 ("sorted(fees)", "sorted", "new sorted list; fees unchanged", "list"),
 ("sorted(fees, reverse=True)", "sorted", "largest first", "list"),
 ("list(reversed(fees))", "reversed", "lazy iterator, wrapped in list() to see it", "list"),
 ("list(enumerate(fees))", "enumerate", "(index, item) pairs", "list"),
 ("list(zip(names, fees))", "zip", "pairs items; stops at the shorter one", "list"),
 ("any(f > 1000 for f in fees)", "any", "True if at least one is true", "bool"),
 ("all(f > 400 for f in fees)", "all", "True only if every one is true", "bool"),
 ("list(map(str, fees))", "map", "apply a function to each item (lazy)", "list"),
 ("list(filter(lambda f: f < 500, fees))", "filter", "keep items where the function is true (lazy)", "list"),
]
MT = []
for code, fn, what, t in MACH:
    r = eval(code, {"fees": FEES, "names": NAMES})
    MT.append({"code": code, "fn": fn, "what": what, "r": repr(r)})
ROUND = [(v, round(v)) for v in [0.5, 1.5, 2.5, 3.5, 4.5, 2.4, 2.6, -2.5]]

SPEC = {
 "slug": "builtins", "num": 7, "part": "Control flow and data",
 "title": "Built-in functions toolbox", "title_plain": "Built-in functions toolbox",
 "desc": "Python fundamentals: len, sum, min, max, sorted, reversed, enumerate, zip, any, all, round, abs, pow, divmod, help and dir, with real outputs.",
 "lede": [
  "Built-ins are always available, no import needed. Most take <b>any iterable</b>: list, tuple, string, set, dict, range, generator.",
  "Some return a value straight away (<span class=\"mono\">len</span>, <span class=\"mono\">sum</span>, <span class=\"mono\">sorted</span>); others return a <b>lazy iterator</b> (<span class=\"mono\">reversed</span>, <span class=\"mono\">enumerate</span>, <span class=\"mono\">zip</span>, <span class=\"mono\">map</span>) you loop over or wrap in <span class=\"mono\">list()</span>.",
  "<span class=\"mono\">sorted()</span> returns a <b>new</b> list; <span class=\"mono\">list.sort()</span> changes the list and returns None.",
  "<span class=\"mono\">round()</span> rounds halves to the <b>even</b> neighbour: <span class=\"mono\">round(2.5)</span> is 2."
 ],
 "walk": {"title": "summarising a day's fees", "code":
'''fees = [800, 450, 1200, 450]
names = ["Asha", "Ravi", "Meera", "John"]
print(len(fees), sum(fees), min(fees), max(fees))
ranked = sorted(fees, reverse=True)
print(ranked, fees)
pairs = list(zip(names, fees))
top = max(zip(fees, names))
print(pairs[0], top)
for i, name in enumerate(names, start=1):
    print(i, name)
print(any(f > 1000 for f in fees), all(f > 500 for f in fees))
print(round(2.5), round(3.5), round(4.567, 2))
print(abs(-7), pow(2, 10), divmod(17, 5))''',
 "steps": [
  {"at": {"after": 2}, "title": "Two parallel lists", "text": "Fees and the patient names, matched by position. Built-ins will summarise them without writing loops."},
  {"at": {"after": 3}, "title": "The four summary functions", "text": "<span class=\"mono\">len</span> counts, <span class=\"mono\">sum</span> adds, <span class=\"mono\">min</span>/<span class=\"mono\">max</span> find the extremes. Each takes the whole list and returns one number."},
  {"at": {"after": 5}, "title": "sorted() makes a new list", "text": "<span class=\"mono\">ranked</span> is a <b>second</b> list object, largest first. <span class=\"mono\">fees</span> is unchanged. <span class=\"mono\">fees.sort()</span> would reorder fees itself and return None."},
  {"at": {"after": 6}, "title": "zip() pairs items up", "text": "<span class=\"mono\">zip(names, fees)</span> walks both lists together and yields tuples. It's lazy, so <span class=\"mono\">list()</span> collects the pairs."},
  {"at": {"after": 8}, "title": "max() on tuples", "text": "Tuples compare item by item, so <span class=\"mono\">max(zip(fees, names))</span> finds the highest fee and brings its name along: <span class=\"mono\">(1200, 'Meera')</span>.", "tip": "Another way: <span class=\"mono\">max(pairs, key=lambda p: p[1])</span>. The <span class=\"mono\">key=</span> argument is covered in Functional tools."},
  {"at": {"after": 10, "n": 1}, "title": "enumerate() adds a counter", "text": "Each round gives <span class=\"mono\">(number, item)</span>. <span class=\"mono\">start=1</span> makes the count human-friendly. No <span class=\"mono\">range(len(...))</span> needed."},
  {"at": {"after": 11}, "title": "any() and all()", "text": "<span class=\"mono\">any</span>: is at least one fee over 1000? Yes. <span class=\"mono\">all</span>: are all over 500? No (450). Both stop as soon as the answer is known."},
  {"at": {"after": 12}, "title": "round() goes to the even neighbour", "text": "<span class=\"mono\">round(2.5)</span> is <b>2</b> and <span class=\"mono\">round(3.5)</span> is <b>4</b>. This \"banker's rounding\" avoids always pushing totals upward. With a second argument it rounds to that many decimals."},
  {"at": "end", "title": "Number helpers", "text": "<span class=\"mono\">abs</span> drops the sign, <span class=\"mono\">pow(2, 10)</span> is <span class=\"mono\">2 ** 10</span>, and <span class=\"mono\">divmod(17, 5)</span> returns the quotient and remainder together: <span class=\"mono\">(3, 2)</span>."}
 ]},
 "walk_out": "4 2900 450 1200 / [1200, 800, 450, 450] [800, 450, 1200, 450] / ('Asha', 800) (1200, 'Meera') / 1 Asha / 2 Ravi / 3 Meera / 4 John / True False / 2 4 4.57 / 7 1024 (3, 2)",
 "puzzles": [
  {"id": "p1", "name": "1 · sort vs sorted", "code": "nums = [3, 1, 2]\nresult = nums.sort()\nprint(result, nums)", "q": "What's printed?", "opts": ["[1, 2, 3] [1, 2, 3]", "None [1, 2, 3]", "None [3, 1, 2]"], "a": 1,
   "why": "<span class=\"mono\">sort()</span> works in place and returns None. Use <span class=\"mono\">sorted(nums)</span> when you want a value back."},
  {"id": "p2", "name": "2 · zip lengths", "code": "print(list(zip([\"a\", \"b\", \"c\"], [1, 2])))", "q": "What's printed?", "opts": ["[('a', 1), ('b', 2), ('c', None)]", "[('a', 1), ('b', 2)]", "ValueError"], "a": 1,
   "why": "zip stops at the shortest input, silently. Add <span class=\"mono\">strict=True</span> (3.10+) to get an error instead."},
  {"id": "p3", "name": "3 · rounding halves", "code": "print(round(0.5), round(1.5), round(2.5))", "q": "What's printed?", "opts": ["1 2 3", "0 2 2", "0 1 2"], "a": 1,
   "why": "Halves round to the nearest <b>even</b> integer: 0, 2, 2."},
  {"id": "p4", "name": "4 · a used-up iterator", "code": "r = reversed([1, 2, 3])\nprint(list(r))\nprint(list(r))", "q": "What's printed?", "opts": ["[3, 2, 1] / [3, 2, 1]", "[3, 2, 1] / []", "[3, 2, 1] / [1, 2, 3]"], "a": 1,
   "why": "Iterators are one-pass. The first list() consumed it."},
  {"id": "p5", "name": "5 · max of strings", "code": "print(max([\"Ravi\", \"asha\", \"Meera\"]))", "q": "What's printed?", "opts": ["Ravi", "asha", "Meera"], "a": 1,
   "why": "Strings compare by character code, and lowercase letters come after uppercase ones. Use <span class=\"mono\">max(names, key=str.lower)</span> for alphabetical."},
  {"id": "p6", "name": "6 · sum of an empty list", "code": "print(sum([]), max([], default=0))\nprint(max([]))", "q": "What's printed?", "opts": ["0 0 / 0", "0 0 / ValueError: max() iterable argument is empty", "ValueError"], "a": 1,
   "why": "sum() of nothing is 0, but max() of nothing is an error unless you give <span class=\"mono\">default=</span>."}
 ],
 "runner_extra": [{"label": "Your turn: a fee report", "code": 'fees = {"Asha": 800, "Ravi": 450, "Meera": 1200}\nprint("patients:", len(fees))\nprint("total:", sum(fees.values()))\nprint("average:", round(sum(fees.values()) / len(fees), 2))\nfor rank, (name, fee) in enumerate(sorted(fees.items(), key=lambda kv: kv[1], reverse=True), start=1):\n    print(rank, name, fee)'}],
 "custom": [
  {"id": "mach", "title": "Function machines", "kind": "Pick a built-in · watch the inputs go in and the real result come out",
   "html": '''    <div class="chips" id="mfBtns"></div>
    <div class="mf-row">
      <div class="mf-in" id="mfIn"></div>
      <div class="mf-box" id="mfBox">?</div>
      <div class="mf-out mono" id="mfOut"></div>
    </div>
    <p class="status-line" id="mfStatus">Pick a function.</p>''',
   "js": '''    const MT = __MT__;
    $('mfBtns').innerHTML = MT.map((m, i) => `<button class="chip-btn mono" type="button" data-i="${i}" aria-pressed="false">${m.code.replace(/</g, '&lt;')}</button>`).join('');
    async function go(m) {
      const run = K.newRun('mf');
      const usesNames = /names/.test(m.code);
      $('mfIn').innerHTML = (usesNames ? '<div class="mf-lbl">names</div><div class="mf-items">' + ['Asha', 'Ravi', 'Meera'].map(n => `<span class="mf-it">'${n}'</span>`).join('') + '</div>' : '') + '<div class="mf-lbl">fees</div><div class="mf-items">' + [800, 450, 1200, 450].map(n => `<span class="mf-it">${n}</span>`).join('') + '</div>';
      $('mfBox').textContent = m.fn; $('mfBox').classList.remove('done'); $('mfOut').textContent = '';
      try {
        for (const it of $('mfIn').querySelectorAll('.mf-it')) { it.classList.add('fed'); await K.sleep(160, run); }
        $('mfBox').classList.add('done'); await K.sleep(250, run);
        $('mfOut').textContent = m.r;
        $('mfStatus').innerHTML = `<span class="mono">${m.code.replace(/</g, '&lt;')}</span> · ${m.what}.`;
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    $('mfBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      $('mfBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); go(MT[+b.dataset.i]);
    }));'''.replace('__MT__', json.dumps(MT))},
  {"id": "rnd", "title": "Where does round() go?", "kind": "Halves go to the even neighbour · everything else to the nearest",
   "html": '''    <div class="scroll"><svg class="diagram narrow" id="rdSvg" viewBox="0 0 700 250" style="min-width:520px;max-width:720px;margin:0 auto;display:block" role="img" aria-label="Number line showing round() results"></svg></div>
    <p class="status-line">Arrows show <span class="mono">round(x)</span> from real Python. Green arrows land on an even number.</p>''',
   "js": '''    const R = __R__; const svg = $('rdSvg'), ns = 'http://www.w3.org/2000/svg', X = v => 170 + (v + 3) * 64;
    function mk(tag, at, txt) { const e = document.createElementNS(ns, tag); for (const k in at) e.setAttribute(k, at[k]); if (txt != null) e.textContent = txt; svg.appendChild(e); return e; }
    mk('line', { x1: X(-3), y1: 200, x2: X(5), y2: 200, class: 'rg-axis' });
    for (let v = -3; v <= 5; v++) { mk('line', { x1: X(v), y1: 194, x2: X(v), y2: 206, class: 'rg-axis' }); const t = mk('text', { x: X(v), y: 228, class: 'rg-num' }, v); t.style.textAnchor = 'middle'; }
    R.filter(([v]) => v >= -3).forEach(([v, r], k) => {
      const y = 18 + k * 20;
      const c = mk('circle', { cx: X(v), cy: y, r: 4, class: 'rd-src' });
      const l = mk('text', { x: X(v) - 9, y: y + 4, class: 'rd-l' }, 'round(' + v + ') → ' + r); l.style.textAnchor = 'end';
      mk('path', { d: `M${X(v)} ${y + 4} L${X(r)} 190`, class: 'rd-ar' + (r % 2 === 0 ? ' even' : ''), 'marker-end': 'url(#rdm)' });
    });
    const defs = mk('defs', {}); defs.innerHTML = '<marker id="rdm" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" class="rd-mk"></path></marker>';'''.replace('__R__', json.dumps(ROUND))}
 ],
 "style": '''  .mf-row { display: grid; grid-template-columns: minmax(0, 1.3fr) auto minmax(0, 1.4fr); gap: 14px; align-items: center; margin-top: 14px; }
  @media (max-width: 640px) { .mf-row { grid-template-columns: 1fr; } }
  .mf-lbl { font-family: var(--mono); font-size: 11px; color: var(--muted); margin: 4px 0; }
  .mf-items { display: flex; flex-wrap: wrap; gap: 6px; }
  .mf-it { font-family: var(--mono); font-size: 14px; padding: 4px 8px; border-radius: 6px; background: var(--panel-2); border: 1px solid var(--line); transition: all .2s; }
  .mf-it.fed { border-color: var(--cyan); background: var(--teal-wash); }
  .mf-box { font-family: var(--mono); font-weight: 700; font-size: 18px; padding: 18px 22px; border-radius: 14px; border: 2px dashed var(--accent-text); color: var(--accent-text); text-align: center; min-width: 110px; }
  .mf-box.done { border-style: solid; box-shadow: 0 0 0 4px var(--teal-wash); }
  .mf-out { font-size: 15px; min-height: 40px; padding: 10px 12px; border-radius: 10px; background: var(--code-bg); border: 1px solid var(--line); overflow-wrap: anywhere; }
  .rg-axis { stroke: var(--muted); stroke-width: 1.5; }
  .rg-num { font-family: var(--mono); font-size: 13px; fill: var(--muted); }
  .rd-src { fill: var(--accent-text); }
  .rd-l { font-family: var(--mono); font-size: 12px; fill: var(--fg); }
  .rd-ar { stroke: var(--fg-soft); stroke-width: 1.5; fill: none; }
  .rd-ar.even { stroke: var(--teal); }
  .rd-mk { fill: var(--fg-soft); }''',
 "cheat": [
  ["Count / total / extremes", "<span class=\"mono\">len sum min max</span>"],
  ["Sorted copy vs sort in place", "<span class=\"mono\">sorted(xs)</span> vs <span class=\"mono\">xs.sort()</span> (returns None)"],
  ["Loop with a counter", "<span class=\"mono\">enumerate(xs, start=1)</span>"],
  ["Walk two lists together", "<span class=\"mono\">zip(a, b)</span>; add <span class=\"mono\">strict=True</span> if lengths must match"],
  ["Any / every item passes a test", "<span class=\"mono\">any(...)</span> / <span class=\"mono\">all(...)</span> with a generator expression"],
  ["Money rounding must be exact", "<span class=\"mono\">decimal.Decimal</span> with <span class=\"mono\">ROUND_HALF_UP</span>, not float + round()"],
  ["What can this object do?", "<span class=\"mono\">dir(obj)</span>, <span class=\"mono\">help(obj)</span>"]
 ],
 "ref_title": "Reference: built-ins by job",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Job</th><th>Built-ins</th><th>Returns</th></tr></thead>
        <tbody>
          <tr><td>Summarise</td><td class="mono">len sum min max any all</td><td>a single value</td></tr>
          <tr><td>Reorder</td><td class="mono">sorted reversed</td><td>new list / lazy iterator</td></tr>
          <tr><td>Combine &amp; count</td><td class="mono">zip enumerate</td><td>lazy iterator of tuples</td></tr>
          <tr><td>Transform &amp; filter</td><td class="mono">map filter</td><td>lazy iterator (a comprehension is often clearer)</td></tr>
          <tr><td>Numbers</td><td class="mono">abs round pow divmod</td><td>number / tuple</td></tr>
          <tr><td>Convert</td><td class="mono">int float str bool list tuple set dict</td><td>new object (see Variables &amp; objects)</td></tr>
          <tr><td>Inspect</td><td class="mono">type isinstance id dir help</td><td>info about an object</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Corrected", "<b>round() in BuiltinFunctions_Math_Numbers.py:</b> the examples (4.56756, 8.542, -13.349) never hit a half, so they hide the surprise: <span class=\"mono\">round(2.5)</span> is 2, <span class=\"mono\">round(0.5)</span> is 0. Also <span class=\"mono\">round(2.675, 2)</span> gives 2.67, because 2.675 can't be stored exactly as a float."],
  ["Added", "<b>Lazy results print oddly:</b> <span class=\"mono\">print(reversed(nums2))</span> in the repo shows <span class=\"mono\">&lt;list_reverseiterator object at 0x…&gt;</span>, not the items. Wrap it in <span class=\"mono\">list()</span> or loop over it, as the next line does."],
  ["Added", "<b>zip() hides length mismatches:</b> the repo zips 3 fruits with 4 numbers and the 4th number vanishes silently. Use <span class=\"mono\">zip(..., strict=True)</span> when they must match."],
  ["Added", "<b>help() and dir()</b> are for the interactive prompt. In scripts they print pages of text; in an editor, hover or go-to-definition is quicker."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">print(sorted(\"cab\"))</span>", "code": 'print(sorted("cab"))', "expect": "['a', 'b', 'c']", "a": "<b class=\"mono\">['a', 'b', 'c']</b>. sorted() always returns a list, whatever it was given."},
  {"q": "<span class=\"mono\">print(sum([0.1] * 3) == 0.3)</span>", "code": "print(sum([0.1] * 3) == 0.3)", "expect": "False", "a": "<b class=\"mono\">False</b>. Floats are approximate; compare with <span class=\"mono\">math.isclose()</span>."},
  {"q": "<span class=\"mono\">print(all([]), any([]))</span>", "code": "print(all([]), any([]))", "expect": "True False", "a": "<b class=\"mono\">True False</b>. \"Every item passes\" is true when there are none; \"at least one passes\" is false."},
  {"q": "<span class=\"mono\">print(divmod(125, 60))</span>", "code": "print(divmod(125, 60))", "expect": "(2, 5)", "a": "<b class=\"mono\">(2, 5)</b>. 125 minutes is 2 hours 5 minutes."},
  {"q": "<span class=\"mono\">print(max([3, 10, 7], key=lambda n: -n))</span>", "code": "print(max([3, 10, 7], key=lambda n: -n))", "expect": "3", "a": "<b class=\"mono\">3</b>. key= changes what is compared; the original item is returned."},
  {"q": "<span class=\"mono\">print(list(enumerate(\"ab\")))</span>", "code": 'print(list(enumerate("ab")))', "expect": "[(0, 'a'), (1, 'b')]", "a": "<b class=\"mono\">[(0, 'a'), (1, 'b')]</b>. Counting starts at 0 unless you pass start=."}
 ],
 "sources": "Sources: Python_Fundamentals repo (Basics/BuiltinFunctions_Iterables.py, BuiltinFunctions_Math_Numbers.py, UtilityBuiltInFunctions.py)."
}
