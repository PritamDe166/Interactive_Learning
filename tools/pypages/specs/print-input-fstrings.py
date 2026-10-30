import json
VALUES = [("450.5", 450.5), ("1234567", 1234567), ("0.4567", 0.4567), ('"Asha"', "Asha")]
SPECS = [":.2f", ":,", ":,.2f", ":>10", ":<10", ":^10", ":08.2f", ":.1%", "!r", "="]
TABLE = {}
for label, v in VALUES:
    for sp in SPECS:
        code = ('f"{v' + sp + '}"')
        try:
            r = eval(code, {"v": v})
            if sp == "=":
                r = r.replace("v=", "value=", 1)
            TABLE[label + "|" + sp] = {"ok": True, "v": r}
        except Exception as e:
            TABLE[label + "|" + sp] = {"ok": False, "v": f"{type(e).__name__}: {e}"}

SPEC = {
 "slug": "print-input-fstrings", "num": 2, "part": "Values and text",
 "title": "print, input &amp; f-strings", "title_plain": "print, input & f-strings",
 "desc": "Python fundamentals: how print() assembles output with sep and end, why input() always returns text, and how f-strings and format specs build strings.",
 "lede": [
  "<b>print()</b> turns each argument into text, joins them with <b>sep</b> (a space) and finishes with <b>end</b> (a newline).",
  "<b>input()</b> shows a prompt and always returns a <b>str</b>, even when the user types a number.",
  "<b>f-strings</b> (<span class=\"mono\">f\"Hi {name}\"</span>) evaluate the code inside <span class=\"mono\">{}</span> and drop the result into the text.",
  "After a colon, a <b>format spec</b> controls the look: <span class=\"mono\">{fee:,.2f}</span> → <span class=\"mono\">1,234.50</span>."
 ],
 "walk": {"title": "printing a clinic receipt", "inputs": ["ravi"], "code":
'''patient = "Asha"
age = 35
fee = 1450.5
print("Patient:", patient)
print("Mon", "Wed", "Fri", sep=" | ")
print("Saving", end="... ")
print("done")
print("Fee: " + str(fee))
print(f"{patient} is {age} years old")
print(f"Fee: {fee:,.2f}, next year {age + 1}")
name = input("Your name: ")
print(f"Hello {name.title()}!")''',
 "steps": [
  {"at": "start", "title": "Three names, three objects", "text": "The first three lines just create a str, an int and a float. Nothing has been printed yet: watch the <b>Output</b> box as the following lines run."},
  {"at": {"after": 4}, "title": "print() with several arguments", "text": "<span class=\"mono\">print(\"Patient:\", patient)</span> converts each argument to text and puts <b>one space</b> between them. That space is the default <span class=\"mono\">sep</span>. Then it adds a newline, the default <span class=\"mono\">end</span>."},
  {"at": {"after": 5}, "title": "sep: what goes between arguments", "text": "<span class=\"mono\">sep=\" | \"</span> replaces the space between arguments. Nothing goes before the first or after the last."},
  {"at": {"after": 7}, "title": "end: what goes after the last one", "text": "<span class=\"mono\">end=\"... \"</span> replaces the newline, so the next print continues <b>on the same line</b>: <span class=\"mono\">Saving... done</span>.", "tip": "Your repo's <span class=\"mono\">print(1,2,3, end=\" \")</span> then <span class=\"mono\">print(4,5,6)</span> works the same way."},
  {"at": {"after": 8}, "title": "+ only joins str with str", "text": "<span class=\"mono\">\"Fee: \" + fee</span> would raise a <b>TypeError</b> because <span class=\"mono\">fee</span> is a float. You must convert with <span class=\"mono\">str(fee)</span> first. Commas in print() don't need that: print converts for you."},
  {"at": {"after": 9}, "title": "f-strings: code inside the braces", "text": "An <b>f-string</b> runs whatever is inside <span class=\"mono\">{}</span> and inserts the result. No conversions, no plus signs. This is the modern way to build text (Python 3.6+)."},
  {"at": {"after": 10}, "title": "Format specs after the colon", "text": "<span class=\"mono\">{fee:,.2f}</span> means: thousands separator, 2 decimals, fixed-point → <span class=\"mono\">1,450.50</span>. Braces can hold any expression: <span class=\"mono\">{age + 1}</span> → 36."},
  {"at": {"after": 11}, "title": "input() always returns text", "text": "The user typed <span class=\"mono\">ravi</span>. input() echoed the prompt and returned a <b>str</b> object. If they had typed 42, it would still be the string <span class=\"mono\">'42'</span>: convert with <span class=\"mono\">int()</span> before doing maths."},
  {"at": "end", "title": "Methods inside an f-string", "text": "<span class=\"mono\">{name.title()}</span> calls a string method right inside the braces: <span class=\"mono\">Hello Ravi!</span>. The original <span class=\"mono\">name</span> is unchanged (strings are immutable)."}
 ]},
 "walk_out": "Patient: Asha / Mon | Wed | Fri / Saving... done / Fee: 1450.5 / Asha is 35 years old / Fee: 1,450.50, next year 36 / Your name: ravi / Hello Ravi!",
 "puzzles": [
  {"id": "p1", "name": "1 · sep and end", "code": 'print("Mon", "Wed", sep=", ", end="!")\nprint("Fri")', "q": "What appears in the output?", "opts": ["Mon, Wed! / Fri", "Mon, Wed!Fri", "Mon,Wed!Fri"], "a": 1,
   "why": "<span class=\"mono\">sep=\", \"</span> goes between the two arguments; <span class=\"mono\">end=\"!\"</span> replaces the newline, so the next print continues right after the <span class=\"mono\">!</span>."},
  {"id": "p2", "name": "2 · + with a number", "code": 'age = 35\nprint("Age: " + age)', "q": "What happens?", "opts": ["Age: 35", "TypeError: can only concatenate str (not \"int\") to str", "Age:35"], "a": 1,
   "why": "<span class=\"mono\">+</span> between a str and an int is an error: Python never converts silently. Use <span class=\"mono\">\"Age: \" + str(age)</span>, a comma, or an f-string."},
  {"id": "p3", "name": "3 · input and maths", "code": 'qty = input("Qty: ")\nprint(qty * 2)', "inputs": ["3"], "q": "The user types 3. What's printed after the prompt?", "opts": ["Qty: 3 / 6", "Qty: 3 / 33", "Qty: 3 / TypeError"], "a": 1,
   "why": "input() returned the <b>string</b> <span class=\"mono\">'3'</span>, and <span class=\"mono\">str * 2</span> repeats it: <span class=\"mono\">'33'</span>. Use <span class=\"mono\">int(input(...))</span>."},
  {"id": "p4", "name": "4 · format spec", "code": 'fee = 1234.5\nprint(f"Rs {fee:,.2f}")', "q": "What's printed?", "opts": ["Rs 1,234.50", "Rs 1234.5", "Rs 1,234.5"], "a": 0,
   "why": "<span class=\"mono\">,</span> adds thousands separators and <span class=\"mono\">.2f</span> fixes two decimals."},
  {"id": "p5", "name": "5 · the = specifier", "code": 'name = "asha"\nvisits = 3\nprint(f"{name=}, {visits=}")', "q": "What's printed?", "opts": ["asha, 3", "name='asha', visits=3", "name=asha, visits=3"], "a": 1,
   "why": "<span class=\"mono\">{x=}</span> (Python 3.8+) prints the expression, an equals sign and the value's <span class=\"mono\">repr</span>: handy for quick debugging."},
  {"id": "p6", "name": "6 · a Windows path", "code": 'print("C:\\new folder")', "q": "What's printed?", "opts": ["C:\\new folder", "C: / ew folder", "C:new folder"], "a": 1,
   "why": "<span class=\"mono\">\\n</span> inside a normal string is a <b>newline</b>. Use a raw string <span class=\"mono\">r\"C:\\new folder\"</span> or forward slashes."}
 ],
 "runner_extra": [{"label": "Your turn: a receipt line", "inputs": ["Meera", "2", "450"], "code": 'name = input("Patient: ")\nvisits = int(input("Visits: "))\nfee = float(input("Fee per visit: "))\ntotal = visits * fee\nprint(f"{name:<10}|{visits:>3} x {fee:>7.2f} = {total:>9,.2f}")'}],
 "custom": [
  {"id": "asm", "title": "The print() assembly line", "kind": "Choose sep and end · watch two print() calls build the output",
   "html": '''    <div class="controls" style="flex-wrap:wrap;gap:16px">
      <div class="chip-group" style="margin:0"><div class="label">sep</div><div class="seg" id="sepSeg" role="group" aria-label="sep"><button type="button" data-v=" " aria-pressed="true">" " (default)</button><button type="button" data-v=", " aria-pressed="false">", "</button><button type="button" data-v=" | " aria-pressed="false">" | "</button><button type="button" data-v="" aria-pressed="false">""</button></div></div>
      <div class="chip-group" style="margin:0"><div class="label">end</div><div class="seg" id="endSeg" role="group" aria-label="end"><button type="button" data-v="\\n" aria-pressed="true">"\\n" (default)</button><button type="button" data-v=" " aria-pressed="false">" "</button><button type="button" data-v="... " aria-pressed="false">"... "</button><button type="button" data-v="" aria-pressed="false">""</button></div></div>
    </div>
    <pre class="codeblock" id="asmCode" style="min-height:0;margin-top:12px"></pre>
    <div class="asm-console" id="asmOut" aria-live="polite"></div>
    <div class="controls" style="margin-top:10px"><button class="btn primary" type="button" id="asmRun">Run both prints</button></div>
    <p class="status-line" id="asmStatus">Dots are spaces, ↵ is a newline.</p>''',
   "js": '''    let sep = ' ', end = '\\n';
    const show = s => s.replace(/ /g, '·').replace(/\\n/g, '↵');
    const lit = s => JSON.stringify(s);
    function code() {
      $('asmCode').innerHTML = [`print("Mon", "Wed", "Fri", sep=${lit(sep)}, end=${lit(end)})`, 'print("done")'].map(l => `<span class="ln">${K.pyHighlight(l)}</span>`).join('');
    }
    async function go() {
      const run = K.newRun('asm');
      const out = $('asmOut'); out.innerHTML = '<span class="asm-line"></span>';
      const add = (txt, cls) => { const line = out.lastElementChild; const s = document.createElement('span'); s.className = 'asm-tok ' + cls; s.textContent = txt; line.appendChild(s); };
      const newline = () => { add('↵', 'nl'); const l = document.createElement('span'); l.className = 'asm-line'; out.appendChild(l); };
      try {
        const args = ['Mon', 'Wed', 'Fri'];
        for (let i = 0; i < args.length; i++) {
          if (i) { if (sep) add(show(sep), 'sep'); await K.sleep(320, run); }
          add(args[i], 'arg'); await K.sleep(320, run);
        }
        if (end.includes('\\n')) { const before = end.split('\\n')[0]; if (before) add(show(before), 'end'); newline(); } else if (end) add(show(end), 'end');
        await K.sleep(500, run);
        add('done', 'arg'); await K.sleep(250, run); newline();
        const text = args.join(sep) + end + 'done\\n';
        $('asmStatus').innerHTML = `Real output: <span class="mono">${text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/\\n/g, '↵')}</span> · ${end === '\\n' ? 'end is a newline, so "done" starts a new line.' : 'end is not a newline, so "done" continues on the same line.'}`;
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    K.seg($('sepSeg'), v => { sep = v; code(); go(); });
    K.seg($('endSeg'), v => { end = v.replace('\\\\n', '\\n'); code(); go(); });
    $('asmRun').addEventListener('click', go);
    code();'''},
  {"id": "fmt", "title": "Format spec explorer", "kind": "Pick a value and a spec · the result is what Python really prints",
   "html": '''    <div class="chip-group"><div class="label">Value</div><div class="chips" id="fvVal" style="margin:0"></div></div>
    <div class="chip-group"><div class="label">Spec</div><div class="chips" id="fvSpec" style="margin:0"></div></div>
    <div class="two" style="margin-top:12px">
      <div class="card"><div class="label">Code</div><pre class="codeblock" id="fvCode" style="min-height:0;margin:0"></pre></div>
      <div class="card"><div class="label">Result (· = space)</div><div class="fv-out" id="fvOut"></div></div>
    </div>
    <p class="status-line" id="fvStatus"></p>''',
   "js": '''    const TABLE = __TABLE__;
    const VALS = __VALS__, SPECS = __SPECS__;
    const MEAN = { ':.2f': 'fixed point, 2 decimals', ':,': 'thousands separator', ':,.2f': 'separator + 2 decimals', ':>10': 'right-align in 10 characters', ':<10': 'left-align in 10', ':^10': 'centre in 10', ':08.2f': 'width 8, pad with zeros, 2 decimals', ':.1%': 'multiply by 100, add %, 1 decimal', '!r': 'use repr() instead of str(): strings get quotes', '=': 'show the expression too (3.8+)' };
    let vi = 0, si = 0;
    $('fvVal').innerHTML = VALS.map((v, i) => `<button class="chip-btn" type="button" data-i="${i}" aria-pressed="${!i}">${v.replace(/</g, '&lt;')}</button>`).join('');
    $('fvSpec').innerHTML = SPECS.map((s, i) => `<button class="chip-btn" type="button" data-i="${i}" aria-pressed="${!i}">${s}</button>`).join('');
    function show() {
      const r = TABLE[VALS[vi] + '|' + SPECS[si]];
      const spec = SPECS[si];
      $('fvCode').innerHTML = `<span class="ln">${K.pyHighlight('value = ' + VALS[vi])}</span><span class="ln">${K.pyHighlight('print(f"{value' + spec + '}")')}</span>`;
      $('fvOut').innerHTML = r.ok ? `<span class="mono">${r.v.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/ /g, '<span class="sp">·</span>')}</span>` : `<span class="bad-text mono">${r.v.replace(/</g, '&lt;')}</span>`;
      $('fvStatus').innerHTML = r.ok ? `<b class="mono">${spec}</b>: ${MEAN[spec]}.` : 'A format spec has to suit the type: <span class="mono">f</span> and <span class="mono">%</span> need a number, not a str.';
    }
    ['fvVal', 'fvSpec'].forEach(id => $(id).querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      $(id).querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      if (id === 'fvVal') vi = +b.dataset.i; else si = +b.dataset.i; show();
    })));
    show();'''.replace('__TABLE__', json.dumps(TABLE, ensure_ascii=False)).replace('__VALS__', json.dumps([v[0] for v in VALUES])).replace('__SPECS__', json.dumps(SPECS))}
 ],
 "style": '''  .asm-console { margin-top: 12px; background: var(--code-bg); border: 1px solid var(--line); border-radius: 12px; padding: 12px 14px; min-height: 76px; font-family: var(--mono); font-size: 15px; display: grid; gap: 6px; }
  .asm-line { display: flex; flex-wrap: wrap; align-items: center; min-height: 26px; }
  .asm-tok { padding: 2px 6px; border-radius: 6px; margin-right: 1px; animation: pop .25s ease-out; }
  .asm-tok.arg { background: var(--teal-wash); color: var(--fg); }
  .asm-tok.sep { background: var(--panel-2); color: var(--accent-text); }
  .asm-tok.end { background: var(--panel-2); color: var(--cyan); }
  .asm-tok.nl { color: var(--cyan); }
  @keyframes pop { from { transform: scale(.6); opacity: 0; } to { transform: none; opacity: 1; } }
  #sepSeg button, #endSeg button { white-space: pre; }
  .fv-out { font-size: 20px; padding: 10px 0; overflow-wrap: anywhere; }
  .fv-out .sp { color: var(--muted); }''',
 "cheat": [
  ["Several values on one line", "<span class=\"mono\">print(a, b, c)</span> (spaces added for you)"],
  ["Different separator / no newline", "<span class=\"mono\">sep=\", \"</span> / <span class=\"mono\">end=\"\"</span>"],
  ["Building text with variables", "f-string: <span class=\"mono\">f\"{name} is {age}\"</span>"],
  ["Number from the user", "<span class=\"mono\">int(input(...))</span> or <span class=\"mono\">float(input(...))</span>"],
  ["Money / decimals", "<span class=\"mono\">{x:,.2f}</span> → 1,234.50"],
  ["Backslashes in paths", "Raw string <span class=\"mono\">r\"C:\\new\"</span> or use <span class=\"mono\">/</span>"]
 ],
 "ref_title": "Reference: format specs and escapes",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Write</th><th>Means</th><th>Example → result</th></tr></thead>
        <tbody>
          <tr><td class="mono">{x:.2f}</td><td>2 decimals</td><td class="mono">3.14159 → 3.14</td></tr>
          <tr><td class="mono">{x:,}</td><td>thousands separator</td><td class="mono">1234567 → 1,234,567</td></tr>
          <tr><td class="mono">{x:&gt;8} {x:&lt;8} {x:^8}</td><td>right / left / centre in 8 characters</td><td class="mono">'Asha' → '····Asha'</td></tr>
          <tr><td class="mono">{x:08.2f}</td><td>zero-pad to width 8</td><td class="mono">450.5 → 00450.50</td></tr>
          <tr><td class="mono">{x:.1%}</td><td>percentage</td><td class="mono">0.4567 → 45.7%</td></tr>
          <tr><td class="mono">{x!r}</td><td>repr() form</td><td class="mono">'Asha' → 'Asha' (with quotes)</td></tr>
          <tr><td class="mono">{x=}</td><td>expression and value (3.8+)</td><td class="mono">x='Asha'</td></tr>
          <tr><td class="mono">\\n \\t \\\\ \\"</td><td>newline, tab, backslash, quote</td><td class="mono">r"..." turns escapes off</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Corrected", "<b>The comma adds its own space.</b> In <span class=\"mono\">Print_statements.py</span>, <span class=\"mono\">print(\"Colors are \"+\": \"+\"Oranges\",\" Apples\")</span> prints <span class=\"mono\">Colors are : Oranges··Apples</span> with two spaces: one from <span class=\"mono\">sep</span>, one inside <span class=\"mono\">\" Apples\"</span>."],
  ["Added", "<b>Prefer f-strings.</b> <span class=\"mono\">\"{} {}\".format(a, b)</span> (your InputOutput examples) and <span class=\"mono\">\"%s\" % a</span> still work and appear in older code, but f-strings are shorter, faster and read left to right."],
  ["Added", "<b>input() + int() can fail.</b> If the user types <span class=\"mono\">abc</span>, <span class=\"mono\">int()</span> raises <span class=\"mono\">ValueError</span>. Wrapping it in <span class=\"mono\">try/except</span> is covered in Errors &amp; exceptions."],
  ["Updated", "<b>Newer f-string features:</b> since Python 3.12 you can reuse the same quote type inside the braces (<span class=\"mono\">f\"{d[\"key\"]}\"</span>) and split long expressions across lines. Python 3.14 adds <b>t-strings</b> (<span class=\"mono\">t\"...\"</span>), template strings that keep the parts separate for safe HTML or SQL building."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">print(1, 2, 3, sep=\"-\")</span>", "code": 'print(1, 2, 3, sep="-")', "expect": "1-2-3", "a": "<b class=\"mono\">1-2-3</b>. sep goes between the arguments only."},
  {"q": "<span class=\"mono\">print(\"a\", end=\"\"); print(\"b\")</span>", "code": 'print("a", end=""); print("b")', "expect": "ab", "a": "<b class=\"mono\">ab</b>. The first print ends with nothing, so the second continues on the same line."},
  {"q": "The user types <span class=\"mono\">42</span>. What does <span class=\"mono\">print(type(input()))</span> show?", "code": "print(type(input()))", "inputs": ["42"], "expect": "<class 'str'>", "a": "<b class=\"mono\">&lt;class 'str'&gt;</b>. input() always returns text."},
  {"q": "<span class=\"mono\">print(f\"{3/4:.0%}\")</span>", "code": 'print(f"{3/4:.0%}")', "expect": "75%", "a": "<b class=\"mono\">75%</b>. % multiplies by 100; .0 means no decimals."},
  {"q": "<span class=\"mono\">print(\"{} + {} = {}\".format(2, 3, 2 + 3))</span>", "code": 'print("{} + {} = {}".format(2, 3, 2 + 3))', "expect": "2 + 3 = 5", "a": "<b class=\"mono\">2 + 3 = 5</b>. Each <span class=\"mono\">{}</span> takes the next argument."},
  {"q": "<span class=\"mono\">print(f\"[{'Asha':>6}]\")</span>", "code": "print(f\"[{'Asha':>6}]\")", "expect": "[  Asha]", "a": "<b class=\"mono\">[··Asha]</b>. Right-aligned in a field 6 wide, padded with spaces on the left."}
 ],
 "sources": "Sources: Python_Fundamentals repo (Basics/Print_statements.py, Basics/InputOutputFunctions.py, PractiseArea/PrintStatement_exercises.py)."
}
