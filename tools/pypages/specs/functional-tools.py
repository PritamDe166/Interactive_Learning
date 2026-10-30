import json
P = [("Ravi", 41, 800), ("Asha", 35, 450), ("meera", 29, 1200), ("John", 41, 450)]
KEYS = [
 ("(no key)", None),
 ("key=lambda p: p[1]", lambda p: p[1]),
 ("key=lambda p: p[2], reverse=True", "rev"),
 ("key=lambda p: (-p[2], p[0])", lambda p: (-p[2], p[0])),
 ("key=lambda p: p[0]", lambda p: p[0]),
 ("key=lambda p: p[0].lower()", lambda p: p[0].lower()),
 ("key=lambda p: len(p[0])", lambda p: len(p[0])),
]
SORTS = []
for label, k in KEYS:
    if k is None: res = sorted(P); kv = {p: repr(p) for p in P}
    elif k == "rev": res = sorted(P, key=lambda p: p[2], reverse=True); kv = {p: repr(p[2]) for p in P}
    else: res = sorted(P, key=k); kv = {p: repr(k(p)) for p in P}
    SORTS.append({"label": label, "order": [P.index(p) for p in res], "keys": [kv[p] for p in P]})

SPEC = {
 "slug": "functional-tools", "num": 15, "part": "Going further",
 "title": "Functional tools &amp; itertools", "title_plain": "Functional tools & itertools",
 "desc": "Python fundamentals: lambda, sorted with key=, map, filter, functools.reduce, and itertools helpers like chain, groupby and islice.",
 "lede": [
  "Functions are objects: you can pass them to other functions. <b>lambda</b> writes a small one inline: <span class=\"mono\">lambda p: p[1]</span>.",
  "<span class=\"mono\">sorted(items, key=f)</span> sorts by <b>f(item)</b>, not by the item itself. Same <span class=\"mono\">key=</span> works for min, max and groupby.",
  "<span class=\"mono\">map(f, xs)</span> transforms, <span class=\"mono\">filter(f, xs)</span> keeps items where f is true, <span class=\"mono\">reduce(f, xs, start)</span> folds them into one value. A comprehension is often clearer for the first two.",
  "<b>itertools</b> has lazy building blocks: <span class=\"mono\">chain</span>, <span class=\"mono\">islice</span>, <span class=\"mono\">groupby</span>, <span class=\"mono\">count</span>…"
 ],
 "walk": {"title": "sorting and summarising patients", "code":
'''from functools import reduce
from itertools import chain, groupby, islice
patients = [("Ravi", 41, 800), ("Asha", 35, 450),
            ("Meera", 29, 1200), ("John", 41, 450)]
by_age = sorted(patients, key=lambda p: p[1])
top = sorted(patients, key=lambda p: (-p[2], p[0]))
names = list(map(lambda p: p[0].upper(), patients))
cheap = list(filter(lambda p: p[2] < 500, patients))
total = reduce(lambda acc, p: acc + p[2], patients, 0)
print(by_age[0][0], top[0][0], names, len(cheap), total)
for age, group in groupby(by_age, key=lambda p: p[1]):
    print(age, [p[0] for p in group])
print(list(chain(["9:00"], ["9:30", "10:00"])), list(islice(names, 2)))''',
 "steps": [
  {"at": 3, "title": "Records as tuples", "text": "Each patient is a tuple (name, age, fee). Sorting them by \"age\" or \"fee\" needs a way to say <b>which part</b> to compare."},
  {"at": 4, "title": "key= calls your function per item", "text": "<span class=\"mono\">sorted(..., key=lambda p: p[1])</span> calls the lambda once for each patient to get a <b>sort key</b> (the age), then sorts by those keys. Here's the first call, with <span class=\"mono\">p</span> = Ravi's tuple."},
  {"at": 16, "title": "Sorted by age", "text": "<span class=\"mono\">by_age</span> is a new list, youngest first. Ravi and John are both 41 and keep their original order: Python's sort is <b>stable</b>."},
  {"at": 29, "title": "Two-level sort with a tuple key", "text": "Key <span class=\"mono\">(-fee, name)</span>: highest fee first (negating flips the order), ties broken alphabetically. Tuples compare item by item."},
  {"at": 42, "title": "map: transform each item", "text": "<span class=\"mono\">map</span> applies the lambda to every patient and returns a lazy iterator; <span class=\"mono\">list()</span> collects the uppercased names. Equivalent: <span class=\"mono\">[p[0].upper() for p in patients]</span>."},
  {"at": 55, "title": "filter: keep what passes", "text": "Only patients with fee &lt; 500 survive: Asha and John. Equivalent: <span class=\"mono\">[p for p in patients if p[2] &lt; 500]</span>."},
  {"at": 68, "title": "reduce: fold into one value", "text": "<span class=\"mono\">reduce</span> carries an accumulator: start 0, then 0+800, +450, +1200, +450 = 2900. For sums, <span class=\"mono\">sum(p[2] for p in patients)</span> is simpler; reduce shines for custom combining.", "tip": "reduce lives in functools because Python prefers explicit loops or sum/any/all for common cases."},
  {"at": 78, "title": "groupby groups neighbours", "text": "<span class=\"mono\">groupby</span> walks the <b>sorted</b> list and bundles consecutive items with the same key. It only groups neighbours, which is why we sorted by age first."},
  {"at": "end", "title": "chain and islice", "text": "<span class=\"mono\">chain</span> joins iterables end to end without copying; <span class=\"mono\">islice</span> slices any iterator (even an infinite one) lazily."}
 ]},
 "walk_out": "Meera Meera ['RAVI', 'ASHA', 'MEERA', 'JOHN'] 2 2900 / 29 ['Meera'] / 35 ['Asha'] / 41 ['Ravi', 'John'] / ['9:00', '9:30', '10:00'] ['RAVI', 'ASHA']",
 "puzzles": [
  {"id": "p1", "name": "1 · default string sort", "code": "print(sorted([\"bob\", \"Asha\", \"carl\"]))", "q": "What's printed?", "opts": ["['Asha', 'bob', 'carl']", "['bob', 'carl', 'Asha']", "['Asha', 'carl', 'bob']"], "a": 0,
   "why": "Uppercase letters sort before lowercase (by character code), and 'A' &lt; 'b' anyway here. For case-insensitive order use <span class=\"mono\">key=str.lower</span>."},
  {"id": "p2", "name": "2 · key=len", "code": "print(sorted([\"Meera\", \"Jo\", \"Asha\"], key=len))", "q": "What's printed?", "opts": ["['Asha', 'Jo', 'Meera']", "['Jo', 'Asha', 'Meera']", "[2, 4, 5]"], "a": 1,
   "why": "Any one-argument function works as a key, including built-ins like len. The items themselves are returned, not the keys."},
  {"id": "p3", "name": "3 · groupby without sorting", "code": "from itertools import groupby\ncities = [\"Pune\", \"Delhi\", \"Pune\"]\nprint([(k, len(list(g))) for k, g in groupby(cities)])", "q": "What's printed?", "opts": ["[('Delhi', 1), ('Pune', 2)]", "[('Pune', 1), ('Delhi', 1), ('Pune', 1)]", "[('Pune', 2), ('Delhi', 1)]"], "a": 1,
   "why": "groupby only merges <b>adjacent</b> equal keys. Sort first, or use <span class=\"mono\">collections.Counter</span> for counting."},
  {"id": "p4", "name": "4 · max with key", "code": "fees = {\"Asha\": 450, \"Ravi\": 800, \"Meera\": 600}\nprint(max(fees), max(fees, key=fees.get))", "q": "What's printed?", "opts": ["Ravi Ravi", "Ravi 800", "Meera Ravi"], "a": 0,
   "why": "<span class=\"mono\">max(fees)</span> compares keys alphabetically: 'Ravi' is the largest string. <span class=\"mono\">key=fees.get</span> compares by fee: Ravi again (800). Same answer here, for different reasons!"},
  {"id": "p5", "name": "5 · map is lazy", "code": "m = map(str.upper, [\"a\", \"b\"])\nprint(list(m), list(m))", "q": "What's printed?", "opts": ["['A', 'B'] ['A', 'B']", "['A', 'B'] []", "<map object> []"], "a": 1,
   "why": "map returns a one-pass iterator, like a generator."}
 ],
 "runner_extra": [{"label": "Your turn: top two fees per city", "code": 'from itertools import groupby\nvisits = [("Pune", "Asha", 450), ("Delhi", "Ravi", 800), ("Pune", "Meera", 1200), ("Pune", "John", 300)]\nvisits.sort(key=lambda v: v[0])\nfor city, rows in groupby(visits, key=lambda v: v[0]):\n    best = sorted(rows, key=lambda v: v[2], reverse=True)[:2]\n    print(city, [name for _, name, _ in best])'}],
 "custom": [
  {"id": "srt", "title": "Sort by key", "kind": "Patients as (name, age, fee) · pick a key and watch the rows move",
   "html": '''    <div class="chips" id="skBtns"></div>
    <div class="sk-table" id="skTable"></div>
    <p class="status-line" id="skStatus"></p>''',
   "js": '''    const P = __P__, S = __S__, H = 42;
    $('skBtns').innerHTML = S.map((s, i) => `<button class="chip-btn mono" type="button" data-i="${i}" aria-pressed="${!i}">${s.label}</button>`).join('');
    $('skTable').style.height = (P.length * H + 34) + 'px';
    $('skTable').innerHTML = '<div class="sk-head"><span>name</span><span>age</span><span>fee</span><span>sort key</span></div>' + P.map((p, i) => `<div class="sk-row" data-i="${i}"><span class="mono">${p[0]}</span><span class="mono">${p[1]}</span><span class="mono">${p[2]}</span><span class="mono sk-k"></span></div>`).join('');
    const rows = [...$('skTable').querySelectorAll('.sk-row')];
    function show(i) {
      const s = S[i];
      rows.forEach((r, k) => { r.style.transform = `translateY(${s.order.indexOf(k) * H + 34}px)`; r.querySelector('.sk-k').textContent = s.keys[k]; });
      $('skStatus').innerHTML = `<span class="mono">sorted(patients${i ? ', ' + s.label : ''})</span> · ` + (i === 0 ? 'no key: whole tuples compare, name first (uppercase before lowercase).' : 'rows are ordered by the key column; equal keys keep their original order (stable sort).');
    }
    $('skBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => { $('skBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); show(+b.dataset.i); }));
    show(0);'''.replace('__P__', json.dumps(P)).replace('__S__', json.dumps(SORTS))}
 ],
 "style": '''  .sk-table { position: relative; margin-top: 12px; }
  .sk-head, .sk-row { display: grid; grid-template-columns: 1.2fr .6fr .7fr 1.6fr; gap: 8px; align-items: center; padding: 0 12px; }
  .sk-head { height: 30px; font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--muted); }
  .sk-row { position: absolute; left: 0; right: 0; top: 0; height: 36px; border: 1px solid var(--line); border-radius: 10px; background: var(--panel-2); transition: transform .5s ease; }
  .sk-k { color: var(--accent-text); overflow-wrap: anywhere; }''',
 "cheat": [
  ["Sort records by a field", "<span class=\"mono\">sorted(rows, key=lambda r: r[\"fee\"])</span>"],
  ["Descending / two levels", "<span class=\"mono\">reverse=True</span> / tuple key <span class=\"mono\">(-fee, name)</span>"],
  ["Same, faster and named", "<span class=\"mono\">from operator import itemgetter, attrgetter</span>"],
  ["Transform or filter a list", "A comprehension; map/filter when you already have a named function"],
  ["Combine everything into one value", "sum / max / any / all first; <span class=\"mono\">reduce</span> for anything else"],
  ["Group records", "Sort by the key, then <span class=\"mono\">groupby</span>; or build a dict of lists"],
  ["Join several iterables", "<span class=\"mono\">chain(a, b, c)</span>"]
 ],
 "ref_title": "Reference: itertools picks",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Function</th><th>Does</th><th>Example → result</th></tr></thead>
        <tbody>
          <tr><td class="mono">chain(a, b)</td><td>one after another</td><td class="mono">chain([1], [2, 3]) → 1 2 3</td></tr>
          <tr><td class="mono">islice(it, n)</td><td>first n of any iterator</td><td class="mono">islice(count(), 3) → 0 1 2</td></tr>
          <tr><td class="mono">groupby(it, key)</td><td>runs of equal keys</td><td class="mono">"aabc" → a:aa b:b c:c</td></tr>
          <tr><td class="mono">count(start)</td><td>endless counter</td><td class="mono">count(1001) → 1001 1002 …</td></tr>
          <tr><td class="mono">product(a, b)</td><td>every pair (nested loops)</td><td class="mono">product("AB", [1, 2]) → A1 A2 B1 B2</td></tr>
          <tr><td class="mono">combinations(it, r)</td><td>unordered picks</td><td class="mono">combinations("ABC", 2) → AB AC BC</td></tr>
          <tr><td class="mono">accumulate(it)</td><td>running totals</td><td class="mono">accumulate([1, 2, 3]) → 1 3 6</td></tr>
          <tr><td class="mono">batched(it, n)</td><td>chunks of n (3.12+)</td><td class="mono">batched("ABCDE", 2) → AB CD E</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Added", "<b>From your Notion plans:</b> \"sorting / filter / map\" (Roadmap) and \"map/filter/reduce/lambda, itertools\" (Week 5 of the 8-week plan)."],
  ["Added", "<b>lambda limits:</b> one expression, no statements. If it needs a name or several lines, write a normal <span class=\"mono\">def</span>; it also gives clearer tracebacks."],
  ["Added", "<b>sort() vs sorted():</b> both accept <span class=\"mono\">key=</span> and <span class=\"mono\">reverse=</span>; <span class=\"mono\">list.sort()</span> sorts in place and returns None (see Built-in functions)."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">print(sorted([3, -5, 2], key=abs))</span>", "code": "print(sorted([3, -5, 2], key=abs))", "expect": "[2, 3, -5]", "a": "<b class=\"mono\">[2, 3, -5]</b>. Sorted by absolute value; the original numbers are returned."},
  {"q": "<span class=\"mono\">from functools import reduce\\nprint(reduce(lambda a, b: a * b, [1, 2, 3, 4]))</span>", "code": "from functools import reduce\nprint(reduce(lambda a, b: a * b, [1, 2, 3, 4]))", "expect": "24", "a": "<b class=\"mono\">24</b>. Without a start value, the first item is the start."},
  {"q": "<span class=\"mono\">print(list(filter(None, [0, 1, \"\", \"a\", None])))</span>", "code": "print(list(filter(None, [0, 1, \"\", \"a\", None])))", "expect": "[1, 'a']", "a": "<b class=\"mono\">[1, 'a']</b>. With None as the function, filter keeps truthy items."}
 ],
 "sources": "From the Notion plans (Roadmap for Python; Planning for python learning, Week 5). Python docs: Sorting HOW TO, functools, itertools."
}
