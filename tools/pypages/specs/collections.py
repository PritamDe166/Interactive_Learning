A = {"Asha", "Ravi", "Meera", "John"}
B = {"Ravi", "John", "Lina"}
OPS = {"&": sorted(A & B), "|": sorted(A | B), "-": sorted(A - B), "^": sorted(A ^ B)}
import json
SPEC = {
 "slug": "collections", "num": 5, "part": "Control flow and data",
 "title": "Collections: list, tuple, set, dict", "title_plain": "Collections: list, tuple, set, dict",
 "desc": "Python fundamentals: lists, tuples, sets and dictionaries drawn as objects in memory, with indexing, unpacking, set operations and dict lookups.",
 "lede": [
  "<b>list</b> <span class=\"mono\">[ ]</span>: ordered, changeable, duplicates allowed. The everyday container.",
  "<b>tuple</b> <span class=\"mono\">( )</span>: ordered but <b>fixed</b>. Good for records like (lat, lon) and for unpacking.",
  "<b>set</b> <span class=\"mono\">{ }</span>: no order, <b>no duplicates</b>, very fast <span class=\"mono\">in</span> checks, maths like union and intersection.",
  "<b>dict</b> <span class=\"mono\">{key: value}</span>: look things up by key. Keys are unique; insertion order is kept."
 ],
 "walk": {"title": "four containers for one clinic", "code":
'''visits = ["Asha", "Ravi", "Asha"]
visits.append("Meera")
first = visits.pop(0)
point = (12.97, 77.59)
lat, lon = point
unique = set(visits)
unique.add("John")
patient = {"name": "Ravi", "age": 41}
patient["age"] = 42
patient["city"] = "Pune"
print(patient.get("phone", "n/a"))
for key, value in patient.items():
    print(key, value)''',
 "steps": [
  {"at": {"after": 1}, "title": "A list holds references", "text": "Each cell of the list points to a str object. The boxes underneath are <b>indexes</b> 0, 1, 2. \"Asha\" appears twice: lists allow duplicates."},
  {"at": {"after": 2}, "title": "append() changes the list in place", "text": "No new list is made: the same object grows by one cell. That's what <b>mutable</b> means. append() returns <span class=\"mono\">None</span>, so never write <span class=\"mono\">visits = visits.append(...)</span>."},
  {"at": {"after": 3}, "title": "pop(0) removes and returns", "text": "<span class=\"mono\">pop(0)</span> takes out the first item and hands it back, so <span class=\"mono\">first</span> now points to \"Asha\". The others shift left: indexes are renumbered.", "tip": "<span class=\"mono\">pop()</span> from the end is fast; <span class=\"mono\">pop(0)</span> has to shift everything. For a real queue use <span class=\"mono\">collections.deque</span>."},
  {"at": {"after": 5}, "title": "A tuple, then unpacking", "text": "<span class=\"mono\">point</span> is a tuple: it can't grow or change. <span class=\"mono\">lat, lon = point</span> <b>unpacks</b> it, one name per item. The count must match, or you get a ValueError."},
  {"at": {"after": 6}, "title": "set() drops duplicates", "text": "Building a set from the list keeps only one \"Asha\". Sets have <b>no index</b>: the order you see is not guaranteed, and <span class=\"mono\">unique[0]</span> is an error."},
  {"at": {"after": 7}, "title": "Sets are mutable too", "text": "<span class=\"mono\">add()</span> puts John in. Adding \"Ravi\" again would change nothing. Checking <span class=\"mono\">\"Ravi\" in unique</span> is very fast, even for millions of items."},
  {"at": {"after": 8}, "title": "A dict maps keys to values", "text": "Each row is a <b>key → value</b> pair. You look values up by key, not by position: <span class=\"mono\">patient[\"name\"]</span>."},
  {"at": {"after": 10}, "title": "Assign to update or add", "text": "<span class=\"mono\">patient[\"age\"] = 42</span> replaces an existing value; <span class=\"mono\">patient[\"city\"] = \"Pune\"</span> adds a new pair. Same syntax, Python checks whether the key exists."},
  {"at": {"after": 11}, "title": "get() for keys that may be missing", "text": "<span class=\"mono\">patient[\"phone\"]</span> would raise <b>KeyError</b>. <span class=\"mono\">get(\"phone\", \"n/a\")</span> returns the default instead."},
  {"at": "end", "title": "Looping over items()", "text": "<span class=\"mono\">items()</span> gives (key, value) pairs, unpacked straight into two names. Order is the order keys were added (guaranteed since Python 3.7)."}
 ]},
 "walk_out": "n/a / name Ravi / age 42 / city Pune",
 "puzzles": [
  {"id": "p1", "name": "1 · append returns None", "code": 'names = ["Asha"]\nnames = names.append("Ravi")\nprint(names)', "q": "What's printed?", "opts": ["['Asha', 'Ravi']", "None", "['Ravi']"], "a": 1,
   "why": "List methods that change the list return <span class=\"mono\">None</span>. Rebinding <span class=\"mono\">names</span> to that result loses the list. Just write <span class=\"mono\">names.append(\"Ravi\")</span>."},
  {"id": "p2", "name": "2 · one-item tuple", "code": 'a = (5)\nb = (5,)\nprint(type(a).__name__, type(b).__name__)', "q": "What's printed?", "opts": ["tuple tuple", "int tuple", "int int"], "a": 1,
   "why": "Parentheses alone are just grouping. The <b>comma</b> makes a tuple."},
  {"id": "p3", "name": "3 · remove()", "code": 'ages = [12, 34, 12, 56]\nages.remove(12)\nprint(ages)', "q": "What's printed?", "opts": ["[34, 56]", "[34, 12, 56]", "[12, 34, 56]"], "a": 1,
   "why": "<span class=\"mono\">remove(x)</span> deletes only the <b>first</b> matching value. To remove all: <span class=\"mono\">[a for a in ages if a != 12]</span>."},
  {"id": "p4", "name": "4 · dict keys are unique", "code": 'd = {"a": 1, "b": 2, "a": 3}\nprint(d, len(d))', "q": "What's printed?", "opts": ["{'a': 1, 'b': 2, 'a': 3} 3", "{'a': 3, 'b': 2} 2", "{'b': 2, 'a': 3} 2"], "a": 1,
   "why": "A repeated key overwrites the earlier value but keeps its original position."},
  {"id": "p5", "name": "5 · empty braces", "code": 'x = {}\ny = set()\nprint(type(x).__name__, type(y).__name__)', "q": "What's printed?", "opts": ["set set", "dict set", "dict dict"], "a": 1,
   "why": "<span class=\"mono\">{}</span> is an empty <b>dict</b>. An empty set must be written <span class=\"mono\">set()</span>."},
  {"id": "p6", "name": "6 · star unpacking", "code": 'first, *rest = [10, 20, 30, 40]\nprint(first, rest)', "q": "What's printed?", "opts": ["10 [20, 30, 40]", "10 (20, 30, 40)", "ValueError: too many values to unpack"], "a": 0,
   "why": "<span class=\"mono\">*rest</span> collects everything left over into a <b>list</b>."}
 ],
 "runner_extra": [{"label": "Your turn: count visits per patient", "code": 'visits = ["Asha", "Ravi", "Asha", "Meera", "Asha", "Ravi"]\ncounts = {}\nfor name in visits:\n    counts[name] = counts.get(name, 0) + 1\nprint(counts)\nprint("unique:", len(set(visits)))\n# Try: find the patient with most visits using max(counts, key=counts.get)'}],
 "custom": [
  {"id": "lb", "title": "List operations bench", "kind": "Click an operation · see the list change and what the call returns",
   "html": '''    <div class="lb-list" id="lbList" aria-live="polite"></div>
    <div class="chips" id="lbOps" style="margin-top:10px"></div>
    <div class="card" style="margin-top:10px"><pre class="codeblock" id="lbCode" style="min-height:0;margin:0"></pre><p class="status-line" id="lbStatus" style="text-align:left;margin:8px 0 0">Pick an operation.</p></div>''',
   "js": '''    const START = [34, 12, 56, 12];
    let L = START.slice();
    const OPS = [
      ['append(90)', l => { l.push(90); return 'None'; }, 'adds one item at the end'],
      ['insert(0, 7)', l => { l.unshift(7); return 'None'; }, 'puts 7 at index 0; everything else shifts right'],
      ['pop()', l => l.length ? String(l.pop()) : 'IndexError: pop from empty list', 'removes the last item and returns it'],
      ['pop(0)', l => l.length ? String(l.shift()) : 'IndexError: pop from empty list', 'removes the first item and returns it'],
      ['remove(12)', l => { const i = l.indexOf(12); if (i < 0) return 'ValueError: list.remove(x): x not in list'; l.splice(i, 1); return 'None'; }, 'deletes the first 12 only'],
      ['sort()', l => { l.sort((a, b) => a - b); return 'None'; }, 'sorts in place'],
      ['reverse()', l => { l.reverse(); return 'None'; }, 'reverses in place'],
      ['extend([1, 2])', l => { l.push(1, 2); return 'None'; }, 'adds each item of the other list'],
      ['index(56)', l => { const i = l.indexOf(56); return i < 0 ? 'ValueError: 56 is not in list' : String(i); }, 'position of the first 56; the list is unchanged'],
      ['count(12)', l => String(l.filter(x => x === 12).length), 'how many 12s; the list is unchanged'],
    ];
    function draw(changed) { $('lbList').innerHTML = L.length ? L.map((v, i) => `<div class="lb-cell${changed ? ' chg' : ''}"><b>${v}</b><span>${i}</span></div>`).join('') : '<span class="muted mono">[] (empty)</span>'; }
    $('lbOps').innerHTML = OPS.map((o, i) => `<button class="chip-btn" type="button" data-i="${i}">.${o[0]}</button>`).join('') + '<button class="chip-btn" type="button" data-i="r">reset</button>';
    $('lbOps').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      if (b.dataset.i === 'r') { L = START.slice(); draw(); $('lbCode').innerHTML = `<span class="ln">${K.pyHighlight('nums = [' + START.join(', ') + ']')}</span>`; $('lbStatus').textContent = 'Back to the start.'; return; }
      const [label, fn, what] = OPS[+b.dataset.i];
      const before = JSON.stringify(L); const r = fn(L); const changed = JSON.stringify(L) !== before;
      draw(changed);
      $('lbCode').innerHTML = `<span class="ln">${K.pyHighlight('result = nums.' + label)}</span>`;
      const err = /Error/.test(r);
      $('lbStatus').innerHTML = err ? `<b class="bad-text">${r}</b>` : `returns <b class="mono">${r}</b> · ${what}.` + (r === 'None' ? ' <span class="muted">(changed in place, nothing returned)</span>' : '');
    }));
    draw(); $('lbCode').innerHTML = `<span class="ln">${K.pyHighlight('nums = [' + START.join(', ') + ']')}</span>`;'''},
  {"id": "venn", "title": "Set operations", "kind": "Two clinics' patient sets · pick an operator to light up the result",
   "html": '''    <div class="scroll"><svg class="diagram narrow" id="vnSvg" viewBox="0 0 560 260" style="min-width:520px;max-width:600px;margin:0 auto;display:block" role="img" aria-label="Venn diagram of clinic A and clinic B patients">
      <path id="vnL" class="vn-reg" d=""></path><path id="vnM" class="vn-reg" d=""></path><path id="vnR" class="vn-reg" d=""></path>
      <circle cx="220" cy="135" r="105" class="vn-c"></circle><circle cx="340" cy="135" r="105" class="vn-c"></circle>
      <text x="150" y="26" class="vn-t">clinic_a</text><text x="370" y="26" class="vn-t">clinic_b</text>
      <text x="165" y="115" class="vn-n">Asha</text><text x="160" y="160" class="vn-n">Meera</text>
      <text x="280" y="115" class="vn-n" style="text-anchor:middle">Ravi</text><text x="280" y="160" class="vn-n" style="text-anchor:middle">John</text>
      <text x="370" y="140" class="vn-n">Lina</text>
    </svg></div>
    <div class="seg" id="vnSeg" role="group" aria-label="Set operator"><button type="button" data-v="&amp;" aria-pressed="false">a &amp; b</button><button type="button" data-v="|" aria-pressed="false">a | b</button><button type="button" data-v="-" aria-pressed="false">a - b</button><button type="button" data-v="^" aria-pressed="false">a ^ b</button></div>
    <p class="status-line" id="vnStatus">clinic_a = {"Asha", "Ravi", "Meera", "John"} · clinic_b = {"Ravi", "John", "Lina"}</p>''',
   "js": '''    const RES = __OPS__;
    const NAME = { '&': 'intersection: in both', '|': 'union: in either', '-': 'difference: in a but not b', '^': 'symmetric difference: in exactly one' };
    // left-only crescent, lens, right-only crescent (circles r=105 at x=220 and 340, y=135)
    const yTop = 135 - Math.sqrt(105 * 105 - 60 * 60), yBot = 135 + Math.sqrt(105 * 105 - 60 * 60);
    $('vnL').setAttribute('d', `M280 ${yTop} A105 105 0 1 0 280 ${yBot} A105 105 0 0 1 280 ${yTop}Z`);
    $('vnM').setAttribute('d', `M280 ${yTop} A105 105 0 0 0 280 ${yBot} A105 105 0 0 0 280 ${yTop}Z`);
    $('vnR').setAttribute('d', `M280 ${yTop} A105 105 0 1 1 280 ${yBot} A105 105 0 0 0 280 ${yTop}Z`);
    const ON = { '&': ['vnM'], '|': ['vnL', 'vnM', 'vnR'], '-': ['vnL'], '^': ['vnL', 'vnR'] };
    K.seg($('vnSeg'), v => {
      ['vnL', 'vnM', 'vnR'].forEach(id => $(id).classList.toggle('on', ON[v].includes(id)));
      $('vnStatus').innerHTML = `<span class="mono">sorted(clinic_a ${v.replace('&', '&amp;')} clinic_b)</span> → <b class="mono">${JSON.stringify(RES[v]).replace(/"/g, "'").replace(/,/g, ', ')}</b> · ${NAME[v]}`;
    });'''.replace('__OPS__', json.dumps(OPS))}
 ],
 "extra_traces": {},
 "style": '''  .lb-list { display: flex; flex-wrap: wrap; gap: 0; min-height: 64px; }
  .lb-cell { border: 1.5px solid var(--line); margin-left: -1.5px; min-width: 56px; text-align: center; background: var(--panel-2); padding: 8px 6px 4px; display: grid; }
  .lb-cell b { font-family: var(--mono); font-size: 20px; }
  .lb-cell span { font-family: var(--mono); font-size: 11px; color: var(--muted); }
  .lb-cell.chg { animation: lbpop .35s ease-out; border-color: var(--cyan); }
  @keyframes lbpop { from { transform: translateY(-6px); opacity: .3; } to { transform: none; opacity: 1; } }
  .vn-c { fill: none; stroke: var(--fg-soft); stroke-width: 2; }
  .vn-reg { fill: transparent; transition: fill .3s; }
  .vn-reg.on { fill: var(--teal-wash); }
  .vn-t { font-family: var(--mono); font-size: 15px; fill: var(--accent-text); }
  .vn-n { font-family: var(--mono); font-size: 15px; fill: var(--fg); }''',
 "cheat": [
  ["Ordered items you'll add to or change", "<b>list</b>"],
  ["A fixed record / return several values", "<b>tuple</b> and unpacking"],
  ["Remove duplicates or fast \"is it in there?\"", "<b>set</b> (<span class=\"mono\">x in s</span>)"],
  ["Look up by a name or id", "<b>dict</b>; <span class=\"mono\">d.get(k, default)</span> when the key may be missing"],
  ["Copy, don't alias", "<span class=\"mono\">b = a.copy()</span> or <span class=\"mono\">a[:]</span> (shallow)"],
  ["Last item", "<span class=\"mono\">items[-1]</span>"],
  ["Counting things", "<span class=\"mono\">d[k] = d.get(k, 0) + 1</span> or <span class=\"mono\">collections.Counter</span>"]
 ],
 "ref_title": "Reference: the four at a glance",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th></th><th>list</th><th>tuple</th><th>set</th><th>dict</th></tr></thead>
        <tbody>
          <tr><td>Literal</td><td class="mono">[1, 2]</td><td class="mono">(1, 2) or 1, 2</td><td class="mono">{1, 2}</td><td class="mono">{"a": 1}</td></tr>
          <tr><td>Empty</td><td class="mono">[]</td><td class="mono">()</td><td class="mono">set()</td><td class="mono">{}</td></tr>
          <tr><td>Ordered</td><td>yes</td><td>yes</td><td>no</td><td>insertion order</td></tr>
          <tr><td>Changeable</td><td>yes</td><td>no</td><td>yes</td><td>yes</td></tr>
          <tr><td>Duplicates</td><td>yes</td><td>yes</td><td>no</td><td>keys unique</td></tr>
          <tr><td>Access</td><td class="mono">x[0]</td><td class="mono">x[0]</td><td class="mono">in</td><td class="mono">x["key"]</td></tr>
          <tr><td>Add</td><td class="mono">append insert extend</td><td>—</td><td class="mono">add update</td><td class="mono">d[k] = v, update</td></tr>
          <tr><td>Remove</td><td class="mono">pop remove del</td><td>—</td><td class="mono">remove discard</td><td class="mono">pop del</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Corrected", "<b>remove() comment in Collections.py:</b> <span class=\"mono\">employee_ages.remove(12)  # Remove the age we just added</span>, but the line before appended <b>100</b>. <span class=\"mono\">remove(12)</span> deletes the first 12 in the list."],
  ["Corrected", "<b>Tuple_exercises.py:</b> the comment says <span class=\"mono\">(10.4)</span> without a comma \"is just an integer\". It's a <b>float</b>: parentheses don't change the type, they just group."],
  ["Corrected", "<b>Lists_exercises.py</b> imports <span class=\"mono\">indexOf</span> from <span class=\"mono\">operator</span> and an unused <span class=\"mono\">math</span>. The normal way is <span class=\"mono\">fruits.index(\"orange\")</span>, or <span class=\"mono\">enumerate()</span> while looping. The \"5 favourite movies\" list has 4 items."],
  ["Added", "<b>Keys must be hashable:</b> str, int, tuple work as dict keys and set items; lists and dicts don't (<span class=\"mono\">TypeError: unhashable type: 'list'</span>)."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">nums = [3, 1, 2]; print(sorted(nums), nums)</span>", "code": "nums = [3, 1, 2]; print(sorted(nums), nums)", "expect": "[1, 2, 3] [3, 1, 2]", "a": "<b class=\"mono\">[1, 2, 3] [3, 1, 2]</b>. sorted() returns a new list; nums is unchanged."},
  {"q": "<span class=\"mono\">print(len({1, 1, 2, 2, 3}))</span>", "code": "print(len({1, 1, 2, 2, 3}))", "expect": "3", "a": "<b class=\"mono\">3</b>. Duplicates are dropped."},
  {"q": "<span class=\"mono\">a = [1, 2]; b = a; b.append(3); print(a)</span>", "code": "a = [1, 2]; b = a; b.append(3); print(a)", "expect": "[1, 2, 3]", "a": "<b class=\"mono\">[1, 2, 3]</b>. a and b are two names for one list (see Variables &amp; objects)."},
  {"q": "<span class=\"mono\">d = {\"x\": 1}; print(\"x\" in d, 1 in d)</span>", "code": 'd = {"x": 1}; print("x" in d, 1 in d)', "expect": "True False", "a": "<b class=\"mono\">True False</b>. <span class=\"mono\">in</span> on a dict checks <b>keys</b>, not values."},
  {"q": "<span class=\"mono\">t = (1, [2]); t[1].append(3); print(t)</span>", "code": "t = (1, [2]); t[1].append(3); print(t)", "expect": "(1, [2, 3])", "a": "<b class=\"mono\">(1, [2, 3])</b>. The tuple can't change which objects it holds, but the list inside is still mutable."},
  {"q": "<span class=\"mono\">print(list({\"b\": 1, \"a\": 2}))</span>", "code": 'print(list({"b": 1, "a": 2}))', "expect": "['b', 'a']", "a": "<b class=\"mono\">['b', 'a']</b>. Turning a dict into a list gives its keys, in insertion order."}
 ],
 "sources": "Sources: Python_Fundamentals repo (Basics/Collections.py, PractiseArea/Lists_exercises.py, PractiseArea/Tuple_exercises.py)."
}
