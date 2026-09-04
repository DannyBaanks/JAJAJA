"""compare_ja_run.py — el programa TM en risas puras, corrido en ambos
runtime: genera el .jaja con proofs/ja_encoding.py (que ya está verificado
byte-identico contra src/proofs_lol/ja_encoding.lol), lo corre en Python y en
LOLCODE (via run_jajaja_lol), y compara output/steps/status/base decodificada
contra el resultado esperado de la MT.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "proofs"))
sys.path.insert(0, str(REPO / "tools"))

import ja_encoding as pyenc  # noqa: E402
import tm_to_jajaja as pygen  # noqa: E402
from jajaja_interpreter import Jajaja  # noqa: E402
from run_jajaja_lol import run_lol  # noqa: E402


def runcase(tm, tape):
    name = tm.name
    source, a = pyenc.compile_tm_ja(tm, tape)
    want_tape = pygen.run_tm(tm, tape)[0].strip("_")

    # oráculo Python
    m = Jajaja(source)
    o_out, o_steps, o_status = m.run(max_steps=200000)

    # runtime LOLCODE via lci
    l_out, l_steps, l_status = run_lol(source, max_steps=200000, timeout=300)

    ok = (o_out == l_out == "" and o_steps == l_steps and
          o_status == l_status == "HALTED")
    decoded = pyenc.decode_tape(m.base, a, tm).strip("_")
    cinta_ok = decoded == want_tape
    print(("PASS" if (ok and cinta_ok) else "FAIL")
          + f"  {name}({tape!r})")
    if not ok:
        print(f"   py:  out={o_out!r} steps={o_steps} status={o_status}")
        print(f"   lol: out={l_out!r} steps={l_steps} status={l_status}")
    if not cinta_ok:
        print(f"   tape expected={want_tape!r} got={decoded!r}")
    return 0 if (ok and cinta_ok) else 1


def main() -> int:
    rc = 0
    rc |= runcase(pygen.tm_binary_increment(), "1011")
    rc |= runcase(pygen.tm_bit_flip(), "1011")
    return rc


if __name__ == "__main__":
    sys.exit(main())
