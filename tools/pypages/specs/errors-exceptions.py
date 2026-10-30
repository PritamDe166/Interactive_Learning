import json, sys, io, contextlib
DIV = '''def divide(a, b):
    try:
        r = int(a) / int(b)
    except ValueError:
        print("bad number")
    except ZeroDivisionError:
        print("can't divide by zero")
    else:
        print("result", r)
    finally:
        print("done")'''
ns = {}
exec(compile(DIV, "<div>", "exec"), ns)
SCEN = []
for label, args in [('divide("10", "4")', ("10", "4")), ('divide("ten", "4")', ("ten", "4")), ('divide("10", "0")', ("10", "0")), ('divide("10", None)', ("10", None))]:
    lines = []
    def tr(frame, event, arg):
        if frame.f_code.co_filename == "<div>":
            if event == "line": lines.append(frame.f_lineno)
            return tr
        return None
    buf = io.StringIO(); err = None
    sys.settrace(tr)
    try:
        with contextlib.redirect_stdout(buf):
            ns["divide"](*args)
    except Exception as e:
        err = f"{type(e).__name__}: {e}"
    finally:
        sys.settrace(None)
    SCEN.append({"label": label, "lines": lines, "out": buf.getvalue().splitlines(), "err": err})

SPEC = {
 "slug": "errors-exceptions", "num": 10, "part": "Real programs",
 "title": "Errors &amp; exceptions", "title_plain": "Errors & exceptions",
 "desc": "Python fundamentals: reading a traceback, try/except/else/finally, catching specific exceptions, raising your own, and how an exception travels up the call stack.",
 "lede": [
  "An <b>exception</b> is an object Python raises when something goes wrong. It stops the current line and travels <b>up the call stack</b> until something catches it.",
  "<span class=\"mono\">try</span> runs risky code; <span class=\"mono\">except SomeError</span> handles that error; <span class=\"mono\">else</span> runs only if nothing went wrong; <span class=\"mono\">finally</span> <b>always</b> runs.",
  "Catch <b>specific</b> exceptions (<span class=\"mono\">ValueError</span>, <span class=\"mono\">KeyError</span>), not everything, so real bugs still show up.",
  "Use <span class=\"mono\">raise</span> to signal a problem yourself. Read a <b>traceback</b> from the bottom: the last line says what went wrong."
 ],
 "walk": {"title": "validating ages from a form", "code":
'''def parse_age(text):
    try:
        age = int(text)
    except ValueError:
        print("not a number:", text)
        return None
    else:
        if age < 0:
            raise ValueError(f"negative age {age}")
        return age
    finally:
        print("checked", text)

print(parse_age("42"))
print(parse_age("abc"))
try:
    parse_age("-5")
except ValueError as e:
    print("caught:", e)''',
 "steps": [
  {"at": {"event": "call", "n": 1}, "title": "A function with all four blocks", "text": "<span class=\"mono\">parse_age(\"42\")</span> starts. The <span class=\"mono\">try</span> block holds the line that might fail: converting text to int."},
  {"at": {"event": "return", "n": 1}, "title": "Happy path: try → else → finally", "text": "<span class=\"mono\">int(\"42\")</span> worked, so <span class=\"mono\">except</span> was skipped and <span class=\"mono\">else</span> ran. Before the function hands back 42, <span class=\"mono\">finally</span> prints <span class=\"mono\">checked 42</span>. finally runs even on <span class=\"mono\">return</span>."},
  {"at": {"event": "exception", "n": 1}, "title": "int(\"abc\") raises ValueError", "text": "Second call. The conversion fails: Python creates a <b>ValueError</b> object and abandons the rest of the <span class=\"mono\">try</span> block. <span class=\"mono\">age</span> is never assigned."},
  {"at": {"after": 5}, "title": "A matching except handles it", "text": "Python checks the except clauses in order. <span class=\"mono\">except ValueError</span> matches, so its block runs. The error is <b>handled</b>: the program carries on normally."},
  {"at": {"event": "return", "n": 2}, "title": "finally runs here too", "text": "The except block returns None, and on the way out <span class=\"mono\">finally</span> still prints. That's what finally is for: closing files, releasing locks, logging."},
  {"at": {"after": 9}, "title": "raise your own exception", "text": "For \"-5\" the conversion works, so <span class=\"mono\">else</span> runs and finds a negative age. <span class=\"mono\">raise ValueError(...)</span> signals a problem the caller must deal with.", "tip": "Raise when the function can't do its job. Returning a special value like -1 is easy for callers to ignore."},
  {"at": {"event": "return", "n": 3}, "title": "The exception leaves the function", "text": "Nothing inside <span class=\"mono\">parse_age</span> catches this one (the <span class=\"mono\">except</span> only covers the <span class=\"mono\">try</span> block), so after finally runs the frame ends <b>without a return value</b> and the exception moves up to the caller."},
  {"at": "end", "title": "Caught by the caller", "text": "The caller's <span class=\"mono\">try/except ValueError as e</span> catches it. <span class=\"mono\">e</span> is the exception object; printing it shows the message. If no one had caught it, Python would print a traceback and stop."}
 ]},
 "walk_out": "checked 42 / 42 / not a number: abc / checked abc / None / checked -5 / caught: negative age -5",
 "puzzles": [
  {"id": "p1", "name": "1 · which block runs?", "code": "try:\n    x = int(\"7\")\nexcept ValueError:\n    print(\"bad\")\nelse:\n    print(\"ok\", x)\nfinally:\n    print(\"end\")", "q": "What's printed?", "opts": ["ok 7 / end", "bad / end", "ok 7"], "a": 0,
   "why": "No error, so except is skipped, else runs, and finally always runs."},
  {"id": "p2", "name": "2 · the wrong except", "code": "try:\n    print({\"a\": 1}[\"b\"])\nexcept ValueError:\n    print(\"handled\")", "q": "What happens?", "opts": ["handled", "KeyError: 'b'", "None"], "a": 1,
   "why": "A missing dict key raises <b>KeyError</b>, which <span class=\"mono\">except ValueError</span> doesn't match, so it isn't caught."},
  {"id": "p3", "name": "3 · order of except", "code": "try:\n    1 / 0\nexcept Exception:\n    print(\"general\")\nexcept ZeroDivisionError:\n    print(\"zero\")", "q": "What's printed?", "opts": ["zero", "general", "general / zero"], "a": 1,
   "why": "The first matching clause wins, and ZeroDivisionError <b>is an</b> Exception. Put specific clauses before general ones."},
  {"id": "p4", "name": "4 · finally vs return", "code": "def f():\n    try:\n        return \"try\"\n    finally:\n        print(\"cleanup\")\n\nprint(f())", "q": "What's printed?", "opts": ["try", "cleanup / try", "try / cleanup"], "a": 1,
   "why": "The return value is ready, but finally runs <b>before</b> the function actually returns, so \"cleanup\" prints first."},
  {"id": "p5", "name": "5 · exception travels up", "code": "def inner():\n    return int(\"x\")\n\ndef outer():\n    return inner() + 1\n\ntry:\n    outer()\nexcept ValueError as e:\n    print(\"caught:\", e)", "q": "What's printed?", "opts": ["caught: invalid literal for int() with base 10: 'x'", "ValueError (uncaught)", "caught: x"], "a": 0,
   "why": "The error starts in inner, passes through outer (which doesn't catch it) and is caught two levels up."},
  {"id": "p6", "name": "6 · raise with a message", "code": "def book(slot):\n    if not slot:\n        raise ValueError(\"slot is required\")\n    return \"booked \" + slot\n\nprint(book(\"9:00\"))\nprint(book(\"\"))", "q": "What happens?", "opts": ["booked 9:00 / booked ", "booked 9:00 / ValueError: slot is required", "ValueError: slot is required"], "a": 1,
   "why": "The first call succeeds; the second raises and, uncaught, stops the program."}
 ],
 "runner_extra": [{"label": "Your turn: ask until valid", "inputs": ["abc", "-3", "35"], "code": 'while True:\n    text = input("Age: ")\n    try:\n        age = int(text)\n        if age < 0:\n            raise ValueError("must be positive")\n    except ValueError as e:\n        print("Try again:", e)\n    else:\n        break\nprint("Saved age", age)'}],
 "custom": [
  {"id": "flow", "title": "try / except / else / finally flow", "kind": "Pick the arguments · the highlighted lines are the ones Python really ran",
   "html": '''    <div class="chips" id="flBtns"></div>
    <div class="two" style="margin-top:10px">
      <pre class="codeblock" id="flCode" style="min-height:0;margin:0"></pre>
      <div><div class="card"><div class="label">Output</div><pre class="mono fl-out" id="flOut"></pre></div><div class="fl-esc" id="flEsc"></div></div>
    </div>
    <p class="status-line" id="flStatus">Pick a call.</p>''',
   "js": '''    const SC = __SC__, SRC = __SRC__.split('\\n');
    $('flBtns').innerHTML = SC.map((s, i) => `<button class="chip-btn mono" type="button" data-i="${i}" aria-pressed="false">${s.label}</button>`).join('');
    const draw = () => { $('flCode').innerHTML = SRC.map((l, i) => `<span class="ln" data-l="${i + 1}">${K.pyHighlight(l)}</span>`).join(''); };
    async function go(s) {
      const run = K.newRun('fl'); draw(); $('flOut').textContent = ''; $('flEsc').className = 'fl-esc'; $('flEsc').textContent = '';
      let o = 0; const lines = [...$('flCode').children];
      try {
        for (const ln of s.lines) {
          lines.forEach(x => x.classList.remove('on'));
          const el = lines[ln - 1]; el.classList.add('on', 'done');
          if (/print\\(/.test(SRC[ln - 1]) && o < s.out.length) { $('flOut').textContent += s.out[o++] + '\\n'; }
          await K.sleep(520, run);
        }
        lines.forEach(x => x.classList.remove('on'));
        if (s.err) { $('flEsc').className = 'fl-esc on'; $('flEsc').textContent = '↑ ' + s.err + ' escapes to the caller'; }
        const ran = b => s.lines.some(l => SRC[l - 1].trim().startsWith(b)) ;
        const hasExcept = s.lines.some(l => /print\\("(bad|can)/.test(SRC[l - 1]));
        const hasElse = s.lines.some(l => /result/.test(SRC[l - 1]));
        $('flStatus').innerHTML = s.err ? 'No except clause matched, so after <b>finally</b> the exception keeps going up to whoever called divide().' : hasExcept ? 'An exception was raised in <b>try</b>; the matching <b>except</b> handled it, <b>else</b> was skipped, <b>finally</b> ran.' : 'No exception: <b>try</b> → <b>else</b> → <b>finally</b>.';
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    $('flBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      $('flBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); go(SC[+b.dataset.i]);
    }));
    draw();'''.replace('__SC__', json.dumps(SCEN)).replace('__SRC__', json.dumps(DIV))}
 ],
 "style": '''  .fl-out { margin: 4px 0 0; min-height: 70px; white-space: pre-wrap; font-size: 14px; }
  .fl-esc { margin-top: 10px; padding: 10px 12px; border-radius: 10px; border: 1.5px dashed var(--line); font-family: var(--mono); font-size: 13px; color: var(--muted); min-height: 20px; }
  .fl-esc.on { border-style: solid; border-color: var(--red); color: var(--bad-text); animation: up .5s ease-out; }
  @keyframes up { from { transform: translateY(10px); opacity: 0; } to { transform: none; opacity: 1; } }''',
 "cheat": [
  ["Input might be bad", "<span class=\"mono\">try: int(x)</span> <span class=\"mono\">except ValueError:</span>"],
  ["Code that must run no matter what", "<span class=\"mono\">finally:</span> (or a <span class=\"mono\">with</span> block for files and locks)"],
  ["Code that should run only on success", "<span class=\"mono\">else:</span>, keeping the try block small"],
  ["Your function can't do its job", "<span class=\"mono\">raise ValueError(\"why\")</span>"],
  ["Need the error details", "<span class=\"mono\">except KeyError as e:</span> then <span class=\"mono\">print(e)</span>"],
  ["Tempted to write bare <span class=\"mono\">except:</span>", "Catch the specific exception; a bare except hides bugs and even Ctrl+C"],
  ["Reading a traceback", "Start at the <b>last line</b> (type and message), then the line above it (where)"]
 ],
 "ref_title": "Reference: exceptions you'll meet first",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Exception</th><th>Typical cause</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td class="mono">ValueError</td><td>right type, bad value</td><td class="mono">int("abc")</td></tr>
          <tr><td class="mono">TypeError</td><td>wrong type for the operation</td><td class="mono">"a" + 1</td></tr>
          <tr><td class="mono">KeyError</td><td>missing dict key</td><td class="mono">d["phone"]</td></tr>
          <tr><td class="mono">IndexError</td><td>list index out of range</td><td class="mono">[1, 2][5]</td></tr>
          <tr><td class="mono">AttributeError</td><td>object has no such attribute</td><td class="mono">None.upper()</td></tr>
          <tr><td class="mono">NameError</td><td>name not defined (typo?)</td><td class="mono">pritn("x")</td></tr>
          <tr><td class="mono">ZeroDivisionError</td><td>division by zero</td><td class="mono">1 / 0</td></tr>
          <tr><td class="mono">FileNotFoundError</td><td>wrong path or working folder</td><td class="mono">open("nope.txt")</td></tr>
        </tbody>
      </table>
    </div>
    <div class="card" style="margin-top:12px"><div class="label">A traceback, read bottom-up</div>
      <pre class="codeblock" style="min-height:0;margin:6px 0 0"><span class="ln">Traceback (most recent call last):</span><span class="ln">  File "app.py", line 8, in &lt;module&gt;      <span class="c"># 3. started here</span></span><span class="ln">    outer()</span><span class="ln">  File "app.py", line 5, in outer         <span class="c"># 2. passed through</span></span><span class="ln">    return inner() + 1</span><span class="ln">  File "app.py", line 2, in inner         <span class="c"># 1. happened here</span></span><span class="ln">    return int("x")</span><span class="ln"><b>ValueError: invalid literal for int() with base 10: 'x'</b></span></pre></div>''',
 "notes": [
  ["Added", "<b>Gap topic:</b> the repo uses <span class=\"mono\">int(input(...))</span> in many exercises but never handles a non-number, so any typo crashes the program. Wrapping those calls is the first real use of try/except."],
  ["Added", "<b>Custom exceptions:</b> <span class=\"mono\">class SlotTakenError(Exception): pass</span> then <span class=\"mono\">raise SlotTakenError(\"9:00\")</span>. Callers can catch exactly that."],
  ["Added", "<b>Re-raising:</b> inside except, a bare <span class=\"mono\">raise</span> re-raises the same error after logging it; <span class=\"mono\">raise NewError(...) from e</span> wraps it while keeping the original cause."],
  ["Updated", "<b>Recent versions:</b> Python 3.11 added <span class=\"mono\">except*</span> and ExceptionGroup for errors from several tasks at once, plus <span class=\"mono\">e.add_note()</span>. Python 3.14 lets you drop the brackets when catching several types: <span class=\"mono\">except ValueError, TypeError:</span> (PEP 758)."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">try:\\n    print(\"a\")\\nexcept Exception:\\n    print(\"b\")\\nfinally:\\n    print(\"c\")</span>", "code": "try:\n    print(\"a\")\nexcept Exception:\n    print(\"b\")\nfinally:\n    print(\"c\")", "expect": "a / c", "a": "<b class=\"mono\">a</b> then <b class=\"mono\">c</b>. No error, so no except."},
  {"q": "<span class=\"mono\">try:\\n    [1][3]\\nexcept (KeyError, IndexError) as e:\\n    print(type(e).__name__)</span>", "code": "try:\n    [1][3]\nexcept (KeyError, IndexError) as e:\n    print(type(e).__name__)", "expect": "IndexError", "a": "<b class=\"mono\">IndexError</b>. A tuple of types catches any of them."},
  {"q": "<span class=\"mono\">try:\\n    x = 1\\nexcept:\\n    x = 2\\nelse:\\n    x = 3\\nprint(x)</span>", "code": "try:\n    x = 1\nexcept:\n    x = 2\nelse:\n    x = 3\nprint(x)", "expect": "3", "a": "<b class=\"mono\">3</b>. try succeeded, then else ran."},
  {"q": "<span class=\"mono\">print(issubclass(ZeroDivisionError, ArithmeticError))</span>", "code": "print(issubclass(ZeroDivisionError, ArithmeticError))", "expect": "True", "a": "<b class=\"mono\">True</b>. Exceptions form a class hierarchy; catching a parent catches its children."},
  {"q": "<span class=\"mono\">try:\\n    raise ValueError(\"bad slot\")\\nexcept ValueError as e:\\n    print(e.args)</span>", "code": "try:\n    raise ValueError(\"bad slot\")\nexcept ValueError as e:\n    print(e.args)", "expect": "('bad slot',)", "a": "<b class=\"mono\">('bad slot',)</b>. The arguments you raise with are stored on the exception."},
  {"q": "<span class=\"mono\">d = {}\\nprint(d.get(\"k\", \"none\"))</span>: why no try needed?", "code": "d = {}\nprint(d.get(\"k\", \"none\"))", "expect": "none", "a": "<b class=\"mono\">none</b>. Many APIs offer a no-exception form (get, find, getattr with a default). Use them when \"missing\" is normal."}
 ],
 "sources": "Gap topic: not in the Python_Fundamentals repo; listed in both Notion plans (exceptions / try-except). Python 3.14 change from What's New in Python 3.14 (PEP 758)."
}
