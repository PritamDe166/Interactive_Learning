import json, sys
MEM = []
for e in range(1, 7):
    n = 10 ** e
    MEM.append({"n": n, "list": sys.getsizeof([x * x for x in range(n)]), "gen": sys.getsizeof((x * x for x in range(n)))})
def slots(start, end, step=30):
    t = start
    while t < end:
        yield t
        t += step
assert list(slots(540, 660)) == [540, 570, 600, 630]

SPEC = {
 "slug": "iterators-generators", "num": 14, "part": "Going further",
 "title": "Iterators &amp; generators", "title_plain": "Iterators & generators",
 "desc": "Python fundamentals: the iterator protocol (iter and next), StopIteration, generator functions with yield, generator expressions, and why lazy evaluation saves memory.",
 "lede": [
  "A <b>for</b> loop calls <span class=\"mono\">iter()</span> on the object to get an <b>iterator</b>, then <span class=\"mono\">next()</span> until it raises <b>StopIteration</b>.",
  "A function containing <span class=\"mono\">yield</span> is a <b>generator function</b>: calling it runs <b>nothing</b> yet and returns a generator object.",
  "Each <span class=\"mono\">next()</span> runs the body up to the next <span class=\"mono\">yield</span>, hands out that value and <b>pauses</b>, keeping its local variables.",
  "Generators are <b>lazy</b>: values are made one at a time, so a stream of a million rows needs memory for one. They can be used <b>once</b>."
 ],
 "walk": {"title": "generating appointment slots", "code":
'''def slots(start, end, step=30):
    t = start
    while t < end:
        yield t
        t += step

gen = slots(540, 630)
print(next(gen))
print(next(gen))
for t in gen:
    print("loop got", t)
nums = iter([10, 20])
print(next(nums), next(nums), next(nums, "done"))
squares = (n * n for n in range(4))
print(sum(squares), list(squares))''',
 "steps": [
  {"at": {"after": 7}, "title": "Calling it runs nothing", "text": "Because <span class=\"mono\">slots</span> contains <span class=\"mono\">yield</span>, calling it just creates a <b>generator object</b>, marked <i>not started</i>. Not even <span class=\"mono\">t = start</span> has run. (540 minutes = 9:00.)"},
  {"at": {"event": "call", "n": 1}, "title": "next() starts the body", "text": "<span class=\"mono\">next(gen)</span> resumes the generator. Its frame appears on top of the stack and runs from the first line."},
  {"at": {"event": "return", "n": 1}, "title": "yield hands out a value and pauses", "text": "At <span class=\"mono\">yield t</span> the generator gives 540 to the caller and <b>freezes</b> right there. Its frame leaves the stack, but the generator object keeps <span class=\"mono\">t</span>, <span class=\"mono\">start</span>, <span class=\"mono\">end</span>…"},
  {"at": {"event": "call", "n": 2}, "title": "The next next() resumes after yield", "text": "Execution continues from the line <b>after</b> <span class=\"mono\">yield</span>: <span class=\"mono\">t += step</span>, then the loop test, then the next yield (570)."},
  {"at": {"after": 11, "n": 1}, "title": "for calls next() for you", "text": "The <span class=\"mono\">for</span> loop picks up where we left off: 600. It doesn't restart the generator, which only goes forward."},
  {"at": {"after": 12}, "title": "StopIteration ends the loop", "text": "After 600, <span class=\"mono\">t</span> becomes 630, the while test fails and the function returns. A finished generator raises <b>StopIteration</b> on the next <span class=\"mono\">next()</span>, which <span class=\"mono\">for</span> treats as \"done\". Its state is now <i>finished</i>."},
  {"at": {"after": 13}, "title": "Every for loop works this way", "text": "<span class=\"mono\">iter([10, 20])</span> gives a list iterator. Two <span class=\"mono\">next()</span> calls return the items; the third would raise StopIteration, but <span class=\"mono\">next(it, default)</span> returns the default instead.", "tip": "Lists, strings, dicts and files are <b>iterables</b> (you can call iter() on them as often as you like). Iterators are one-pass cursors over them."},
  {"at": "end", "title": "Generator expressions are one-pass too", "text": "<span class=\"mono\">sum(squares)</span> consumed every value (0+1+4+9 = 14). Asking again gives nothing: <span class=\"mono\">list(squares)</span> is empty."}
 ]},
 "walk_out": "540 / 570 / loop got 600 / 10 20 done / 14 []",
 "puzzles": [
  {"id": "p1", "name": "1 · when does the body run?", "code": "def gen():\n    print(\"start\")\n    yield 1\n    print(\"end\")\n\ng = gen()\nprint(\"made\")\nprint(next(g))", "q": "What's printed?", "opts": ["start / made / 1", "made / start / 1", "made / start / 1 / end"], "a": 1,
   "why": "Calling gen() runs nothing. The body starts at the first next() and stops at yield, so \"end\" never prints here."},
  {"id": "p2", "name": "2 · list() twice", "code": "def countdown(n):\n    while n > 0:\n        yield n\n        n -= 1\n\nc = countdown(3)\nprint(list(c), list(c))", "q": "What's printed?", "opts": ["[3, 2, 1] [3, 2, 1]", "[3, 2, 1] []", "[3, 2, 1] [0]"], "a": 1,
   "why": "A generator can be consumed once. Call <span class=\"mono\">countdown(3)</span> again for a fresh one."},
  {"id": "p3", "name": "3 · next past the end", "code": "it = iter(\"ab\")\nprint(next(it), next(it))\nprint(next(it))", "q": "What happens?", "opts": ["a b / (empty line)", "a b / StopIteration", "a b / a"], "a": 1,
   "why": "An exhausted iterator raises StopIteration. for loops catch it for you; a bare next() doesn't."},
  {"id": "p4", "name": "4 · yield from", "code": "def morning():\n    yield \"9:00\"\n    yield \"9:30\"\n\ndef day():\n    yield from morning()\n    yield \"14:00\"\n\nprint(list(day()))", "q": "What's printed?", "opts": ["['9:00', '9:30', '14:00']", "[<generator object morning>, '14:00']", "['14:00']"], "a": 0,
   "why": "<span class=\"mono\">yield from</span> passes on every value of another iterable, one by one."},
  {"id": "p5", "name": "5 · infinite but lazy", "code": "from itertools import count, islice\nids = count(1001)\nprint(list(islice(ids, 3)), next(ids))", "q": "What's printed?", "opts": ["[1001, 1002, 1003] 1004", "[1001, 1002, 1003] 1001", "it never finishes"], "a": 0,
   "why": "<span class=\"mono\">count()</span> never ends, but values are only made when asked. islice took three; the iterator continues from 1004."}
 ],
 "runner_extra": [{"label": "Your turn: read records lazily", "code": 'def read_rows(lines):\n    for line in lines:\n        name, fee = line.split(",")\n        yield {"name": name, "fee": int(fee)}\n\ndata = ["Asha,450", "Ravi,800", "Meera,1200"]\nrows = read_rows(data)\nprint(next(rows))\nprint(sum(r["fee"] for r in rows))\n# Which rows did the sum see? Why not Asha?'}],
 "custom": [
  {"id": "pull", "title": "Pull values with next()", "kind": "Press next() · see where the generator pauses and what it remembers",
   "html": '''    <div class="two">
      <pre class="codeblock" id="plCode" style="min-height:0;margin:0"></pre>
      <div>
        <div class="card"><div class="label">Generator state</div><div class="mono" id="plState" style="font-size:15px">not started</div><div class="mono muted" id="plVars" style="margin-top:6px"></div></div>
        <div class="card" style="margin-top:10px"><div class="label">Caller received</div><div class="mono" id="plGot" style="font-size:15px;overflow-wrap:anywhere">—</div></div>
      </div>
    </div>
    <div class="controls" style="margin-top:12px"><button class="btn primary" type="button" id="plNext">next(gen)</button><button class="btn" type="button" id="plReset">gen = slots(540, 660)</button></div>
    <p class="status-line" id="plStatus">The generator is created but hasn't run a single line.</p>''',
   "js": '''    const SRC = ['def slots(start, end, step=30):', '    t = start', '    while t < end:', '        yield t', '        t += step'];
    let t = null, phase = 'new', got = [];
    const hm = m => `${Math.floor(m / 60)}:${String(m % 60).padStart(2, '0')}`;
    function draw(hl) {
      $('plCode').innerHTML = SRC.map((l, i) => `<span class="ln${hl.includes(i) ? ' on' : ''}${i === 3 && phase === 'paused' ? ' pl-pause' : ''}">${K.pyHighlight(l)}</span>`).join('');
      $('plState').innerHTML = phase === 'new' ? 'not started' : phase === 'paused' ? 'paused at line 4 (yield)' : '<span class="bad-text">finished</span>';
      $('plVars').textContent = phase === 'paused' ? `start=540  end=660  step=30  t=${t}` : '';
      $('plGot').textContent = got.length ? got.map(hm).join(', ') : '—';
    }
    $('plNext').addEventListener('click', () => {
      if (phase === 'done') { $('plStatus').innerHTML = '<b class="bad-text">StopIteration</b> · a finished generator stays finished. Create a new one to start over.'; return; }
      let ran;
      if (phase === 'new') { t = 540; ran = [1, 2, 3]; }
      else { t += 30; ran = [4, 2]; if (t < 660) ran.push(3); }
      if (t < 660) { phase = 'paused'; got.push(t); $('plStatus').innerHTML = `Ran lines ${ran.map(i => i + 1).join(', ')} and yielded <b class="mono">${t}</b> (${hm(t)}). Paused, keeping t.`; }
      else { phase = 'done'; $('plStatus').innerHTML = `Ran <span class="mono">t += step</span> (t = ${t}), the while test failed, the function ended → <b>StopIteration</b>. A for loop would stop here.`; }
      draw(ran);
    });
    $('plReset').addEventListener('click', () => { t = null; phase = 'new'; got = []; draw([]); $('plStatus').textContent = 'A fresh generator: nothing has run yet.'; });
    draw([]);'''},
  {"id": "mem", "title": "List or generator: memory", "kind": "sys.getsizeof() of a list comprehension vs a generator expression",
   "html": '''    <label class="label" for="mmN">n = <span class="mono" id="mmNv"></span></label><input type="range" id="mmN" min="0" max="5" value="3" style="width:100%">
    <div class="mm-row"><span class="mono">list</span><div class="mm-bar"><i id="mmL"></i></div><span class="mono" id="mmLv"></span></div>
    <div class="mm-row"><span class="mono">generator</span><div class="mm-bar"><i id="mmG"></i></div><span class="mono" id="mmGv"></span></div>
    <p class="status-line" id="mmStatus"></p>''',
   "js": '''    const MEM = __MEM__;
    const fmt = b => b >= 1e6 ? (b / 1e6).toFixed(1) + ' MB' : b >= 1e3 ? (b / 1e3).toFixed(1) + ' KB' : b + ' B';
    function draw() {
      const m = MEM[+$('mmN').value]; const mx = MEM[MEM.length - 1].list;
      $('mmNv').textContent = m.n.toLocaleString('en');
      $('mmL').style.width = Math.max(1, Math.log10(m.list) / Math.log10(mx) * 100) + '%';
      $('mmG').style.width = Math.max(1, Math.log10(m.gen) / Math.log10(mx) * 100) + '%';
      $('mmLv').textContent = fmt(m.list); $('mmGv').textContent = fmt(m.gen);
      $('mmStatus').innerHTML = `The list holds all ${m.n.toLocaleString('en')} results at once; the generator stays at ${m.gen} bytes whatever n is. (Log scale; the list figure counts only its slots, not the int objects themselves.)`;
    }
    $('mmN').addEventListener('input', draw); draw();'''.replace('__MEM__', json.dumps(MEM))}
 ],
 "style": '''  .ln.pl-pause { box-shadow: inset 3px 0 0 var(--accent-text); }
  .mm-row { display: grid; grid-template-columns: 90px 1fr 80px; gap: 10px; align-items: center; margin-top: 10px; }
  .mm-bar { height: 18px; border-radius: 9px; background: var(--panel-2); border: 1px solid var(--line); overflow: hidden; }
  .mm-bar i { display: block; height: 100%; background: var(--cyan); transition: width .3s; }''',
 "cheat": [
  ["Produce a sequence step by step", "A generator function with <span class=\"mono\">yield</span>"],
  ["One-off lazy transform", "Generator expression <span class=\"mono\">(f(x) for x in xs)</span>"],
  ["Huge file or API pages", "Yield one record at a time instead of building a list"],
  ["Need to loop twice", "Make a list, or call the generator function again"],
  ["Get one item / safe default", "<span class=\"mono\">next(it)</span> / <span class=\"mono\">next(it, None)</span>"],
  ["Delegate to another generator", "<span class=\"mono\">yield from other()</span>"]
 ],
 "ref_title": "Reference: iterable vs iterator vs generator",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th></th><th>What it is</th><th>Examples</th><th>Reusable?</th></tr></thead>
        <tbody>
          <tr><td>Iterable</td><td>anything with <span class="mono">__iter__</span>: you can loop over it</td><td class="mono">list, str, dict, range, file</td><td>yes (each loop gets a fresh iterator)</td></tr>
          <tr><td>Iterator</td><td>has <span class="mono">__next__</span>; remembers its position</td><td class="mono">iter(list), zip(), map(), file lines</td><td>no, one pass</td></tr>
          <tr><td>Generator</td><td>an iterator written as a function with yield, or as <span class="mono">( … for … )</span></td><td class="mono">slots(540, 660)</td><td>no, one pass</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Added", "<b>From your Notion plan:</b> \"Iterators &amp; generators (yield)\" (8-week plan, Week 2). The repo meets lazy objects (reversed, zip, map) but never writes its own."],
  ["Added", "<b>range() is not a generator:</b> it's a lazy <i>sequence</i>. You can index it, take its len() and loop over it many times."],
  ["Added", "<b>Real use:</b> reading a large CSV with <span class=\"mono\">csv.DictReader</span> is already lazy; wrapping it in a generator that cleans each row keeps memory flat however big the file is."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">def g():\\n    yield 1\\n    yield 2\\nprint(sum(g()), len(list(g())))</span>", "code": "def g():\n    yield 1\n    yield 2\nprint(sum(g()), len(list(g())))", "expect": "3 2", "a": "<b class=\"mono\">3 2</b>. Each call to g() makes a new generator."},
  {"q": "<span class=\"mono\">r = range(3)\\nprint(list(r), list(r), r[1])</span>", "code": "r = range(3)\nprint(list(r), list(r), r[1])", "expect": "[0, 1, 2] [0, 1, 2] 1", "a": "<b class=\"mono\">[0, 1, 2] [0, 1, 2] 1</b>. range is reusable and indexable."},
  {"q": "<span class=\"mono\">it = iter([1, 2, 3])\\nfor x in it:\\n    print(x, next(it))</span>", "code": "it = iter([1, 2, 3])\nfor x in it:\n    print(x, next(it))", "expect": "1 2", "a": "<b class=\"mono\">1 2</b> then <b>StopIteration</b>. The loop and your next() share one iterator: x=1, next→2, x=3, next→nothing left."}
 ],
 "sources": "From the Notion plan (Planning for python learning, Week 2: iterators &amp; generators). Python docs: Iterators, Generators, itertools."
}
