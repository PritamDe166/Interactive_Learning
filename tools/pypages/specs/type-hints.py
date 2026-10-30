import json, subprocess, tempfile, os, io, contextlib, sys, re
CASES = [
 ("Wrong argument type", 'def with_tax(amount: float) -> float:\n    return amount * 1.18\n\nprint(with_tax("100"))'),
 ("Correct call", 'def with_tax(amount: float) -> float:\n    return amount * 1.18\n\nprint(with_tax(100))'),
 ("Possibly None", 'def find(name: str) -> str | None:\n    return None if name == "x" else name.upper()\n\nprint(find("asha").lower())'),
 ("None handled", 'def find(name: str) -> str | None:\n    return None if name == "x" else name.upper()\n\nresult = find("asha")\nif result is not None:\n    print(result.lower())'),
 ("Wrong return type", 'def total(fees: list[int]) -> int:\n    return sum(fees) / len(fees)\n\nprint(total([450, 800]))'),
 ("Dict value type", 'fees: dict[str, int] = {"Asha": 450}\nfees["Ravi"] = "800"\nprint(fees)'),
 ("Typo in attribute", 'from dataclasses import dataclass\n\n@dataclass\nclass Patient:\n    name: str\n    age: int\n\np = Patient("Asha", 35)\nprint(p.agee)'),
]
TH = []
d = tempfile.mkdtemp()
for title, code in CASES:
    f = os.path.join(d, "check.py"); open(f, "w").write(code)
    r = subprocess.run([sys.executable, "-m", "mypy", "--no-error-summary", "--hide-error-context", "--no-color-output", "--no-incremental", f], capture_output=True, text=True)
    mp = [re.sub(r"^.*check\.py:", "line ", l) for l in r.stdout.strip().splitlines() if l.strip()]
    buf = io.StringIO(); ns = {"__name__": "__main__"}
    try:
        with contextlib.redirect_stdout(buf): exec(compile(code, "check.py", "exec"), ns)
        rt = buf.getvalue().strip()
    except Exception as e:
        rt = (buf.getvalue() + f"{type(e).__name__}: {e}").strip()
    TH.append({"title": title, "code": code, "mypy": mp or ["Success: no issues found"], "run": rt})
MYPY_V = subprocess.run([sys.executable, "-m", "mypy", "--version"], capture_output=True, text=True).stdout.split()[1]

