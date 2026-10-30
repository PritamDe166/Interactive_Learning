SPEC = {
 "slug": "classes-objects", "num": 12, "part": "Real programs",
 "title": "Classes &amp; objects", "title_plain": "Classes & objects",
 "desc": "Python fundamentals: classes as blueprints, __init__ and self, instance vs class attributes, methods, inheritance with super(), and how attribute lookup works.",
 "lede": [
  "A <b>class</b> is a blueprint; calling it (<span class=\"mono\">Patient(\"Asha\", 35)</span>) creates an <b>instance</b>, a new object with its own attributes.",
  "<span class=\"mono\">__init__</span> runs right after the object is created to fill in its attributes. <span class=\"mono\">self</span> is that new object.",
  "<b>Methods</b> are functions defined in the class. <span class=\"mono\">asha.book(\"9:00\")</span> is really <span class=\"mono\">Patient.book(asha, \"9:00\")</span>.",
  "A <b>subclass</b> inherits everything from its parent, can <b>override</b> methods, and calls the parent's version with <span class=\"mono\">super()</span>.",
  "Looking up <span class=\"mono\">obj.x</span> checks the <b>instance</b>, then its <b>class</b>, then the <b>parent classes</b>."
 ],
 "walk": {"title": "patients and VIP patients", "code":
'''class Patient:
    clinic = "Pune"
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.visits = []
    def book(self, slot):
        self.visits.append(slot)
        return len(self.visits)

class VIPPatient(Patient):
    def __init__(self, name, age, tier):
        super().__init__(name, age)
        self.tier = tier
    def book(self, slot):
        n = super().book(slot)
        return f"{self.tier} #{n}"

asha = Patient("Asha", 35)
ravi = VIPPatient("Ravi", 41, "gold")
print(asha.book("9:00"), ravi.book("9:30"))
print(asha.clinic, isinstance(ravi, Patient))''',
 "steps": [
  {"at": 13, "title": "class statements build class objects", "text": "Running a <span class=\"mono\">class</span> block creates a <b>class object</b> holding its attributes: <span class=\"mono\">clinic</span> and the functions <span class=\"mono\">__init__</span> and <span class=\"mono\">book</span>. No patient exists yet."},
  {"at": 14, "title": "Calling the class: __init__ gets a blank object", "text": "<span class=\"mono\">Patient(\"Asha\", 35)</span> makes a new, empty instance and passes it to <span class=\"mono\">__init__</span> as <b>self</b>, followed by your arguments."},
  {"at": 18, "title": "self.x = … stores on the instance", "text": "Each <span class=\"mono\">self.attr = value</span> puts an attribute on <b>this</b> object. <span class=\"mono\">__init__</span> returns None; the call to <span class=\"mono\">Patient(...)</span> evaluates to the new instance, now bound to <span class=\"mono\">asha</span>."},
  {"at": 22, "title": "Subclass __init__ calls super()", "text": "<span class=\"mono\">VIPPatient</span> has its own <span class=\"mono\">__init__</span>. Its first line, <span class=\"mono\">super().__init__(name, age)</span>, runs the parent's version on the <b>same</b> self. Two frames for one object."},
  {"at": 29, "title": "The VIP instance", "text": "<span class=\"mono\">ravi</span> got name, age and visits from Patient's <span class=\"mono\">__init__</span>, plus <span class=\"mono\">tier</span> from its own. It is a VIPPatient <b>and</b> a Patient."},
  {"at": 30, "title": "asha.book(\"9:00\")", "text": "Python finds <span class=\"mono\">book</span> on the Patient class and calls it with <span class=\"mono\">self = asha</span>. The method changes asha's own <span class=\"mono\">visits</span> list."},
  {"at": 36, "title": "Override + super()", "text": "For <span class=\"mono\">ravi.book</span>, Python finds VIPPatient's <span class=\"mono\">book</span> first (it <b>overrides</b> the parent's). That method calls <span class=\"mono\">super().book(slot)</span> to reuse the parent logic, then adds the tier."},
  {"at": "end", "title": "Class attributes are shared", "text": "<span class=\"mono\">asha.clinic</span> isn't on the instance, so Python looks in the class: <span class=\"mono\">'Pune'</span>, shared by every patient. <span class=\"mono\">isinstance(ravi, Patient)</span> is True because a subclass instance counts as its parent type."}
 ]},
 "walk_out": "1 gold #1 / Pune True",
 "puzzles": [
  {"id": "p1", "name": "1 · forgetting self", "code": "class Counter:\n    def __init__(self):\n        count = 0\n\nc = Counter()\nprint(c.count)", "q": "What happens?", "opts": ["0", "AttributeError: 'Counter' object has no attribute 'count'", "None"], "a": 1,
   "why": "<span class=\"mono\">count = 0</span> without <span class=\"mono\">self.</span> is just a local variable of __init__, gone when it returns. Write <span class=\"mono\">self.count = 0</span>."},
  {"id": "p2", "name": "2 · shared class list", "code": "class Ward:\n    beds = []\n    def add(self, name):\n        self.beds.append(name)\n\na = Ward(); b = Ward()\na.add(\"Asha\")\nprint(b.beds)", "q": "What's printed?", "opts": ["[]", "['Asha']", "AttributeError"], "a": 1,
   "why": "<span class=\"mono\">beds</span> is a <b>class</b> attribute: one list shared by all instances. Create per-instance lists in __init__: <span class=\"mono\">self.beds = []</span>."},
  {"id": "p3", "name": "3 · shadowing a class attribute", "code": "class Patient:\n    clinic = \"Pune\"\n\na = Patient(); b = Patient()\na.clinic = \"Delhi\"\nprint(a.clinic, b.clinic, Patient.clinic)", "q": "What's printed?", "opts": ["Delhi Delhi Delhi", "Delhi Pune Pune", "Delhi Pune Delhi"], "a": 1,
   "why": "Assigning <span class=\"mono\">a.clinic</span> creates an <b>instance</b> attribute on a only, which hides the class one for a. b still finds the class value."},
  {"id": "p4", "name": "4 · printing an object", "code": "class Patient:\n    def __init__(self, name):\n        self.name = name\n\nprint(Patient(\"Asha\"))", "q": "What's printed?", "opts": ["Asha", "<__main__.Patient object at 0x…>", "Patient(name='Asha')"], "a": 1, "check": False,
   "why": "Without <span class=\"mono\">__str__</span> or <span class=\"mono\">__repr__</span>, Python prints the class and a memory address. Adding <span class=\"mono\">__repr__</span> is covered in OOP deeper; <span class=\"mono\">@dataclass</span> writes it for you."},
  {"id": "p5", "name": "5 · override without super", "code": "class Base:\n    def __init__(self):\n        self.id = 1\n\nclass Child(Base):\n    def __init__(self):\n        self.name = \"c\"\n\nprint(vars(Child()))", "q": "What's printed?", "opts": ["{'id': 1, 'name': 'c'}", "{'name': 'c'}", "{'id': 1}"], "a": 1,
   "why": "Child's __init__ replaces Base's completely. Base's code never ran because <span class=\"mono\">super().__init__()</span> wasn't called."},
  {"id": "p6", "name": "6 · method call = function call", "code": "class Account:\n    def __init__(self, balance):\n        self.balance = balance\n    def deposit(self, amount):\n        self.balance += amount\n\nacc = Account(100)\nAccount.deposit(acc, 50)\nacc.deposit(25)\nprint(acc.balance)", "q": "What's printed?", "opts": ["175", "125", "TypeError"], "a": 0,
   "why": "<span class=\"mono\">acc.deposit(25)</span> is shorthand for <span class=\"mono\">Account.deposit(acc, 25)</span>: both work, both add."}
 ],
 "runner_extra": [{"label": "Your turn: a safer bank account", "code": 'class BankAccount:\n    def __init__(self, owner, balance=0):\n        self.owner = owner\n        self.balance = balance\n    def withdraw(self, amount):\n        if amount > self.balance:\n            raise ValueError("insufficient funds")\n        self.balance -= amount\n    def __repr__(self):\n        return f"BankAccount({self.owner!r}, {self.balance})"\n\nacc = BankAccount("John", 1000)\nacc.withdraw(200)\nprint(acc)\n# Try: acc.withdraw(5000) inside try/except'}],
 "custom": [
  {"id": "mro", "title": "Attribute lookup chain", "kind": "Look up an attribute on ravi · Python walks instance → class → parents",
   "html": '''    <div class="chips" id="moBtns"><button class="chip-btn mono" type="button" data-a="name">ravi.name</button><button class="chip-btn mono" type="button" data-a="tier">ravi.tier</button><button class="chip-btn mono" type="button" data-a="book">ravi.book</button><button class="chip-btn mono" type="button" data-a="clinic">ravi.clinic</button><button class="chip-btn mono" type="button" data-a="__eq__">ravi.__eq__</button><button class="chip-btn mono" type="button" data-a="phone">ravi.phone</button></div>
    <div class="mo-row" id="moRow">
      <div class="mo-box" data-k="inst"><div class="mo-h">instance <span class="mono">ravi</span></div><div class="mono mo-a">name · age · visits · tier</div></div>
      <div class="mo-arr">→</div>
      <div class="mo-box" data-k="vip"><div class="mo-h">class <span class="mono">VIPPatient</span></div><div class="mono mo-a">__init__ · book</div></div>
      <div class="mo-arr">→</div>
      <div class="mo-box" data-k="pat"><div class="mo-h">class <span class="mono">Patient</span></div><div class="mono mo-a">clinic · __init__ · book</div></div>
      <div class="mo-arr">→</div>
      <div class="mo-box" data-k="obj"><div class="mo-h">class <span class="mono">object</span></div><div class="mono mo-a">__eq__ · __repr__ · __str__ · …</div></div>
    </div>
    <p class="status-line" id="moStatus">Pick an attribute. <span class="mono">VIPPatient.__mro__</span> is exactly this order.</p>''',
   "js": '''    const WHERE = { name: 'inst', tier: 'inst', book: 'vip', clinic: 'pat', __eq__: 'obj' };
    const NOTE = { name: "'Ravi', set by Patient.__init__ via super()", tier: "'gold', set by VIPPatient.__init__", book: "VIPPatient.book: the override wins; Patient.book is never reached", clinic: "'Pune', a class attribute shared by all patients", __eq__: "inherited from object, the root of every class" };
    const order = ['inst', 'vip', 'pat', 'obj'];
    async function go(a) {
      const run = K.newRun('mo'); const boxes = [...document.querySelectorAll('#moRow .mo-box')];
      boxes.forEach(b => b.classList.remove('look', 'hit', 'miss'));
      try {
        for (const k of order) {
          const b = boxes.find(x => x.dataset.k === k); b.classList.add('look'); await K.sleep(500, run); b.classList.remove('look');
          if (WHERE[a] === k) { b.classList.add('hit'); $('moStatus').innerHTML = `Found <span class="mono">${a}</span> here → ${NOTE[a]}.`; return; }
          b.classList.add('miss');
        }
        $('moStatus').innerHTML = `<b class="bad-text mono">AttributeError: 'VIPPatient' object has no attribute '${a}'</b>`;
      } catch (e) { if (!(e instanceof K.Stop)) throw e; }
    }
    $('moBtns').querySelectorAll('button').forEach(b => b.addEventListener('click', () => go(b.dataset.a)));'''}
 ],
 "style": '''  .mo-row { display: flex; flex-wrap: wrap; align-items: stretch; gap: 8px; margin-top: 12px; }
  .mo-box { flex: 1 1 150px; border: 2px solid var(--line); border-radius: 12px; padding: 10px 12px; background: var(--panel-2); transition: all .3s; }
  .mo-h { font-size: 13px; color: var(--fg-soft); margin-bottom: 4px; }
  .mo-h .mono { color: var(--accent-text); font-weight: 700; }
  .mo-a { font-size: 13px; color: var(--muted); }
  .mo-arr { align-self: center; color: var(--muted); font-size: 20px; }
  .mo-box.look { border-color: var(--cyan); box-shadow: 0 0 0 3px var(--teal-wash); }
  .mo-box.hit { border-color: var(--teal); background: var(--teal-wash); }
  .mo-box.miss { opacity: .5; }''',
 "cheat": [
  ["Data + behaviour that belong together", "A class (or <span class=\"mono\">@dataclass</span> for mostly-data)"],
  ["Per-object values", "Set on <span class=\"mono\">self</span> in <span class=\"mono\">__init__</span>"],
  ["Value shared by all instances", "Class attribute, but never a mutable one like []"],
  ["Reuse and extend a class", "<span class=\"mono\">class Child(Parent):</span> + <span class=\"mono\">super().__init__(...)</span>"],
  ["Change one method in a subclass", "Override it; call <span class=\"mono\">super().method()</span> to keep the parent's part"],
  ["Is it this kind of thing?", "<span class=\"mono\">isinstance(obj, Cls)</span> (works with subclasses)"],
  ["Something went wrong in a method", "<span class=\"mono\">raise</span>, don't just print"]
 ],
 "ref_title": "Reference: vocabulary",
 "ref_html": '''    <div class="scroll card table-card">
      <table>
        <thead><tr><th>Term</th><th>Meaning</th><th>Example</th></tr></thead>
        <tbody>
          <tr><td>class</td><td>blueprint; itself an object</td><td class="mono">class Patient:</td></tr>
          <tr><td>instance</td><td>one object made from the class</td><td class="mono">asha = Patient("Asha", 35)</td></tr>
          <tr><td>instance attribute</td><td>stored on one object</td><td class="mono">self.name</td></tr>
          <tr><td>class attribute</td><td>stored on the class, shared</td><td class="mono">clinic = "Pune"</td></tr>
          <tr><td>method</td><td>function in the class; first parameter is self</td><td class="mono">def book(self, slot):</td></tr>
          <tr><td>constructor</td><td><span class="mono">__init__</span> initialises a new instance</td><td class="mono">def __init__(self, name):</td></tr>
          <tr><td>inheritance</td><td>subclass gets the parent's attributes</td><td class="mono">class VIPPatient(Patient):</td></tr>
          <tr><td>MRO</td><td>method resolution order: lookup path</td><td class="mono">VIPPatient.__mro__</td></tr>
        </tbody>
      </table>
    </div>''',
 "notes": [
  ["Corrected", "<b>BankAccount.withdraw</b> in class_objects_practise.py prints \"Insufficient funds.\" and carries on, so the caller can't tell it failed. Raise an exception instead (see the Your turn starter). Money is also stored as float; real systems use <span class=\"mono\">decimal.Decimal</span> or integer paise/cents."],
  ["Added", "<b>Attribute names:</b> <span class=\"mono\">self.car_make</span>, <span class=\"mono\">self.account_balance</span>, <span class=\"mono\">self.employee_name</span> repeat the class name. Inside a Car, <span class=\"mono\">self.make</span> is clear enough, and callers write <span class=\"mono\">car.make</span>."],
  ["Added", "<b>display_car_info / show_balance</b> print directly. Defining <span class=\"mono\">__str__</span> or <span class=\"mono\">__repr__</span> lets <span class=\"mono\">print(car)</span> and f-strings work, and keeps formatting separate from logic (OOP deeper page)."],
  ["Added", "<b>main() runs on import.</b> The file ends with a bare <span class=\"mono\">main()</span>. Use <span class=\"mono\">if __name__ == \"__main__\": main()</span> so importing the classes from another file doesn't run the demo (Modules page)."]
 ],
 "quiz": [
  {"q": "<span class=\"mono\">class A:\\n    x = 1\\na = A(); A.x = 2\\nprint(a.x)</span>", "code": "class A:\n    x = 1\na = A(); A.x = 2\nprint(a.x)", "expect": "2", "a": "<b class=\"mono\">2</b>. a has no own x, so it reads the class attribute's current value."},
  {"q": "<span class=\"mono\">class A: pass\\nclass B(A): pass\\nprint(isinstance(B(), A), issubclass(A, B))</span>", "code": "class A: pass\nclass B(A): pass\nprint(isinstance(B(), A), issubclass(A, B))", "expect": "True False", "a": "<b class=\"mono\">True False</b>. Inheritance goes one way."},
  {"q": "<span class=\"mono\">class P:\\n    def hi(self): return \"P\"\\nclass C(P):\\n    def hi(self): return \"C\" + super().hi()\\nprint(C().hi())</span>", "code": "class P:\n    def hi(self): return \"P\"\nclass C(P):\n    def hi(self): return \"C\" + super().hi()\nprint(C().hi())", "expect": "CP", "a": "<b class=\"mono\">CP</b>. The override runs, then super() runs the parent's."},
  {"q": "<span class=\"mono\">class A:\\n    def __init__(self, v): self.v = v\\nprint(A(3).v + A(4).v)</span>", "code": "class A:\n    def __init__(self, v): self.v = v\nprint(A(3).v + A(4).v)", "expect": "7", "a": "<b class=\"mono\">7</b>. Two independent instances, each with its own v."},
  {"q": "<span class=\"mono\">class A: pass\\nprint([c.__name__ for c in A.__mro__])</span>", "code": "class A: pass\nprint([c.__name__ for c in A.__mro__])", "expect": "['A', 'object']", "a": "<b class=\"mono\">['A', 'object']</b>. Every class ultimately inherits from object."},
  {"q": "<span class=\"mono\">class A:\\n    def f(self): return self\\na = A(); print(a.f() is a)</span>", "code": "class A:\n    def f(self): return self\na = A(); print(a.f() is a)", "expect": "True", "a": "<b class=\"mono\">True</b>. self is the very object the method was called on."}
 ],
 "sources": "Sources: Python_Fundamentals repo (classes_and_objects/class_objects_practise.py)."
}
