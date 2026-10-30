import json, ast
def book(patient, slot, room="A1", *extras, urgent=False, **notes):
    return dict(patient=patient, slot=slot, room=room, extras=extras, urgent=urgent, notes=notes)
CALLS = ['book("Asha", "9:00")', 'book("Asha", "9:00", "B2")', 'book("Asha", slot="9:00", urgent=True)',
         'book("Asha", "9:00", "B2", "x-ray", "ECG")', 'book("Asha", "9:00", doctor="Rao", floor=2)',
         'book(slot="9:00", patient="Asha")', 'book("Asha", "9:00", True)', 'book("Asha")', 'book("Asha", "9:00", patient="Ravi")']
PARAMS = ["patient", "slot", "room", "extras", "urgent", "notes"]
BIND = []
for c in CALLS:
    node = ast.parse(c, mode="eval").body
    npos = len(node.args); kws = {k.arg for k in node.keywords}
    try:
        r = eval(c, {"book": book})
        slots = []
        for i, p in enumerate(PARAMS):
            if p == "extras": src = "collected by *extras" if r[p] else "nothing left over"
            elif p == "notes": src = "collected by **notes" if r[p] else "no unknown keywords"
            elif p in kws: src = "keyword"
            elif i < 3 and i < npos: src = "position " + str(i + 1)
            else: src = "default"
            slots.append({"p": p, "v": repr(r[p]), "src": src})
        BIND.append({"call": c, "ok": True, "slots": slots})
    except TypeError as e:
        BIND.append({"call": c, "ok": False, "err": "TypeError: " + str(e)})

