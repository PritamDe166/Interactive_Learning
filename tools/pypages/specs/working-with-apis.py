import json
REQS = [
 {"label": "GET patients in Pune", "code": 'r = requests.get(f"{BASE}/patients", params={"city": "Pune"}, headers=AUTH, timeout=10)',
  "req": "GET /v1/patients?city=Pune HTTP/1.1\nHost: api.example.com\nAuthorization: Bearer ••••\nAccept: application/json",
  "status": "200 OK", "body": json.dumps({"items": [{"id": 7, "name": "Asha", "age": 35}, {"id": 9, "name": "Meera", "age": 29}], "next": None}, indent=1),
  "py": "r.status_code → 200\nr.raise_for_status() → (nothing, it's OK)\nr.json()[\"items\"][0][\"name\"] → 'Asha'", "ok": True},
 {"label": "POST a new appointment", "code": 'r = requests.post(f"{BASE}/appointments", json={"patient_id": 7, "slot": "2026-11-02T09:00"}, headers=AUTH, timeout=10)',
  "req": "POST /v1/appointments HTTP/1.1\nHost: api.example.com\nAuthorization: Bearer ••••\nContent-Type: application/json\n\n{\"patient_id\": 7, \"slot\": \"2026-11-02T09:00\"}",
  "status": "201 Created", "body": json.dumps({"id": 501, "patient_id": 7, "slot": "2026-11-02T09:00", "status": "booked"}, indent=1),
  "py": "r.status_code → 201\nr.json()[\"id\"] → 501", "ok": True},
 {"label": "GET a missing patient", "code": 'r = requests.get(f"{BASE}/patients/999", headers=AUTH, timeout=10)',
  "req": "GET /v1/patients/999 HTTP/1.1\nHost: api.example.com\nAuthorization: Bearer ••••", "status": "404 Not Found", "body": json.dumps({"error": "patient 999 not found"}, indent=1),
  "py": "r.status_code → 404\nr.ok → False\nr.raise_for_status() → raises requests.HTTPError: 404 Client Error", "ok": False},
 {"label": "Forgot the token", "code": 'r = requests.get(f"{BASE}/patients", timeout=10)',
  "req": "GET /v1/patients HTTP/1.1\nHost: api.example.com", "status": "401 Unauthorized", "body": json.dumps({"error": "missing bearer token"}, indent=1),
  "py": "r.status_code → 401\nr.raise_for_status() → raises requests.HTTPError: 401 Client Error", "ok": False},
 {"label": "Server too slow", "code": 'r = requests.get(f"{BASE}/reports/yearly", headers=AUTH, timeout=10)',
  "req": "GET /v1/reports/yearly HTTP/1.1\nHost: api.example.com\nAuthorization: Bearer ••••", "status": "(no response within 10 s)", "body": "",
  "py": "requests.get(...) → raises requests.Timeout\n(no r object at all: wrap the call in try/except)", "ok": False},
]

