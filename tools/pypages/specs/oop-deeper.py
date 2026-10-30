import json, io, contextlib
LOG = []
class Money:
    def __init__(self, paise): self.paise = paise
    def __repr__(self): LOG.append("__repr__"); return f"Money({self.paise})"
    def __str__(self): LOG.append("__str__"); return f"Rs {self.paise / 100:.2f}"
    def __add__(self, o): LOG.append("__add__"); return Money(self.paise + o.paise)
    def __eq__(self, o): LOG.append("__eq__"); return isinstance(o, Money) and self.paise == o.paise
    def __lt__(self, o): LOG.append("__lt__"); return self.paise < o.paise
    def __bool__(self): LOG.append("__bool__"); return self.paise != 0
    __hash__ = None
class Cart:
    def __init__(self, items): self.items = items
    def __len__(self): LOG.append("__len__"); return len(self.items)
    def __iter__(self): LOG.append("__iter__"); return iter(self.items)
    def __getitem__(self, i): LOG.append("__getitem__"); return self.items[i]
    def __contains__(self, x): LOG.append("__contains__"); return x in self.items
EXPRS = ["print(a)", "str(a)", "repr(a)", "print([a, b])", "a + b", "a == Money(45050)", "a < b", "sorted([b, a])", "bool(Money(0))", "len(cart)", "cart[0]", "'ECG' in cart", "list(cart)", "f'{a}'", "a > b", "{a}"]
DUN = []
for e in EXPRS:
    LOG.clear()
    a, b, cart = Money(45050), Money(100000), Cart(["ECG", "X-ray"])
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            if e.startswith("print"):
                eval(e, {"a": a, "b": b, "Money": Money, "cart": cart}); r = buf.getvalue().rstrip("\n"); shown = "prints " + r
            else:
                r = eval(e, {"a": a, "b": b, "Money": Money, "cart": cart}); LOG_before = list(LOG); shown = repr(r); LOG[:] = LOG_before
    except TypeError as ex:
        shown = "TypeError: " + str(ex)
    calls = []
    for x in LOG:
        if not calls or calls[-1] != x: calls.append(x)
    DUN.append({"e": e, "calls": calls, "r": shown})

