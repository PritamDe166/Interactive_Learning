import json
PYVALS = [
 ('{"name": "Asha", "age": 35}', {"name": "Asha", "age": 35}),
 ('{"active": True, "phone": None}', {"active": True, "phone": None}),
 ('{"slot": (9, 30)}', {"slot": (9, 30)}),
 ('{1: "one", 2: "two"}', {1: "one", 2: "two"}),
 ('{"fee": 450.5, "tags": ["new", "vip"]}', {"fee": 450.5, "tags": ["new", "vip"]}),
 ('{"name": "Zoë"}', {"name": "Zoë"}),
]
JS = []
for src, v in PYVALS:
    d = json.dumps(v)
    JS.append({"py": src, "json": d, "back": repr(json.loads(d))})
JS.append({"py": '{"ids": {1, 2}}', "json": "TypeError: Object of type set is not JSON serializable", "back": ""})
try:
    json.dumps({"ids": {1, 2}})
except TypeError as e:
    assert str(e) == "Object of type set is not JSON serializable", e

SPEC = {
 "slug": "files-csv-json", "num": 11, "part": "Real programs",
 "title": "Files, CSV &amp; JSON", "title_plain": "Files, CSV & JSON",
 "desc": "Python fundamentals: open() modes, the with statement, reading line by line, csv.reader and DictReader, csv.writer, and converting between Python objects and JSON.",
 "lede": [
  "<span class=\"mono\">open(path, mode)</span> returns a <b>file object</b>. Mode <b>\"r\"</b> reads, <b>\"w\"</b> <b>erases</b> then writes, <b>\"a\"</b> appends to the end.",
  "Always use <span class=\"mono\">with open(...) as f:</span>. The file is <b>closed automatically</b> when the block ends, even after an error.",
  "Pass <span class=\"mono\">encoding=\"utf-8\"</span>, and <span class=\"mono\">newline=\"\"</span> for CSV files.",
  "<b>csv.DictReader</b> turns each row into a dict keyed by the header. Values are always <b>strings</b>.",
  "<b>json</b>: <span class=\"mono\">dump/load</span> work with files, <span class=\"mono\">dumps/loads</span> with strings (the s is for string)."
 ],
 "walk": {"title": "a day's appointments on disk", "code":
'''import csv, json
with open("notes.txt", "w", encoding="utf-8") as f:
    f.write("Asha 9:00\\n")
    f.write("Ravi 9:30\\n")
with open("notes.txt", "a", encoding="utf-8") as f:
    f.write("Meera 10:00\\n")
with open("notes.txt", encoding="utf-8") as f:
    for line in f:
        print(line.strip())
with open("visits.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerows([["name", "fee"], ["Asha", "450"], ["Ravi", "800"]])
with open("visits.csv", newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
print(rows[0], sum(int(r["fee"]) for r in rows))
text = json.dumps({"clinic": "Pune", "visits": rows})
data = json.loads(text)
print(data["visits"][1]["name"], type(text).__name__)''',
 "steps": [
  {"at": {"after": 2}, "title": "open in \"w\" mode", "text": "<span class=\"mono\">\"w\"</span> creates <span class=\"mono\">notes.txt</span>, or <b>empties it</b> if it already exists. <span class=\"mono\">f</span> is the file object; <span class=\"mono\">with</span> will close it for us."},
  {"at": {"after": 4}, "title": "write() doesn't add newlines", "text": "Each <span class=\"mono\">write</span> appends text at the cursor. You add <span class=\"mono\">\\n</span> yourself; print() adds it for you, write() never does."},
  {"at": {"after": 6}, "title": "The with block ended: file closed", "text": "Leaving the block closed the first file. Reopening with <span class=\"mono\">\"a\"</span> puts the cursor at the <b>end</b>, so Meera is added after the existing lines."},
  {"at": {"after": 9, "n": 3}, "title": "Read line by line", "text": "Looping over a file gives one line at a time, <b>including</b> its <span class=\"mono\">\\n</span>, so <span class=\"mono\">strip()</span> removes it. This uses little memory even for huge files.", "tip": "<span class=\"mono\">f.read()</span> gives the whole file as one string; <span class=\"mono\">f.readlines()</span> a list of lines."},
  {"at": {"after": 12}, "title": "csv.writer writes rows", "text": "<span class=\"mono\">writerows</span> takes a list of lists and handles commas and quoting for you. <span class=\"mono\">newline=\"\"</span> stops blank lines appearing between rows on Windows."},
  {"at": {"after": 14}, "title": "DictReader: rows become dicts", "text": "<span class=\"mono\">DictReader</span> uses the first row as keys. <span class=\"mono\">rows</span> is now a list of dicts, one per patient. Notice <span class=\"mono\">'450'</span> is a <b>string</b>: CSV has no types."},
  {"at": {"after": 15}, "title": "Convert before doing maths", "text": "<span class=\"mono\">int(r[\"fee\"])</span> converts each fee; the generator expression feeds sum(): 1250."},
  {"at": {"after": 16}, "title": "json.dumps: Python → JSON text", "text": "<span class=\"mono\">dumps</span> turns dicts and lists into one <b>string</b> of JSON, ready to save or send to an API. <span class=\"mono\">json.dump(obj, f)</span> writes it straight to a file."},
  {"at": "end", "title": "json.loads: JSON text → Python", "text": "<span class=\"mono\">loads</span> parses the string back into new dicts and lists, so you can index into it: <span class=\"mono\">data[\"visits\"][1][\"name\"]</span> → Ravi."}
 ]},
 "walk_out": "Asha 9:00 / Ravi 9:30 / Meera 10:00 / {'name': 'Asha', 'fee': '450'} 1250 / Ravi str",
 "puzzles": [
  {"id": "p1", "name": "1 · \"w\" twice", "code": "with open(\"log.txt\", \"w\") as f:\n    f.write(\"one\\n\")\nwith open(\"log.txt\", \"w\") as f:\n    f.write(\"two\\n\")\nwith open(\"log.txt\") as f:\n    print(f.read().strip())", "q": "What's printed?", "opts": ["one / two", "two", "one"], "a": 1,
   "why": "Each <span class=\"mono\">\"w\"</span> open empties the file first. Use <span class=\"mono\">\"a\"</span> to keep what's there."},
  {"id": "p2", "name": "2 · write without newline", "code": "with open(\"a.txt\", \"w\") as f:\n    f.write(\"Asha\")\n    f.write(\"Ravi\")\nwith open(\"a.txt\") as f:\n    print(f.readlines())", "q": "What's printed?", "opts": ["['Asha', 'Ravi']", "['AshaRavi']", "['Asha\\n', 'Ravi\\n']"], "a": 1,
   "why": "write() writes exactly what you give it. Without <span class=\"mono\">\\n</span> it's all one line."},
  {"id": "p3", "name": "3 · CSV numbers", "code": "import csv, io\nf = io.StringIO(\"name,fee\\nAsha,450\\nRavi,800\\n\")\nrows = list(csv.DictReader(f))\nprint(rows[0][\"fee\"] + rows[1][\"fee\"])", "q": "What's printed?", "opts": ["1250", "450800", "TypeError"], "a": 1,
   "why": "Everything from CSV is a string, so + joins text. Convert with int() first. (<span class=\"mono\">io.StringIO</span> is an in-memory file, handy for testing.)"},
  {"id": "p4", "name": "4 · reading twice", "code": "with open(\"n.txt\", \"w\") as f:\n    f.write(\"x\\ny\\n\")\nwith open(\"n.txt\") as f:\n    print(len(f.read()), len(f.read()))", "q": "What's printed?", "opts": ["4 4", "4 0", "2 0"], "a": 1,
   "why": "The first read() moves the cursor to the end; the second has nothing left. Use <span class=\"mono\">f.seek(0)</span> to rewind."},
  {"id": "p5", "name": "5 · JSON types", "code": "import json\nprint(json.dumps({\"ok\": True, \"phone\": None, \"slot\": (9, 30)}))", "q": "What's printed?", "opts": ["{'ok': True, 'phone': None, 'slot': (9, 30)}", "{\"ok\": true, \"phone\": null, \"slot\": [9, 30]}", "TypeError: tuple is not JSON serializable"], "a": 1,
   "why": "JSON spells them <span class=\"mono\">true</span> and <span class=\"mono\">null</span>, uses double quotes, and has no tuples: they become arrays (lists)."},
  {"id": "p6", "name": "6 · int keys", "code": "import json\nd = json.loads(json.dumps({1: \"one\"}))\nprint(d, 1 in d)", "q": "What's printed?", "opts": ["{1: 'one'} True", "{'1': 'one'} False", "TypeError"], "a": 1,
   "why": "JSON object keys are always strings, so int keys come back as <span class=\"mono\">'1'</span>."}
 ],
 "runner_extra": [{"label": "Your turn: average fee per patient", "code": 'import csv, io\ndata = io.StringIO("name,fee\\nAsha,450\\nRavi,800\\nAsha,300\\n")\ntotals = {}\nfor row in csv.DictReader(data):\n    totals[row["name"]] = totals.get(row["name"], 0) + int(row["fee"])\nprint(totals)\n# Try: write totals to "totals.json" with json.dump, then read it back'}],
 "custom": [
  {"id": "tape", "title": "The file and its cursor", "kind": "Open in a mode, then write or read · watch the contents and the cursor",
   "html": '''    <div class="chips" id="tpBtns">
      <button class="chip-btn mono" type="button" data-a="w">open("notes.txt", "w")</button>
      <button class="chip-btn mono" type="button" data-a="a">open("notes.txt", "a")</button>
      <button class="chip-btn mono" type="button" data-a="r">open("notes.txt", "r")</button>
      <button class="chip-btn mono" type="button" data-a="write">f.write("Ravi\\n")</button>
      <button class="chip-btn mono" type="button" data-a="readline">f.readline()</button>
      <button class="chip-btn mono" type="button" data-a="read">f.read()</button>
      <button class="chip-btn mono" type="button" data-a="close">end of with (close)</button>
    </div>
    <div class="tp-file"><div class="tp-name mono">notes.txt <span id="tpState" class="muted">closed</span></div><div class="tp-tape mono" id="tpTape"></div></div>
    <p class="status-line" id="tpStatus">The file starts with two lines. Open it first.</p>''',
   "js": '''    let content = 'Asha\\nMeera\\n', mode = null, pos = 0;
    const show = () => {
      const chars = [...content];
      $('tpTape').innerHTML = chars.map((c, i) => `${i === pos && mode ? '<span class="tp-cur"></span>' : ''}<span class="tp-ch${c === '\\n' ? ' nl' : ''}">${c === '\\n' ? '\\\\n' : c}</span>`).join('') + (pos >= chars.length && mode ? '<span class="tp-cur"></span>' : '') + (chars.length ? '' : '<span class="muted">(empty file)</span>');
      $('tpState').textContent = mode ? `open in "${mode}" mode · cursor at ${pos}` : 'closed';
    };
    const say = h => { $('tpStatus').innerHTML = h; };
    const lit = s => JSON.stringify(s);
    $('tpBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      const a = b.dataset.a;
      if (['w', 'a', 'r'].includes(a)) {
        if (mode) { say('Close the file first (end the <span class="mono">with</span> block).'); return; }
        mode = a;
        if (a === 'w') { content = ''; pos = 0; say('<b>"w"</b> emptied the file straight away, before writing anything.'); }
        if (a === 'a') { pos = content.length; say('<b>"a"</b> keeps the contents; every write goes to the end.'); }
        if (a === 'r') { pos = 0; say('<b>"r"</b> starts reading at the beginning. Writing is not allowed.'); }
      } else if (!mode) { say('<span class="bad-text">ValueError: I/O operation on closed file.</span> Open it first.'); return; }
      else if (a === 'write') {
        if (mode === 'r') { say('<span class="bad-text">io.UnsupportedOperation: not writable</span> · a file opened with "r" is read-only.'); return; }
        if (mode === 'a') pos = content.length;
        content = content.slice(0, pos) + 'Ravi\\n' + content.slice(pos + 5); pos += 5; say('write() returned <b class="mono">5</b> (characters written). Cursor moved past them.');
      } else if (a === 'readline' || a === 'read') {
        if (mode !== 'r') { say('<span class="bad-text">io.UnsupportedOperation: not readable</span> · open with "r" to read.'); return; }
        let end = a === 'read' ? content.length : (content.indexOf('\\n', pos) < 0 ? content.length : content.indexOf('\\n', pos) + 1);
        const got = content.slice(pos, end); pos = end;
        say(`returned <b class="mono">${lit(got)}</b>` + (got === '' ? ' · empty string: you are at the end of the file.' : a === 'readline' ? ' · one line, including its \\\\n.' : ' · everything from the cursor to the end.'));
      } else if (a === 'close') { mode = null; pos = 0; say('Closed. <span class="mono">with</span> does this automatically, even if an exception happens inside the block.'); }
      show();
    }));
    show();'''},
  {"id": "pj", "title": "Python ⇄ JSON", "kind": "json.dumps then json.loads · results from real Python",
   "html": '''    <div class="scroll card table-card"><table><thead><tr><th>Python object</th><th>json.dumps(obj)</th><th>json.loads(...) back</th></tr></thead><tbody id="pjBody"></tbody></table></div>
    <p class="status-line">Round trips aren't always exact: tuples come back as lists and int keys as strings.</p>''',
   "js": '''    const JS = __JS__;
    const e = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    $('pjBody').innerHTML = JS.map(r => `<tr><td class="mono">${e(r.py)}</td><td class="mono ${r.json.startsWith('TypeError') ? 'bad-text' : ''}">${e(r.json)}</td><td class="mono">${e(r.back) || '—'}</td></tr>`).join('');'''.replace('__JS__', json.dumps(JS, ensure_ascii=False))}
 ],
 "style": '''  .tp-file { margin-top: 12px; border: 1.5px solid var(--line); border-radius: 12px; background: var(--code-bg); padding: 10px 12px; }
  .tp-name { font-size: 13px; color: var(--accent-text); margin-bottom: 8px; }
  .tp-tape { display: flex; flex-wrap: wrap; align-items: center; gap: 2px; min-height: 36px; font-size: 16px; }
  .tp-ch { padding: 3px 5px; border-radius: 4px; background: var(--panel-2); }
  .tp-ch.nl { color: var(--cyan); font-size: 12px; }
  .tp-cur { width: 3px; height: 26px; background: var(--accent-text); border-radius: 2px; animation: blink 1s steps(2) infinite; }
  @keyframes blink { 50% { opacity: .2; } }''',
 "cheat": [
  ["Read a text file", "<span class=\"mono\">with open(p, encoding=\"utf-8\") as f: for line in f:</span>"],
  ["Add to a file without losing it", "Mode <span class=\"mono\">\"a\"</span>; <span class=\"mono\">\"w\"</span> erases"],
  ["CSV with a header row", "<span class=\"mono\">csv.DictReader</span> / <span class=\"mono\">csv.DictWriter</span>, and <span class=\"mono\">newline=\"\"</span>"],
  ["Numbers from CSV", "Convert: <span class=\"mono\">int(row[\"fee\"])</span>"],
  ["Save / load settings or API data", "<span class=\"mono\">json.dump(obj, f, indent=2)</span> / <span class=\"mono\">json.load(f)</span>"],
  ["JSON in a string (e.g. an HTTP body)", "<span class=\"mono\">json.loads(text)</span> / <span class=\"mono\">json.dumps(obj)</span>"],
  ["Paths that work from any folder", "<span class=\"mono\">Path(__file__).parent / \"data\" / \"notes.txt\"</span> (pathlib)"]
 ],
 "ref_title": "Reference: open() modes",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Mode</th><th>If the file exists</th><th>If it doesn't</th><th>Cursor starts</th></tr></thead>
        <tbody>
          <tr><td class="mono">"r"</td><td>read it</td><td>FileNotFoundError</td><td>start</td></tr>
          <tr><td class="mono">"w"</td><td><b>emptied</b>, then write</td><td>created</td><td>start</td></tr>
          <tr><td class="mono">"a"</td><td>kept; writes go to the end</td><td>created</td><td>end</td></tr>
          <tr><td class="mono">"x"</td><td>FileExistsError</td><td>created</td><td>start</td></tr>
          <tr><td class="mono">"r+"</td><td>read and write</td><td>FileNotFoundError</td><td>start</td></tr>
          <tr><td class="mono">add "b"</td><td colspan="3">binary (bytes), e.g. <span class="mono">"rb"</span> for images and PDFs; no encoding</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Corrected", "<b>file_read_write_using_Open.py</b> opens <span class=\"mono\">notes.txt</span> with <span class=\"mono\">\"w\"</span>, which <b>erases</b> the notes the other scripts wrote and replaces them with one line. Easy to lose data this way: use \"a\", or write to a new file."],
  ["Corrected", "<b>csv_read.py, ReadCsvHeaders:</b> <span class=\"mono\">for row in header</span> loops over the <b>column names</b> of the header row, not rows. Name it <span class=\"mono\">for column in header</span>."],
  ["Corrected", "<b>Paths:</b> every script uses <span class=\"mono\">\"File read and write/files repository/...\"</span>, which only works when you run Python from the repo root. Build the path from the script's location with <span class=\"mono\">pathlib.Path(__file__).parent</span>."],
  ["Updated", "<b>Encoding:</b> none of the repo's open() calls pass <span class=\"mono\">encoding=</span>. Before Python 3.15 the default depended on the OS (often cp1252 on Windows), so non-English names could break. Python 3.15 (Oct 2026) makes UTF-8 the default (PEP 686), but passing <span class=\"mono\">encoding=\"utf-8\"</span> keeps code correct on older versions too."],
  ["Added", "<b>Naming:</b> functions like <span class=\"mono\">ReadCsvAsDictionaries</span> use PascalCase; PEP 8 uses snake_case for functions (<span class=\"mono\">read_csv_as_dicts</span>) and PascalCase for classes."]
 ],
 "quiz": [
  {"q": "What does <span class=\"mono\">with</span> guarantee?", "a": "The file is <b>closed</b> when the block ends, whether it ends normally, with return, or with an exception. It's a <b>context manager</b> (its own page in Part 5)."},
  {"q": "<span class=\"mono\">import json; print(json.loads('[1, \"a\", null]'))</span>", "code": "import json; print(json.loads('[1, \"a\", null]'))", "expect": "[1, 'a', None]", "a": "<b class=\"mono\">[1, 'a', None]</b>. JSON null becomes None."},
  {"q": "<span class=\"mono\">import csv, io\\nprint(next(csv.reader(io.StringIO('a,\"b,c\",d'))))</span>", "code": "import csv, io\nprint(next(csv.reader(io.StringIO('a,\"b,c\",d'))))", "expect": "['a', 'b,c', 'd']", "a": "<b class=\"mono\">['a', 'b,c', 'd']</b>. The csv module handles quoted commas; <span class=\"mono\">split(\",\")</span> wouldn't."},
  {"q": "<span class=\"mono\">import json; print(json.dumps({\"b\": 1, \"a\": 2}, sort_keys=True))</span>", "code": "import json; print(json.dumps({\"b\": 1, \"a\": 2}, sort_keys=True))", "expect": "{\"a\": 2, \"b\": 1}", "a": "<b class=\"mono\">{\"a\": 2, \"b\": 1}</b>. sort_keys gives stable output, handy for diffs and tests."},
  {"q": "<span class=\"mono\">open(\"missing.txt\")</span> raises…?", "code": "open(\"missing.txt\")", "expect": "FileNotFoundError", "a": "<b class=\"mono\">FileNotFoundError</b>. Catch it with try/except, or check <span class=\"mono\">Path(p).exists()</span> first."},
  {"q": "<span class=\"mono\">import io; f = io.StringIO(\"a\\nb\\n\"); print([l.strip() for l in f])</span>", "code": "import io; f = io.StringIO(\"a\\nb\\n\"); print([l.strip() for l in f])", "expect": "['a', 'b']", "a": "<b class=\"mono\">['a', 'b']</b>. Iterating a file-like object gives lines."}
 ],
 "sources": "Sources: Python_Fundamentals repo (File read and write/*.py). Python 3.15 UTF-8 default from PEP 686 / What's New in Python 3.15."
}
