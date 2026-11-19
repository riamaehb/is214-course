"""IS 214 self-test for PE4, PE5 and the final interpreter.

Put this file in the folder that holds your language.json, lexer.py, parser.py,
evaluator.py and interpreter.py, then run one of:

    python selftest.py pe4      # tokenize() and parse()
    python selftest.py pe5      # evaluate()
    python selftest.py final    # run()

Programs and expected answers are generated from YOUR language.json. The grader uses
the same kind of tests with different programs, plus invalid programs for the parser
that are not shown here. Writing your own invalid programs is part of PE4.
"""
"""Generate tests for one language.json (an 'IS 214 calculator language' spec).

Each test is a dict:
  id, group, kind ('tokenize' | 'parse' | 'evaluate' | 'run'), input, expect
  expect is {"value": ...} or {"exc": [ExceptionName, message]}
Tokens and ASTs are plain lists so they can be stored as JSON.
Expected values come from an independent oracle in this file, not from the
reference lexer, parser or evaluator.
"""
import random

OPS = ("ADD", "SUB", "MUL", "DIV")
LEX_ERR = ["ValueError", "Invalid token"]
SYN_ERR = ["SyntaxError", "Invalid syntax"]
DIV_ERR = ["ZeroDivisionError", "Division by zero"]


# ---------------------------------------------------------------- oracle
def oracle_eval(node):
    if node[0] == "INTEGER":
        return node[1]
    a, b = oracle_eval(node[1]), oracle_eval(node[2])
    if node[0] == "ADD":
        return a + b
    if node[0] == "SUB":
        return a - b
    if node[0] == "MUL":
        return a * b
    if b == 0:
        raise ZeroDivisionError
    q = abs(a) // abs(b)
    return q if (a < 0) == (b < 0) else -q


def lst(x):
    if isinstance(x, (tuple, list)):
        return [lst(i) for i in x]
    return x


# ---------------------------------------------------------------- rendering
class Renderer:
    def __init__(self, spec, rng):
        self.spec, self.rng = spec, rng
        self.fn = spec["notation"] == "function"
        self.semi = spec["statement_terminator"] == "semicolon"
        self.cs = spec["case_sensitive"]
        self.bounded = bool(spec["program_boundaries"].get("enabled"))

    def word(self, text):
        if self.cs:
            return text
        return self.rng.choice([text, text.upper(), text.lower(), text.swapcase()])

    def kw(self, name):
        return self.word(self.spec["keywords"][name])

    def expr(self, node, loose=False):
        """-> (text, tokens)"""
        sp = (lambda: self.rng.choice(["", " ", "  ", "\t"])) if loose else (lambda: "")
        if node[0] == "INTEGER":
            lex = ("00" + str(node[1])) if getattr(self, "zeros", False) else str(node[1])
            return lex, [("INTEGER_LITERAL", lex)]
        op = {"ADD": "add", "SUB": "sub", "MUL": "mul", "DIV": "div"}[node[0]]
        w = self.kw(op)
        lt, ltok = self.expr(node[1], loose)
        rt, rtok = self.expr(node[2], loose)
        if self.fn:
            text = f"{w}{sp()}({sp()}{lt}{sp()},{sp() or ' '}{rt}{sp()})"
            toks = [(node[0], w), ("LEFT_PAREN", "(")] + ltok + [("COMMA", ",")] + rtok + [("RIGHT_PAREN", ")")]
        else:
            text = f"({sp()}{w} {lt} {rt}{sp()})"
            toks = [("LEFT_PAREN", "(")] + [(node[0], w)] + ltok + rtok + [("RIGHT_PAREN", ")")]
        return text, toks

    def statement(self, node, loose=False):
        w = self.kw("print")
        et, etok = self.expr(node, loose)
        text = f"{w} {et}" + (";" if self.semi else "")
        toks = [("PRINT", w)] + etok + ([("SEMICOLON", ";")] if self.semi else [])
        if loose and self.rng.random() < 0.5:
            text = "  " + text + " "
        return text, toks

    def program(self, nodes, loose=False, blank=False, crlf=False, trailing=True):
        items = []  # list of (text|None, tokens)
        if self.bounded:
            b = self.spec["program_boundaries"]
            items.append((self.word(b["start"]), [("START", None)]))
        for n in nodes:
            if blank and self.rng.random() < 0.5:
                items.append(("", []))
            items.append(self.statement(n, loose))
        if self.bounded:
            if blank:
                items.append(("", []))
            items.append((self.word(b["end"]), [("END", None)]))
        eol = "\r\n" if crlf else "\n"
        lines, toks = [], []
        for idx, (text, tk) in enumerate(items):
            lines.append(text)
            if tk:
                if tk[0][1] is None:  # boundary keyword: lexeme is the text itself
                    tk = [(tk[0][0], text)]
                toks.extend(tk)
            has_break = idx < len(items) - 1 or trailing
            if has_break and toks and toks[-1][0] != "NEWLINE":
                toks.append(("NEWLINE", "\n"))
        src = eol.join(lines) + (eol if trailing else "")
        return src, toks


