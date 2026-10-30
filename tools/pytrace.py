"""pytrace.py: run a short Python snippet and record every step for the explainer
code stepper (Kit.trace). Python Tutor-style: frames, heap objects, references, output.

Usage:
    python3 tools/pytrace.py python-fundamentals/snippets/<page>.json
Writes python-fundamentals/traces/<page>.js defining window.TRACES[<page>] = {snippetId: trace}.

Snippet file format (JSON):
    { "page": "variables-objects", "snippets": {
        "intro": { "code": "x = 1\\nprint(x)", "inputs": ["42"], "inline": false } } }
  inline=true shows int/float/str/bool/None inside frames instead of as heap objects.

Trace format: {"code": str, "python": "3.13.x", "steps": [step, ...]}
  step = {"line": next line to run (1-based) or null at the end,
          "ran": line just executed or null,
          "event": "line" | "call" | "return" | "exception" | "end",
          "frames": [{"name": str, "vars": [[name, value]], "ret": value?}],   # outermost first
          "heap": {"id": obj}, "out": stdout so far, "exc": message?}
  value = {"ref": id} | {"p": repr}   (p = primitive shown inline)
  obj = {"t": type, "v": repr} for scalars;
        {"t": "list"|"tuple"|"set", "items": [value]}; {"t": "dict", "items": [[value, value]]};
        {"t": "function", "v": name}; {"t": "class", "v": name, "attrs": [[name, value]]};
        {"t": "instance", "cls": name, "attrs": [[name, value]]}
"""
import builtins, dis, importlib, inspect, io, json, os, re, sys, types

SCALARS = (int, float, str, bool, complex, type(None))
HIDE = {"__builtins__", "__name__", "__doc__", "__package__", "__loader__", "__spec__",
        "__annotations__", "__file__", "__cached__", "__conditional_annotations__"}


def exc_text(etype, e):
    """'ValueError: msg' like the last traceback line; just the name when there is no message."""
    msg = str(e)
    return f"{etype.__name__}: {msg}" if msg else etype.__name__


def ret_kind(frame):
    """Why a 'return' trace event fired: 'return', 'yield' or 'raise' (exception unwinding)."""
    try:
        code = frame.f_code.co_code
        op = dis.opname[code[frame.f_lasti]]
        if op == "RESUME" and frame.f_lasti >= 2:          # 3.13 reports the RESUME after YIELD_VALUE
            op = dis.opname[code[frame.f_lasti - 2]]
    except Exception:
        return "return"
    if op.startswith("RETURN"):
        return "return"
    if op.startswith("YIELD"):
        return "yield"
    return "raise"


