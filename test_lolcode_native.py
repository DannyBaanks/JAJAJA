"""test_lolcode_native.py — corre la suite nativa LOLCODE via lci.

No reimplementa lógica: arma el ejecutable con tools/build_lol.py, lo lanza
como proceso externo y exige "FAILURES 0" en la salida junto con exit=0.
Requiere LOLCODE_CMD o lci en PATH; si no hay runtime externo, se omite.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "tools"))
sys.path.insert(0, str(HERE))

from run_jajaja_lol import resolve_lci, TransportError  # noqa: E402
from build_lol import build  # noqa: E402

passed = 0
failed = 0
skipped = 0


def check(name, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        print(f"OK   {name}")
    else:
        failed += 1
        print(f"FAIL {name} {detail}")


def skip(name, why):
    global skipped
    skipped += 1
    print(f"SKIPPED  {name} ({why})")


def main() -> int:
    try:
        lci = resolve_lci()
    except TransportError:
        skip("runtime_tests.lol", "sin runtime externo (LOLCODE_CMD o lci en PATH)")
        print(f"\n{passed} OK, {failed} FAILED, {skipped} SKIPPED")
        return 0

    built = build("jajaja_tests.cfg")
    check("build produce runtime_tests.lol", built.name == "runtime_tests.lol",
          built.as_posix())

    proc = subprocess.run([lci, str(built)], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)
    check("lci exit 0", proc.returncode == 0, f"rc={proc.returncode} {proc.stderr[:200]!r}")

    out = proc.stdout
    check("suite imprime PASS/FAILURES", "PASS " in out and "FAILURES" in out)
    import re
    m = re.search(r"FAILURES\s+(\d+)", out)
    check("FAILURES == 0", m is not None and m.group(1) == "0",
          out.splitlines()[-4:] if m is None else None)

    print(f"\n{passed} OK, {failed} FAILED, {skipped} SKIPPED")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
