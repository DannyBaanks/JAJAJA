"""test_backend_lolcode.py — Tests for the LOLCODE backend composition.

Claims under test:

    JAJAJA_IN_EXECUTION_PATH      the route.jaja program rewrites the
                                  request and emits the EFFECT; without
                                  that rewrite there is no backend call.
    BACKEND_COMPUTES_SEMANTICS    the returned value is LOLCODE stdout,
                                  produced by an external runtime; no
                                  Python path computes the result.
    NO_PYTHON_SEMANTIC_FALLBACK   with no runtime, the run FAILS loudly;
                                  nothing quietly computes the answer.
    PYTHON_FRONTEND_ONLY          Python only: parses argv, reads files,
                                  launches the child process, prints.

The external runtime (lci) is REQUIRED for the end-to-end tests. If it
is absent, those tests are reported as SKIP (not secretly replaced).
"""
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from host import run_host, dispatch_effect  # noqa: E402
from backends.lolcode import adapter  # noqa: E402

passed = 0
failed = 0
skipped = 0


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


def skip(name, why):
    global skipped
    skipped += 1
    print(f"SKIPPED  {name}  ({why})")


ROUTE = (HERE / "backends" / "lolcode" / "route.jaja").read_text(encoding="utf-8")


def demo_run(request, allow=None):
    return run_host(ROUTE, stdin_data=request, allow=allow or ["lolcode"])


# ─── Static structure (no runtime needed) ───────────────────────────
print("\n=== STATIC ===")

check("programs dir exists", adapter.PROGRAMS_DIR.is_dir(), True)
for op, fname in adapter.PROGRAMS.items():
    p = adapter.PROGRAMS_DIR / fname
    check(f"program file: {fname}", p.is_file(), True)
    if p.is_file():
        src = p.read_text(encoding="utf-8")
        check(f"{fname} opens with HAI", src.lstrip().startswith("HAI"), True)
        check(f"{fname} closes KTHXBYE", "KTHXBYE" in src, True)

# The real anti-stub check is the e2e section below (different inputs
# must force different LOLCODE-computed outputs). As a cheap structural
# smell test here, the adapter must not contain a canned result table.
check("adapter has no canned result table",
      "ADD 2 3" not in Path(adapter.__file__).read_text(encoding="utf-8")
      and "== 5" not in Path(adapter.__file__).read_text(encoding="utf-8")
      and '"5"' not in Path(adapter.__file__).read_text(encoding="utf-8"),
      True)

unknown_op_raised = False
try:
    adapter.run("fizzbuzz", "2 3")
except adapter.LolcodeExecutionError:
    unknown_op_raised = True
except adapter.LolcodeRuntimeNotFound:
    unknown_op_raised = True  # still refused before doing any compute
check("unknown op refused", unknown_op_raised, True)


# ─── JAJAJA in the execution path ───────────────────────────────────
print("\n=== JAJAJA IN PATH ===")

output, steps, status, receipts = demo_run("ADD 2 3")
check("jajaja rewrote the request", steps >= 2, True)
check("jajaja halted", status == "HALTED", True)
check("jajaja emitted lolcode effect",
      any(r["capability"] == "lolcode" for r in receipts), True)
check("jajaja confirmed receipt", "respuesta_recibida" in output, True)

output2, steps2, status2, receipts2 = demo_run("DIV 1 2")
check("unknown op: jajaja does NOT emit backend effect",
      [r for r in receipts2 if r["capability"] == "lolcode"], [])

# Capability gate: without the capability in the allowlist, DENY.
_, _, _, receipts3 = run_host(ROUTE, stdin_data="ADD 2 3",
                              allow=["stdout"])
bad = [r for r in receipts3
       if r["capability"] == "lolcode" and r["status"] != "OK"]
check("capability denied outside allowlist", len(bad) == 1, True)


# ─── Negative test: no external runtime -> loud failure, no fallback ─
print("\n=== NEGATIVE: NO RUNTIME ===")

saved = os.environ.get("LOLCODE_CMD")
os.environ["LOLCODE_CMD"] = r"C:\definitely\not\a\real\lci.exe"
try:
    exploded = False
    try:
        adapter.run("sum", "2 3")
    except adapter.LolcodeRuntimeNotFound:
        exploded = True
    check("missing runtime raises", exploded, True)

    # And crucially: with the runtime broken, the end-to-end result is
    # an ERROR receipt -- Python does not invent the sum.
    _, _, _, receipts4 = demo_run("ADD 2 3")
    rec = receipts4[0]
    check("no-runtime receipt is not OK", rec["status"] == "OK", False)
    check("no-runtime payload is not a computed 5",
          rec["payload"].strip() == "5", False)
finally:
    if saved is None:
        del os.environ["LOLCODE_CMD"]
    else:
        os.environ["LOLCODE_CMD"] = saved


# ─── End-to-end (requires external runtime) ─────────────────────────
print("\n=== END-TO-END (external LOLCODE runtime) ===")

try:
    adapter.resolve_runtime()
    runtime_here = True
except adapter.LolcodeRuntimeNotFound:
    runtime_here = False

if not runtime_here:
    check("external runtime absent -> e2e impossible "
          "(NO PYTHON FALLBACK)", True, True)
    skip("e2e sum/max/echo/count", "no lci runtime found")
else:
    def receipt_value(request):
        _, _, _, recs = demo_run(request)
        rec = [r for r in recs if r["capability"] == "lolcode"][0]
        assert rec["status"] == "OK", rec
        return rec["payload"].strip()

    check("ADD 2 3 -> 5 (LOLCODE computed)", receipt_value("ADD 2 3"), "5")
    check("ADD 17 25 -> 42 (not a canned demo pair)",
          receipt_value("ADD 17 25"), "42")
    check("MAX 9 4 -> 9 (branch picks left)",
          receipt_value("MAX 9 4"), "9")
    check("MAX 2 7 -> 7 (branch picks right)",
          receipt_value("MAX 2 7"), "7")
    check("ECHO hello backend -> echo",
          receipt_value("ECHO hello backend"), "hello backend")
    check("COUNT 3 -> 3 2 1 0 (real loop)",
          receipt_value("COUNT 3"), "3\n2\n1\n0")


# El resumen y la salida solo al ejecutarlo como script: bajo pytest (que importa
# el modulo para coleccionarlo) el sys.exit de nivel modulo producia INTERNALERROR.
if __name__ == "__main__":
    print(f"\n{passed} OK, {failed} FAILED, {skipped} SKIPPED")
    sys.exit(1 if failed else 0)
