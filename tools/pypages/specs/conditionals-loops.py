SPEC = {
 "slug": "conditionals-loops", "num": 4, "part": "Control flow and data",
 "title": "Conditionals &amp; loops", "title_plain": "Conditionals & loops",
 "desc": "Python fundamentals: if/elif/else, for loops over sequences and range(), while loops, break, continue and the loop else clause, stepped line by line.",
 "lede": [
  "<b>if / elif / else</b> checks conditions top to bottom and runs <b>only the first</b> branch that is true.",
  "A <b>for</b> loop takes items one at a time from any sequence (list, string, <span class=\"mono\">range()</span>); a <b>while</b> loop repeats as long as a condition stays true.",
  "<b>continue</b> skips to the next item; <b>break</b> leaves the loop completely.",
  "Indentation is the syntax: the indented lines under a colon <b>are</b> the block."
 ],
 "walk": {"title": "grading a list of scores", "code":
'''scores = [72, 45, 91, 60]
passed = 0
for i, score in enumerate(scores):
    if score < 50:
        print(i, "fail")
        continue
    if score >= 90:
        print(i, "top")
    passed += 1
print("passed:", passed)
n = 2
while n > 0:
    print("T-minus", n)
    n -= 1''',
 "steps": [
  {"at": {"after": 2}, "title": "Set up before the loop", "text": "A list of four scores and a counter starting at 0. Watch <b>i</b> and <b>score</b> appear once the loop starts."},
  {"at": {"after": 3, "n": 1}, "title": "for takes the first item", "text": "<span class=\"mono\">enumerate(scores)</span> hands out pairs (position, value). The loop <b>unpacks</b> the first pair into <span class=\"mono\">i = 0</span> and <span class=\"mono\">score = 72</span>."},
  {"at": {"after": 9, "n": 1}, "title": "Conditions checked, counter updated", "text": "72 is not &lt; 50 and not ≥ 90, so both <span class=\"mono\">if</span> bodies are skipped. Only <span class=\"mono\">passed += 1</span> runs. Then the loop goes back to the top for the next item."},
  {"at": {"after": 5, "n": 1}, "title": "45: the fail branch", "text": "Second item: <span class=\"mono\">score = 45</span>. The condition is true, so the indented block runs and prints <span class=\"mono\">1 fail</span>."},
  {"at": {"after": 6, "n": 1}, "title": "continue skips the rest", "text": "<span class=\"mono\">continue</span> jumps straight back to the <span class=\"mono\">for</span> line. <span class=\"mono\">passed += 1</span> does <b>not</b> run for 45.", "tip": "Use <span class=\"mono\">break</span> instead and the loop would stop completely: 91 and 60 would never be looked at."},
  {"at": {"after": 8, "n": 1}, "title": "91: a second if", "text": "These are two separate <span class=\"mono\">if</span> statements, not if/elif, so after the first check fails Python still checks <span class=\"mono\">score &gt;= 90</span>, which is true: <span class=\"mono\">2 top</span>."},
  {"at": {"after": 10}, "title": "The loop ends by itself", "text": "After the last item (60) the sequence is used up and execution continues after the loop. Three scores passed. <b>i</b> and <b>score</b> still exist: Python has no block scope."},
  {"at": {"after": 13, "n": 1}, "title": "while checks before every round", "text": "<span class=\"mono\">while n &gt; 0</span> is tested, it's true, the body prints <span class=\"mono\">T-minus 2</span>…"},
  {"at": "end", "title": "…until the condition turns false", "text": "<span class=\"mono\">n -= 1</span> moves toward the exit. When <span class=\"mono\">n</span> becomes 0 the test fails and the loop stops. Forget that line and the loop never ends."}
 ]},
 "walk_out": "1 fail / 2 top / passed: 3 / T-minus 2 / T-minus 1",
 "puzzles": [
  {"id": "p1", "name": "1 · range with a step", "code": "for n in range(2, 10, 3):\n    print(n, end=\" \")", "q": "What's printed?", "opts": ["2 5 8", "2 5 8 11", "3 6 9"], "a": 0,
   "why": "Start at 2, add 3 each time, stop <b>before</b> 10: 2, 5, 8."},
  {"id": "p2", "name": "2 · order of elif", "code": "score = 95\nif score >= 60:\n    print(\"D\")\nelif score >= 90:\n    print(\"A\")", "q": "What's printed?", "opts": ["A", "D", "D / A"], "a": 1,
   "why": "Only the <b>first</b> true branch runs. 95 ≥ 60 is true, so the A branch is never reached. Put the strictest condition first."},
  {"id": "p3", "name": "3 · for … else", "code": "for slot in [\"9:00\", \"9:30\", \"10:00\"]:\n    if slot == \"9:30\":\n        print(\"booked\", slot)\n        break\nelse:\n    print(\"no slot\")", "q": "What's printed?", "opts": ["booked 9:30", "booked 9:30 / no slot", "no slot"], "a": 0,
   "why": "A loop's <span class=\"mono\">else</span> runs only if the loop finished <b>without</b> break. Here break happened, so <span class=\"mono\">no slot</span> is skipped."},
  {"id": "p4", "name": "4 · changing the loop variable", "code": "for i in range(3):\n    print(i, end=\" \")\n    i = 10", "q": "What's printed?", "opts": ["0", "0 1 2", "0 10"], "a": 1,
   "why": "Each round, <span class=\"mono\">for</span> rebinds <span class=\"mono\">i</span> to the next value from <span class=\"mono\">range</span>. Assigning 10 inside the body doesn't affect what comes next."},
  {"id": "p5", "name": "5 · truthiness", "code": "name = \"\"\nvisits = [0]\nif name:\n    print(\"has name\")\nif visits:\n    print(\"has visits\")", "q": "What's printed?", "opts": ["has visits", "has name / has visits", "(nothing)"], "a": 0,
   "why": "Empty string is falsy. A list with one item is truthy, even if that item is 0."},
  {"id": "p6", "name": "6 · chained comparison", "code": "age = 15\nprint(10 < age < 18, 10 < age > 18)", "q": "What's printed?", "opts": ["True False", "True True", "SyntaxError"], "a": 0,
   "why": "<span class=\"mono\">a &lt; b &lt; c</span> means <span class=\"mono\">a &lt; b and b &lt; c</span>. The second is <span class=\"mono\">10 &lt; 15 and 15 &gt; 18</span> → False."}
 ],
 "runner_extra": [{"label": "Your turn: password with 3 tries", "inputs": ["abc", "System@123"], "code": 'correct = "System@123"\nfor attempt in range(1, 4):\n    pw = input("Password: ")\n    if pw == correct:\n        print("Welcome! attempt", attempt)\n        break\n    print("Wrong,", 3 - attempt, "left")\nelse:\n    print("Locked out")'}],
 "custom": [
  {"id": "range", "title": "range() on a number line", "kind": "Drag start, stop and step · the dots are the values the loop gets",
   "html": '''    <div class="scroll"><svg class="diagram narrow" id="rgSvg" viewBox="0 0 660 120" style="min-width:520px" role="img" aria-label="Number line from -5 to 15"></svg></div>
    <div class="grid3" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin-top:8px">
      <div class="card"><label class="label" for="rgA">start <span class="mono" id="rgAv"></span></label><input type="range" id="rgA" min="-5" max="15" value="0" style="width:100%"></div>
      <div class="card"><label class="label" for="rgB">stop <span class="mono" id="rgBv"></span></label><input type="range" id="rgB" min="-5" max="15" value="5" style="width:100%"></div>
      <div class="card"><label class="label" for="rgC">step <span class="mono" id="rgCv"></span></label><input type="range" id="rgC" min="-4" max="4" value="1" style="width:100%"></div>
    </div>
    <p class="status-line" id="rgStatus" style="font-size:16px"></p>''',
   "js": '''    const svg = $('rgSvg'), ns = 'http://www.w3.org/2000/svg', X = v => 30 + (v + 5) * 30;
    function mk(tag, at, txt) { const e = document.createElementNS(ns, tag); for (const k in at) e.setAttribute(k, at[k]); if (txt != null) e.textContent = txt; svg.appendChild(e); return e; }
    function draw() {
      const a = +$('rgA').value, b = +$('rgB').value, c = +$('rgC').value;
      $('rgAv').textContent = a; $('rgBv').textContent = b; $('rgCv').textContent = c;
      svg.innerHTML = '';
      mk('line', { x1: X(-5), y1: 60, x2: X(15), y2: 60, class: 'rg-axis' });
      for (let v = -5; v <= 15; v++) { mk('line', { x1: X(v), y1: 55, x2: X(v), y2: 65, class: 'rg-axis' }); const t = mk('text', { x: X(v), y: 92, class: 'rg-num' }, v); t.style.textAnchor = 'middle'; }
      if (c === 0) { $('rgStatus').innerHTML = '<span class="mono">range(' + a + ', ' + b + ', 0)</span> → <b class="bad-text">ValueError: range() arg 3 must not be zero</b>'; return; }
      const vals = []; for (let v = a; c > 0 ? v < b : v > b; v += c) vals.push(v);
      const sx = mk('path', { d: `M${X(b)} 32 v56`, class: 'rg-stop' });
      const st = mk('text', { x: X(b), y: 24, class: 'rg-stopl' }, 'stop (excluded)'); st.style.textAnchor = 'middle';
      vals.forEach((v, k) => { mk('circle', { cx: X(v), cy: 60, r: 9, class: 'rg-dot', style: `animation-delay:${k * 70}ms` }); });
      $('rgStatus').innerHTML = `<span class="mono">list(range(${a}, ${b}, ${c}))</span> → <b class="mono">[${vals.join(', ')}]</b>` + (vals.length ? ` · ${vals.length} value${vals.length > 1 ? 's' : ''}` : (c > 0 ? ' · empty: a positive step needs start &lt; stop' : ' · empty: a negative step needs start &gt; stop'));
    }
    ['rgA', 'rgB', 'rgC'].forEach(id => $(id).addEventListener('input', draw));
    draw();'''},
  {"id": "lc", "title": "break vs continue vs neither", "kind": "Same loop, three endings · watch which patients get processed",
   "html": '''    <pre class="codeblock" id="lcCode" style="min-height:0"></pre>
    <div class="seg" id="lcSeg" role="group" aria-label="Loop control"><button type="button" data-v="none" aria-pressed="true">no control</button><button type="button" data-v="continue" aria-pressed="false">continue</button><button type="button" data-v="break" aria-pressed="false">break</button></div>
    <div class="lc-row" id="lcRow"></div>
    <div class="lc-else" id="lcElse">else: print("all checked")</div>
    <p class="status-line" id="lcStatus">Press a button to run the loop.</p>''',
   "js": '''    const P = [['Asha', 'ok'], ['Ravi', 'ok'], ['Meera', 'urgent'], ['John', 'ok'], ['Lina', 'ok']];
    let mode = 'none';
    function code() {
      const lines = ['for name, status in patients:', '    if status == "urgent":'];
      lines.push(mode === 'none' ? '        print("flag", name)' : mode === 'continue' ? '        continue' : '        break');
      lines.push('    print("process", name)', 'else:', '    print("all checked")');
      $('lcCode').innerHTML = lines.map(l => `<span class="ln">${K.pyHighlight(l)}</span>`).join('');
    }
    async function go() {
      const run = K.newRun('lc'); code();
      $('lcRow').innerHTML = P.map(([n, s]) => `<div class="lc-p${s === 'urgent' ? ' urgent' : ''}"><b>${n}</b><span>${s}</span><i></i></div>`).join('');
      $('lcElse').className = 'lc-else';
      const cells = [...$('lcRow').children]; const out = [];
      try {
        let broke = false;
        for (let k = 0; k < P.length; k++) {
          const c = cells[k], [n, s] = P[k]; c.classList.add('cur'); await K.sleep(450, run);
          if (s === 'urgent') {
            if (mode === 'none') { out.push('flag ' + n); c.querySelector('i').textContent = 'flagged'; }
            if (mode === 'continue') { c.classList.remove('cur'); c.classList.add('skip'); c.querySelector('i').textContent = 'skipped'; out.push('(skip)'); await K.sleep(400, run); continue; }
            if (mode === 'break') { c.classList.remove('cur'); c.classList.add('stop'); c.querySelector('i').textContent = 'break!'; broke = true; break; }
          }
          out.push('process ' + n); c.classList.remove('cur'); c.classList.add('done'); c.querySelector('i').textContent = (c.querySelector('i').textContent ? c.querySelector('i').textContent + ' + ' : '') + 'processed';
          await K.sleep(300, run);
        }
        if (broke) cells.slice(3).forEach(c => { c.classList.add('never'); c.querySelector('i').textContent = 'never seen'; });
        $('lcElse').className = 'lc-else ' + (broke ? 'off' : 'on');
        $('lcStatus').innerHTML = mode === 'none' ? 'Every patient processed; Meera also flagged. The loop finished normally, so <b>else ran</b>.' : mode === 'continue' ? '<b>continue</b> skipped the rest of the body for Meera only. The loop still finished normally, so <b>else ran</b>.' : '<b>break</b> left the loop at Meera: John and Lina were never looked at, and <b>else was skipped</b>.';
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    K.seg($('lcSeg'), v => { mode = v; go(); });
    code();
    $('lcRow').innerHTML = P.map(([n, s]) => `<div class="lc-p${s === 'urgent' ? ' urgent' : ''}"><b>${n}</b><span>${s}</span><i></i></div>`).join('');'''}
 ],
 "style": '''  .rg-axis { stroke: var(--muted); stroke-width: 1.5; }
  .rg-num { font-family: var(--mono); font-size: 12px; fill: var(--muted); }
  .rg-dot { fill: var(--cyan); animation: pop .3s ease-out both; transform-box: fill-box; transform-origin: center; }
  .rg-stop { stroke: var(--red); stroke-width: 2; stroke-dasharray: 4 4; }
  .rg-stopl { font-size: 11px; fill: var(--bad-text); font-family: var(--mono); }
  @keyframes pop { from { transform: scale(0); } to { transform: none; } }
  .lc-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(96px, 1fr)); gap: 8px; margin-top: 12px; }
  .lc-p { border: 1.5px solid var(--line); border-radius: 10px; padding: 8px 10px; background: var(--panel-2); display: grid; gap: 2px; transition: all .25s; }
  .lc-p span { font-size: 12px; color: var(--muted); font-family: var(--mono); }
  .lc-p i { font-style: normal; font-size: 12px; min-height: 16px; color: var(--fg-soft); }
  .lc-p.urgent span { color: var(--bad-text); }
  .lc-p.cur { border-color: var(--cyan); box-shadow: 0 0 0 3px var(--teal-wash); }
  .lc-p.done { border-color: var(--teal); }
  .lc-p.done i { color: var(--good-text); }
  .lc-p.skip { border-style: dashed; opacity: .75; }
  .lc-p.skip i, .lc-p.stop i { color: var(--bad-text); }
  .lc-p.stop { border-color: var(--red); }
  .lc-p.never { opacity: .35; }
  .lc-else { margin-top: 10px; font-family: var(--mono); font-size: 14px; padding: 8px 12px; border-radius: 10px; border: 1.5px dashed var(--line); color: var(--muted); }
  .lc-else.on { border-style: solid; border-color: var(--teal); color: var(--good-text); }
  .lc-else.off { text-decoration: line-through; }''',
 "cheat": [
  ["Several mutually exclusive cases", "<span class=\"mono\">if / elif / else</span>, strictest condition first"],
  ["Need the position too", "<span class=\"mono\">for i, x in enumerate(items):</span> (not <span class=\"mono\">range(len(...))</span>)"],
  ["Count 1 to n", "<span class=\"mono\">range(1, n + 1)</span>: stop is excluded"],
  ["Skip this item", "<span class=\"mono\">continue</span>"],
  ["Found it, stop looking", "<span class=\"mono\">break</span>; add a loop <span class=\"mono\">else:</span> for \"not found\""],
  ["Repeat until something happens", "<span class=\"mono\">while True:</span> … <span class=\"mono\">if done: break</span>"],
  ["Range check", "<span class=\"mono\">60 &lt;= score &lt; 70</span> (chained comparison)"]
 ],
 "ref_title": "Reference: truthiness and match",
 "ref_html": '''    <div class="two">
      <div class="card"><div class="label">Falsy values (everything else is truthy)</div><p class="mono" style="margin:6px 0 0">False · None · 0 · 0.0 · "" · [] · () · {} · set() · range(0)</p><p class="muted" style="margin:8px 0 0">So <span class="mono">if items:</span> means "if the list isn't empty".</p></div>
      <div class="card"><div class="label">match / case (Python 3.10+)</div><pre class="codeblock" style="min-height:0;margin:6px 0 0"><span class="ln"><span class="k">match</span> status:</span><span class="ln">    <span class="k">case</span> <span class="s">"urgent"</span>: ...</span><span class="ln">    <span class="k">case</span> <span class="s">"ok"</span> | <span class="s">"done"</span>: ...</span><span class="ln">    <span class="k">case</span> _: ...</span></pre><p class="muted" style="margin:8px 0 0">Like a switch, but it can also match shapes (tuples, dicts, classes). No fall-through.</p></div>
    </div>''',
 "notes": [
  ["Corrected", "<b>Grade exercise in Conditionals.py:</b> after <span class=\"mono\">if num &lt; 60</span> fails, the next <span class=\"mono\">elif</span> already knows num ≥ 60, so <span class=\"mono\">num &gt;= 60 and</span> is redundant. Write <span class=\"mono\">elif num &lt; 70:</span>, or <span class=\"mono\">elif 60 &lt;= num &lt; 70:</span> if you want it explicit. There's also a typo: \"Ypur Grade\"."],
  ["Added", "<b>Validate the input range:</b> the same exercise prints \"Grade A\" for 150 and \"Failed\" for -5. Check <span class=\"mono\">0 &lt;= num &lt;= 100</span> first."],
  ["Added", "<b>Topics the repo doesn't cover yet:</b> <span class=\"mono\">break</span>, <span class=\"mono\">continue</span>, the loop <span class=\"mono\">else</span>, <span class=\"mono\">enumerate()</span> and <span class=\"mono\">match</span>. All are on this page."],
  ["Added", "<b>Sum loops:</b> <span class=\"mono\">current_sum = current_sum + i</span> works, but Python has <span class=\"mono\">sum(list_of_numbers)</span> and <span class=\"mono\">sum(range(1, n + 1))</span>. Write the loop to learn, use the built-in in real code."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">print(list(range(5, 0, -2)))</span>", "code": "print(list(range(5, 0, -2)))", "expect": "[5, 3, 1]", "a": "<b class=\"mono\">[5, 3, 1]</b>. Counts down by 2 and stops before 0."},
  {"q": "<span class=\"mono\">for c in \"hi\": print(c * 2, end=\"\")</span>", "code": 'for c in "hi": print(c * 2, end="")', "expect": "hhii", "a": "<b class=\"mono\">hhii</b>. A string is iterated character by character."},
  {"q": "<span class=\"mono\">x = 0\\nwhile x &lt; 10: x += 3\\nprint(x)</span>", "code": "x = 0\nwhile x < 10: x += 3\nprint(x)", "expect": "12", "a": "<b class=\"mono\">12</b>. 0 → 3 → 6 → 9 → 12; then 12 &lt; 10 is false."},
  {"q": "<span class=\"mono\">for i in range(3):\\n    if i == 1: break\\nelse: print(\"done\")\\nprint(i)</span>", "code": "for i in range(3):\n    if i == 1: break\nelse: print(\"done\")\nprint(i)", "expect": "1", "a": "<b class=\"mono\">1</b> only. break skipped the else, and i keeps its last value."},
  {"q": "<span class=\"mono\">print(\"yes\" if [] else \"no\")</span>", "code": 'print("yes" if [] else "no")', "expect": "no", "a": "<b class=\"mono\">no</b>. An empty list is falsy. This one-line form is the conditional expression."},
  {"q": "<span class=\"mono\">for i, ch in enumerate(\"ab\", start=1): print(i, ch)</span>", "code": 'for i, ch in enumerate("ab", start=1): print(i, ch)', "expect": "1 a / 2 b", "a": "<b class=\"mono\">1 a</b> then <b class=\"mono\">2 b</b>. <span class=\"mono\">start=</span> changes the first number."}
 ],
 "sources": "Sources: Python_Fundamentals repo (Basics/Conditionals.py, Basics/Loops.py); break/continue/else/enumerate/match added from the Python tutorial."
}
