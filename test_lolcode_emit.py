"""test_lolcode_emit.py — Tests for the LOLCODE source emitter.

Two layers:
1. Unit: emitted text matches expected LOLCODE syntax (no runtime needed).
2. Integration: compile demo programs with the emitter and RUN them on
   the external lci runtime; verify outputs end-to-end.

If lci is not available the integration layer is SKIPPED (never faked).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "backends" / "lolcode"))

import emit as L  # noqa: E402

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


# ─── Unit layer ─────────────────────────────────────────────────────
print("\n=== EMITTER UNIT ===")
check("declare bare", L.declare("X"), "I HAS A X")
check("declare value", L.declare("X", 5), "I HAS A X ITZ 5")
check("declare expr", L.declare("X", "SUM OF 1 AN 2"), "I HAS A X ITZ SUM OF 1 AN 2")
check("assign", L.assign("X", "1"), "X R 1")
check("visible", L.visible("X"), "VISIBLE X")
check("visible bang", L.visible("X", bang=True), "VISIBLE X!")
check("visible literal", L.visible(L.str_lit("hi")), 'VISIBLE "hi"')
check("gimmeh", L.gimmeh("X"), "GIMMEH X")
check("call 0", L.call("FOO"), "I IZ FOO MKAY")
check("call 2", L.call("FOO", "1", "BAR"), "I IZ FOO YR 1 AN YR BAR MKAY")
check("cmp eq", L.cmp_eq("A", 1), "BOTH SAEM A AN 1")
check("cmp ne", L.cmp_ne("A", "B"), "DIFFRINT A AN B")
check("str_lit escape", L.str_lit('a"b'), '"a:"b"')
check("orly shape",
      L.orly(L.cmp_eq("X", 1), ['VISIBLE "Y"'], ['VISIBLE "N"']),
      ['BOTH SAEM X AN 1, O RLY?', '  YA RLY', '    VISIBLE "Y"',
       '  NO WAI', '    VISIBLE "N"', 'OIC'])
check("iminyr shape",
      L.iminyr("LULZ", [L.visible("X")], wile=L.cmp_ne("X", 0)),
      ["IM IN YR LULZ", "  WILE DIFFRINT X AN 0", "  VISIBLE X",
       "IM OUTTA YR LULZ"])
check("funcdec shape",
      L.funcdec("F", ["A", "B"], ["FOUND YR SUM OF A AN B"]),
      ["HOW IZ I F YR A AN YR B", "FOUND YR SUM OF A AN B", "IF U SAY SO"])
check("program wraps", L.program(['VISIBLE "X"']),
      'HAI 1.3\nVISIBLE "X"\nKTHXBYE\n')

# ─── Integration layer (needs lci) ──────────────────────────────────
print("\n=== EMITTER + LCI INTEGRATION ===")

LCI = os.environ.get("LOLCODE_CMD", "").strip() or None
if not LCI:
    import shutil
    LCI = shutil.which("lci") or shutil.which("lci.exe")

TMP = Path(tempfile.mkdtemp(prefix="lolcode_emit_"))


def run_lol(source: str, stdin_data: str = ""):
    """Run compiled LOLCODE on external lci. Returns (stdout, exit)."""
    prog = TMP / "prog.lol"
    prog.write_text(source, encoding="ascii")
    proc = subprocess.run([LCI, str(prog)], input=stdin_data,
                          capture_output=True, text=True, timeout=30)
    return proc.stdout, proc.returncode


if not LCI:
    skip("integration: generated programs vs lci", "no external runtime found")
else:
    e = L.Emitter()
    e.emit(L.declare("XVAR"), L.declare("YVAR"), L.gimmeh("XVAR"),
           L.gimmeh("YVAR"), L.visible("SUM OF XVAR AN YVAR"))
    out, code = run_lol(e.source(), "2\n3\n")
    check("compiled sum 2+3", (out.strip(), code), ("5", 0))

    e2 = L.Emitter()
    e2.emit(L.declare("XVAR"), L.declare("YVAR"),
            L.gimmeh("XVAR"), L.gimmeh("YVAR"),
            L.assign("XVAR", "MAEK XVAR NUMBR"), L.assign("YVAR", "MAEK YVAR NUMBR"))
    e2.block(L.orly(
        "BOTH SAEM XVAR AN BIGGR OF XVAR AN YVAR",
        [L.visible("XVAR")], [L.visible("YVAR")]))
    out, code = run_lol(e2.source(), "9\n4\n")
    check("compiled max 9 4 -> 9", out.strip(), "9")
    out, code = run_lol(e2.source(), "2\n7\n")
    check("compiled max 2 7 -> 7", out.strip(), "7")

    e3 = L.Emitter()
    e3.emit(L.declare("N"), L.gimmeh("N"), L.assign("N", "MAEK N NUMBR"))
    e3.block(L.iminyr("LULZ", [
        L.visible("N"),
        L.assign("N", "DIFF OF N AN 1"),
        *L.orly("BOTH SAEM N AN 0", [L.visible("0"), "GTFO"]),
    ]))
    out, code = run_lol(e3.source(), "3")
    check("compiled count 3 -> 3..0 loop", out.strip().split(), ["3", "2", "1", "0"])

    e4 = L.Emitter()
    e4.emit(L.declare("MSG"), L.gimmeh("MSG"), L.visible("MSG"))
    out, code = run_lol(e4.source(), "emit me\n")
    check("compiled echo", out.strip(), "emit me")


print(f"\n{passed} OK, {failed} FAILED, {skipped} SKIPPED")
sys.exit(1 if failed else 0)
