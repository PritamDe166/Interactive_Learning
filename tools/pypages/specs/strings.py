import json
WORD = "Cardiology"
IDX = [None] + list(range(-11, 12))
STEPS = [None, 1, 2, 3, -1, -2]
SL = {}
for a in IDX:
    for b in IDX:
        for c in STEPS:
            SL[f"{a}|{b}|{c}"] = WORD[a:b:c]
S0 = "  Asha Rao, Pune  "
METHODS = [
 ("upper()", "s.upper()"), ("lower()", "s.lower()"), ("title()", "s.title()"), ("strip()", "s.strip()"),
 ("split(\",\")", "s.split(',')"), ("split()", "s.split()"), ("replace(\"Pune\", \"Delhi\")", "s.replace('Pune', 'Delhi')"),
 ("find(\"Rao\")", "s.find('Rao')"), ("find(\"Xyz\")", "s.find('Xyz')"), ("count(\"a\")", "s.count('a')"),
 ("startswith(\"Asha\")", "s.startswith('Asha')"), ("strip().startswith(\"Asha\")", "s.strip().startswith('Asha')"),
 ("isdigit()", "s.isdigit()"), ("center(24, \"*\")", "s.strip().center(24, '*')"),
]
MT = []
for label, expr in METHODS:
    r = eval(expr, {"s": S0})
    MT.append({"label": label, "expr": expr.replace("'", '"'), "r": repr(r), "t": type(r).__name__})

