"""tools/parity_check.py — differential parity: Python oracle vs LOLCODE.

Corre cada fixture .jaja con DOS runtimes:

- ORACLE:  jajaja_interpreter.run (Python)
- LOLCODE: tools/run_jajaja_lol.run_lol -> src/jajaja.lol sobre lci

Compara (output, steps, status) EXACTAMENTE y escribe
evidence/lolcode_port/parity.json. Sin equivalencias suaves:
un mismatch es un mismatch.

Uso:
    python tools/parity_check.py             # corre y escribe evidence
    python tools/parity_check.py --check-only   # exit distinto de 0 si hay mismatch
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from jajaja_interpreter import run as oracle_run  # noqa: E402
from run_jajaja_lol import run_lol  # noqa: E402


# (nombre, fuente .jaja, stdin, max_steps) — el corpus cubre:
# leftmost, reglas ordenadas, emision, newline, stdin, halting, vacio
CASES = [
    ("hola",            "examples/hola.jaja",        "",             200000),
    ("amplificacion",   "examples/amplificacion.jaja","",            200000),
    ("eco",             "examples/eco.jaja",         "",             200000),
    ("echo_stdin",      "examples/echo.jaja",       "jajaja?",      200000),
    ("command",         "examples/command.jaja",     "",             200000),
    ("stdin_prefix",    "examples/echo.jaja",        "abcde",        200000),
    ("busy_beaver",     "examples/busy_beaver.jaja", "",             200000),
    ("crlf",            "examples/bootstrap_crlf.jaja","",           200000),
    # Los programs que no terminan usan un presupuesto PEQUENO e identico
    # en ambos lados: compara semantica, no velocidad (el oraculo corre
    # 200k pasos en ms; LOLCODE igualaria en minutos).
    ("simple_counter",  "examples/simple_counter.jaja","",           20),
    ("grow",            "examples/grow.jaja",        "",             20),
    ("max_steps_cap",   "examples/loop.jaja",        "",             3),
]

# Fixtures inline de semantica tramposa (P06):
# lhs_dentro_rhs, solapamiento, orden, autorewrite infinito, stop natural,
# CRLF en base, input runtime, regla larga vs corta.
INLINE_CASES = [
    ("lhs_in_rhs_grows", "jajajaja::=~STOP\njaja::=jajajaja\n::=\njaja", "", 10),
    ("self_rewrite_infinite", "a::=aa\n::=\na", "", 25),
    ("order_first_long", "abc::=~X\nab::=~Y\n::=\nabc", "", 100),
    ("order_fallback", "zzz::=~NO\nab::=~SI\n::=\nzab", "", 100),
    ("overlap_leftmost", "ab::=X\n::=\nabab", "", 100),
    ("empty_lhs_rule", "::=esto_no_se_aplica\na::=~fin\n::=\na", "", 100),
    ("nl_only_rhs", "a::=~\n::=\na", "", 100),
    ("stdin_special_input", None, "jajaja!?<>", 200000),
    # parser edge: separador con espacios
    ("sep_with_spaces", "a::=~ok\n   ::=   \na", "", 100),
    # parser edge: comentario como primera linea y entre reglas
    ("comments_between_rules", "# header\na::=~uno\n# entre\nb::=~dos\n::=\nab", "", 100),
    # parser edge: regla con '#' (el # va dentro del patron si no es linea completa)
    ("hash_in_rhs", "a::=~#valor\n::=\na", "", 100),
    # stdin vacio -> sin prefijo
    ("stdin_empty", None, "", 200000),
    # input con caracteres que chocan con marcadores solo si bugs de transporte
    ("stdin_brackets", None, "hello <<N>> world", 200000),
]


def run_case(name: str, rel: str, stdin_data: str, max_steps: int,
             inline: str | None = None) -> dict:
    if inline is not None:
        src = inline
    else:
        src = (REPO / rel).read_text(encoding="utf-8")
    t0 = time.perf_counter()
    o_out, o_steps, o_status = oracle_run(src, max_steps=max_steps,
                                          stdin_data=stdin_data)
    t_py = time.perf_counter() - t0
    t0 = time.perf_counter()
    l_out, l_steps, l_status = run_lol(src, stdin_data=stdin_data,
                                       max_steps=max_steps)
    t_lol = time.perf_counter() - t0
    match = (o_out == l_out) and (o_steps == l_steps) and (o_status == l_status)
    return {
        "case": name,
        "file": rel,
        "stdin": stdin_data,
        "max_steps": max_steps,
        "python": {"output": o_out, "steps": o_steps, "status": o_status},
        "lolcode": {"output": l_out, "steps": l_steps, "status": l_status},
        "match": match,
        "time_python_s": round(t_py, 6),
        "time_lolcode_s": round(t_lol, 3),
    }


def main() -> int:
    check_only = "--check-only" in sys.argv
    results = []
    mismatches = 0
    for name, rel, stdin_data, max_steps in CASES:
        r = run_case(name, rel, stdin_data, max_steps)
        results.append(r)
        ok = r["match"]
        mismatches += 0 if ok else 1
        mark = "MATCH  " if ok else "MISMATCH"
        print(f"{mark} {name}: steps={r['lolcode']['steps']} "
              f"status={r['lolcode']['status']} "
              f"(py {r['time_python_s']}s / lol {r['time_lolcode_s']}s)")
    for name, inline, stdin_data, max_steps in INLINE_CASES:
        if inline is None:
            # caso con archivo + stdin especial
            r = run_case(name, rel="examples/echo.jaja", stdin_data=stdin_data,
                         max_steps=max_steps)
        elif name.startswith(("sep_", "comments_", "hash_in")):
            r = run_case(name, "(inline)", stdin_data, max_steps, inline=inline)
        else:
            r = run_case(name, "(inline)", stdin_data, max_steps, inline=inline)
        results.append(r)
        ok = r["match"]
        mismatches += 0 if ok else 1
        mark = "MATCH  " if ok else "MISMATCH"
        print(f"{mark} {name}: steps={r['lolcode']['steps']} "
              f"status={r['lolcode']['status']} "
              f"(py {r['time_python_s']}s / lol {r['time_lolcode_s']}s)")

    n = len(results)
    print(f"\n{n} cases, {n - mismatches} identical, {mismatches} mismatches")

    if not check_only:
        out_dir = REPO / "evidence" / "lolcode_port"
        out_dir.mkdir(parents=True, exist_ok=True)
        doc = {
            "suite": "JAJAJA Python-oracle vs LOLCODE-runtime parity",
            "cases": results,
            "total": n,
            "identical": n - mismatches,
            "mismatches": mismatches,
            "parity": mismatches == 0,
        }
        (out_dir / "parity.json").write_text(
            json.dumps(doc, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"escrito: {out_dir / 'parity.json'}")

    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
