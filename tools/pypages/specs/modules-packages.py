SPEC = {
 "slug": "modules-packages", "num": 13, "part": "Going further",
 "title": "Modules, packages, pip &amp; venv", "title_plain": "Modules, packages, pip & venv",
 "desc": "Python fundamentals: what import does, module caching, from-imports and aliases, if __name__ == '__main__', packages, pip and virtual environments.",
 "lede": [
  "Every <b>.py file is a module</b>. <span class=\"mono\">import billing</span> runs billing.py <b>once</b>, caches it in <span class=\"mono\">sys.modules</span>, and binds the name <span class=\"mono\">billing</span>.",
  "<span class=\"mono\">from billing import tax</span> copies just that name into your file; <span class=\"mono\">import numpy as np</span> picks a shorter alias.",
  "<span class=\"mono\">__name__</span> is <span class=\"mono\">\"__main__\"</span> when a file is run directly and the module's name when it's imported, hence <span class=\"mono\">if __name__ == \"__main__\":</span>.",
  "A <b>package</b> is a folder of modules. <b>pip</b> installs third-party packages; a <b>virtual environment</b> (venv) keeps each project's packages separate."
 ],
 "walk": {"title": "writing and importing our own module", "code":
'''src = """print("loading billing")
RATE = 0.18
def tax(amount):
    return amount * RATE
if __name__ == "__main__":
    print("billing run directly")
"""
with open("billing.py", "w") as f:
    f.write(src)
import billing
import billing
from billing import tax, RATE
import statistics as st
print(billing.tax(1000), tax(500), RATE)
print(st.mean([450, 800, 1200]))
print(billing.__name__, __name__)''',
 "steps": [
  {"at": {"after": 9}, "title": "A module is just a .py file", "text": "To keep everything in one runnable box, this snippet writes <span class=\"mono\">billing.py</span> next to itself. It has a print, a constant, a function and a <span class=\"mono\">__main__</span> check."},
  {"at": {"after": 10}, "title": "import runs the file once", "text": "<span class=\"mono\">import billing</span> found billing.py, <b>ran it top to bottom</b> (so \"loading billing\" printed) and bound the name <span class=\"mono\">billing</span> to the resulting <b>module object</b>. The <span class=\"mono\">__main__</span> block didn't run: inside billing, <span class=\"mono\">__name__</span> is <span class=\"mono\">\"billing\"</span>."},
  {"at": {"after": 11}, "title": "A second import is free", "text": "Nothing printed. Python found <span class=\"mono\">billing</span> in its cache, <span class=\"mono\">sys.modules</span>, and reused the same module object. Module code runs once per program.", "tip": "This is why modules are a natural place for configuration and shared constants."},
  {"at": {"after": 12}, "title": "from … import copies names", "text": "<span class=\"mono\">tax</span> and <span class=\"mono\">RATE</span> now exist directly in this file, pointing at the same objects as <span class=\"mono\">billing.tax</span> and <span class=\"mono\">billing.RATE</span>. Handy, but you lose the reminder of where they came from."},
  {"at": {"after": 13}, "title": "Standard library + alias", "text": "<span class=\"mono\">statistics</span> ships with Python (the \"batteries included\" standard library). <span class=\"mono\">as st</span> binds a shorter name."},
  {"at": {"after": 15}, "title": "Using what you imported", "text": "<span class=\"mono\">billing.tax(1000)</span> and the copied <span class=\"mono\">tax(500)</span> call the same function. <span class=\"mono\">st.mean</span> averages the fees."},
  {"at": "end", "title": "__name__ tells you how you were started", "text": "The imported module's <span class=\"mono\">__name__</span> is <span class=\"mono\">'billing'</span>; this file, run directly, is <span class=\"mono\">'__main__'</span>. Put demo or start-up code under <span class=\"mono\">if __name__ == \"__main__\":</span> so importing the file stays side-effect free."}
 ]},
 "walk_out": "loading billing / 180.0 90.0 0.18 / 816.6666666666666 / billing __main__",
 "puzzles": [
  {"id": "p1", "name": "1 · importing twice", "code": "with open(\"greet.py\", \"w\") as f:\n    f.write('print(\"hello from greet\")\\n')\nimport greet\nimport greet\nimport greet as g\nprint(g is greet)", "q": "What's printed?", "opts": ["hello from greet / hello from greet / hello from greet / True", "hello from greet / True", "hello from greet / False"], "a": 1,
   "why": "The module runs once and is cached; every import (with or without an alias) gives back the same module object."},
  {"id": "p2", "name": "2 · from-import is a copy of the name", "code": "with open(\"counter.py\", \"w\") as f:\n    f.write(\"count = 0\\ndef bump():\\n    global count\\n    count += 1\\n\")\nfrom counter import count, bump\nimport counter\nbump()\nprint(count, counter.count)", "q": "What's printed?", "opts": ["1 1", "0 1", "0 0"], "a": 1,
   "why": "<span class=\"mono\">from counter import count</span> bound <i>your</i> name to the int 0 at import time. bump() rebinds the module's <span class=\"mono\">count</span>, which you only see through <span class=\"mono\">counter.count</span>."},
  {"id": "p3", "name": "3 · alias only", "code": "import statistics as st\nprint(st.median([3, 1, 2]))\nprint(statistics.median([3, 1, 2]))", "q": "What happens?", "opts": ["2 / 2", "2 / NameError: name 'statistics' is not defined", "NameError"], "a": 1,
   "why": "<span class=\"mono\">import x as y</span> binds only <span class=\"mono\">y</span>."},
  {"id": "p4", "name": "4 · __name__ inside a module", "code": "with open(\"tool.py\", \"w\") as f:\n    f.write('print(\"tool:\", __name__)\\nif __name__ == \"__main__\":\\n    print(\"demo\")\\n')\nimport tool\nprint(\"me:\", __name__)", "q": "What's printed?", "opts": ["tool: tool / me: __main__", "tool: __main__ / demo / me: __main__", "tool: tool / demo / me: __main__"], "a": 0,
   "why": "Imported, the module's <span class=\"mono\">__name__</span> is its own name, so the demo block is skipped."}
 ],
 "runner_extra": [{"label": "Your turn: a module with a main()", "code": 'src = """def greet(name):\n    return f"Hello {name}"\n\ndef main():\n    print(greet("from main"))\n\nif __name__ == "__main__":\n    main()\n"""\nwith open("hello.py", "w") as f:\n    f.write(src)\nimport hello\nprint(hello.greet("Asha"))\n# Nothing from main() printed: it only runs when hello.py is the started file'}],
 "custom": [
  {"id": "nm", "title": "Run it, or import it?", "kind": "Same file, two ways to start it · watch which lines run",
   "html": '''    <div class="seg" id="nmSeg" role="group" aria-label="How billing.py starts"><button type="button" data-v="run" aria-pressed="false">python billing.py</button><button type="button" data-v="imp" aria-pressed="false">python app.py (imports billing)</button><button type="button" data-v="imp2" aria-pressed="false">app.py imports it twice</button></div>
    <div class="two" style="margin-top:12px">
      <div><div class="label mono">billing.py</div><pre class="codeblock" id="nmCode" style="min-height:0;margin:4px 0 0"></pre></div>
      <div><div class="label">Terminal</div><pre class="mono nm-term" id="nmOut"></pre><div class="nm-cache" id="nmCache">sys.modules: { … }</div></div>
    </div>
    <p class="status-line" id="nmStatus">Pick how the program starts.</p>''',
   "js": '''    const SRC = ['print("loading billing")', 'RATE = 0.18', 'def tax(amount):', '    return amount * RATE', 'if __name__ == "__main__":', '    print("demo:", tax(100))'];
    const draw = () => { $('nmCode').innerHTML = SRC.map(l => `<span class="ln">${K.pyHighlight(l)}</span>`).join(''); };
    async function go(v) {
      const run = K.newRun('nm'); draw(); $('nmOut').textContent = (v === 'run' ? '$ python billing.py' : '$ python app.py') + '\\n'; $('nmCache').textContent = 'sys.modules: { … }';
      const L = [...$('nmCode').children]; const say = t => { $('nmOut').textContent += t + '\\n'; };
      const pass = async (main) => {
        const lines = main ? [0, 1, 2, 4, 5] : [0, 1, 2, 4];
        for (const i of lines) {
          L.forEach(x => x.classList.remove('on')); L[i].classList.add('on', 'done');
          if (i === 0) say('loading billing');
          if (i === 4) { $('nmStatus').innerHTML = `<span class="mono">__name__</span> is <b class="mono">${main ? '"__main__"' : '"billing"'}</b> here, so the check is ${main ? 'True' : 'False'}.`; }
          if (i === 5) say('demo: 18.0');
          await K.sleep(600, run);
        }
        L.forEach(x => x.classList.remove('on'));
      };
      try {
        if (v === 'run') { await pass(true); $('nmStatus').innerHTML += ' Run directly, the demo runs.'; return; }
        say('>>> import billing'); await K.sleep(300, run);
        await pass(false); $('nmCache').textContent = "sys.modules: { 'billing': <module 'billing'>, … }";
        if (v === 'imp2') {
          say('>>> import billing'); await K.sleep(500, run);
          $('nmStatus').innerHTML = 'Second import: found in <span class="mono">sys.modules</span>, so <b>no line of billing.py runs again</b>.';
        } else $('nmStatus').innerHTML += ' Imported, the demo is skipped.';
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    K.seg($('nmSeg'), go); draw();'''}
 ],
 "style": '''  .nm-term { margin: 4px 0 0; min-height: 120px; padding: 10px 12px; border-radius: 10px; background: var(--code-bg); border: 1px solid var(--line); font-size: 13.5px; white-space: pre-wrap; }
  .nm-cache { margin-top: 8px; font-family: var(--mono); font-size: 12.5px; color: var(--accent-text); padding: 6px 10px; border: 1px dashed var(--line); border-radius: 8px; overflow-wrap: anywhere; }''',
 "cheat": [
  ["Use code from another file", "<span class=\"mono\">import module</span>, then <span class=\"mono\">module.name</span>"],
  ["A few names, used a lot", "<span class=\"mono\">from module import name</span>"],
  ["Long module name", "<span class=\"mono\">import pandas as pd</span> (follow the community's alias)"],
  ["Code that should only run when the file is started", "<span class=\"mono\">if __name__ == \"__main__\":</span> + <span class=\"mono\">main()</span>"],
  ["Group several modules", "A folder = a package; import with <span class=\"mono\">from clinic.billing import tax</span>"],
  ["New project", "<span class=\"mono\">python3 -m venv .venv</span>, activate, then <span class=\"mono\">pip install …</span>"],
  ["Share exact dependencies", "<span class=\"mono\">pip freeze &gt; requirements.txt</span> / <span class=\"mono\">pip install -r requirements.txt</span>"],
  ["Avoid", "<span class=\"mono\">from x import *</span> and naming your file like a library (<span class=\"mono\">random.py</span>, <span class=\"mono\">json.py</span>)"]
 ],
 "ref_title": "Reference: project layout, venv and pip (macOS / Linux)",
 "ref_html": '''    <div class="two">
      <div class="card"><div class="label">A small package</div><pre class="codeblock" style="min-height:0;margin:6px 0 0"><span class="ln">clinic_app/</span><span class="ln">├── .venv/              <span class="c"># virtual env (don't commit)</span></span><span class="ln">├── requirements.txt</span><span class="ln">├── main.py             <span class="c"># from clinic.billing import tax</span></span><span class="ln">└── clinic/</span><span class="ln">    ├── __init__.py     <span class="c"># marks a regular package</span></span><span class="ln">    ├── billing.py</span><span class="ln">    └── booking.py</span></pre></div>
      <div class="card"><div class="label">Terminal</div><pre class="codeblock" style="min-height:0;margin:6px 0 0"><span class="ln">python3 -m venv .venv          <span class="c"># create</span></span><span class="ln">source .venv/bin/activate      <span class="c"># activate (Windows: .venv\\Scripts\\activate)</span></span><span class="ln">python -m pip install requests <span class="c"># install into this venv</span></span><span class="ln">pip list                       <span class="c"># what's installed</span></span><span class="ln">pip freeze &gt; requirements.txt  <span class="c"># pin versions</span></span><span class="ln">deactivate                     <span class="c"># leave the venv</span></span></pre></div>
    </div>''',
 "notes": [
  ["Added", "<b>From your Notion plans:</b> \"Modules &amp; packages (math/os/json, own modules, pip)\" and \"Virtual environments &amp; pip\" (Roadmap for Python), and \"Modules &amp; imports, venv\" (Week 2 of the 8-week plan)."],
  ["Added", "<b>Why a venv:</b> without one, <span class=\"mono\">pip install</span> puts packages into the system or user Python shared by every project, and versions clash. A venv is a folder with its own interpreter link and site-packages, like a per-project <span class=\"mono\">node_modules</span> or NuGet packages folder."],
  ["Added", "<b>Running a package module:</b> <span class=\"mono\">python -m clinic.billing</span> runs it with the right import paths; running <span class=\"mono\">python clinic/billing.py</span> directly often breaks its imports of sibling modules."],
  ["Updated", "<b>Newer tools:</b> <span class=\"mono\">uv</span> (Astral) creates venvs and installs packages much faster and is widely used now (<span class=\"mono\">uv venv</span>, <span class=\"mono\">uv pip install</span>, <span class=\"mono\">uv add</span>). Project metadata lives in <span class=\"mono\">pyproject.toml</span>. Plain venv + pip still works everywhere and is what the docs teach."]
 ],
 "quiz": [
  {"q": "You run <span class=\"mono\">python app.py</span>, and app.py does <span class=\"mono\">import billing</span>. What is <span class=\"mono\">__name__</span> inside billing.py?", "a": "<b class=\"mono\">\"billing\"</b>. Only the started file is <span class=\"mono\">\"__main__\"</span>."},
  {"q": "<span class=\"mono\">import math\\nprint(math.floor(2.7), math.ceil(2.1))</span>", "code": "import math\nprint(math.floor(2.7), math.ceil(2.1))", "expect": "2 3", "a": "<b class=\"mono\">2 3</b>. floor rounds down, ceil rounds up."},
  {"q": "Where does <span class=\"mono\">pip install requests</span> put the package when a venv is active?", "a": "Into that venv's <span class=\"mono\">site-packages</span> folder only. Other projects (and the system Python) don't see it. Check with <span class=\"mono\">which python</span> / <span class=\"mono\">python -m pip --version</span>."}
 ],
 "sources": "From the Notion plans (Roadmap for Python; Planning for python learning, Week 2). Python docs: Modules tutorial, venv, pip user guide."
}
