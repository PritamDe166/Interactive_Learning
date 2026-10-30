SPEC = {
 "slug": "scope", "num": 9, "part": "Functions",
 "title": "Scope (LEGB)", "title_plain": "Scope (LEGB)",
 "desc": "Python fundamentals: local, enclosing, global and built-in scopes, how Python looks up a name, global and nonlocal, closures, and UnboundLocalError.",
 "lede": [
  "To find a name, Python searches four places in order: <b>L</b>ocal → <b>E</b>nclosing function → <b>G</b>lobal (module) → <b>B</b>uilt-ins. First match wins.",
  "<b>Reading</b> an outer name works automatically. <b>Assigning</b> to a name inside a function makes it <b>local</b> to that function.",
  "To assign to a module-level name, declare <span class=\"mono\">global</span>; for the enclosing function's name, declare <span class=\"mono\">nonlocal</span>.",
  "An inner function that keeps using an outer function's variable after it returns is a <b>closure</b>."
 ],
 "walk": {"title": "names inside nested functions", "code":
'''clinic = "Pune"
count = 0
def outer():
    doctor = "Rao"
    def inner():
        patient = "Asha"
        print(patient, doctor, clinic, len("ab"))
    inner()
def bump():
    global count
    count += 1
def make_counter():
    n = 0
    def step():
        nonlocal n
        n += 1
        return n
    return step
outer()
bump()
tick = make_counter()
print(count, tick(), tick())''',
 "steps": [
  {"at": {"after": 12}, "title": "The global scope", "text": "Module-level names live in the <b>global</b> frame: two variables and three functions. Every function in this file can <b>read</b> them."},
  {"at": {"event": "call", "n": 2}, "title": "Nested frames", "text": "<span class=\"mono\">outer()</span> made <span class=\"mono\">doctor</span> and defined <span class=\"mono\">inner</span>; now <span class=\"mono\">inner()</span> runs on top of it. Three frames are alive at once."},
  {"at": {"after": 7}, "title": "One line, all four scopes", "text": "In <span class=\"mono\">print(patient, doctor, clinic, len(\"ab\"))</span>: <b>patient</b> is Local, <b>doctor</b> comes from the Enclosing <span class=\"mono\">outer</span>, <b>clinic</b> is Global, and <b>len</b> is a Built-in. Python checked L, E, G, B in that order for each.", "tip": "The interactive LEGB explorer below animates this search."},
  {"at": {"event": "call", "n": 3}, "title": "global: assign to the module name", "text": "<span class=\"mono\">count += 1</span> assigns, which would normally create a local <span class=\"mono\">count</span>. <span class=\"mono\">global count</span> tells Python to use the module-level one instead."},
  {"at": {"after": 11}, "title": "The global changed", "text": "The global frame's <span class=\"mono\">count</span> is now 1. Without the <span class=\"mono\">global</span> line this function would crash with <b>UnboundLocalError</b> (see puzzle 2)."},
  {"at": {"event": "return", "n": 4}, "title": "make_counter returns a function", "text": "<span class=\"mono\">make_counter</span> created <span class=\"mono\">n = 0</span> and a function <span class=\"mono\">step</span> that uses <span class=\"mono\">n</span>, then returned <span class=\"mono\">step</span>. Its frame is about to end…"},
  {"at": {"event": "call", "n": 5}, "title": "…but n survives: a closure", "text": "<span class=\"mono\">tick</span> points to the inner <span class=\"mono\">step</span> function, which still remembers <span class=\"mono\">n</span> from the finished <span class=\"mono\">make_counter</span> call. That remembered environment is the <b>closure</b>."},
  {"at": {"event": "return", "n": 5}, "title": "nonlocal updates the enclosing n", "text": "<span class=\"mono\">nonlocal n</span> means \"the n from the enclosing function\", so <span class=\"mono\">n += 1</span> updates it to 1 instead of creating a new local."},
  {"at": "end", "title": "State kept between calls", "text": "The second <span class=\"mono\">tick()</span> returns 2: the closure's <span class=\"mono\">n</span> persisted. This is how decorators and callback factories keep state without globals."}
 ]},
 "walk_out": "Asha Rao Pune 2 / 1 1 2",
 "puzzles": [
  {"id": "p1", "name": "1 · assign makes it local", "code": "var1 = 10\ndef change():\n    var1 = 20\nchange()\nprint(var1)", "q": "What's printed?", "opts": ["10", "20", "UnboundLocalError"], "a": 0,
   "why": "Inside <span class=\"mono\">change</span>, <span class=\"mono\">var1 = 20</span> creates a <b>new local</b> var1. The global one is untouched. (Your Scopes.py shows this as \"incorrect\".)"},
  {"id": "p2", "name": "2 · read then assign", "code": "count = 0\ndef bump():\n    count += 1\nbump()", "q": "What happens?", "opts": ["count becomes 1", "UnboundLocalError: cannot access local variable 'count' where it is not associated with a value", "NameError: name 'count' is not defined"], "a": 1,
   "why": "Because <span class=\"mono\">count</span> is assigned somewhere in the function, Python treats it as local for the <b>whole</b> function, so reading it first fails. Add <span class=\"mono\">global count</span>, or better, pass and return the value."},
  {"id": "p3", "name": "3 · shadowing a built-in", "code": "list = [1, 2]\nprint(list)\nprint(list(\"ab\"))", "q": "What's printed?", "opts": ["[1, 2] / ['a', 'b']", "[1, 2] / TypeError: 'list' object is not callable", "TypeError"], "a": 1,
   "why": "A global named <span class=\"mono\">list</span> is found (G) before the built-in (B). Avoid naming variables list, dict, str, id, sum, type…"},
  {"id": "p4", "name": "4 · loop variable in a function", "code": "def f():\n    for i in range(3):\n        pass\n    return i\nprint(f())", "q": "What's printed?", "opts": ["2", "3", "NameError"], "a": 0,
   "why": "Blocks (for, if, while) don't create scopes in Python. <span class=\"mono\">i</span> is a local of f with its last value, 2."},
  {"id": "p5", "name": "5 · late binding", "code": "funcs = []\nfor i in range(3):\n    funcs.append(lambda: i)\nprint([f() for f in funcs])", "q": "What's printed?", "opts": ["[0, 1, 2]", "[2, 2, 2]", "[3, 3, 3]"], "a": 1,
   "why": "Each lambda looks <span class=\"mono\">i</span> up <b>when called</b>, and by then the loop has finished with i = 2. Capture the value with a default: <span class=\"mono\">lambda i=i: i</span>."},
  {"id": "p6", "name": "6 · nonlocal", "code": "def outer():\n    msg = \"old\"\n    def inner():\n        nonlocal msg\n        msg = \"new\"\n    inner()\n    return msg\nprint(outer())", "q": "What's printed?", "opts": ["old", "new", "SyntaxError"], "a": 1,
   "why": "<span class=\"mono\">nonlocal</span> makes the assignment update outer's <span class=\"mono\">msg</span>."}
 ],
 "runner_extra": [{"label": "Your turn: avoid global, return instead", "code": 'def bump(count):\n    return count + 1\n\ncount = 0\ncount = bump(count)\ncount = bump(count)\nprint(count)\n# Try: write make_greeter(greeting) that returns a function greet(name)'}],
 "custom": [
  {"id": "legb", "title": "LEGB lookup explorer", "kind": "Look up a name from inside inner() · watch Python search outward",
   "html": '''    <div class="chips" id="lgBtns"><button class="chip-btn mono" type="button" data-n="patient">patient</button><button class="chip-btn mono" type="button" data-n="doctor">doctor</button><button class="chip-btn mono" type="button" data-n="clinic">clinic</button><button class="chip-btn mono" type="button" data-n="len">len</button><button class="chip-btn mono" type="button" data-n="room">room</button></div>
    <div class="lg-box lg-b" id="lgB"><div class="lg-h"><b>B</b>uilt-in <span class="mono">print len sum list …</span></div>
      <div class="lg-box lg-g" id="lgG"><div class="lg-h"><b>G</b>lobal (module) <span class="mono">clinic = "Pune"</span></div>
        <div class="lg-box lg-e" id="lgE"><div class="lg-h"><b>E</b>nclosing: outer() <span class="mono">doctor = "Rao"</span></div>
          <div class="lg-box lg-l" id="lgL"><div class="lg-h"><b>L</b>ocal: inner() <span class="mono">patient = "Asha"</span></div><div class="lg-probe mono" id="lgProbe">print(?)</div></div>
        </div>
      </div>
    </div>
    <p class="status-line" id="lgStatus">Pick a name.</p>''',
   "js": '''    const WHERE = { patient: 'lgL', doctor: 'lgE', clinic: 'lgG', len: 'lgB' };
    const VAL = { patient: "'Asha'", doctor: "'Rao'", clinic: "'Pune'", len: '&lt;built-in function len&gt;' };
    const ORDER = ['lgL', 'lgE', 'lgG', 'lgB'], NAME = { lgL: 'Local', lgE: 'Enclosing', lgG: 'Global', lgB: 'Built-in' };
    async function go(n) {
      const run = K.newRun('lg');
      ORDER.forEach(id => $(id).classList.remove('miss', 'hit', 'look'));
      $('lgProbe').textContent = 'print(' + n + ')';
      try {
        for (const id of ORDER) {
          $(id).classList.add('look'); $('lgStatus').innerHTML = `Checking <b>${NAME[id]}</b> for <span class="mono">${n}</span>…`;
          await K.sleep(600, run); $(id).classList.remove('look');
          if (WHERE[n] === id) { $(id).classList.add('hit'); $('lgStatus').innerHTML = `Found in <b>${NAME[id]}</b> → <span class="mono">${VAL[n]}</span>. The search stops at the first match.`; return; }
          $(id).classList.add('miss');
        }
        $('lgStatus').innerHTML = `<b class="bad-text mono">NameError: name '${n}' is not defined</b> · not in any of the four scopes.`;
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    $('lgBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => go(b.dataset.n)));'''}
 ],
 "extra_traces": {},
 "style": '''  .lg-box { border: 2px solid var(--line); border-radius: 14px; padding: 10px 12px 12px; margin-top: 10px; transition: all .3s; }
  .lg-h { font-size: 14px; color: var(--fg-soft); margin-bottom: 4px; }
  .lg-h b { color: var(--accent-text); font-size: 17px; }
  .lg-h .mono { color: var(--muted); margin-left: 8px; font-size: 13px; }
  .lg-box.look { border-color: var(--cyan); box-shadow: 0 0 0 3px var(--teal-wash); }
  .lg-box.miss > .lg-h { opacity: .5; text-decoration: line-through; }
  .lg-box.hit { border-color: var(--teal); background: var(--teal-wash); }
  .lg-probe { margin-top: 8px; padding: 8px 12px; border-radius: 8px; background: var(--code-bg); border: 1px solid var(--line); display: inline-block; }''',
 "cheat": [
  ["Read an outer variable", "Just use it (LEGB finds it)"],
  ["Change a module variable inside a function", "Prefer passing it in and returning; otherwise <span class=\"mono\">global x</span>"],
  ["Change an enclosing function's variable", "<span class=\"mono\">nonlocal x</span>"],
  ["UnboundLocalError", "You assign to that name somewhere in the function: it's local everywhere in it"],
  ["A variable named list / str / id", "Rename it; it hides the built-in"],
  ["Keep state between calls without globals", "A closure, or a class"]
 ],
 "ref_title": "Reference: what creates a scope",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Construct</th><th>New scope?</th><th>Note</th></tr></thead>
        <tbody>
          <tr><td>Module (the .py file)</td><td>yes: global</td><td>one per file; <span class="mono">import</span> gives access to another module's globals</td></tr>
          <tr><td><span class="mono">def</span> / <span class="mono">lambda</span></td><td>yes: local</td><td>a new frame on every call</td></tr>
          <tr><td>Class body</td><td>yes, but special</td><td>methods don't see class-level names directly; use <span class="mono">self.x</span> or <span class="mono">ClassName.x</span></td></tr>
          <tr><td>Comprehension</td><td>yes</td><td>its loop variable doesn't leak</td></tr>
          <tr><td><span class="mono">if</span> / <span class="mono">for</span> / <span class="mono">while</span> / <span class="mono">with</span> / <span class="mono">try</span></td><td>no</td><td>names created inside live in the surrounding function or module</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Corrected", "<b>Scope_Examples.py, Exercise 5:</b> the message says <span class=\"mono\">\"This variable is in inner function\"</span>, but <span class=\"mono\">message</span> is created in <b>outerfunction1</b> (the enclosing scope) and only read by the inner one."],
  ["Corrected", "<b>Scopes.py:</b> <span class=\"mono\">local_scope()</span> is defined but never called, so its print never runs. Mixed naming (<span class=\"mono\">fetchGlobalVar</span> vs <span class=\"mono\">change_global_correct</span>): PEP 8 uses snake_case for functions."],
  ["Added", "<b>UnboundLocalError</b> (puzzle 2) is the error you hit when you forget <span class=\"mono\">global</span>/<span class=\"mono\">nonlocal</span>; the repo shows the fix but not the failure. Since 3.12 the message says \"cannot access local variable … where it is not associated with a value\"."],
  ["Added", "<b>Use global sparingly.</b> Functions that take inputs and return outputs are easier to test. Closures (shown in the walkthrough) are the foundation for decorators."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">x = 1\\ndef f(): return x\\nx = 2\\nprint(f())</span>", "code": "x = 1\ndef f(): return x\nx = 2\nprint(f())", "expect": "2", "a": "<b class=\"mono\">2</b>. Names are looked up when the function runs, not when it's defined."},
  {"q": "<span class=\"mono\">def f():\\n    y = 5\\nf()\\nprint(y)</span>", "code": "def f():\n    y = 5\nf()\nprint(y)", "expect": "NameError", "a": "<b class=\"mono\">NameError</b>. y was local to f and vanished when the call ended."},
  {"q": "<span class=\"mono\">def f():\\n    global z\\n    z = 3\\nf(); print(z)</span>", "code": "def f():\n    global z\n    z = 3\nf(); print(z)", "expect": "3", "a": "<b class=\"mono\">3</b>. global can even create a module-level name."},
  {"q": "<span class=\"mono\">def adder(n):\\n    return lambda x: x + n\\nadd5 = adder(5); print(add5(10))</span>", "code": "def adder(n):\n    return lambda x: x + n\nadd5 = adder(5); print(add5(10))", "expect": "15", "a": "<b class=\"mono\">15</b>. The lambda closes over n = 5."},
  {"q": "<span class=\"mono\">x = \"g\"\\ndef f():\\n    x = \"l\"\\n    def g(): return x\\n    return g()\\nprint(f())</span>", "code": "x = \"g\"\ndef f():\n    x = \"l\"\n    def g(): return x\n    return g()\nprint(f())", "expect": "l", "a": "<b class=\"mono\">l</b>. Enclosing beats Global."},
  {"q": "<span class=\"mono\">if True:\\n    w = 1\\nprint(w)</span>", "code": "if True:\n    w = 1\nprint(w)", "expect": "1", "a": "<b class=\"mono\">1</b>. An if block is not a scope."}
 ],
 "sources": "Sources: Python_Fundamentals repo (Basics/Scopes.py, Basics/Scope_Examples.py)."
}
