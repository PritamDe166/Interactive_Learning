import json, io, contextlib
CM = '''class Lock:
    def __init__(self, suppress=False):
        self.suppress = suppress
    def __enter__(self):
        print("enter: lock taken")
        return self
    def __exit__(self, exc_type, exc, tb):
        print("exit: lock released, error =", exc_type.__name__ if exc_type else None)
        return self.suppress
'''
SC = []
for label, sup, fail in [("body succeeds", False, False), ("body raises", False, True), ("body raises, __exit__ returns True", True, True)]:
    ns = {}; exec(CM, ns); buf = io.StringIO(); err = None
    with contextlib.redirect_stdout(buf):
        try:
            with ns["Lock"](sup):
                print("body: start")
                if fail:
                    raise ValueError("slot taken")
                print("body: end")
            print("after the with block")
        except ValueError as e:
            err = f"ValueError: {e}"
    SC.append({"label": label, "sup": sup, "fail": fail, "out": buf.getvalue().splitlines(), "err": err})

SPEC = {
 "slug": "context-managers", "num": 17, "part": "Going further",
 "title": "Context managers", "title_plain": "Context managers",
 "desc": "Python fundamentals: the with statement, __enter__ and __exit__, guaranteed cleanup when errors happen, and writing your own with contextlib.contextmanager.",
 "lede": [
  "<span class=\"mono\">with X as v:</span> calls <span class=\"mono\">X.__enter__()</span> before the block (its return value becomes <span class=\"mono\">v</span>) and <span class=\"mono\">X.__exit__()</span> after it, <b>no matter how</b> the block ends.",
  "That makes <span class=\"mono\">with</span> the standard way to <b>acquire and release</b>: files, locks, database transactions, network connections, temporary settings.",
  "<span class=\"mono\">__exit__</span> receives the exception (if any). Returning a true value <b>swallows</b> it; usually you return False and let it propagate.",
  "<span class=\"mono\">@contextmanager</span> lets you write one as a generator: code before <span class=\"mono\">yield</span> is enter, code after (in <span class=\"mono\">finally</span>) is exit."
 ],
 "walk": {"title": "a lock and a booking", "code":
'''from contextlib import contextmanager

class Timer:
    def __enter__(self):
        print("enter")
        return self
    def __exit__(self, exc_type, exc, tb):
        print("exit, error:", exc_type)
        return False

with Timer() as t:
    print("working")

@contextmanager
def booking(slot):
    print("lock", slot)
    try:
        yield f"booked {slot}"
    finally:
        print("unlock", slot)

try:
    with booking("9:00") as b:
        print(b)
        raise ValueError("double booking")
except ValueError as e:
    print("caught:", e)''',
 "steps": [
  {"at": {"event": "call", "n": 2}, "title": "with calls __enter__", "text": "<span class=\"mono\">with Timer() as t</span> creates the object, then calls its <span class=\"mono\">__enter__</span>. Whatever it returns (here <span class=\"mono\">self</span>) is bound to <span class=\"mono\">t</span>."},
  {"at": {"after": 12}, "title": "The body runs", "text": "Ordinary code inside the block: <span class=\"mono\">working</span>."},
  {"at": {"event": "call", "n": 3}, "title": "Leaving the block calls __exit__", "text": "As soon as the block ends, Python calls <span class=\"mono\">__exit__(exc_type, exc, tb)</span>. No error happened, so all three are <span class=\"mono\">None</span>."},
  {"at": {"event": "call", "n": 4}, "title": "A generator-based manager", "text": "<span class=\"mono\">@contextmanager</span> wraps the <span class=\"mono\">booking</span> generator. Entering the with block runs it up to <span class=\"mono\">yield</span>."},
  {"at": {"after": 24}, "title": "yield's value goes to as", "text": "The yielded string became <span class=\"mono\">b</span>. The generator is paused inside <span class=\"mono\">try</span>, holding the \"lock\"."},
  {"at": {"event": "exception", "n": 1}, "title": "An error inside the block", "text": "<span class=\"mono\">raise ValueError</span> interrupts the block. Python doesn't jump straight to <span class=\"mono\">except</span>: first it gives the context manager a chance to clean up."},
  {"at": {"after": 20}, "title": "finally releases the lock", "text": "The exception is thrown <b>into</b> the paused generator at the <span class=\"mono\">yield</span>, so its <span class=\"mono\">finally</span> runs: <span class=\"mono\">unlock 9:00</span>. Cleanup happened even though the block failed.", "tip": "Without try/finally around the yield, an exception would skip your cleanup code."},
  {"at": "end", "title": "Then the exception continues", "text": "The manager didn't suppress the error, so it reaches the outer <span class=\"mono\">except</span>. Order: lock → body → unlock → caught."}
 ]},
 "walk_out": "enter / working / exit, error: None / lock 9:00 / booked 9:00 / unlock 9:00 / caught: double booking",
 "puzzles": [
  {"id": "p1", "name": "1 · return in the block", "code": "class CM:\n    def __enter__(self):\n        print(\"in\")\n    def __exit__(self, *exc):\n        print(\"out\")\n\ndef f():\n    with CM():\n        return \"result\"\n\nprint(f())", "q": "What's printed?", "opts": ["in / result", "in / out / result", "in / result / out"], "a": 1,
   "why": "Returning from inside a with block still triggers __exit__ before the function actually returns."},
  {"id": "p2", "name": "2 · as gets __enter__'s value", "code": "class CM:\n    def __enter__(self):\n        return 42\n    def __exit__(self, *exc):\n        pass\n\nwith CM() as x:\n    print(x)", "q": "What's printed?", "opts": ["<__main__.CM object>", "42", "None"], "a": 1,
   "why": "<span class=\"mono\">as</span> binds the return value of __enter__, not the manager itself (open() just happens to return itself)."},
  {"id": "p3", "name": "3 · suppressing", "code": "from contextlib import suppress\nwith suppress(KeyError):\n    print({}[\"x\"])\n    print(\"never\")\nprint(\"after\")", "q": "What's printed?", "opts": ["after", "never / after", "KeyError"], "a": 0,
   "why": "<span class=\"mono\">suppress</span>'s __exit__ returns True for KeyError: the rest of the block is skipped and the program continues after it."},
  {"id": "p4", "name": "4 · file closed after with", "code": "with open(\"cm.txt\", \"w\") as f:\n    f.write(\"hi\")\nprint(f.closed)\nf.write(\"more\")", "q": "What happens?", "opts": ["True / ValueError: I/O operation on closed file.", "False / (writes more)", "True / (writes more)"], "a": 0,
   "why": "The name f still exists after the block, but the file object is closed."}
 ],
 "runner_extra": [{"label": "Your turn: a temporary setting", "code": 'from contextlib import contextmanager\n\nsettings = {"currency": "INR"}\n\n@contextmanager\ndef temp_setting(key, value):\n    old = settings[key]\n    settings[key] = value\n    try:\n        yield\n    finally:\n        settings[key] = old\n\nwith temp_setting("currency", "USD"):\n    print("inside:", settings)\nprint("after:", settings)'}],
 "custom": [
  {"id": "tl", "title": "Enter, body, exit: three endings", "kind": "A Lock context manager · results captured from real runs",
   "html": '''    <details class="rn-inputs" style="margin-bottom:10px"><summary>Show the Lock class</summary><pre class="codeblock" id="tlCode" style="min-height:0"></pre></details>
    <div class="seg" id="tlSeg" role="group" aria-label="Scenario"></div>
    <div class="tl-lanes">
      <div class="tl-lane"><span>__enter__</span><div class="tl-track"><i id="tlE"></i></div></div>
      <div class="tl-lane"><span>body</span><div class="tl-track"><i id="tlB"></i></div></div>
      <div class="tl-lane"><span>__exit__</span><div class="tl-track"><i id="tlX"></i></div></div>
      <div class="tl-lane"><span>after</span><div class="tl-track"><i id="tlA"></i></div></div>
    </div>
    <div class="card" style="margin-top:10px"><div class="label">Output</div><pre class="mono fl-out" id="tlOut"></pre></div>
    <p class="status-line" id="tlStatus">Pick a scenario.</p>''',
   "js": '''    const SC = __SC__;
    $('tlCode').innerHTML = __CM__.trimEnd().split('\\n').map(l => `<span class="ln">${K.pyHighlight(l)}</span>`).join('');
    $('tlSeg').innerHTML = SC.map((s, i) => `<button type="button" data-v="${i}" aria-pressed="false">${s.label}</button>`).join('');
    async function go(i) {
      const run = K.newRun('tl'), s = SC[i];
      ['tlE', 'tlB', 'tlX', 'tlA'].forEach(id => { $(id).className = ''; });
      $('tlOut').textContent = '';
      const out = t => { $('tlOut').textContent += t + '\\n'; };
      try {
        $('tlE').className = 'on'; out(s.out[0]); await K.sleep(600, run);
        $('tlB').className = s.fail ? 'on bad' : 'on'; out(s.out[1]); await K.sleep(600, run);
        if (!s.fail) { out(s.out[2]); await K.sleep(300, run); }
        $('tlX').className = 'on'; out(s.out[s.fail ? 2 : 3]); await K.sleep(600, run);
        if (!s.fail || s.sup) { $('tlA').className = 'on'; out(s.out[s.out.length - 1]); }
        else { $('tlA').className = 'skip'; out('→ ' + s.err + ' propagates to the caller'); }
        $('tlStatus').innerHTML = !s.fail ? 'Normal run: enter → whole body → exit (error = None) → code after the block.' : s.sup ? '<b>__exit__ returned True</b>: the error is swallowed, the rest of the body is skipped, and execution continues after the block. Use sparingly.' : 'The body stopped at the raise, <b>__exit__ still ran</b> and saw the ValueError, then the error continued outward. The code after the block never ran.';
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    K.seg($('tlSeg'), v => go(+v));'''.replace('__SC__', json.dumps(SC)).replace('__CM__', json.dumps(CM))}
 ],
 "style": '''  .tl-lanes { margin-top: 12px; display: grid; gap: 8px; }
  .tl-lane { display: grid; grid-template-columns: 90px 1fr; gap: 10px; align-items: center; font-family: var(--mono); font-size: 13px; color: var(--fg-soft); }
  .tl-track { height: 22px; border-radius: 11px; background: var(--panel-2); border: 1px solid var(--line); overflow: hidden; }
  .tl-track i { display: block; height: 100%; width: 0; background: var(--cyan); transition: width .5s ease; }
  .tl-track i.on { width: 100%; }
  .tl-track i.bad { width: 55%; background: var(--red); }
  .tl-track i.skip { width: 100%; background: repeating-linear-gradient(45deg, var(--line) 0 6px, transparent 6px 12px); }
  .fl-out { margin: 4px 0 0; min-height: 60px; white-space: pre-wrap; font-size: 14px; }''',
 "cheat": [
  ["Anything opened must be closed", "<span class=\"mono\">with open(...) as f:</span> (files, sockets, DB sessions)"],
  ["Several resources", "<span class=\"mono\">with open(a) as fa, open(b) as fb:</span> (bracketed over lines since 3.10)"],
  ["Write your own quickly", "<span class=\"mono\">@contextmanager</span> + <span class=\"mono\">try: yield … finally: cleanup</span>"],
  ["Write your own as a class", "<span class=\"mono\">__enter__</span> returns the value for <span class=\"mono\">as</span>; <span class=\"mono\">__exit__</span> cleans up"],
  ["Ignore one specific error", "<span class=\"mono\">with contextlib.suppress(FileNotFoundError):</span>"],
  ["Don't swallow errors by accident", "<span class=\"mono\">__exit__</span> should return False/None unless you really mean it"]
 ],
 "ref_title": "Reference: what with does",
 "ref_html": '''    <div class="two">
      <div class="card"><div class="label">You write</div><pre class="codeblock" style="min-height:0;margin:6px 0 0"><span class="ln"><span class="k">with</span> Lock() <span class="k">as</span> v:</span><span class="ln">    body()</span></pre></div>
      <div class="card"><div class="label">Python does (roughly)</div><pre class="codeblock" style="min-height:0;margin:6px 0 0"><span class="ln">mgr = Lock()</span><span class="ln">v = mgr.__enter__()</span><span class="ln"><span class="k">try</span>:</span><span class="ln">    body()</span><span class="ln"><span class="k">except</span> BaseException <span class="k">as</span> e:</span><span class="ln">    <span class="k">if not</span> mgr.__exit__(type(e), e, e.__traceback__):</span><span class="ln">        <span class="k">raise</span></span><span class="ln"><span class="k">else</span>:</span><span class="ln">    mgr.__exit__(<span class="b">None</span>, <span class="b">None</span>, <span class="b">None</span>)</span></pre></div>
    </div>''',
 "notes": [
  ["Added", "<b>From your Notion plan:</b> \"context managers\" (8-week plan, Week 5) and \"with open\" (Week 2). Your file scripts already use <span class=\"mono\">with open(...)</span>; this page shows the mechanism behind it."],
  ["Added", "<b>Coming from C#:</b> <span class=\"mono\">with</span> plays the role of <span class=\"mono\">using</span> / <span class=\"mono\">IDisposable</span>, with the extra ability to see and even suppress the exception in <span class=\"mono\">__exit__</span>."],
  ["Added", "<b>Async code</b> uses <span class=\"mono\">async with</span> and <span class=\"mono\">__aenter__</span>/<span class=\"mono\">__aexit__</span> (e.g. HTTP client sessions); same idea."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">from contextlib import contextmanager\\n@contextmanager\\ndef tag(n):\\n    print(f\"&lt;{n}&gt;\", end=\"\")\\n    yield\\n    print(f\"&lt;/{n}&gt;\")\\nwith tag(\"b\"):\\n    print(\"hi\", end=\"\")</span>", "code": "from contextlib import contextmanager\n@contextmanager\ndef tag(n):\n    print(f\"<{n}>\", end=\"\")\n    yield\n    print(f\"</{n}>\")\nwith tag(\"b\"):\n    print(\"hi\", end=\"\")", "expect": "<b>hi</b>", "a": "<b class=\"mono\">&lt;b&gt;hi&lt;/b&gt;</b>. Before yield, the body, after yield."},
  {"q": "Why put the code after <span class=\"mono\">yield</span> inside <span class=\"mono\">finally</span>?", "a": "If the with-block raises, the exception is thrown into the generator at the <span class=\"mono\">yield</span>. Without try/finally the cleanup lines after yield would be <b>skipped</b>."},
  {"q": "What does <span class=\"mono\">with open(p) as f:</span> guarantee that <span class=\"mono\">f = open(p)</span> doesn't?", "a": "<span class=\"mono\">f.close()</span> is called when the block ends, even on an exception or return. With plain open() you must close it yourself in a finally."}
 ],
 "sources": "From the Notion plan (Planning for python learning, Weeks 2 and 5). Python docs: The with statement, contextlib."
}