SPEC = {
 "slug": "strings", "num": 3, "part": "Values and text",
 "title": "Strings in depth", "title_plain": "Strings in depth",
 "desc": "Python fundamentals: string indexing with positive and negative positions, slicing with start:stop:step, common methods, and why strings are immutable.",
 "lede": [
  "A <b>str</b> is an ordered sequence of characters. Each one has a position: <b>0</b> from the left, <b>-1</b> from the right.",
  "<b>Slicing</b> <span class=\"mono\">s[start:stop:step]</span> copies a part; <b>stop is excluded</b> and missing values mean \"from the start\" / \"to the end\".",
  "Strings are <b>immutable</b>: methods like <span class=\"mono\">upper()</span>, <span class=\"mono\">strip()</span> and <span class=\"mono\">replace()</span> return a <b>new</b> string and leave the original alone.",
  "<span class=\"mono\">split()</span> turns text into a list; <span class=\"mono\">\"sep\".join(list)</span> turns a list back into text."
 ],
 "walk": {"title": "cleaning a department name", "code":
'''raw = "  cardiology  "
dept = raw.strip().title()
print(dept[0], dept[-1])
print(dept[0:6], dept[6:])
print(dept[::-1])
print(len(dept), "logy" in dept)
upper = dept.upper()
print(dept, upper)
parts = "Asha,35,Pune".split(",")
print(parts)
line = " | ".join(parts)
print(line)
print(dept.find("x"), dept.replace("Cardio", "Neuro"))''',
 "steps": [
  {"at": {"after": 1}, "title": "Text with untidy spaces", "text": "A string arriving from a form often has stray spaces. <span class=\"mono\">raw</span> points to a str object holding them, quotes and all."},
  {"at": {"after": 2}, "title": "Methods return new strings", "text": "<span class=\"mono\">raw.strip()</span> makes a new string without the outer spaces, and <span class=\"mono\">.title()</span> makes another with a capital first letter. Chaining works because each call returns a str. <b>raw is untouched</b>."},
  {"at": {"after": 3}, "title": "Indexing: 0 from the left, -1 from the right", "text": "<span class=\"mono\">dept[0]</span> is <span class=\"mono\">C</span>; <span class=\"mono\">dept[-1]</span> is the last character, <span class=\"mono\">y</span>. Negative indexes count back from the end, so you never need <span class=\"mono\">len(dept) - 1</span>."},
  {"at": {"after": 4}, "title": "Slicing: stop is excluded", "text": "<span class=\"mono\">dept[0:6]</span> takes positions 0 to 5 → <span class=\"mono\">Cardio</span>. <span class=\"mono\">dept[6:]</span> runs from 6 to the end → <span class=\"mono\">logy</span>. The two halves always join back into the original.", "tip": "Think of the indexes as <b>gaps between characters</b>: the slice cuts at gap 0 and gap 6."},
  {"at": {"after": 5}, "title": "A step of -1 reverses", "text": "The third number is the <b>step</b>. <span class=\"mono\">[::-1]</span> walks from the end to the start: <span class=\"mono\">ygoloidraC</span>."},
  {"at": {"after": 6}, "title": "len() and the in operator", "text": "<span class=\"mono\">len()</span> counts characters (10). <span class=\"mono\">\"logy\" in dept</span> checks for a <b>substring</b> and returns a bool."},
  {"at": {"after": 8}, "title": "Immutable: the original stays", "text": "<span class=\"mono\">upper()</span> created a second object. <span class=\"mono\">dept</span> still points to <span class=\"mono\">'Cardiology'</span>. To \"change\" a string you rebind the name: <span class=\"mono\">dept = dept.upper()</span>."},
  {"at": {"after": 10}, "title": "split() → a list", "text": "<span class=\"mono\">split(\",\")</span> cuts at every comma and returns a <b>list of strings</b>. Note <span class=\"mono\">'35'</span> is still text: convert with <span class=\"mono\">int()</span> if you need a number."},
  {"at": {"after": 12}, "title": "join() glues a list together", "text": "<span class=\"mono\">\" | \".join(parts)</span> is called <b>on the separator</b>, with the list as the argument. It is the reverse of split()."},
  {"at": "end", "title": "find() and replace()", "text": "<span class=\"mono\">find()</span> returns the position, or <b>-1</b> when not found (<span class=\"mono\">index()</span> would raise an error instead). <span class=\"mono\">replace()</span> returns a new string with every match swapped."}
 ]},
 "walk_out": "C y / Cardio logy / ygoloidraC / 10 True / Cardiology CARDIOLOGY / ['Asha', '35', 'Pune'] / Asha | 35 | Pune / -1 Neurology",
 "puzzles": [
  {"id": "p1", "name": "1 · slice ends", "code": 's = "Hyderabad"\nprint(s[2:5], s[-3:])', "q": "What's printed?", "opts": ["der bad", "dera bad", "der abad"], "a": 0,
   "why": "<span class=\"mono\">[2:5]</span> takes positions 2, 3, 4 (stop excluded) → <span class=\"mono\">der</span>. <span class=\"mono\">[-3:]</span> is the last three → <span class=\"mono\">bad</span>."},
  {"id": "p2", "name": "2 · change a letter", "code": 'name = "asha"\nname[0] = "A"\nprint(name)', "q": "What happens?", "opts": ["Asha", "TypeError: 'str' object does not support item assignment", "asha"], "a": 1,
   "why": "Strings are immutable. Build a new one instead: <span class=\"mono\">name = \"A\" + name[1:]</span> or <span class=\"mono\">name.capitalize()</span>."},
  {"id": "p3", "name": "3 · method without rebinding", "code": 'city = "pune"\ncity.upper()\nprint(city)', "q": "What's printed?", "opts": ["PUNE", "pune", "None"], "a": 1,
   "why": "<span class=\"mono\">upper()</span> returned a new string, but nothing kept it. <span class=\"mono\">city</span> still points to the original. Write <span class=\"mono\">city = city.upper()</span>."},
  {"id": "p4", "name": "4 · out of range", "code": 's = "Pune"\nprint(s[1:99])\nprint(s[99])', "q": "What's printed?", "opts": ["une / IndexError: string index out of range", "IndexError: string index out of range", "une / (empty line)"], "a": 0,
   "why": "Slices are forgiving: a stop past the end just stops at the end. A single index past the end raises <b>IndexError</b>."},
  {"id": "p5", "name": "5 · split with no argument", "code": 'msg = "  book   2   slots "\nprint(msg.split())\nprint(msg.split(" ")[:3])', "q": "What's printed?", "opts": ["['book', '2', 'slots'] / ['', '', 'book']", "['book', '2', 'slots'] / ['book', '2', 'slots']", "['', 'book', '2', 'slots'] / ['', '', 'book']"], "a": 0,
   "why": "<span class=\"mono\">split()</span> with no argument splits on any run of whitespace and drops empty pieces. <span class=\"mono\">split(\" \")</span> cuts at every single space, so you get empty strings."},
  {"id": "p6", "name": "6 · join numbers", "code": 'ids = [101, 102]\nprint(", ".join(ids))', "q": "What happens?", "opts": ["101, 102", "TypeError: sequence item 0: expected str instance, int found", "[101, 102]"], "a": 1,
   "why": "join() only accepts strings. Convert first: <span class=\"mono\">\", \".join(str(i) for i in ids)</span>."}
 ],
 "runner_extra": [{"label": "Your turn: initials and a masked phone", "code": 'full_name = "asha kumari rao"\nphone = "9876543210"\ninitials = "".join(part[0] for part in full_name.split()).upper()\nmasked = "*" * (len(phone) - 4) + phone[-4:]\nprint(initials, masked)\n# Try: print the surname only, or the phone in groups of 5'}],
 "custom": [
  {"id": "ruler", "title": "Slice ruler", "kind": "Move start, stop and step · the result comes from real Python slicing",
   "html": '''    <div class="scroll"><svg class="diagram narrow" id="rulerSvg" viewBox="0 0 640 200" style="min-width:520px" role="img" aria-label="Index ruler for the word Cardiology"></svg></div>
    <div class="two" style="margin-top:8px">
      <div class="card"><label class="label" for="rStart">start <span class="mono" id="rStartV"></span></label><input type="range" id="rStart" min="-11" max="11" value="-11" style="width:100%"></div>
      <div class="card"><label class="label" for="rStop">stop <span class="mono" id="rStopV"></span></label><input type="range" id="rStop" min="-11" max="11" value="11" style="width:100%"></div>
    </div>
    <div class="chip-group"><div class="label">step</div><div class="seg" id="rStep" role="group" aria-label="step"><button type="button" data-v="" aria-pressed="true">(none)</button><button type="button" data-v="2" aria-pressed="false">2</button><button type="button" data-v="3" aria-pressed="false">3</button><button type="button" data-v="-1" aria-pressed="false">-1</button><button type="button" data-v="-2" aria-pressed="false">-2</button></div></div>
    <div class="chips" style="margin-top:6px"><button class="chip-btn" type="button" data-p="0|6|">first 6</button><button class="chip-btn" type="button" data-p="-4||">last 4</button><button class="chip-btn" type="button" data-p="||-1">reverse</button><button class="chip-btn" type="button" data-p="||2">every 2nd</button><button class="chip-btn" type="button" data-p="6|2|">start after stop</button></div>
    <p class="status-line" id="rStatus" style="font-size:16px"></p>''',
   "js": '''    const SL = __SL__, W = "__W__";
    const svg = $('rulerSvg'); const ns = 'http://www.w3.org/2000/svg';
    const cw = 52, x0 = 60, y0 = 70;
    let a = null, b = null, c = null;
    function mk(tag, attrs, txt) { const e = document.createElementNS(ns, tag); for (const k in attrs) e.setAttribute(k, attrs[k]); if (txt != null) e.textContent = txt; svg.appendChild(e); return e; }
    function draw() {
      svg.innerHTML = '';
      const key = `${a}|${b}|${c}`.replace(/null/g, 'None');
      const res = SL[key];
      // which indexes are picked
      const n = W.length, step = c == null ? 1 : c;
      const norm = (v, def) => v == null ? def : (v < 0 ? Math.max(v + n, step < 0 ? -1 : 0) : Math.min(v, step < 0 ? n - 1 : n));
      const s0 = norm(a, step > 0 ? 0 : n - 1), s1 = norm(b, step > 0 ? n : -1);
      const picked = [];
      for (let i = s0; step > 0 ? i < s1 : i > s1; i += step) picked.push(i);
      for (let i = 0; i < n; i++) {
        const on = picked.includes(i);
        mk('rect', { x: x0 + i * cw, y: y0, width: cw - 4, height: 48, rx: 8, class: 'ruler-cell' + (on ? ' on' : '') });
        const t = mk('text', { x: x0 + i * cw + (cw - 4) / 2, y: y0 + 31, class: 'ruler-ch' + (on ? ' on' : '') }, W[i]); t.style.textAnchor = 'middle';
        const p = mk('text', { x: x0 + i * cw + (cw - 4) / 2, y: y0 - 12, class: 'ruler-ix' }, i); p.style.textAnchor = 'middle';
        const q = mk('text', { x: x0 + i * cw + (cw - 4) / 2, y: y0 + 70, class: 'ruler-ix neg' }, i - n); q.style.textAnchor = 'middle';
      }
      const lbl1 = mk('text', { x: 4, y: y0 - 12, class: 'ruler-ix' }, 'index'); const lbl2 = mk('text', { x: 4, y: y0 + 70, class: 'ruler-ix neg' }, 'from end');
      picked.forEach((i, k) => { const o = mk('text', { x: x0 + i * cw + (cw - 4) / 2, y: y0 + 98, class: 'ruler-ord' }, k + 1); o.style.textAnchor = 'middle'; });
      const code = `"${W}"[${a ?? ''}:${b ?? ''}${c == null ? '' : ':' + c}]`;
      $('rStatus').innerHTML = `<span class="mono">${code}</span> → <b class="mono">${JSON.stringify(res)}</b>` + (res === '' ? ' · empty: with a positive step, start must be left of stop.' : (step < 0 ? ' · negative step walks right to left; the numbers under the cells show the order.' : ''));
      $('rStartV').textContent = a ?? '(none)'; $('rStopV').textContent = b ?? '(none)';
    }
    const rv = el => { const v = +el.value; return (el.id === 'rStart' && v === -11) || (el.id === 'rStop' && v === 11) ? null : v; };
    $('rStart').addEventListener('input', e => { a = rv(e.target); draw(); });
    $('rStop').addEventListener('input', e => { b = rv(e.target); draw(); });
    K.seg($('rStep'), v => { c = v === '' ? null : +v; draw(); });
    document.querySelectorAll('[data-p]').forEach(btn => btn.addEventListener('click', () => {
      const [x, y, z] = btn.dataset.p.split('|').map(s => s === '' ? null : +s);
      a = x; b = y; c = z;
      $('rStart').value = a ?? -11; $('rStop').value = b ?? 11;
      $('rStep').querySelectorAll('button').forEach(bb => bb.setAttribute('aria-pressed', String(bb.dataset.v === (c == null ? '' : String(c)))));
      draw();
    }));
    draw();'''.replace('__SL__', json.dumps(SL)).replace('__W__', WORD)},
  {"id": "meth", "title": "Method bench", "kind": "Call a method · the original string never changes",
   "html": '''    <div class="card" style="margin-bottom:10px"><div class="label">s (· = space)</div><div class="mono" style="font-size:18px" id="mOrig"></div></div>
    <div class="chips" id="mBtns"></div>
    <div class="card" style="margin-top:10px"><div class="label">Result (· = space)</div><pre class="codeblock" id="mCode" style="min-height:0;margin:0 0 8px"></pre><div class="mono" style="font-size:18px;overflow-wrap:anywhere" id="mRes"></div></div>
    <p class="status-line" id="mStatus"></p>''',
   "js": '''    const MT = __MT__, S0 = __S0__;
    const vis = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/ /g, '<span class="sp">·</span>');
    $('mOrig').innerHTML = vis(JSON.stringify(S0));
    $('mBtns').innerHTML = MT.map((m, i) => `<button class="chip-btn" type="button" data-i="${i}" aria-pressed="false">.${m.label}</button>`).join('');
    $('mBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      $('mBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      const m = MT[+b.dataset.i];
      $('mCode').innerHTML = `<span class="ln">${K.pyHighlight('print(' + m.expr + ')')}</span>`;
      $('mRes').innerHTML = vis(m.r) + ` <span class="muted">(${m.t})</span>`;
      $('mOrig').innerHTML = vis(JSON.stringify(S0));
      $('mOrig').parentElement.classList.remove('flash'); void $('mOrig').offsetWidth; $('mOrig').parentElement.classList.add('flash');
      $('mStatus').innerHTML = m.t === 'str' ? 'A <b>new</b> str came back. <span class="mono">s</span> above is unchanged.' : m.t === 'list' ? 'split() returns a <b>list</b> of new strings.' : `This method answers a question, so it returns a <b>${m.t}</b>.`;
    }));
    $('mBtns').querySelector('button').click();'''.replace('__MT__', json.dumps(MT)).replace('__S0__', json.dumps(S0))}
 ],
 "style": '''  .ruler-cell { fill: var(--panel-2); stroke: var(--line); }
  .ruler-cell.on { fill: var(--teal-wash); stroke: var(--cyan); stroke-width: 2; }
  .ruler-ch { font-family: var(--mono); font-size: 22px; fill: var(--muted); }
  .ruler-ch.on { fill: var(--fg); font-weight: 700; }
  .ruler-ix { font-family: var(--mono); font-size: 13px; fill: var(--accent-text); }
  .ruler-ix.neg { fill: var(--cyan); }
  .ruler-ord { font-family: var(--mono); font-size: 12px; fill: var(--muted); }
  #mOrig .sp, #mRes .sp { color: var(--muted); }
  .card.flash { animation: flash .6s ease-out; }
  @keyframes flash { from { box-shadow: 0 0 0 3px var(--cyan); } to { box-shadow: 0 0 0 0 transparent; } }''',
 "cheat": [
  ["First / last character", "<span class=\"mono\">s[0]</span> / <span class=\"mono\">s[-1]</span>"],
  ["First n / last n", "<span class=\"mono\">s[:n]</span> / <span class=\"mono\">s[-n:]</span>"],
  ["Reverse", "<span class=\"mono\">s[::-1]</span>"],
  ["A method \"didn't work\"", "Strings are immutable: assign the result, <span class=\"mono\">s = s.strip()</span>"],
  ["Text → list → text", "<span class=\"mono\">s.split(\",\")</span> and <span class=\"mono\">\", \".join(items)</span>"],
  ["Is it there? Where?", "<span class=\"mono\">\"x\" in s</span>; <span class=\"mono\">s.find(\"x\")</span> (-1 if missing)"],
  ["Building a long string in a loop", "Collect pieces in a list, then <span class=\"mono\">\"\".join(pieces)</span>"]
 ],
 "ref_title": "Reference: everyday string methods",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Method</th><th>Returns</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td class="mono">strip() lstrip() rstrip()</td><td>str without outer whitespace (or given chars)</td><td class="mono">" a ".strip() → 'a'</td></tr>
          <tr><td class="mono">lower() upper() title() capitalize()</td><td>str with changed case</td><td class="mono">"asha rao".title() → 'Asha Rao'</td></tr>
          <tr><td class="mono">split(sep) / sep.join(list)</td><td>list / str</td><td class="mono">"a,b".split(",") → ['a', 'b']</td></tr>
          <tr><td class="mono">replace(old, new)</td><td>str with every match replaced</td><td class="mono">"a-b-c".replace("-", "") → 'abc'</td></tr>
          <tr><td class="mono">find(x) / index(x)</td><td>position; -1 / ValueError when missing</td><td class="mono">"pune".find("n") → 2</td></tr>
          <tr><td class="mono">count(x)</td><td>number of non-overlapping matches</td><td class="mono">"banana".count("a") → 3</td></tr>
          <tr><td class="mono">startswith(x) endswith(x)</td><td>bool (accepts a tuple of options)</td><td class="mono">f.endswith((".csv", ".json"))</td></tr>
          <tr><td class="mono">isdigit() isalpha() isspace()</td><td>bool</td><td class="mono">"42".isdigit() → True</td></tr>
          <tr><td class="mono">removeprefix() removesuffix()</td><td>str (3.9+)</td><td class="mono">"Dr. Rao".removeprefix("Dr. ") → 'Rao'</td></tr>
          <tr><td class="mono">zfill(n) center(n) ljust(n) rjust(n)</td><td>padded str</td><td class="mono">"7".zfill(3) → '007'</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Added", "<b>Why this page exists:</b> the repo uses strings everywhere but has no file on slicing or methods. These are among the most-used Python skills, so this is a gap topic."],
  ["Added", "<b>strip() removes characters, not a word.</b> <span class=\"mono\">\"report.csv\".strip(\".csv\")</span> gives <span class=\"mono\">'report'</span> by luck but <span class=\"mono\">\"vacs.csv\".strip(\".csv\")</span> gives <span class=\"mono\">''</span>. Use <span class=\"mono\">removesuffix(\".csv\")</span>."],
  ["Added", "<b>Comparing text from users:</b> normalise first with <span class=\"mono\">s.strip().lower()</span> (or <span class=\"mono\">casefold()</span> for non-English text) before using <span class=\"mono\">==</span>."],
  ["Added", "<b>Multi-line strings</b> use triple quotes <span class=\"mono\">\"\"\"...\"\"\"</span>; the newlines are part of the value. Adjacent literals join automatically: <span class=\"mono\">\"ab\" \"cd\"</span> is <span class=\"mono\">'abcd'</span>."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">print(\"Python\"[1:4])</span>", "code": 'print("Python"[1:4])', "expect": "yth", "a": "<b class=\"mono\">yth</b>. Positions 1, 2, 3; stop 4 is excluded."},
  {"q": "<span class=\"mono\">print(\"Python\"[-2:])</span>", "code": 'print("Python"[-2:])', "expect": "on", "a": "<b class=\"mono\">on</b>. From the second-last to the end."},
  {"q": "<span class=\"mono\">s = \"hi\"; t = s.upper(); print(s, t)</span>", "code": 's = "hi"; t = s.upper(); print(s, t)', "expect": "hi HI", "a": "<b class=\"mono\">hi HI</b>. upper() returns a new string; s is unchanged."},
  {"q": "<span class=\"mono\">print(\"-\".join(\"abc\"))</span>", "code": 'print("-".join("abc"))', "expect": "a-b-c", "a": "<b class=\"mono\">a-b-c</b>. A string is itself a sequence of one-character strings."},
  {"q": "<span class=\"mono\">print(\"banana\".find(\"an\"), \"banana\".count(\"an\"))</span>", "code": 'print("banana".find("an"), "banana".count("an"))', "expect": "1 2", "a": "<b class=\"mono\">1 2</b>. First match at position 1; two non-overlapping matches."},
  {"q": "<span class=\"mono\">print(\"a,b,,c\".split(\",\"))</span>", "code": 'print("a,b,,c".split(","))', "expect": "['a', 'b', '', 'c']", "a": "<b class=\"mono\">['a', 'b', '', 'c']</b>. Two commas in a row produce an empty string between them."}
 ],
 "sources": "Gap topic: not in the Python_Fundamentals repo; added because slicing and string methods are core skills (Python docs: Text Sequence Type)."
}
