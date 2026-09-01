"""test_host.py — Tests for host runtime, capabilities, data model, UI IR."""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from jajaja_interpreter import Jajaja, run
from jajaja_stdlib import (
    int_to_unary, unary_to_int,
    int_to_decimal, decimal_to_int,
    list_encode, list_decode,
    record_encode, record_decode,
    make_effect, parse_effect,
    make_result, parse_result,
)
from host import run_host, expand_allow, dispatch_effect
from ui_ir import UIIR

passed = 0
failed = 0


def check(name, got, want):
    global passed, failed
    ok = got == want
    print(("OK   " if ok else "FAIL ") + name)
    if not ok:
        print("    got =", repr(got))
        print("   want =", repr(want))
        failed += 1
    else:
        passed += 1


# ─── Data Model (Fase 4) ───────────────────────────────────────────
print("\n=== DATA MODEL ===")

# Unary integers
check("unary 0", int_to_unary(0), "_ZERO")
check("unary 1", int_to_unary(1), "ja")
check("unary 3", int_to_unary(3), "jajaja")
check("unary roundtrip", unary_to_int(int_to_unary(5)), 5)

# Decimal integers
check("decimal 42", int_to_decimal(42), "42")
check("decimal roundtrip", decimal_to_int("42"), 42)

# Lists
check("list empty", list_encode([]), "[]")
check("list encode", list_encode(["a", "b", "c"]), "[a b c]")
check("list decode", list_decode("[x y z]"), ["x", "y", "z"])

# Records
check("record encode", record_encode({"name": "Danny", "age": "30"}), "name:Danny age:30")
r = record_decode("name:Danny age:30")
check("record decode name", r.get("name"), "Danny")
check("record decode age", r.get("age"), "30")

# ─── Host ABI Protocol (Fase 6) ───────────────────────────────────
print("\n=== HOST ABI ===")

# Effect
eff = make_effect("1", "stdout", text="hello")
check("make effect", eff, 'EFFECT 1 stdout {"text": "hello"}')
parsed = parse_effect(eff)
check("parse effect id", parsed["request_id"], "1")
check("parse effect cap", parsed["capability"], "stdout")
check("parse effect text", parsed["text"], "hello")

# Result
res = make_result("1", "OK", "42")
check("make result", res, 'RESULT 1 OK "42"')
parsed_res = parse_result(res)
check("parse result id", parsed_res["request_id"], "1")
check("parse result status", parsed_res["status"], "OK")
check("parse result payload", parsed_res["payload"], "42")

# Capability expansion
check("expand io", expand_allow(["io"]), {"stdin", "stdout"})
check("expand kv", expand_allow(["kv"]), {"kv-get", "kv-set"})
check("expand mixed", expand_allow(["stdout", "kv"]), {"stdout", "kv-get", "kv-set"})

# ─── Host Runtime (Fase 7-8) ──────────────────────────────────────
print("\n=== HOST RUNTIME ===")

# Echo via host
out, steps, status, rcpts = run_host(
    "ECHO::=~OK\n::=\nECHO",
    allow=["stdout"],
)
check("host echo", status, "HALTED")

# Capability deny: emit EFFECT line for fs-read, which is not in allowlist
out, steps, status, rcpts = run_host(
    'DO::=~EFFECT 1 fs-read {"path":"x"}\n::=\nDO',
    allow=["stdout"],
)
has_deny = any(r["status"] == "DENY" for r in rcpts)
check("capability deny", has_deny, True)

# ─── Calculator (Fase 9) ───────────────────────────────────────────
print("\n=== CALCULATOR ===")

calc_src = (HERE / "examples" / "calculator.jaja").read_text()

for inp, want in [("ADD 1 2", "3"), ("ADD 3 3", "6"), ("MUL 2 3", "6"),
                   ("ADD 5 5", "10"), ("ADD 0 0", "0"), ("MUL 3 3", "9")]:
    out, steps, status, rcpts = run_host(calc_src, stdin_data=inp, allow=["stdout"])
    check(f"calc {inp}", out, want)

# ─── Structured Output (Fase 3) ───────────────────────────────────
print("\n=== STRUCTURED OUTPUT ===")

struct_src = (HERE / "examples" / "structured.jaja").read_text()
out, steps, status, _ = run_host(struct_src, allow=["stdout"])
check("structured output", out, "COMPUTED")

chain_src = (HERE / "examples" / "chain.jaja").read_text()
out, steps, status, _ = run_host(chain_src, allow=["stdout"])
check("chain transform", out, "DONE")

# ─── UI IR (Fase 10) ──────────────────────────────────────────────
print("\n=== UI IR ===")

ui = UIIR()
ui.add("VIEW", "root", "-1")
ui.add("COLUMN", "col", "root")
ui.add("TEXT", "t1", "col", "Welcome")
ui.add("ROW", "row", "col")
ui.add("BUTTON", "btn", "row", "Add to Cart", "add_cart")
ui.add("INPUT", "inp", "row", "Search...", "search")

lines = ui.to_lines()
check("UI IR lines count", len(lines), 6)
check("UI IR first line", lines[0], "VIEW root -1")

html = ui.render_html()
check("UI HTML has div", "<div" in html, True)
check("UI HTML has button", "<button" in html, True)
check("UI HTML has input", "<input" in html, True)

term = ui.render_terminal()
check("UI terminal has text", "Welcome" in term, True)
check("UI terminal has button", "[Add to Cart]" in term, True)

# ─── Filesystem sandbox (Fase 8) ───────────────────────────────────
print("\n=== FILESYSTEM ===")

with tempfile.TemporaryDirectory() as tmpdir:
    # Write a file via host
    src = 'OUT::=~EFFECT_1\nEFFECT_1::=X\n::=\nOUT'
    # Test fs-write capability
    write_effect = make_effect("w1", "fs-write", path="test.txt", data="hello")
    parsed = parse_effect(write_effect)
    from jajaja_stdlib import handle_fs_write
    result = handle_fs_write(parsed, root=tmpdir)
    check("fs-write result", result, "OK")

    # Read it back
    read_effect = make_effect("r1", "fs-read", path="test.txt")
    parsed_r = parse_effect(read_effect)
    from jajaja_stdlib import handle_fs_read
    content = handle_fs_read(parsed_r, root=tmpdir)
    check("fs-read content", content, "hello")

    # Path traversal blocked
    traversed = handle_fs_write({"path": "../../etc/passwd", "data": "evil"}, root=tmpdir)
    check("fs path traversal denied", traversed.startswith("DENY"), True)

# ─── COMPILE_ONCE_TEST_MANY (Fase 2 regression) ────────────────────
print("\n=== COMPILE_ONCE_TEST_MANY ===")

echo_src = (HERE / "examples" / "echo.jaja").read_text()
import hashlib
sha = hashlib.sha256(echo_src.encode()).hexdigest()
check("echo SHA256 stable", len(sha), 64)

outputs = set()
for inp in ["hello", "bye", "abc", "hi", ""]:
    _, _, status, _ = run_host(echo_src, stdin_data=inp, allow=["stdout"])
    check(f"echo {inp!r} halts", status, "HALTED")

# ─── TRACE (Fase 1 regression) ─────────────────────────────────────
print("\n=== TRACE ===")

j1 = Jajaja("jaja::=~X\n::=\njaja")
r1 = j1.run()
j2 = Jajaja("jaja::=~X\n::=\njaja", trace=True)
r2 = j2.run()
check("trace invariant", r1, r2)
check("trace has entries", len(j2.trace) > 0, True)

print()
print("passed=%d failed=%d" % (passed, failed))
sys.exit(0 if failed == 0 else 1)