class Recorder:
    def __init__(self, code, inputs=(), inline=False, max_steps=5000):
        self.code, self.inline, self.max_steps = code, inline, max_steps
        self.inputs = list(inputs)
        self.steps, self.ids = [], {}
        self.out = io.StringIO()
        self.last_line = None

    # ---------- encoding ----------
    def hid(self, obj):
        k = id(obj)
        if k not in self.ids:
            self.ids[k] = len(self.ids) + 1
        return str(self.ids[k])

    def val(self, obj, heap):
        if self.inline and isinstance(obj, SCALARS):
            return {"p": repr(obj)}
        h = self.hid(obj)
        if h not in heap:
            heap[h] = None  # placeholder against cycles
            heap[h] = self.encode(obj, heap)
        return {"ref": h}

    def encode(self, o, heap):
        if isinstance(o, SCALARS):
            return {"t": type(o).__name__, "v": repr(o)}
        if isinstance(o, (list, tuple)):
            return {"t": type(o).__name__, "items": [self.val(x, heap) for x in o]}
        if isinstance(o, (set, frozenset)):
            return {"t": type(o).__name__, "items": [self.val(x, heap) for x in sorted(o, key=repr)]}
        if isinstance(o, dict):
            return {"t": "dict", "items": [[self.val(k, heap), self.val(v, heap)] for k, v in o.items()]}
        if isinstance(o, types.ModuleType):
            return {"t": "module", "v": o.__name__}
        if isinstance(o, io.IOBase):
            if isinstance(o, io.StringIO):
                return {"t": "StringIO", "v": "in-memory file" + (" (closed)" if o.closed else "")}
            name, mode = getattr(o, "name", "?"), getattr(o, "mode", "?")
            return {"t": "file", "v": f"{name!r} mode={mode!r}" + (" (closed)" if o.closed else " (open)")}
        if isinstance(o, (types.FunctionType, types.BuiltinFunctionType, types.MethodType)):
            return {"t": "function", "v": getattr(o, "__qualname__", getattr(o, "__name__", "?")) + "()"}
        if isinstance(o, type):
            if o.__module__ != "__main__":          # library / built-in class: just its name
                return {"t": "class", "v": o.__name__, "attrs": []}
            attrs = [[k, self.val(v, heap)] for k, v in vars(o).items() if not k.startswith("__")]
            return {"t": "class", "v": o.__name__, "attrs": attrs}
        if isinstance(o, types.GeneratorType):
            state = inspect.getgeneratorstate(o)
            label = {"GEN_CREATED": "not started", "GEN_RUNNING": "running",
                     "GEN_CLOSED": "finished"}.get(state)
            if state == "GEN_SUSPENDED":
                label = f"paused at line {o.gi_frame.f_lineno}"
            attrs = []
            if state == "GEN_SUSPENDED":
                attrs = [[k, self.val(v, heap)] for k, v in o.gi_frame.f_locals.items() if not k.startswith(".")]
            return {"t": "generator", "v": f"{o.__name__} · {label}", "attrs": attrs}
        if hasattr(o, "__dict__") and type(o).__module__ == "__main__":
            return {"t": "instance", "cls": type(o).__name__,
                    "attrs": [[k, self.val(v, heap)] for k, v in vars(o).items()]}
        r = re.sub(r" (object )?at 0x[0-9a-fA-F]+", "", repr(o))
        return {"t": type(o).__name__, "v": r if len(r) < 60 else r[:57] + "..."}

    def snapshot(self, frame, event, arg=None):
        stack = []
        f = frame
        while f is not None:
            if f.f_code.co_filename == "<snippet>":
                stack.append(f)
            f = f.f_back
        stack.reverse()
        heap, frames = {}, []
        for i, fr in enumerate(stack):
            if fr.f_code.co_name == "<module>":
                name = "Global frame"
            elif not fr.f_code.co_flags & 1:          # not CO_OPTIMIZED: a class body
                name = "class " + getattr(fr.f_code, "co_qualname", fr.f_code.co_name) + " (body)"
            else:
                name = getattr(fr.f_code, "co_qualname", fr.f_code.co_name).replace(".<locals>", "") + "()"
            items = [(k, v) for k, v in fr.f_locals.items() if k not in HIDE and not (k.startswith("__") and k.endswith("__"))]
            entry = {"name": name, "vars": [[k, self.val(v, heap)] for k, v in items]}
            if fr is frame and event == "return" and fr.f_code.co_name != "<module>":
                kind = ret_kind(fr)
                if kind == "raise":
                    entry["raising"] = True        # leaving because an exception is propagating
                elif kind == "yield":
                    entry["yield"] = self.val(arg, heap)
                else:
                    entry["ret"] = self.val(arg, heap)
            frames.append(entry)
        return frames, heap

    # ---------- tracing ----------
    def tracer(self, frame, event, arg):
        if frame.f_code.co_filename != "<snippet>":
            return None
        if event in ("line", "call", "return", "exception"):
            frames, heap = self.snapshot(frame, event, arg)
            step = {"event": event, "line": frame.f_lineno, "ran": self.last_line,
                    "frames": frames, "heap": heap, "out": self.out.getvalue()}
            if event == "exception":
                step["exc"] = exc_text(arg[0], arg[1])
            if event == "call" and frame.f_code.co_name == "<module>":
                return self.tracer
            self.steps.append(step)
            if len(self.steps) > self.max_steps:
                raise RuntimeError(f"stopped after {self.max_steps} steps (infinite loop?)")
            if event == "line":
                self.last_line = frame.f_lineno
            if event == "return":
                self.last_line = frame.f_lineno
        return self.tracer

    def run(self):
        def fake_input(prompt=""):
            v = self.inputs.pop(0) if self.inputs else ""
            self.out.write(str(prompt) + v + "\n")
            return v
        g = {"__name__": "__main__", "__builtins__": builtins}
        old_input, old_out = builtins.input, sys.stdout
        builtins.input, sys.stdout = fake_input, self.out
        err = None
        # behave like a script in the current folder: its own modules are importable,
        # and anything it imports is forgotten afterwards so every snippet starts fresh
        before = set(sys.modules)
        old_dwb, sys.dont_write_bytecode = sys.dont_write_bytecode, True
        sys.path.insert(0, os.getcwd())
        importlib.invalidate_caches()
        try:
            compiled = compile(self.code, "<snippet>", "exec")
            sys.settrace(self.tracer)
            try:
                exec(compiled, g)
            finally:
                sys.settrace(None)
        except Exception as e:  # uncaught: shown at the end like a traceback line
            err = exc_text(type(e), e)
        finally:
            builtins.input, sys.stdout = old_input, old_out
            sys.path.remove(os.getcwd())
            sys.dont_write_bytecode = old_dwb
            for name in set(sys.modules) - before:
                mod = sys.modules.get(name)
                if getattr(mod, "__file__", None) and os.path.dirname(os.path.abspath(mod.__file__)) == os.getcwd():
                    del sys.modules[name]
        # collapse: keep line + return + exception events; drop the module "return"
        steps = [s for s in self.steps if not (s["event"] == "return" and s["frames"] and s["frames"][-1]["name"] == "Global frame")]
        # final state
        heap = {}
        frames = [{"name": "Global frame", "vars": [[k, self.val(v, heap)] for k, v in g.items()
                                                    if k not in HIDE and not (k.startswith("__") and k.endswith("__"))]}]
        end = {"event": "end", "line": None, "ran": self.last_line, "frames": frames, "heap": heap,
               "out": self.out.getvalue() + (f"Traceback (most recent call last):\n  ...\n{err}\n" if err else "")}
        if err:
            end["exc"] = err
        steps.append(end)
        # 'ran' for each step = previous step's line
        for i in range(len(steps) - 1):
            steps[i]["ran"] = steps[i - 1]["line"] if i > 0 else None
        return {"code": self.code, "python": sys.version.split()[0], "steps": steps}


def main(path):
    spec = json.load(open(path))
    out = {}
    for sid, s in spec["snippets"].items():
        out[sid] = Recorder(s["code"], s.get("inputs", []), s.get("inline", False)).run()
    root = os.path.dirname(os.path.dirname(os.path.abspath(path)))
    dst = os.path.join(root, "traces", spec["page"] + ".js")
    with open(dst, "w") as f:
        f.write("/* generated by tools/pytrace.py from snippets/%s.json - do not edit */\n" % spec["page"])
        f.write("window.TRACES = window.TRACES || {};\nwindow.TRACES[%s] = %s;\n" % (json.dumps(spec["page"]), json.dumps(out, separators=(",", ":"))))
    print("wrote", dst, {k: len(v["steps"]) for k, v in out.items()})


if __name__ == "__main__":
    main(sys.argv[1])
