"""turing_parity_lol.py — ejecuta los fixtures de la prueba de Turing en el
runtime LOLCODE y verifica paridad con el oraculo Python.

El GENERADOR `proofs/tm_to_jajaja.compile_tm` se sigue usando igual: es
codificacion estatica (produce texto .jaja). Lo que se prueba es que el
texto generado se ejecuta identico en ambos runtimes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "proofs"))
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(REPO))

from tm_to_jajaja import CASES, compile_tm  # noqa: E402
from jajaja_interpreter import run as oracle_run  # noqa: E402
from run_jajaja_lol import run_lol  # noqa: E402


def main() -> int:
    results = []
    mismatches = 0
    for i, (tm, tape) in enumerate(CASES):
        src = compile_tm(tm, tape)
        expected_final = None
        # oraculo
        o_out, o_steps, o_status = oracle_run(src)
        l_out, l_steps, l_status = run_lol(src, timeout=300)
        ok = (o_out == l_out) and (o_steps == l_steps) and (o_status == l_status)
        mismatches += 0 if ok else 1
        results.append({
            "case": i, "tape_in": tape,
            "oracle":  {"output": o_out, "steps": o_steps, "status": o_status},
            "lolcode": {"output": l_out, "steps": l_steps, "status": l_status},
            "match": ok,
        })
        print(f"{'MATCH' if ok else 'MISMATCH'}  tm case {i} tape={tape} "
              f"steps={o_steps} status={o_status}")
    n = len(results)
    print(f"\n{n}/N cases, {n - mismatches} identical, {mismatches} mismatches")

    out = REPO / "evidence" / "lolcode_port"
    out.mkdir(parents=True, exist_ok=True)
    (out / "turing_parity.json").write_text(
        json.dumps({
            "suite": "Turing-machine fixtures (proofs/tm_to_jajaja) parity",
            "generator": "proofs/tm_to_jajaja.compile_tm (unchanged, static encoding)",
            "runtimes": ["jajaja_interpreter.run (oracle)", "src/jajaja.lol via lci"],
            "cases": results, "total": n, "identical": n - mismatches,
            "mismatches": mismatches, "parity": mismatches == 0,
        }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