SPEC = {
 "slug": "functions-arguments", "num": 8, "part": "Functions",
 "title": "Functions &amp; arguments", "title_plain": "Functions & arguments",
 "desc": "Python fundamentals: def and return, the call stack, positional and keyword arguments, defaults, *args and **kwargs, returning several values, and the mutable default trap.",
 "lede": [
  "<span class=\"mono\">def</span> creates a <b>function object</b> and a name for it. Calling it creates a fresh <b>frame</b> holding the parameters and local variables.",
  "Arguments bind to parameters <b>by position</b>, then <b>by keyword</b>; anything not given falls back to its <b>default</b>.",
  "<span class=\"mono\">*args</span> collects extra positional values into a <b>tuple</b>; <span class=\"mono\">**kwargs</span> collects extra keywords into a <b>dict</b>.",
  "<span class=\"mono\">return a, b</span> returns <b>one tuple</b>. No return means the function returns <span class=\"mono\">None</span>.",
  "Defaults are created <b>once</b>, when <span class=\"mono\">def</span> runs. A mutable default like <span class=\"mono\">[]</span> is shared between calls."
 ],
 "walk": {"title": "functions for a clinic bill", "code":
'''def with_tax(amount, rate=0.18):
    tax = amount * rate
    return amount + tax

def summary(name, *fees, **info):
    total = sum(fees)
    return name, total, info

def add_visit(name, log=[]):
    log.append(name)
    return log

bill = with_tax(1000)
low = with_tax(1000, rate=0.05)
who, total, extra = summary("Asha", 400, 600, city="Pune")
print(bill, low, who, total, extra)
print(add_visit("x"), add_visit("y"))''',
 "steps": [
  {"at": {"after": 9}, "title": "def only creates function objects", "text": "Running the three <span class=\"mono\">def</span> lines runs <b>none</b> of their bodies. It makes three function objects and three names. The default values (0.18 and the empty list) are created now, once."},
  {"at": {"event": "call", "n": 1}, "title": "A call opens a new frame", "text": "<span class=\"mono\">with_tax(1000)</span> creates a frame for this call. <span class=\"mono\">amount</span> gets 1000 by position; <span class=\"mono\">rate</span> wasn't given, so it uses its default 0.18."},
  {"at": {"after": 2, "n": 1}, "title": "Locals live in that frame", "text": "<span class=\"mono\">tax</span> exists only inside this call's frame. The global frame can't see it."},
  {"at": {"event": "return", "n": 1}, "title": "return hands back a value", "text": "The return value (1180.0) goes back to the caller and the frame is <b>thrown away</b>, along with <span class=\"mono\">tax</span>. The caller binds the value to <span class=\"mono\">bill</span>."},
  {"at": {"event": "call", "n": 2}, "title": "Keyword arguments", "text": "<span class=\"mono\">rate=0.05</span> passes a value <b>by name</b>, overriding the default. Keywords make calls readable and order-independent."},
  {"at": {"event": "call", "n": 3}, "title": "*fees and **info collect extras", "text": "After <span class=\"mono\">name</span> takes \"Asha\", the leftover positional values <b>400, 600</b> are packed into a <b>tuple</b> <span class=\"mono\">fees</span>. The unknown keyword <span class=\"mono\">city=\"Pune\"</span> goes into a <b>dict</b> <span class=\"mono\">info</span>."},
  {"at": 18, "title": "Returning several values = one tuple", "text": "<span class=\"mono\">return name, total, info</span> built a single tuple, and the caller unpacked it into three names. Your repo's <span class=\"mono\">calculator_func</span> does the same."},
  {"at": {"event": "return", "n": 4}, "title": "The mutable default trap", "text": "<span class=\"mono\">add_visit(\"x\")</span> appended to the default list, the one created at <span class=\"mono\">def</span> time. Watch the next call: it gets the <b>same</b> list, not a fresh one."},
  {"at": "end", "title": "…both calls share one list", "text": "The second call returned the same list, now <span class=\"mono\">['x', 'y']</span>, so both printed values show both names. The fix: <span class=\"mono\">def add_visit(name, log=None):</span> then <span class=\"mono\">if log is None: log = []</span>.", "tip": "Linters flag this pattern (Ruff B006). Use None as the default for lists, dicts and sets."}
 ]},
 "walk_out": "1180.0 1050.0 Asha 1000 {'city': 'Pune'} / ['x', 'y'] ['x', 'y']",
 "puzzles": [
  {"id": "p1", "name": "1 · grades() from the repo", "code": "def grades(num):\n    if num > 80:\n        return \"Grade A\"\n    elif num < 80 and num > 60:\n        return \"Grade B\"\n    else:\n        return \"Grade C\"\n\nprint(grades(80), grades(60))", "q": "What's printed?", "opts": ["Grade A Grade B", "Grade B Grade C", "Grade C Grade C"], "a": 2,
   "why": "80 is neither &gt; 80 nor &lt; 80, and 60 is not &gt; 60, so both fall to <span class=\"mono\">else</span>. Use <span class=\"mono\">&gt;=</span>: <span class=\"mono\">if num &gt;= 80 … elif num &gt;= 60 …</span>."},
  {"id": "p2", "name": "2 · return inside a loop", "code": "def pet_details2(pet_type, **pet_details):\n    for key, value in pet_details.items():\n        return f\"{pet_type}: {key} is {value}\"\n\nprint(pet_details2(\"Dog\", name=\"Tommy\", age=3))", "q": "What's printed?", "opts": ["Dog: name is Tommy", "Dog: name is Tommy / Dog: age is 3", "Dog: age is 3"], "a": 0,
   "why": "<span class=\"mono\">return</span> ends the function on the <b>first</b> round. Collect the lines in a list and return after the loop."},
  {"id": "p3", "name": "3 · no return", "code": "def greet(name):\n    print(\"Hello\", name)\n\nresult = greet(\"Asha\")\nprint(result)", "q": "What's printed?", "opts": ["Hello Asha / Hello Asha", "Hello Asha / None", "None"], "a": 1,
   "why": "A function without <span class=\"mono\">return</span> returns <span class=\"mono\">None</span>. Printing and returning are different things."},
  {"id": "p4", "name": "4 · what is *args?", "code": "def show(*args, **kwargs):\n    print(type(args).__name__, args, kwargs)\n\nshow(1, 2, x=3)", "q": "What's printed?", "opts": ["list [1, 2] {'x': 3}", "tuple (1, 2) {'x': 3}", "tuple (1, 2, 3) {}"], "a": 1,
   "why": "Extra positionals become a <b>tuple</b>, extra keywords a <b>dict</b>. The names args/kwargs are just convention; the stars do the work."},
  {"id": "p5", "name": "5 · unpacking into a call", "code": "def slot(day, time, room):\n    return f\"{day} {time} in {room}\"\n\nparts = [\"Mon\", \"9:00\"]\nprint(slot(*parts, room=\"B2\"))", "q": "What's printed?", "opts": ["Mon 9:00 in B2", "TypeError: missing 1 required positional argument", "['Mon', '9:00'] in B2"], "a": 0,
   "why": "In a <b>call</b>, <span class=\"mono\">*parts</span> spreads the list out into separate positional arguments (and <span class=\"mono\">**d</span> spreads a dict into keywords)."},
  {"id": "p6", "name": "6 · the type hint lies", "code": "def calculator_func(a: int, b: int) -> int:\n    return a + b, a - b\n\nr = calculator_func(4, 2)\nprint(r, type(r).__name__)", "q": "What's printed?", "opts": ["6 int", "(6, 2) tuple", "TypeError: expected int"], "a": 1,
   "why": "Python doesn't check type hints at run time. The function returns a tuple, so the hint should be <span class=\"mono\">-&gt; tuple[int, int]</span>. A checker like mypy would catch it."}
 ],
 "runner_extra": [{"label": "Your turn: fix the mutable default", "code": 'def add_visit(name, log=None):\n    if log is None:\n        log = []\n    log.append(name)\n    return log\n\nprint(add_visit("x"), add_visit("y"))\n# Try: write average(*nums) that returns 0 when called with no numbers'}],
 "custom": [
  {"id": "bind", "title": "Argument binding", "kind": "Pick a call · see where each argument lands",
   "html": '''    <pre class="codeblock" style="min-height:0"><span class="ln"><span class="k">def</span> book(patient, slot, room=<span class="s">"A1"</span>, *extras, urgent=<span class="b">False</span>, **notes):</span></pre>
    <div class="chips" id="bdBtns"></div>
    <div class="bd-grid" id="bdGrid"></div>
    <p class="status-line" id="bdStatus">Pick a call to see where each argument lands.</p>''',
   "js": '''    const B = __B__;
    $('bdBtns').innerHTML = B.map((b, i) => `<button class="chip-btn mono" type="button" data-i="${i}" aria-pressed="false">${b.call}</button>`).join('');
    const KIND = { patient: 'required', slot: 'required', room: 'has default', extras: '*extras → tuple', urgent: 'keyword-only', notes: '**notes → dict' };
    function empty() { $('bdGrid').innerHTML = ['patient', 'slot', 'room', 'extras', 'urgent', 'notes'].map(p => `<div class="bd-slot"><div class="bd-p">${p}</div><div class="bd-k">${KIND[p]}</div><div class="bd-v mono">·</div><div class="bd-s"></div></div>`).join(''); }
    async function go(b) {
      const run = K.newRun('bd'); empty();
      const cells = [...$('bdGrid').children];
      try {
        if (!b.ok) { cells.forEach(c => c.classList.add('dim')); await K.sleep(200, run); $('bdStatus').innerHTML = `<b class="bad-text mono">${b.err.replace(/</g, '&lt;')}</b>`; return; }
        for (let k = 0; k < b.slots.length; k++) {
          const s = b.slots[k], c = cells[k];
          c.querySelector('.bd-v').textContent = s.v; c.querySelector('.bd-s').textContent = s.src;
          c.classList.add(s.src.startsWith('position') ? 'pos' : s.src === 'keyword' ? 'kw' : s.src.startsWith('collected') ? 'col' : 'def');
          await K.sleep(220, run);
        }
        $('bdStatus').innerHTML = 'Blue: by position · yellow: by keyword · green: collected by * or ** · grey: default or empty.';
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    $('bdBtns').querySelectorAll('button').forEach(btn => btn.addEventListener('click', () => {
      $('bdBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === btn))); go(B[+btn.dataset.i]);
    }));
    empty();'''.replace('__B__', json.dumps(BIND))}
 ],
 "style": '''  .bd-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; margin-top: 12px; }
  .bd-slot { border: 1.5px solid var(--line); border-radius: 10px; padding: 8px 10px; background: var(--panel-2); display: grid; gap: 2px; transition: all .25s; }
  .bd-slot.dim { opacity: .45; }
  .bd-p { font-family: var(--mono); font-weight: 700; }
  .bd-k { font-size: 11px; color: var(--muted); }
  .bd-v { font-size: 15px; overflow-wrap: anywhere; min-height: 22px; }
  .bd-s { font-size: 12px; color: var(--fg-soft); }
  .bd-slot.pos { border-color: var(--cyan); }
  .bd-slot.pos .bd-s { color: var(--cyan); }
  .bd-slot.kw { border-color: var(--accent-text); }
  .bd-slot.kw .bd-s { color: var(--accent-text); }
  .bd-slot.col { border-color: var(--teal); }
  .bd-slot.col .bd-s { color: var(--good-text); }''',
 "cheat": [
  ["Optional parameter", "Give it a default: <span class=\"mono\">def f(x, rate=0.18)</span>"],
  ["Default should be a list / dict", "<span class=\"mono\">=None</span>, then create it inside"],
  ["Any number of values", "<span class=\"mono\">*args</span> (tuple)"],
  ["Any extra named options", "<span class=\"mono\">**kwargs</span> (dict)"],
  ["Force callers to name an argument", "Put it after <span class=\"mono\">*</span>: <span class=\"mono\">def f(a, *, urgent=False)</span>"],
  ["Return several things", "<span class=\"mono\">return a, b</span> and unpack <span class=\"mono\">x, y = f()</span>"],
  ["Pass a list / dict as separate arguments", "<span class=\"mono\">f(*items)</span> / <span class=\"mono\">f(**options)</span>"]
 ],
 "ref_title": "Reference: parameter order",
 "ref_html": '''    <div class="card">
      <pre class="codeblock" style="min-height:0;margin:0"><span class="ln"><span class="k">def</span> f(pos_only, /, normal, default=<span class="n">1</span>, *args, kw_only, kw_default=<span class="n">2</span>, **kwargs):</span></pre>
      <ul class="cheat" style="margin-top:10px">
        <li><span>before <span class="mono">/</span></span><span>positional only (3.8+); rarely needed in your own code</span></li>
        <li><span><span class="mono">normal</span>, <span class="mono">default=1</span></span><span>by position or keyword; defaults must come after non-defaults</span></li>
        <li><span><span class="mono">*args</span> or a bare <span class="mono">*</span></span><span>everything after it must be passed by keyword</span></li>
        <li><span><span class="mono">**kwargs</span></span><span>always last</span></li>
        <li><span>In calls</span><span>positional arguments first, then keywords: <span class="mono">f(1, b=2)</span>, never <span class="mono">f(b=2, 1)</span></span></li>
      </ul>
    </div>''',
 "notes": [
  ["Corrected", "<b>grades() in Function_basics.py</b> returns \"Grade C\" for exactly 80 and 60 (see puzzle 1). Use <span class=\"mono\">&gt;=</span> boundaries, and since <span class=\"mono\">elif</span> already excludes the first case, <span class=\"mono\">num &lt; 80 and</span> isn't needed."],
  ["Corrected", "<b>pet_details2 in Keyword_Args_functions.py</b> returns inside the loop, so only the first keyword is reported (puzzle 2)."],
  ["Corrected", "<b>calculator_func</b> is annotated <span class=\"mono\">-&gt; int</span> but returns a 4-tuple, and <span class=\"mono\">a/b</span> fails when b is 0. Annotate <span class=\"mono\">-&gt; tuple[int, int, int, float]</span>. Likewise <span class=\"mono\">average_func([])</span> raises ZeroDivisionError."],
  ["Updated", "<b>Union[str, None]</b> (parse_age) is written <span class=\"mono\">str | None</span> since Python 3.10, with no import from <span class=\"mono\">typing</span>. More in Type hints."],
  ["Added", "<b>Mutable default arguments</b> aren't in the repo but are the classic Python function bug: the walkthrough's last two steps show it happening."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">def f(a, b=2): return a * b\\nprint(f(3), f(3, 3), f(b=1, a=5))</span>", "code": "def f(a, b=2): return a * b\nprint(f(3), f(3, 3), f(b=1, a=5))", "expect": "6 9 5", "a": "<b class=\"mono\">6 9 5</b>. Default, positional, then keywords in any order."},
  {"q": "<span class=\"mono\">def f(*n): return len(n)\\nprint(f(), f(1, 2, 3))</span>", "code": "def f(*n): return len(n)\nprint(f(), f(1, 2, 3))", "expect": "0 3", "a": "<b class=\"mono\">0 3</b>. With no extras, args is an empty tuple."},
  {"q": "<span class=\"mono\">def f(): return 1, 2\\nprint(type(f()).__name__)</span>", "code": "def f(): return 1, 2\nprint(type(f()).__name__)", "expect": "tuple", "a": "<b class=\"mono\">tuple</b>. The comma makes one tuple."},
  {"q": "<span class=\"mono\">def f(x): x = x + [1]\\nnums = [0]; f(nums); print(nums)</span>", "code": "def f(x): x = x + [1]\nnums = [0]; f(nums); print(nums)", "expect": "[0]", "a": "<b class=\"mono\">[0]</b>. <span class=\"mono\">x + [1]</span> makes a new list and rebinds the local x only. <span class=\"mono\">x.append(1)</span> would change nums."},
  {"q": "<span class=\"mono\">def f(**kw): return sorted(kw)\\nprint(f(b=1, a=2))</span>", "code": "def f(**kw): return sorted(kw)\nprint(f(b=1, a=2))", "expect": "['a', 'b']", "a": "<b class=\"mono\">['a', 'b']</b>. kwargs is a dict; sorting a dict sorts its keys."},
  {"q": "<span class=\"mono\">def f(a, *, b): return a + b\\nprint(f(1, b=2))</span>, and what does <span class=\"mono\">f(1, 2)</span> do?", "code": "def f(a, *, b): return a + b\nprint(f(1, b=2))", "expect": "3", "a": "<b class=\"mono\">3</b>; <span class=\"mono\">f(1, 2)</span> raises TypeError because b is keyword-only."}
 ],
 "sources": "Sources: Python_Fundamentals repo (Basics/Function_basics.py, Basics/Function_Arguments.py, Basics/Keyword_Args_functions.py)."
}
