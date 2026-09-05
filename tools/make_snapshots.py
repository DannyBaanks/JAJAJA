"""tools/make_snapshots.py — genera tests/snapshots.json con el resultado
(output, steps, status) de ejecutar cada fixture conocido usando el
runtime Python como oráculo; lo archiva de forma determinista.

Luego puede correr (sin Python) un verificador PS1 que corre cada fixture
contra el snapshot. Si hay drift: el runtime ha cambiado de conducta en
forma no intencionada.

Solo se corre cuando cambian fixtures o runtime. Determinista.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from jajaja_interpreter import run  # noqa: E402


def snapshot_case(name: str, source: str, stdin_data: str = "",
                  max_steps: int = 5000, path: str = "") -> dict:
    output, steps, status = run(source, stdin_data=stdin_data, max_steps=max_steps)
    return {
        "name": name,
        "path": path,
        "stdin": stdin_data,
        "max_steps": max_steps,
        "output_sha256": hashlib.sha256(output.encode("utf-8")).hexdigest(),
        "output": output,
        "steps": steps,
        "status": status,
    }


def main() -> int:
    snaps: list[dict] = []

    # 1) Todos los examples/*.jaja
    for p in sorted((REPO / "examples").glob("*.jaja")):
        src = p.read_text(encoding="utf-8")
        stdin = ""
        if p.name == "echo.jaja":
            stdin = "hello"
        if p.name == "calculator.jaja":
            stdin = "ADD 1 2"
        snaps.append(snapshot_case(p.name, src, stdin, max_steps=30,
                                   path=f"examples/{p.name}"))

    # 2) Bootstrap canónico
    snaps.append(snapshot_case("bootstrap", (REPO / "bootstrap.jaja").read_text(encoding="utf-8"),
                               path="bootstrap.jaja"))

    # 3) Fixtures adicionales tracked (tienen camino real)
    snaps.append(snapshot_case("inline_echo", "a::=~a\n ::=~ \n::=\n\n", stdin_data="",
                               max_steps=1, path="tests/fixtures/inline_echo.jaja"))

    data = {
        "version": 1,
        "source_responsible": "jajaja_interpreter.run",
        "frozen_at": "2026-09-04",
        "cases": snaps,
    }
    out = REPO / "tests" / "snapshots.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"snapshot: {len(snaps)} casos en {out}")
    print(f"sha256:{hashlib.sha256(out.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