SPEC = {
 "slug": "working-with-apis", "num": 20, "part": "Going further",
 "title": "Working with APIs", "title_plain": "Working with APIs",
 "desc": "Python fundamentals: calling HTTP APIs with requests, query parameters, JSON bodies, status codes, raise_for_status, timeouts, and paging through results.",
 "lede": [
  "A web API is a URL that returns <b>data</b> (usually JSON) instead of a page. You send an HTTP <b>request</b> (method, URL, headers, body) and get a <b>response</b> (status code, headers, body).",
  "The <b>requests</b> library: <span class=\"mono\">requests.get(url, params=…, headers=…, timeout=…)</span>, <span class=\"mono\">requests.post(url, json=…)</span>.",
  "Check the outcome with <span class=\"mono\">r.status_code</span> or <span class=\"mono\">r.raise_for_status()</span>, then decode with <span class=\"mono\">r.json()</span>, which gives plain dicts and lists.",
  "Always set a <b>timeout</b>, keep secrets out of code, and expect lists to come in <b>pages</b>."
 ],
 "walk": {"title": "paging through an API (simulated)", "code":
'''import json
from urllib.parse import urlencode

def fake_get(url):
    pages = {
        "/patients?city=Pune&page=1": (200, '{"items": [{"name": "Asha"}], "next": 2}'),
        "/patients?city=Pune&page=2": (200, '{"items": [{"name": "Meera"}], "next": null}'),
    }
    return pages.get(url, (404, '{"error": "not found"}'))

page, everyone = 1, []
while page:
    url = "/patients?" + urlencode({"city": "Pune", "page": page})
    status, body = fake_get(url)
    if status != 200:
        raise RuntimeError(f"HTTP {status}")
    data = json.loads(body)
    everyone += [p["name"] for p in data["items"]]
    page = data["next"]
print(everyone)
status, body = fake_get("/doctors")
print(status, json.loads(body)["error"])''',
 "steps": [
  {"at": {"after": 4}, "title": "A stand-in for the network", "text": "The page runs in your browser, which can't call real APIs freely, so <span class=\"mono\">fake_get</span> plays the server: it returns a <b>status code</b> and a JSON <b>text body</b>, exactly what <span class=\"mono\">requests.get</span> gives you as <span class=\"mono\">r.status_code</span> and <span class=\"mono\">r.text</span>."},
  {"at": {"after": 13, "n": 1}, "title": "Build the query string safely", "text": "<span class=\"mono\">urlencode</span> turns a dict into <span class=\"mono\">city=Pune&amp;page=1</span>, escaping spaces and symbols. With requests you'd pass <span class=\"mono\">params={\"city\": \"Pune\", \"page\": 1}</span> and it does this for you."},
  {"at": 13, "title": "Send the request, get status + body", "text": "The response body is still <b>text</b>. Nothing is a dict yet."},
  {"at": 14, "title": "Check the status first", "text": "2xx means success. Anything else should stop or retry rather than be parsed as data. <span class=\"mono\">r.raise_for_status()</span> does this check in one call."},
  {"at": 15, "title": "JSON text → Python objects", "text": "<span class=\"mono\">json.loads(body)</span> (or <span class=\"mono\">r.json()</span>) gives dicts and lists; JSON <span class=\"mono\">null</span> becomes <span class=\"mono\">None</span>."},
  {"at": {"after": 19, "n": 1}, "title": "Follow the next page", "text": "APIs return big lists in <b>pages</b>. This one says <span class=\"mono\">\"next\": 2</span>, so the loop asks again with page=2."},
  {"at": {"after": 19, "n": 2}, "title": "No next page: done", "text": "Page 2's <span class=\"mono\">next</span> is null → None, which is falsy, so <span class=\"mono\">while page</span> ends. We collected both patients."},
  {"at": "end", "title": "Errors come back as data too", "text": "An unknown path returns <b>404</b> with an error message in the body. Read the body: good APIs explain what went wrong."}
 ]},
 "walk_out": "['Asha', 'Meera'] / 404 not found",
 "puzzles": [
  {"id": "p1", "name": "1 · text or dict?", "code": "import json\nbody = '{\"name\": \"Asha\", \"vip\": false}'\nprint(type(body).__name__, json.loads(body)[\"vip\"])", "q": "What's printed?", "opts": ["dict False", "str False", "str false"], "a": 1,
   "why": "A response body is text until you decode it. JSON <span class=\"mono\">false</span> becomes Python <span class=\"mono\">False</span>."},
  {"id": "p2", "name": "2 · query strings", "code": "from urllib.parse import urlencode\nprint(urlencode({\"name\": \"Asha Rao\", \"city\": \"Pune & Co\"}))", "q": "What's printed?", "opts": ["name=Asha Rao&city=Pune & Co", "name=Asha+Rao&city=Pune+%26+Co", "name=Asha%20Rao,city=Pune%26Co"], "a": 1,
   "why": "Spaces become + and & becomes %26, so values can't break the URL. Never build query strings with plain f-strings."},
  {"id": "p3", "name": "3 · missing key", "code": "import json\ndata = json.loads('{\"items\": []}')\nprint(data.get(\"next\"), len(data[\"items\"]))\nprint(data[\"next\"])", "q": "What's printed?", "opts": ["None 0 / None", "None 0 / KeyError: 'next'", "KeyError"], "a": 1,
   "why": "Optional fields may be absent. Use <span class=\"mono\">.get()</span> for those, and <span class=\"mono\">[ ]</span> only for fields the API guarantees."},
  {"id": "p4", "name": "4 · status ranges", "code": "for code in [200, 201, 204, 301, 404, 500]:\n    print(code, 200 <= code < 300, end=\" | \")", "q": "Which codes count as success?", "opts": ["200 only", "200, 201, 204", "200, 201, 204, 301"], "a": 1, "check": False,
   "why": "Every 2xx is success: 201 Created and 204 No Content included. 3xx is a redirect (requests follows them for you), 4xx is your mistake, 5xx the server's."}
 ],
 "runner_extra": [{"label": "Your turn: summarise an API response", "code": 'import json\nbody = """{"items": [\n  {"name": "Asha", "city": "Pune", "fee": 450},\n  {"name": "Ravi", "city": "Delhi", "fee": 800},\n  {"name": "Meera", "city": "Pune", "fee": 1200}\n]}"""\nrows = json.loads(body)["items"]\nby_city = {}\nfor r in rows:\n    by_city.setdefault(r["city"], []).append(r["name"])\nprint(by_city)\nprint("total fees:", sum(r["fee"] for r in rows))'}],
 "custom": [
  {"id": "http", "title": "An HTTP round trip", "kind": "Pick a request · see what travels, what comes back, and what requests gives you",
   "html": '''    <div class="chips" id="htBtns"></div>
    <pre class="codeblock" id="htCode" style="min-height:0;margin-top:10px"></pre>
    <div class="ht-lane"><div class="ht-end">Your Python</div><div class="ht-wire"><span class="ht-pill" id="htPill">request</span></div><div class="ht-end">api.example.com</div></div>
    <div class="two">
      <div class="card"><div class="label">Request</div><pre class="mono ht-msg" id="htReq"></pre></div>
      <div class="card"><div class="label">Response <span id="htStatus" class="mono"></span></div><pre class="mono ht-msg" id="htBody"></pre></div>
    </div>
    <div class="card" style="margin-top:10px"><div class="label">In Python</div><pre class="mono ht-msg" id="htPy"></pre></div>''',
   "js": '''    const RQ = __RQ__;
    $('htBtns').innerHTML = RQ.map((r, i) => `<button class="chip-btn" type="button" data-i="${i}" aria-pressed="false">${r.label}</button>`).join('');
    const e = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;');
    async function go(i) {
      const run = K.newRun('ht'), r = RQ[i], pill = $('htPill');
      $('htCode').innerHTML = `<span class="ln">${K.pyHighlight(r.code)}</span>`;
      $('htReq').textContent = ''; $('htBody').textContent = ''; $('htStatus').textContent = ''; $('htPy').textContent = '';
      pill.className = 'ht-pill'; pill.textContent = r.req.split(' ')[0] + ' ' + r.req.split(' ')[1].split('?')[0];
      try {
        $('htReq').textContent = r.req; pill.classList.add('go'); await K.sleep(900, run);
        if (!r.body) { pill.classList.add('lost'); pill.textContent = 'waiting…'; await K.sleep(900, run); $('htStatus').innerHTML = `<span class="bad-text">${r.status}</span>`; }
        else {
          pill.textContent = r.status; pill.classList.add('back', r.ok ? 'ok' : 'bad'); await K.sleep(900, run);
          $('htStatus').innerHTML = `<span class="${r.ok ? 'ok-text' : 'bad-text'}">${r.status}</span>`; $('htBody').textContent = r.body;
        }
        $('htPy').innerHTML = e(r.py).replace(/raises ([\\w.]+)/g, '<span class="bad-text">raises $1</span>');
      } catch (er) { if (!(er instanceof K.Stop)) throw er; }
    }
    $('htBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => { $('htBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b))); go(+b.dataset.i); }));'''.replace('__RQ__', json.dumps(REQS))}
 ],
 "style": '''  .ht-lane { display: grid; grid-template-columns: auto 1fr auto; gap: 10px; align-items: center; margin: 14px 0 10px; }
  .ht-end { font-family: var(--mono); font-size: 13px; padding: 10px 12px; border-radius: 10px; border: 1.5px solid var(--line); background: var(--panel-2); }
  .ht-wire { position: relative; height: 34px; border-bottom: 2px dashed var(--line); }
  .ht-pill { position: absolute; left: 0; top: 2px; font-family: var(--mono); font-size: 12px; padding: 4px 10px; border-radius: 999px; background: var(--cyan); color: var(--bg, #000); white-space: nowrap; transition: left .8s ease, transform .8s ease; transform: translateX(0); }
  .ht-pill.go { left: 100%; transform: translateX(-100%); }
  .ht-pill.go.back { left: 0; transform: translateX(0); }
  .ht-pill.ok { background: var(--teal); }
  .ht-pill.bad { background: var(--red); }
  .ht-pill.lost { opacity: .5; }
  .ht-msg { margin: 4px 0 0; white-space: pre-wrap; overflow-wrap: anywhere; font-size: 12.5px; min-height: 40px; }''',
 "cheat": [
  ["Read data", "<span class=\"mono\">r = requests.get(url, params={...}, timeout=10)</span>"],
  ["Send data", "<span class=\"mono\">requests.post(url, json=payload, timeout=10)</span> (sets the JSON header for you)"],
  ["Did it work?", "<span class=\"mono\">r.raise_for_status()</span>, or check <span class=\"mono\">r.ok</span> / <span class=\"mono\">r.status_code</span>"],
  ["Body as Python", "<span class=\"mono\">r.json()</span>; <span class=\"mono\">r.text</span> for raw text"],
  ["API keys and tokens", "From an environment variable: <span class=\"mono\">os.environ[\"API_TOKEN\"]</span>, never in the code"],
  ["Many calls to one host", "<span class=\"mono\">with requests.Session() as s:</span> reuses connections and headers"],
  ["Long lists", "Loop on the API's next page / cursor until it's empty"]
 ],
 "ref_title": "Reference: requests in a real script",
 "ref_html": '''    <div class="card"><pre class="codeblock" style="min-height:0;margin:0"><span class="ln"><span class="k">import</span> os</span><span class="ln"><span class="k">import</span> requests   <span class="c"># pip install requests (inside your venv)</span></span><span class="ln"></span><span class="ln">BASE = <span class="s">"https://api.example.com/v1"</span></span><span class="ln">AUTH = {<span class="s">"Authorization"</span>: <span class="s">f"Bearer {os.environ['API_TOKEN']}"</span>}</span><span class="ln"></span><span class="ln"><span class="k">try</span>:</span><span class="ln">    r = requests.get(<span class="s">f"{BASE}/patients"</span>, params={<span class="s">"city"</span>: <span class="s">"Pune"</span>}, headers=AUTH, timeout=<span class="n">10</span>)</span><span class="ln">    r.raise_for_status()</span><span class="ln"><span class="k">except</span> requests.Timeout:</span><span class="ln">    <span class="b">print</span>(<span class="s">"server too slow, try later"</span>)</span><span class="ln"><span class="k">except</span> requests.HTTPError <span class="k">as</span> e:</span><span class="ln">    <span class="b">print</span>(<span class="s">"API said no:"</span>, e.response.status_code, e.response.text)</span><span class="ln"><span class="k">else</span>:</span><span class="ln">    <span class="k">for</span> p <span class="k">in</span> r.json()[<span class="s">"items"</span>]:</span><span class="ln">        <span class="b">print</span>(p[<span class="s">"name"</span>])</span></pre></div>
    <div class="scroll card table-card" style="margin-top:12px"><table><thead><tr><th>Status</th><th>Meaning</th><th>Typical reaction</th></tr></thead><tbody>
      <tr><td class="mono">200 / 201 / 204</td><td>OK / created / no content</td><td>use the body (none for 204)</td></tr>
      <tr><td class="mono">400 / 422</td><td>your request is invalid</td><td>fix the data; read the error body</td></tr>
      <tr><td class="mono">401 / 403</td><td>not authenticated / not allowed</td><td>check the token or permissions</td></tr>
      <tr><td class="mono">404</td><td>no such resource</td><td>handle \"not found\"</td></tr>
      <tr><td class="mono">429</td><td>too many requests</td><td>wait (Retry-After header) and retry</td></tr>
      <tr><td class="mono">500 / 502 / 503</td><td>server-side problem</td><td>retry later with backoff</td></tr>
    </tbody></table></div>''',
 "notes": [
  ["Added", "<b>From your Notion Roadmap:</b> \"Working with APIs (requests, JSON)\", the last step before AI agents, which are mostly API calls with JSON in and JSON out."],
  ["Added", "<b>Why it's simulated here:</b> the edit-and-run box uses Pyodide in the browser, where <span class=\"mono\">requests</span> can't open network connections and browsers block most cross-site calls (CORS). Run the reference script in your own venv against a real or test API."],
  ["Added", "<b>Timeouts:</b> requests has <b>no default timeout</b>, so a hung server can freeze your script forever. Always pass <span class=\"mono\">timeout=</span>."],
  ["Updated", "<b>Alternatives:</b> <span class=\"mono\">httpx</span> offers the same style plus async support (<span class=\"mono\">async with httpx.AsyncClient()</span>), common in FastAPI and agent code. requests remains the most widely used synchronous client."]
 ],
 "quiz": [
  {"q": "What's the difference between <span class=\"mono\">params=</span> and <span class=\"mono\">json=</span> in requests?", "a": "<span class=\"mono\">params</span> go into the <b>URL query string</b> (<span class=\"mono\">?city=Pune</span>); <span class=\"mono\">json</span> is serialised into the <b>request body</b> with a <span class=\"mono\">Content-Type: application/json</span> header (typical for POST/PUT)."},
  {"q": "<span class=\"mono\">import json\\nprint(json.loads('{\"next\": null}')[\"next\"] is None)</span>", "code": "import json\nprint(json.loads('{\"next\": null}')[\"next\"] is None)", "expect": "True", "a": "<b class=\"mono\">True</b>. JSON null → None."},
  {"q": "Does <span class=\"mono\">requests.get()</span> raise an exception for a 404?", "a": "<b>No.</b> It returns a response with <span class=\"mono\">status_code</span> 404. Only network problems (timeouts, DNS, refused connections) raise. Call <span class=\"mono\">r.raise_for_status()</span> to turn 4xx/5xx into an <span class=\"mono\">HTTPError</span>."}
 ],
 "sources": "From the Notion Roadmap for Python (Working with APIs: requests, JSON). requests documentation (Quickstart, Timeouts). Example host api.example.com is a reserved example domain."
}