SPEC = {
 "slug": "oop-deeper", "num": 18, "part": "Going further",
 "title": "OOP deeper: dunders, properties, dataclasses", "title_plain": "OOP deeper: dunders, properties, dataclasses",
 "desc": "Python fundamentals: special (dunder) methods like __repr__, __str__, __eq__ and __add__, @property, @classmethod and @staticmethod, polymorphism, and @dataclass.",
 "lede": [
  "Python's operators and built-ins call <b>dunder methods</b> (double underscore): <span class=\"mono\">a + b</span> → <span class=\"mono\">a.__add__(b)</span>, <span class=\"mono\">len(x)</span> → <span class=\"mono\">x.__len__()</span>, <span class=\"mono\">print(x)</span> → <span class=\"mono\">x.__str__()</span>.",
  "Define <span class=\"mono\">__repr__</span> (for developers) and optionally <span class=\"mono\">__str__</span> (for users) so objects print usefully.",
  "<b>@property</b> makes a method read like an attribute; <b>@classmethod</b> gets the class (alternative constructors); <b>@staticmethod</b> gets neither.",
  "<b>@dataclass</b> writes <span class=\"mono\">__init__</span>, <span class=\"mono\">__repr__</span> and <span class=\"mono\">__eq__</span> from type-annotated fields: the quickest way to a clean data class."
 ],
 "walk": {"title": "money and patients done properly", "code":
'''from dataclasses import dataclass, field

class Money:
    def __init__(self, paise):
        self.paise = paise
    @classmethod
    def from_rupees(cls, rupees):
        return cls(round(rupees * 100))
    def __repr__(self):
        return f"Money({self.paise})"
    def __str__(self):
        return f"Rs {self.paise / 100:,.2f}"
    def __add__(self, other):
        return Money(self.paise + other.paise)

fee = Money.from_rupees(450.5) + Money(100000)
print(fee, repr(fee))

@dataclass
class Patient:
    name: str
    age: int
    visits: list = field(default_factory=list)
    @property
    def is_senior(self):
        return self.age >= 60

ravi = Patient("Ravi", 64)
print(ravi, ravi.is_senior, ravi == Patient("Ravi", 64))''',
 "steps": [
  {"at": 14, "title": "A classmethod gets the class", "text": "<span class=\"mono\">Money.from_rupees(450.5)</span> receives <span class=\"mono\">cls</span> (the Money class itself) instead of an instance. It's an <b>alternative constructor</b>: it converts rupees and calls <span class=\"mono\">cls(...)</span>."},
  {"at": 23, "title": "+ calls __add__", "text": "<span class=\"mono\">left + right</span> becomes <span class=\"mono\">left.__add__(right)</span>. Our method returns a <b>new</b> Money with the summed paise."},
  {"at": 36, "title": "print uses __str__, repr uses __repr__", "text": "<span class=\"mono\">print(fee)</span> called <span class=\"mono\">__str__</span>: <span class=\"mono\">Rs 1,450.50</span> for people. <span class=\"mono\">repr(fee)</span> called <span class=\"mono\">__repr__</span>: <span class=\"mono\">Money(145050)</span>, unambiguous, for logs and debugging. Storing paise as an int avoids float rounding errors."},
  {"at": 50, "title": "@dataclass writes the boilerplate", "text": "From the annotated fields <span class=\"mono\">name: str</span>, <span class=\"mono\">age: int</span>, <span class=\"mono\">visits: list</span>, the decorator generated <span class=\"mono\">__init__</span>, <span class=\"mono\">__repr__</span> and <span class=\"mono\">__eq__</span>.", "tip": "<span class=\"mono\">field(default_factory=list)</span> gives each patient its own new list: the dataclass way around the mutable-default trap."},
  {"at": 51, "title": "The generated __init__", "text": "<span class=\"mono\">Patient(\"Ravi\", 64)</span> set name, age and a fresh empty visits list. We didn't write a single <span class=\"mono\">self.x = x</span>."},
  {"at": 52, "title": "@property: a computed attribute", "text": "<span class=\"mono\">ravi.is_senior</span> has no brackets, yet it runs the method. Callers read it like data; you can later change how it's computed without breaking them."},
  {"at": "end", "title": "Free repr and equality", "text": "<span class=\"mono\">print(ravi)</span> shows <span class=\"mono\">Patient(name='Ravi', age=64, visits=[])</span>, and two patients with equal fields compare equal. A plain class would print an address and compare by identity."}
 ]},
 "walk_out": "Rs 1,450.50 Money(145050) / Patient(name='Ravi', age=64, visits=[]) True True",
 "puzzles": [
  {"id": "p1", "name": "1 · repr inside a list", "code": "class P:\n    def __init__(self, n): self.n = n\n    def __str__(self): return f\"P {self.n}\"\n    def __repr__(self): return f\"P({self.n!r})\"\n\nprint(P(\"a\"), [P(\"a\")])", "q": "What's printed?", "opts": ["P a [P a]", "P a [P('a')]", "P('a') [P('a')]"], "a": 1,
   "why": "print uses __str__ for the object itself, but a list shows its items with __repr__."},
  {"id": "p2", "name": "2 · == without __eq__", "code": "class P:\n    def __init__(self, n): self.n = n\n\nprint(P(1) == P(1))", "q": "What's printed?", "opts": ["True", "False", "TypeError"], "a": 1,
   "why": "The default __eq__ compares identity: two different objects are never equal. Define __eq__ or use @dataclass."},
  {"id": "p3", "name": "3 · property setter", "code": "class Patient:\n    def __init__(self, age):\n        self.age = age\n    @property\n    def age(self):\n        return self._age\n    @age.setter\n    def age(self, value):\n        if value < 0:\n            raise ValueError(\"age must be >= 0\")\n        self._age = value\n\np = Patient(30)\np.age = -1", "q": "What happens?", "opts": ["p.age becomes -1", "ValueError: age must be >= 0", "AttributeError"], "a": 1,
   "why": "Assigning to a property calls its setter, so validation runs on every assignment, including the one in __init__."},
  {"id": "p4", "name": "4 · polymorphism", "code": "class Email:\n    def send(self, msg): return f\"email: {msg}\"\nclass SMS:\n    def send(self, msg): return f\"sms: {msg[:10]}\"\n\nfor channel in [Email(), SMS()]:\n    print(channel.send(\"Your appointment is at 9:00\"))", "q": "What's printed?", "opts": ["email: Your appointment is at 9:00 / sms: Your appoi", "email: Your appointment is at 9:00 / email: Your appointment is at 9:00", "TypeError: no common base class"], "a": 0,
   "why": "Python only cares that the object has a <span class=\"mono\">send</span> method (\"duck typing\"). No shared base class or interface is required."},
  {"id": "p5", "name": "5 · staticmethod", "code": "class Fees:\n    @staticmethod\n    def with_tax(amount):\n        return amount * 1.18\n\nprint(Fees.with_tax(100), Fees().with_tax(100))", "q": "What's printed?", "opts": ["118.0 118.0", "118.0 TypeError", "TypeError"], "a": 0,
   "why": "A staticmethod gets no self or cls; call it on the class or an instance. It's just a function grouped in the class's namespace."}
 ],
 "runner_extra": [{"label": "Your turn: a dataclass with ordering", "code": 'from dataclasses import dataclass\n\n@dataclass(order=True)\nclass Slot:\n    hour: int\n    minute: int = 0\n    def __str__(self):\n        return f"{self.hour}:{self.minute:02d}"\n\nslots = [Slot(10, 30), Slot(9), Slot(9, 30)]\nprint([str(s) for s in sorted(slots)])\nprint(slots[1])'}],
 "custom": [
  {"id": "dun", "title": "Which dunder runs?", "kind": "a = Money(45050), b = Money(100000), cart holds two tests · pick an expression",
   "html": '''    <details class="rn-inputs" style="margin-bottom:10px"><summary>Which dunders do Money and Cart define?</summary><p class="mono" style="margin:8px 0 0">Money: __init__ __repr__ __str__ __add__ __eq__ __lt__ __bool__ (and __hash__ = None)<br>Cart: __init__ __len__ __iter__ __getitem__ __contains__</p></details>
    <div class="chips" id="dnBtns"></div>
    <div class="dn-flow"><div class="dn-box mono" id="dnExpr">expression</div><div class="dn-arr">→</div><div class="dn-box mono dn-calls" id="dnCalls">dunder calls</div><div class="dn-arr">→</div><div class="dn-box mono" id="dnRes">result</div></div>
    <p class="status-line" id="dnStatus">Every result here was produced by running the expression and logging each dunder call.</p>''',
   "js": '''    const DUN = __DUN__;
    $('dnBtns').innerHTML = DUN.map((d, i) => `<button class="chip-btn mono" type="button" data-i="${i}" aria-pressed="false">${d.e.replace(/</g, '&lt;')}</button>`).join('');
    const NOTE = { 'a > b': 'There is no __gt__, so Python tried the reflected b.__lt__(a).', '{a}': 'A set needs __hash__; defining __eq__ without __hash__ makes objects unhashable (we set it to None explicitly).', 'print([a, b])': 'Containers show their items with __repr__.', "f'{a}'": 'f-strings call format(), which falls back to __str__.', 'sorted([b, a])': 'sorted() only needs __lt__.', 'list(cart)': 'list() iterates with __iter__, and also asks __len__ for a size hint to pre-allocate.' };
    $('dnBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => {
      $('dnBtns').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === b)));
      const d = DUN[+b.dataset.i];
      $('dnExpr').textContent = d.e;
      $('dnCalls').innerHTML = d.calls.length ? d.calls.map(c => `<span class="dn-c">${c}</span>`).join(' ') : '<span class="muted">(none)</span>';
      $('dnRes').innerHTML = /Error/.test(d.r) ? `<span class="bad-text">${d.r.replace(/</g, '&lt;')}</span>` : d.r.replace(/</g, '&lt;');
      $('dnStatus').textContent = NOTE[d.e] || 'Python translated the syntax into the dunder call shown.';
    }));'''.replace('__DUN__', json.dumps(DUN))}
 ],
 "style": '''  .dn-flow { display: grid; grid-template-columns: 1fr auto 1.2fr auto 1.4fr; gap: 10px; align-items: center; margin-top: 14px; }
  @media (max-width: 640px) { .dn-flow { grid-template-columns: 1fr; } .dn-arr { transform: rotate(90deg); justify-self: center; } }
  .dn-box { border: 1.5px solid var(--line); border-radius: 12px; padding: 12px; background: var(--panel-2); min-height: 48px; overflow-wrap: anywhere; font-size: 14px; }
  .dn-arr { color: var(--muted); font-size: 20px; }
  .dn-c { display: inline-block; padding: 2px 8px; margin: 2px; border-radius: 6px; background: var(--teal-wash); color: var(--fg); }''',
 "cheat": [
  ["Objects print as &lt;… at 0x…&gt;", "Add <span class=\"mono\">__repr__</span> (or use @dataclass)"],
  ["Mostly-data class", "<span class=\"mono\">@dataclass</span>; <span class=\"mono\">frozen=True</span> for immutable, <span class=\"mono\">order=True</span> for sorting"],
  ["Validate on assignment / computed value", "<span class=\"mono\">@property</span> (+ <span class=\"mono\">@x.setter</span>)"],
  ["Build an object from another format", "<span class=\"mono\">@classmethod def from_json(cls, data):</span>"],
  ["Helper that needs no self or cls", "<span class=\"mono\">@staticmethod</span>, or just a module-level function"],
  ["Make == work", "<span class=\"mono\">__eq__</span> (and <span class=\"mono\">__hash__</span> if used in sets/dict keys)"],
  ["Different classes, same method name", "Polymorphism: call it without checking the type"]
 ],
 "ref_title": "Reference: common dunders",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>You write</th><th>Python calls</th><th>Default without it</th></tr></thead>
        <tbody>
          <tr><td class="mono">print(x), str(x)</td><td class="mono">__str__</td><td>falls back to __repr__</td></tr>
          <tr><td class="mono">repr(x), x in a list</td><td class="mono">__repr__</td><td class="mono">&lt;Cls object at 0x…&gt;</td></tr>
          <tr><td class="mono">x == y</td><td class="mono">__eq__</td><td>identity (<span class="mono">is</span>)</td></tr>
          <tr><td class="mono">x &lt; y, sorted()</td><td class="mono">__lt__</td><td>TypeError</td></tr>
          <tr><td class="mono">x + y</td><td class="mono">__add__ / __radd__</td><td>TypeError</td></tr>
          <tr><td class="mono">len(x), bool(x)</td><td class="mono">__len__, __bool__</td><td>len: TypeError; bool: True</td></tr>
          <tr><td class="mono">for i in x, x[i], k in x</td><td class="mono">__iter__, __getitem__, __contains__</td><td>TypeError</td></tr>
          <tr><td class="mono">with x:</td><td class="mono">__enter__, __exit__</td><td>TypeError</td></tr>
          <tr><td class="mono">x()</td><td class="mono">__call__</td><td>TypeError: not callable</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Added", "<b>From your Notion plan:</b> \"classes (__init__/__str__/__repr__), inheritance &amp; polymorphism, @staticmethod/@classmethod\" (8-week plan, Week 5)."],
  ["Added", "<b>Fixing the repo's classes:</b> <span class=\"mono\">Car</span> and <span class=\"mono\">Employee</span> are mostly data, so <span class=\"mono\">@dataclass</span> would remove their __init__ boilerplate and give printable objects; <span class=\"mono\">display_car_info()</span> becomes <span class=\"mono\">__str__</span>."],
  ["Added", "<b>Coming from C#:</b> @property ≈ a C# property with get/set; dunders ≈ operator overloads and ToString()/Equals()/GetHashCode() overrides; @dataclass ≈ a <span class=\"mono\">record</span>. Python has no interfaces by default: duck typing, or <span class=\"mono\">typing.Protocol</span> / <span class=\"mono\">abc.ABC</span> when you want them."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">from dataclasses import dataclass\\n@dataclass(frozen=True)\\nclass P:\\n    x: int\\np = P(1); p.x = 2</span>", "code": "from dataclasses import dataclass\n@dataclass(frozen=True)\nclass P:\n    x: int\np = P(1); p.x = 2", "expect": "FrozenInstanceError", "a": "<b class=\"mono\">FrozenInstanceError</b>. Frozen dataclasses are immutable (and hashable)."},
  {"q": "<span class=\"mono\">class A:\\n    def __len__(self): return 0\\nprint(bool(A()))</span>", "code": "class A:\n    def __len__(self): return 0\nprint(bool(A()))", "expect": "False", "a": "<b class=\"mono\">False</b>. Without __bool__, truthiness falls back to __len__ != 0."},
  {"q": "<span class=\"mono\">class C:\\n    count = 0\\n    @classmethod\\n    def make(cls):\\n        cls.count += 1\\n        return cls()\\nC.make(); C.make(); print(C.count)</span>", "code": "class C:\n    count = 0\n    @classmethod\n    def make(cls):\n        cls.count += 1\n        return cls()\nC.make(); C.make(); print(C.count)", "expect": "2", "a": "<b class=\"mono\">2</b>. A classmethod can update class-level state."}
 ],
 "sources": "From the Notion plan (Planning for python learning, Week 5). Python docs: Data model, dataclasses, property."
}
