"""tools/compare_tm_compile.py — Verifica que src/proofs_lol/tm_compile.lol
produce bo byte a byte el .jaja que proofs/tm_to_jajaja.py produce.

Esto migra el generador (autoridad 'hacer .jaja') a LOLCODE, dejando
Python sólo como comparador independiente de la salida. Sin falsas
verificaciones: si ambos compiladores dan distinto, el diff se imprime y
el exit code es 1.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "proofs"))
sys.path.insert(0, str(REPO / "tools"))

import tm_to_jajaja as pygen  # noqa: E402
from run_jajaja_lol import resolve_lci  # noqa: E402

TMC_SRC = REPO / "src" / "proofs_lol" / "tm_compile.lol"


def python_compile(name: str, tape: str) -> str:
    if name == "binary_increment":
        tm = pygen.tm_binary_increment()
    elif name == "bit_flip":
        tm = pygen.tm_bit_flip()
    elif name == "parity":
        tm = pygen.tm_unary_to_binary_parity()
    else:
        raise ValueError(name)
    return pygen.compile_tm(tm, tape)


def lolcode_all() -> dict[str, str]:
    """Run the LOLCODE compiler; parse sections."""
    lci = resolve_lci()
    proc = subprocess.run([lci, str(TMC_SRC)], capture_output=True, text=True,
                          encoding="utf-8", timeout=60)
    if proc.returncode != 0:
        raise SystemExit(f"lci failed: {proc.stderr}")
    out = proc.stdout
    sections = {}
    cur = None
    buf = []
    for line in out.splitlines(keepends=True):
        m = re.match(r"^==== (\S+) (\S+) ====\s*$", line)
        if m:
            if cur is not None:
                sections[f"{cur[0]}|{cur[1]}"] = "".join(buf)
            cur = (m.group(1), m.group(2))
            buf = []
            continue
        buf.append(line)
    if cur is not None:
        sections[f"{cur[0]}|{cur[1]}"] = "".join(buf)
    return sections


def main() -> int:
    lci_out = lolcode_all()
    cases = [("binary_increment", "1011"), ("bit_flip", "1011"), ("parity", "1111")]
    failures = 0
    for name, tape in cases:
        expected = python_compile(name, tape)
        got = lci_out.get(f"{name}|{tape}", "")
        ok = got == expected
        print(("PASS" if ok else "FAIL") + f"  {name}({tape!r})")
        if not ok:
            failures += 1
            for i, (a, b) in enumerate(zip(expected.splitlines(), got.splitlines())):
                if a != b:
                    print(f"   linea {i}: oracle={a!r}  lolcode={b!r}")
            if len(expected) != len(got):
                print(f"   longitudes: oracle={len(expected)} lolcode={len(got)}")
    print(f"{len(cases) - failures}/{len(cases)} byte-identical")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