# ---------------------------------------------------------------- random trees
def rand_tree(rng, depth, allow_div=True):
    if depth == 0 or rng.random() < 0.25:
        return ("INTEGER", rng.choice([0, 1, 2, 3, 5, 7, 9, 10, 12, 42, 100]))
    for _ in range(20):
        op = rng.choice(OPS if allow_div else OPS[:3])
        node = (op, rand_tree(rng, depth - 1, allow_div), rand_tree(rng, depth - 1, allow_div))
        try:
            oracle_eval(node)
            return node
        except ZeroDivisionError:
            continue
    return ("INTEGER", 1)


def I(n):
    return ("INTEGER", n)


def tree_ast(nodes):
    return ["PROGRAM", [["PRINT", lst(n)] for n in nodes]]


# ---------------------------------------------------------------- builder
def build_tests(spec, seed=214, student=False):
    """student=True leaves out the invalid-program tests for the parser (students write their own)."""
    rng = random.Random(seed)
    R = Renderer(spec, rng)
    tests = []

    def add(group, kind, inp, expect, name):
        tests.append({"id": f"{group}-{len(tests) + 1:03d}", "group": group, "kind": kind,
                      "input": inp, "expect": expect, "name": name})

    def valid(name, nodes, **fmt):
        src, toks = R.program(nodes, **fmt)
        ast = tree_ast(nodes)
        res = [oracle_eval(n) for n in nodes]
        add("lexer", "tokenize", src, {"value": lst(toks)}, name)
        add("parser", "parse", lst(toks), {"value": ast}, name)
        add("evaluator", "evaluate", ast, {"value": res}, name)
        add("run", "run", src, {"value": res}, name)

    # ---- valid programs
    valid("single literal", [I(5)])
    valid("zero", [I(0), I(7)])
    R.zeros = True
    valid("leading zeros", [I(7), ("ADD", I(0), I(12))])
    R.zeros = False
    valid("sum of two", [("ADD", I(2), I(3))])
    valid("plan example", [("ADD", I(2), I(3)), ("MUL", ("ADD", I(2), I(3)), I(4))])
    valid("all four operations", [("ADD", I(6), I(3)), ("SUB", I(6), I(3)), ("MUL", I(6), I(3)), ("DIV", I(6), I(3))])
    valid("negative intermediate", [("SUB", I(2), I(5)), ("ADD", ("SUB", I(0), I(4)), I(1))])
    valid("division truncates toward zero",
          [("DIV", ("SUB", I(0), I(3)), I(2)), ("DIV", I(7), ("SUB", I(0), I(2))),
           ("DIV", ("SUB", I(0), I(7)), ("SUB", I(0), I(2))), ("DIV", I(7), I(2))])
    valid("deep nesting", [("ADD", ("MUL", ("SUB", I(9), I(4)), ("DIV", I(20), I(5))), ("ADD", I(1), ("MUL", I(2), I(3))))])
    for k in range(4):
        valid(f"random program {k + 1}", [rand_tree(rng, rng.choice([2, 3, 4])) for _ in range(rng.choice([1, 2, 3, 4]))])
    valid("extra spaces and tabs", [("ADD", I(2), ("MUL", I(3), I(4))), I(8)], loose=True)
    valid("blank lines", [I(1), ("ADD", I(2), I(2)), I(3)], blank=True)
    valid("windows line endings", [I(1), ("ADD", I(2), I(2))], crlf=True)
    valid("no trailing newline", [I(1), ("ADD", I(2), I(2))], trailing=False)
    valid("many statements", [rand_tree(rng, 2) for _ in range(6)], blank=True, loose=True)

    big = 10 ** 12
    valid("large values", [("MUL", I(big), I(big)), ("DIV", I(big * big), I(7))])

    # ---- lexer errors (ValueError)
    kw = spec["keywords"]
    P, A = kw["print"], kw["add"]

    def stmt_text(body):
        return f"{P} {body}" + (";" if R.semi else "")

    taken = {w.casefold() for w in kw.values()}
    if R.bounded:
        taken |= {spec["program_boundaries"]["start"].casefold(), spec["program_boundaries"]["end"].casefold()}

    def fresh(base):
        """A word that is not any of this language's keywords, whatever the student chose."""
        w = base
        while w.casefold() in taken:
            w += "Z"
        return w

    lex_bad = {
        "invalid character @": stmt_text("5 @ 2"),
        "invalid character $": stmt_text("$"),
        "decimal point": stmt_text("3.5"),
        "unknown word": stmt_text(fresh("FOO")),
        "non-ASCII letter": stmt_text("ñ"),
        "word starting with underscore": stmt_text("_x"),
    }
    if R.fn:
        lex_bad["unknown function word"] = stmt_text(fresh("NOPE") + "(1, 2)")
    if spec["notation"] == "prefix":
        lex_bad["comma is not in prefix notation"] = stmt_text(f"({A} 1, 2)")
    if not R.semi:
        lex_bad["semicolon without semicolon mode"] = f"{P} 5;"
    if R.cs:
        lex_bad["wrong keyword case"] = stmt_text("5").replace(P, P.swapcase() if P.swapcase() != P else fresh(P + "x"), 1)
    if not R.bounded:
        lex_bad["boundary-like word when boundaries are off"] = fresh("BEGIN_X") + "\n" + stmt_text("5")
    lex_bad["longer word starting with a keyword"] = stmt_text("5").replace(P, fresh(P + "x"), 1)
    for name, src in lex_bad.items():
        add("lexer-error", "tokenize", src, {"exc": LEX_ERR}, name)
        add("run-error", "run", src, {"exc": LEX_ERR}, name)

    # ---- parser errors (SyntaxError); inputs are valid-lexing sources
    def lexes(src):
        raise RuntimeError("instructor only")

    w = {"add": kw["add"], "mul": kw["mul"]}
    pb = {}
    if R.fn:
        a, m = kw["add"], kw["mul"]
        pb["missing second operand"] = stmt_text(f"{a}(2,)")
        pb["missing first operand"] = stmt_text(f"{a}(, 2)")
        pb["three operands"] = stmt_text(f"{a}(1, 2, 3)")
        pb["one operand"] = stmt_text(f"{a}(1)")
        pb["empty argument list"] = stmt_text(f"{a}()")
        pb["missing closing parenthesis"] = stmt_text(f"{a}(1, 2")
        pb["missing opening parenthesis"] = stmt_text(f"{a} 1, 2)")
        pb["extra closing parenthesis"] = stmt_text(f"{a}(1, 2))")
        pb["operator used as a value"] = stmt_text(f"{a}({m}, 2)")
        pb["missing comma"] = stmt_text(f"{a}(1 2)")
        pb["nested missing operand"] = stmt_text(f"{a}({m}(2,), 3)")
        pb["bare operator"] = stmt_text(f"{a}")
    else:
        a, m = kw["add"], kw["mul"]
        pb["missing second operand"] = stmt_text(f"({a} 2)")
        pb["three operands"] = stmt_text(f"({a} 1 2 3)")
        pb["empty parentheses"] = stmt_text("()")
        pb["missing closing parenthesis"] = stmt_text(f"({a} 1 2")
        pb["extra closing parenthesis"] = stmt_text(f"({a} 1 2))")
        pb["missing operator"] = stmt_text("(1 2)")
        pb["operator outside parentheses"] = stmt_text(f"{a} 1 2")
        pb["operator used as a value"] = stmt_text(f"({a} {m} 2)")
        pb["nested missing operand"] = stmt_text(f"({a} ({m} 2) 3)")
        pb["bare parentheses around a number"] = stmt_text("(5)")
    pb["missing expression after output keyword"] = stmt_text("")
    pb["output keyword only"] = P
    pb["operand after complete expression"] = stmt_text("5 6")
    if R.semi:
        pb["missing semicolon"] = f"{P} 5"
        pb["missing semicolon, two lines"] = f"{P} 5\n{P} 6;"
        pb["two statements on one line"] = f"{P} 1; {P} 2;"
        pb["double semicolon"] = f"{P} 5;;"
    else:
        pb["two statements on one line"] = f"{P} 1 {P} 2"
    pb["stray token on a later line"] = stmt_text("1") + "\n)"
    pb["expression on a later line without an output keyword"] = stmt_text("1") + "\n7"
    pb["expression split across lines"] = stmt_text("5").replace(" ", "\n", 1)
    pb["empty program"] = ""
    pb["only blank lines"] = "\n\n"
    pb["output keyword missing, bare expression"] = "5" + (";" if R.semi else "")
    if R.bounded:
        b = spec["program_boundaries"]
        S, E = b["start"], b["end"]
        pb["missing start keyword"] = f"{stmt_text('1')}\n{E}"
        pb["missing end keyword"] = f"{S}\n{stmt_text('1')}"
        pb["start and end on one line"] = f"{S} {stmt_text('1')} {E}"
        pb["nothing between start and end"] = f"{S}\n{E}"
        pb["statement after end"] = f"{S}\n{stmt_text('1')}\n{E}\n{stmt_text('2')}"
        pb["start keyword twice"] = f"{S}\n{S}\n{stmt_text('1')}\n{E}"
        pb["end before start"] = f"{E}\n{stmt_text('1')}\n{S}"
    for name, src in ([] if student else pb.items()):
        toks = lexes(src)
        add("parser-error", "parse", toks, {"exc": SYN_ERR}, name)
        add("run-error", "run", src, {"exc": SYN_ERR}, name)

    # ---- evaluation errors (ZeroDivisionError)
    zero = [
        ("division by zero literal", [("DIV", I(1), I(0))]),
        ("division by a zero expression", [("DIV", I(4), ("SUB", I(2), I(2)))]),
        ("zero divided by zero", [("DIV", I(0), I(0))]),
        ("zero buried in a nested expression", [("ADD", I(1), ("MUL", I(2), ("DIV", I(5), I(0))))]),
        ("second statement fails", [I(1), ("DIV", I(1), I(0))]),
    ]
    for name, nodes in zero:
        src, _ = R.program(nodes)
        add("evaluator-error", "evaluate", tree_ast(nodes), {"exc": DIV_ERR}, name)
        add("run-error", "run", src, {"exc": DIV_ERR}, name)

    # ---- evaluator-only checks on hand-written ASTs
    for name, nodes in [("literal only", [I(9)]), ("operation order for subtraction", [("SUB", I(10), I(4))]),
                        ("operation order for division", [("DIV", I(20), I(4))]),
                        ("evaluation of a long chain", [("ADD", ("ADD", ("ADD", I(1), I(2)), I(3)), I(4))])]:
        add("evaluator", "evaluate", tree_ast(nodes), {"value": [oracle_eval(n) for n in nodes]}, name)
    return tests