SPEC = {
 "slug": "type-hints", "num": 19, "part": "Going further",
 "title": "Type hints", "title_plain": "Type hints",
 "desc": "Python fundamentals: annotating variables, parameters and return values, built-in generics like list[int], X | None, and what a type checker such as mypy catches that Python itself doesn't.",
 "lede": [
  "Type hints describe what a value <b>should</b> be: <span class=\"mono\">def with_tax(amount: float) -&gt; float:</span>.",
  "Python <b>does not check them at run time</b>. They're read by your editor and by type checkers such as <b>mypy</b> or <b>pyright</b> before the code runs.",
  "Modern syntax: <span class=\"mono\">list[int]</span>, <span class=\"mono\">dict[str, float]</span>, <span class=\"mono\">str | None</span> (3.10+). No <span class=\"mono\">typing</span> import needed for these.",
  "Hints document intent, power autocomplete, and catch whole classes of bugs (None, wrong types, typos) early: the closest Python gets to C#'s compiler checks."
 ],
 "walk": {"title": "annotations are stored, not enforced", "code":
'''def with_tax(amount: float, rate: float = 0.18) -> float:
    return amount * (1 + rate)

def find(names: list[str], wanted: str) -> int | None:
    for i, name in enumerate(names):
        if name == wanted:
            return i
    return None

fee: float = with_tax(1000)
oops = with_tax("ab", 2)
where = find(["Asha", "Ravi"], "Ravi")
print(fee, oops, where)
print(with_tax.__annotations__)''',
 "steps": [
  {"at": {"after": 1}, "title": "Annotations on a function", "text": "<span class=\"mono\">amount: float</span> says the parameter should be a float; <span class=\"mono\">-&gt; float</span> describes the return value. Defaults still come after the annotation: <span class=\"mono\">rate: float = 0.18</span>."},
  {"at": {"after": 4}, "title": "Generics and Optional", "text": "<span class=\"mono\">list[str]</span> means \"a list of strings\". <span class=\"mono\">int | None</span> says the function may return an int <b>or</b> None, a warning to every caller to handle both."},
  {"at": 6, "title": "Variables can be annotated too", "text": "<span class=\"mono\">fee: float = …</span> works like a normal assignment plus a hint for tools."},
  {"at": 8, "title": "Python doesn't stop a wrong type", "text": "<span class=\"mono\">with_tax(\"ab\", 2)</span> passes a str where a float was promised. Python runs it anyway: inside, <span class=\"mono\">amount * (1 + rate)</span> is <span class=\"mono\">\"ab\" * 3</span>…", "tip": "mypy would flag this line before you ever ran it: Argument 1 has incompatible type \"str\"; expected \"float\"."},
  {"at": 10, "title": "…and gets a nonsense result", "text": "<span class=\"mono\">oops</span> is <span class=\"mono\">'ababab'</span>: no error, just a wrong value that surfaces later. That's the class of bug a type checker removes."},
  {"at": 19, "title": "Optional results", "text": "<span class=\"mono\">find</span> returned 1 here, but callers must still allow for None (not found) before using the result as a number."},
  {"at": "end", "title": "Hints live in __annotations__", "text": "Python stores the hints on the function as plain data. Frameworks such as FastAPI and Pydantic read them to validate requests at run time; Python itself never does."}
 ]},
 "walk_out": "1180.0 ababab 1 / {'amount': <class 'float'>, 'rate': <class 'float'>, 'return': <class 'float'>}",
 "puzzles": [
  {"id": "p1", "name": "1 · does this raise?", "code": "def double(n: int) -> int:\n    return n * 2\n\nprint(double(\"7\"))", "q": "What happens when you run it?", "opts": ["TypeError: expected int", "77", "14"], "a": 1,
   "why": "Hints aren't enforced. <span class=\"mono\">\"7\" * 2</span> is <span class=\"mono\">\"77\"</span>. A type checker would report the call."},
  {"id": "p2", "name": "2 · the return hint", "code": "def avg(xs: list[int]) -> int:\n    return sum(xs) / len(xs)\n\nr = avg([1, 2])\nprint(r, type(r).__name__)", "q": "What's printed?", "opts": ["1 int", "1.5 float", "TypeError"], "a": 1,
   "why": "<span class=\"mono\">/</span> always returns a float, whatever the hint says. The hint should be <span class=\"mono\">-&gt; float</span>, or use <span class=\"mono\">//</span> if you really want an int."},
  {"id": "p3", "name": "3 · annotation without a value", "code": "count: int\nprint(count)", "q": "What happens?", "opts": ["0", "None", "NameError: name 'count' is not defined"], "a": 2,
   "why": "A bare annotation records the type but doesn't create the variable."},
  {"id": "p4", "name": "4 · isinstance with |", "code": "def label(x: int | str) -> str:\n    if isinstance(x, int):\n        return f\"#{x:03d}\"\n    return x.upper()\n\nprint(label(7), label(\"vip\"))", "q": "What's printed?", "opts": ["#007 VIP", "7 vip", "#7 VIP"], "a": 0,
   "why": "Checking with isinstance <b>narrows</b> the type: a checker knows x is an int inside the if, and a str after it."}
 ],
 "runner_extra": [{"label": "Your turn: annotate and use TypedDict", "code": 'from typing import TypedDict\n\nclass PatientRow(TypedDict):\n    name: str\n    fee: int\n\ndef total(rows: list[PatientRow]) -> int:\n    return sum(r["fee"] for r in rows)\n\nrows: list[PatientRow] = [{"name": "Asha", "fee": 450}, {"name": "Ravi", "fee": 800}]\nprint(total(rows))\nprint(total.__annotations__)'}],
 "custom": [
  {"id": "chk", "title": "Run time vs type checker", "kind": "Same code, two verdicts · from real runs of Python and mypy",
   "html": '''    <div class="chips" id="ckBtns"></div>
    <pre class="codeblock" id="ckCode" style="min-height:0;margin-top:10px"></pre>
    <div class="two">
      <div class="card"><div class="label">python check.py</div><pre class="mono ck-out" id="ckRun"></pre></div>
      <div class="card"><div class="label">mypy check.py <span class="muted" id="ckVer"></span></div><pre class="mono ck-out" id="ckMy"></pre></div>
    </div>
    <p class="status-line" id="ckStatus"></p>''',
   "js": '''    const TH = __TH__;
    $('ckVer').textContent = '(mypy __V__)';
    $('ckBtns').innerHTML = TH.map((t, i) => `<button class="chip-btn" type="button" data-i="${i}" aria-pressed="${!i}">${t.title}</button>`).join('');
    function show(i) {
      const t = TH[i];
      $('ckCode').innerHTML = t.code.split('\\n').map(l => `<span class="ln">${K.pyHighlight(l)}</span>`).join('');
      const runErr = /Error:/.test(t.run), myErr = !/^Success/.test(t.mypy[0]);
      $('ckRun').innerHTML = `<span class="${runErr ? 'bad-text' : ''}">${t.run.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span>`;
      $('ckMy').innerHTML = t.mypy.map(l => `<span class="${/error/.test(l) ? 'bad-text' : /note/.test(l) ? 'muted' : 'ok-text'}">${l.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span>`).join('\\n');
      $('ckStatus').innerHTML = myErr && !runErr ? '<b>Runs without an error this time</b>, yet mypy found a bug waiting to happen: a wrong type stored or returned, or a None that will crash on other input.' : myErr && runErr ? 'Both fail, but mypy tells you <b>before</b> running, with the exact line.' : 'Clean for both.';
    }
    $('ckBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => { $('ckBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); show(+b.dataset.i); }));
    show(0);'''.replace('__TH__', json.dumps(TH)).replace('__V__', MYPY_V)}
 ],
 "style": '''  .ck-out { margin: 4px 0 0; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 13px; min-height: 48px; }''',
 "cheat": [
  ["Function signature", "<span class=\"mono\">def f(x: int, name: str = \"\") -&gt; bool:</span>"],
  ["Collections", "<span class=\"mono\">list[int]</span>, <span class=\"mono\">dict[str, float]</span>, <span class=\"mono\">tuple[int, str]</span>, <span class=\"mono\">set[str]</span>"],
  ["Might be missing", "<span class=\"mono\">str | None</span>, then check <span class=\"mono\">if x is not None</span>"],
  ["Either type", "<span class=\"mono\">int | str</span> + <span class=\"mono\">isinstance</span> to narrow"],
  ["Dict with fixed keys (JSON rows)", "<span class=\"mono\">TypedDict</span>, or a dataclass / Pydantic model"],
  ["Any object with a .send() method", "<span class=\"mono\">typing.Protocol</span> (structural typing)"],
  ["Check the whole project", "<span class=\"mono\">pip install mypy</span> → <span class=\"mono\">mypy .</span>; or pyright / your editor's checker"]
 ],
 "ref_title": "Reference: old vs modern spellings",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Older (typing module)</th><th>Modern</th><th>Since</th></tr></thead>
        <tbody>
          <tr><td class="mono">List[int], Dict[str, int]</td><td class="mono">list[int], dict[str, int]</td><td>3.9</td></tr>
          <tr><td class="mono">Optional[str]</td><td class="mono">str | None</td><td>3.10</td></tr>
          <tr><td class="mono">Union[int, str]</td><td class="mono">int | str</td><td>3.10</td></tr>
          <tr><td class="mono">TypeVar("T") + Generic[T]</td><td class="mono">def first[T](xs: list[T]) -&gt; T:</td><td>3.12</td></tr>
          <tr><td class="mono">Alias = list[int]</td><td class="mono">type Alias = list[int]</td><td>3.12</td></tr>
          <tr><td class="mono">"Patient" (quoted forward ref)</td><td class="mono">Patient (annotations evaluated lazily)</td><td>3.14</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Corrected", "<b>Function_basics.py</b> uses <span class=\"mono\">Union[str, None]</span> imported from typing; since Python 3.10 write <span class=\"mono\">str | None</span>. Its <span class=\"mono\">calculator_func(...) -&gt; int</span> actually returns a tuple of four numbers; mypy would report that line."],
  ["Added", "<b>From your Notion plan:</b> \"type hints\" (8-week plan, Week 5). Hints also matter for the AI-agent goal in your Roadmap: tool-calling libraries and FastAPI/Pydantic build JSON schemas from them."],
  ["Updated", "<b>Python 3.14</b> evaluates annotations lazily (PEP 649/749), so a class can refer to itself or to classes defined later without quotes or <span class=\"mono\">from __future__ import annotations</span>."]
 ],
 "quiz": [
  {"q": "Does Python raise an error for <span class=\"mono\">x: int = \"hello\"</span>?", "code": "x: int = \"hello\"\nprint(x)", "expect": "hello", "a": "<b>No</b>, it prints <span class=\"mono\">hello</span>. Only a type checker would complain."},
  {"q": "What does <span class=\"mono\">-&gt; None</span> on a function mean?", "a": "It returns nothing useful (implicitly None). A checker will flag callers that try to use the result, a common bug with methods like <span class=\"mono\">list.sort()</span>."},
  {"q": "<span class=\"mono\">def f(a: int, b: int = 2) -&gt; int: return a + b\\nprint(f.__annotations__[\"return\"].__name__)</span>", "code": "def f(a: int, b: int = 2) -> int: return a + b\nprint(f.__annotations__[\"return\"].__name__)", "expect": "int", "a": "<b class=\"mono\">int</b>. The return hint is stored under the key \"return\"."}
 ],
 "sources": "From the Notion plan (Planning for python learning, Week 5: type hints). mypy results generated with mypy __V__. Python docs: typing, PEP 604, PEP 695, PEP 649.".replace("__V__", MYPY_V)
}
