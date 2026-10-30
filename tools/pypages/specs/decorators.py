import json, io, contextlib
LAYERS = '''import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("log: calling", func.__name__)
        result = func(*args, **kwargs)
        print("log: returned", result)
        return result
    return wrapper

def require_role(role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(user, *args, **kwargs):
            if user["role"] != role:
                raise PermissionError(f"{user['name']} is not {role}")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator

@log_calls
@require_role("admin")
def delete_patient(user, patient_id):
    print("deleting", patient_id)
    return "deleted"
'''
RUNS = []
for who in [{"name": "Asha", "role": "admin"}, {"name": "Ravi", "role": "nurse"}]:
    ns = {}; exec(LAYERS, ns); buf = io.StringIO(); err = None
    with contextlib.redirect_stdout(buf):
        try: ns["delete_patient"](who, 42)
        except PermissionError as e: err = f"PermissionError: {e}"
    RUNS.append({"who": who, "out": buf.getvalue().splitlines(), "err": err})

SPEC = {
 "slug": "decorators", "num": 16, "part": "Going further",
 "title": "Decorators", "title_plain": "Decorators",
 "desc": "Python fundamentals: functions as objects, wrapper functions, the @ syntax, functools.wraps, decorators with arguments, and stacking decorators.",
 "lede": [
  "A <b>decorator</b> is a function that takes a function and returns a <b>replacement</b>, usually a wrapper that adds behaviour before and after the original.",
  "<span class=\"mono\">@log_calls</span> above <span class=\"mono\">def f</span> is shorthand for <span class=\"mono\">f = log_calls(f)</span>, run <b>once</b>, when the def runs.",
  "The wrapper uses <span class=\"mono\">*args, **kwargs</span> to accept any arguments and a <b>closure</b> to remember the original function.",
  "Always add <span class=\"mono\">@functools.wraps(func)</span> so the wrapper keeps the original's name and docstring. Used everywhere: logging, timing, caching, permissions, web routes."
 ],
 "walk": {"title": "logging every call", "code":
'''import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("calling", func.__name__, args)
        result = func(*args, **kwargs)
        print("returned", result)
        return result
    return wrapper

@log_calls
def with_tax(amount, rate=0.18):
    return amount * (1 + rate)

total = with_tax(1000)
print(total, with_tax.__name__)''',
 "steps": [
  {"at": 2, "title": "A function that takes a function", "text": "<span class=\"mono\">log_calls</span> is an ordinary function. Its parameter <span class=\"mono\">func</span> will receive another function object."},
  {"at": 5, "title": "@ runs the decorator at def time", "text": "When Python reaches <span class=\"mono\">@log_calls def with_tax…</span>, it first creates the with_tax function, then calls <span class=\"mono\">log_calls(with_tax)</span>. Nothing has been taxed yet."},
  {"at": 11, "title": "It returns a wrapper", "text": "Inside, <span class=\"mono\">def wrapper</span> builds a new function that remembers <span class=\"mono\">func</span> (a closure), and <span class=\"mono\">functools.wraps</span> copies the name and docstring onto it. The wrapper is returned…"},
  {"at": 13, "title": "…and takes over the name", "text": "The name <span class=\"mono\">with_tax</span> now points to the <b>wrapper</b>. The original function still exists, but only the wrapper can reach it, through <span class=\"mono\">func</span>.", "tip": "Equivalent without @: <span class=\"mono\">with_tax = log_calls(with_tax)</span>."},
  {"at": 14, "title": "Calling with_tax calls the wrapper", "text": "<span class=\"mono\">with_tax(1000)</span> actually runs <span class=\"mono\">wrapper(1000)</span>: <span class=\"mono\">args</span> is <span class=\"mono\">(1000,)</span>. It prints the \"calling\" line first."},
  {"at": 17, "title": "The wrapper calls the original", "text": "<span class=\"mono\">func(*args, **kwargs)</span> passes the same arguments on to the real with_tax. Now there are two frames: wrapper and the original."},
  {"at": 21, "title": "After-work, then return", "text": "The original returned 1180.0; the wrapper logs it and returns it to the caller unchanged. Callers don't know a wrapper exists."},
  {"at": "end", "title": "wraps kept the name", "text": "<span class=\"mono\">with_tax.__name__</span> is still <span class=\"mono\">'with_tax'</span>. Without <span class=\"mono\">@functools.wraps</span> it would say <span class=\"mono\">'wrapper'</span>, confusing logs, debuggers and frameworks."}
 ]},
 "walk_out": "calling with_tax (1000,) / returned 1180.0 / 1180.0 with_tax",
 "puzzles": [
  {"id": "p1", "name": "1 · when does the decorator run?", "code": "def shout(func):\n    print(\"decorating\", func.__name__)\n    return func\n\n@shout\ndef hello():\n    print(\"hello\")\n\nprint(\"ready\")\nhello()\nhello()", "q": "What's printed?", "opts": ["ready / decorating hello / hello / hello", "decorating hello / ready / hello / hello", "ready / decorating hello / hello / decorating hello / hello"], "a": 1,
   "why": "The decorator runs once, when the def is executed. Calls afterwards just call whatever it returned."},
  {"id": "p2", "name": "2 · forgetting return", "code": "def twice(func):\n    def wrapper(*args):\n        func(*args)\n        func(*args)\n    return wrapper\n\n@twice\ndef add(a, b):\n    return a + b\n\nprint(add(2, 3))", "q": "What's printed?", "opts": ["5", "10", "None"], "a": 2,
   "why": "The wrapper calls add twice but never returns anything, so the caller gets None. A wrapper must <span class=\"mono\">return func(*args, **kwargs)</span>."},
  {"id": "p3", "name": "3 · without wraps", "code": "def deco(func):\n    def wrapper():\n        return func()\n    return wrapper\n\n@deco\ndef report():\n    \"\"\"Daily report.\"\"\"\n\nprint(report.__name__, report.__doc__)", "q": "What's printed?", "opts": ["report Daily report.", "wrapper None", "deco None"], "a": 1,
   "why": "The name now points at <span class=\"mono\">wrapper</span>, with its own name and no docstring. <span class=\"mono\">@functools.wraps(func)</span> fixes both."},
  {"id": "p4", "name": "4 · stacking order", "code": "def a(f):\n    def w():\n        return \"a(\" + f() + \")\"\n    return w\n\ndef b(f):\n    def w():\n        return \"b(\" + f() + \")\"\n    return w\n\n@a\n@b\ndef x():\n    return \"x\"\n\nprint(x())", "q": "What's printed?", "opts": ["a(b(x))", "b(a(x))", "x"], "a": 0,
   "why": "Decorators apply bottom-up: <span class=\"mono\">x = a(b(x))</span>. So a's wrapper is outermost and runs first."},
  {"id": "p5", "name": "5 · a cache decorator", "code": "from functools import lru_cache\n\n@lru_cache\ndef fee(code):\n    print(\"looking up\", code)\n    return len(code) * 100\n\nprint(fee(\"ECG\"), fee(\"ECG\"), fee(\"XRAY\"))", "q": "What's printed?", "opts": ["looking up ECG / looking up ECG / looking up XRAY / 300 300 400", "looking up ECG / looking up XRAY / 300 300 400", "300 300 400"], "a": 1,
   "why": "<span class=\"mono\">lru_cache</span> remembers results by argument, so the second fee(\"ECG\") never runs the body. Only use it for functions without side effects."}
 ],
 "runner_extra": [{"label": "Your turn: a timing decorator", "code": 'import functools, time\n\ndef timed(func):\n    @functools.wraps(func)\n    def wrapper(*args, **kwargs):\n        start = time.perf_counter()\n        result = func(*args, **kwargs)\n        ms = (time.perf_counter() - start) * 1000\n        print(f"{func.__name__} took {ms:.2f} ms")\n        return result\n    return wrapper\n\n@timed\ndef total(n):\n    return sum(range(n))\n\nprint(total(100_000))'}],
 "custom": [
  {"id": "onion", "title": "Layers of wrappers", "kind": "Two decorators stacked on delete_patient · choose who calls it",
   "html": '''    <details class="rn-inputs" style="margin-bottom:10px"><summary>Show the decorator code</summary><pre class="codeblock" id="onCode" style="min-height:0"></pre></details>
    <div class="seg" id="onSeg" role="group" aria-label="Caller"><button type="button" data-v="0" aria-pressed="false">Asha (admin)</button><button type="button" data-v="1" aria-pressed="false">Ravi (nurse)</button></div>
    <div class="on-wrap"><div class="on-l on-log" id="onLog"><div class="on-h">@log_calls → wrapper</div>
      <div class="on-l on-role" id="onRole"><div class="on-h">@require_role("admin") → wrapper</div>
        <div class="on-l on-fn" id="onFn"><div class="on-h">delete_patient (original)</div></div>
      </div></div></div>
    <div class="two" style="margin-top:12px"><div class="card"><div class="label">Output</div><pre class="mono fl-out" id="onOut"></pre></div><div class="card"><div class="label">Caller gets</div><div class="mono" id="onRes" style="font-size:15px;overflow-wrap:anywhere">—</div></div></div>
    <p class="status-line" id="onStatus">Pick a caller.</p>''',
   "js": '''    const RUNS = __RUNS__, SRC = __SRC__;
    $('onCode').innerHTML = SRC.trimEnd().split('\\n').map(l => `<span class="ln">${K.pyHighlight(l)}</span>`).join('');
    async function go(i) {
      const run = K.newRun('on'), R = RUNS[i];
      ['onLog', 'onRole', 'onFn'].forEach(id => $(id).classList.remove('in', 'stop', 'out'));
      $('onOut').textContent = ''; $('onRes').textContent = '…';
      const out = t => { $('onOut').textContent += t + '\\n'; };
      try {
        $('onLog').classList.add('in'); out(R.out[0]); await K.sleep(700, run);
        $('onRole').classList.add('in'); await K.sleep(700, run);
        if (R.err) {
          $('onRole').classList.add('stop'); await K.sleep(500, run);
          $('onRes').innerHTML = `<span class="bad-text">${R.err}</span>`;
          $('onStatus').innerHTML = 'The role wrapper <b>raised before calling the original</b>. The exception passes back out through the log wrapper (which never prints "returned") to the caller.';
          return;
        }
        $('onFn').classList.add('in'); out(R.out[1]); await K.sleep(700, run);
        $('onFn').classList.add('out'); await K.sleep(400, run); $('onRole').classList.add('out'); await K.sleep(400, run);
        out(R.out[2]); $('onLog').classList.add('out');
        $('onRes').textContent = "'deleted'";
        $('onStatus').innerHTML = 'In through each wrapper, the original runs, then the result travels back out. The outer decorator (listed first) runs first.';
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    K.seg($('onSeg'), v => go(+v));'''.replace('__RUNS__', json.dumps(RUNS)).replace('__SRC__', json.dumps(LAYERS))}
 ],
 "style": '''  .on-wrap { margin-top: 12px; }
  .on-l { border: 2px solid var(--line); border-radius: 14px; padding: 10px 12px 12px; margin-top: 8px; transition: all .3s; }
  .on-h { font-family: var(--mono); font-size: 13px; color: var(--fg-soft); }
  .on-l.in { border-color: var(--cyan); box-shadow: 0 0 0 3px var(--teal-wash); }
  .on-l.out { border-color: var(--teal); box-shadow: none; }
  .on-l.stop { border-color: var(--red); }
  .on-fn { min-height: 44px; }
  .fl-out { margin: 4px 0 0; min-height: 60px; white-space: pre-wrap; font-size: 14px; }''',
 "cheat": [
  ["Add behaviour around many functions", "Write a decorator once, put <span class=\"mono\">@it</span> on each"],
  ["Writing the wrapper", "<span class=\"mono\">def wrapper(*args, **kwargs): … return func(*args, **kwargs)</span>"],
  ["Keep the name and docstring", "<span class=\"mono\">@functools.wraps(func)</span>"],
  ["Decorator that takes settings", "Three levels: <span class=\"mono\">def require_role(role): def decorator(func): def wrapper(...)</span>"],
  ["Cache pure function results", "<span class=\"mono\">@functools.cache</span> / <span class=\"mono\">@lru_cache(maxsize=…)</span>"],
  ["Several decorators", "Bottom one wraps first; top one runs first"]
 ],
 "ref_title": "Reference: decorators you'll meet",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Decorator</th><th>Where</th><th>Does</th></tr></thead>
        <tbody>
          <tr><td class="mono">@property</td><td>built-in</td><td>method read like an attribute (OOP deeper)</td></tr>
          <tr><td class="mono">@classmethod / @staticmethod</td><td>built-in</td><td>method gets the class / nothing instead of self</td></tr>
          <tr><td class="mono">@dataclass</td><td>dataclasses</td><td>writes __init__, __repr__, __eq__ for you</td></tr>
          <tr><td class="mono">@functools.cache / lru_cache</td><td>functools</td><td>memoise results</td></tr>
          <tr><td class="mono">@contextlib.contextmanager</td><td>contextlib</td><td>turns a generator into a with-block helper</td></tr>
          <tr><td class="mono">@app.get("/patients")</td><td>FastAPI / Flask</td><td>registers a function as a web route</td></tr>
          <tr><td class="mono">@pytest.fixture</td><td>pytest</td><td>marks reusable test setup</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Added", "<b>From your Notion plan:</b> \"basic decorators\" (8-week plan, Week 2). They build directly on closures from the Scope page."],
  ["Added", "<b>Coming from .NET:</b> the effect resembles an ASP.NET action filter or middleware, but a Python decorator is just a function call at definition time. There is no attribute metadata involved."],
  ["Added", "<b>Keep wrappers thin:</b> they run on every call. Put heavy setup outside the wrapper, in the decorator body, which runs only once."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">def d(f): return lambda: f() * 2\\n@d\\ndef five(): return 5\\nprint(five())</span>", "code": "def d(f): return lambda: f() * 2\n@d\ndef five(): return 5\nprint(five())", "expect": "10", "a": "<b class=\"mono\">10</b>. Any callable can be the replacement, even a lambda."},
  {"q": "<span class=\"mono\">@d</span> above <span class=\"mono\">def g</span> is the same as…?", "a": "<span class=\"mono\">def g(...): ...</span> followed by <b class=\"mono\">g = d(g)</b>."},
  {"q": "<span class=\"mono\">def count(f):\\n    def w(*a):\\n        w.calls += 1\\n        return f(*a)\\n    w.calls = 0\\n    return w\\n@count\\ndef hi(): pass\\nhi(); hi()\\nprint(hi.calls)</span>", "code": "def count(f):\n    def w(*a):\n        w.calls += 1\n        return f(*a)\n    w.calls = 0\n    return w\n@count\ndef hi(): pass\nhi(); hi()\nprint(hi.calls)", "expect": "2", "a": "<b class=\"mono\">2</b>. Functions are objects and can carry attributes; the wrapper keeps state between calls."}
 ],
 "sources": "From the Notion plan (Planning for python learning, Week 2: basic decorators). Python docs: functools.wraps, PEP 318."
}