# ------------------------------------------------------------------ runner
import sys, os, json, signal, importlib, io as _io

STAGES = {"pe4": {"tokenize", "parse"}, "pe5": {"evaluate"}, "final": {"run"}}
DEFAULT_SPEC = {"schema_version": "1.0", "language_name": "Calcora", "notation": "function",
                "keywords": {"print": "SHOW", "add": "SUM", "sub": "DIFF", "mul": "PRODUCT", "div": "QUOTIENT"},
                "statement_terminator": "newline", "case_sensitive": True,
                "program_boundaries": {"enabled": False}, "design_reflection": ""}


def to_ast(x):
    kind = x[0]
    if kind == "PROGRAM":
        return ("PROGRAM", [to_ast(s) for s in x[1]])
    if kind == "PRINT":
        return ("PRINT", to_ast(x[1]))
    if kind == "INTEGER":
        return ("INTEGER", x[1])
    return (kind, to_ast(x[1]), to_ast(x[2]))


class _Timeout(Exception):
    pass


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in STAGES:
        print(__doc__)
        return 2
    stage = sys.argv[1]
    folder = sys.argv[2] if len(sys.argv) > 2 else os.getcwd()
    sys.path.insert(0, folder)
    spec_path = os.path.join(folder, "language.json")
    if os.path.exists(spec_path):
        spec = json.load(open(spec_path))
    elif stage == "pe5":
        spec = DEFAULT_SPEC
    else:
        print("language.json not found in", folder)
        return 2
    wanted = {"tokenize": ("lexer", "tokenize"), "parse": ("parser", "parse"),
              "evaluate": ("evaluator", "evaluate"), "run": ("interpreter", "run")}
    funcs = {}
    for kind in STAGES[stage]:
        mod, name = wanted[kind]
        try:
            funcs[kind] = getattr(importlib.import_module(mod), name)
        except BaseException as e:
            print(f"Could not load {mod}.{name}: {type(e).__name__}: {e}")
            return 1
    tests = [t for t in build_tests(spec, seed=7, student=True) if t["kind"] in STAGES[stage]]
    if hasattr(signal, "SIGALRM"):
        signal.signal(signal.SIGALRM, lambda s, f: (_ for _ in ()).throw(_Timeout()))
    summary, failures = {}, []
    for t in tests:
        fn, inp, kind = funcs[t["kind"]], t["input"], t["kind"]
        out = _io.StringIO()
        real, sys.stdout = sys.stdout, out
        if hasattr(signal, "SIGALRM"):
            signal.alarm(2)
        try:
            if kind == "tokenize":
                got = {"value": lst(fn(inp, spec))}
            elif kind == "parse":
                got = {"value": lst(fn([tuple(x) for x in inp], spec))}
            elif kind == "evaluate":
                got = {"value": lst(fn(to_ast(inp)))}
            else:
                got = {"value": lst(fn(inp, spec))}
        except _Timeout:
            got = {"exc": ["Timeout", "took longer than 2 seconds"]}
        except BaseException as e:
            got = {"exc": [type(e).__name__, str(e)], "mro": [c.__name__ for c in type(e).__mro__]}
        finally:
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
            sys.stdout = real
        exp = t["expect"]
        if "value" in exp:
            ok = "exc" not in got and got["value"] == exp["value"]
        else:
            ok = "exc" in got and exp["exc"][0] in got.get("mro", [got["exc"][0]]) and got["exc"][1] == exp["exc"][1]
        s = summary.setdefault(t["group"], [0, 0])
        s[1] += 1
        s[0] += ok
        if not ok:
            failures.append((t, got))
    print(f"Language: {spec['language_name']}  ({spec['notation']}, {spec['statement_terminator']}, "
          f"{'case-sensitive' if spec['case_sensitive'] else 'case-insensitive'}, "
          f"boundaries {'on' if spec['program_boundaries'].get('enabled') else 'off'})\n")
    for g, (p, n) in summary.items():
        print(f"  {g:16} {p}/{n}")
    total = sum(n for _, n in summary.values())
    passed = sum(p for p, _ in summary.values())
    print(f"\n{passed} of {total} tests passed.")
    for t, got in failures[:5]:
        print(f"\nFAILED {t['id']}: {t['name']}")
        print("  input:   ", repr(t["input"])[:300])
        print("  expected:", json.dumps(t["expect"])[:300])
        print("  got:     ", json.dumps({k: v for k, v in got.items() if k != 'mro'})[:300])
    if len(failures) > 5:
        print(f"\n...and {len(failures) - 5} more failures.")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
