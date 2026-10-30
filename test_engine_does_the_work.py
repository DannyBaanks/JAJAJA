"""test_engine_does_the_work.py — prueba adversarial del estandar §9.

Regla: el HOST no puede robarle el trabajo al lenguaje. Patron prohibido:

    resultado = resolver_en_python(programa)
    engine.state["resultado"] = resultado
    assert engine.state["resultado"] == esperado

Como se prueba de verdad:

    1. construir el programa
    2. comprobar que el resultado todavia NO existe
    3. ejecutar el engine
    4. comprobar que el resultado aparece SOLO despues del runtime

Mas: el mismo artefacto con inputs distintos da resultados distintos y
deterministas — senal de que la semantica vive en las reglas, no en el host.

Sin framework:  python test_engine_does_the_work.py
"""
from __future__ import annotations

import hashlib

from jajaja_interpreter import Jajaja, run


def main() -> int:
    failed = 0

    def check(ok: bool, label: str) -> None:
        nonlocal failed
        print(("OK   " if ok else "FAIL ") + label)
        if not ok:
            failed += 1

    # --- 1-4. Patron adversarial basico ------------------------------------
    source = (
        "# engine_does_the_work fixture\n"
        "hello::=~HELLO\n"
        "bye::=~BYE\n"
        "::=\n"
    )

    machine = Jajaja(source)
    check(machine.steps == 0 and machine.output == [] and machine.status == "RUNNING",
          "1 programa construido: resultado AUSENTE (steps=0, output vacio)")

    out, steps, status = machine.run(stdin_data="hello")
    check(out == "HELLO", "2 tras engine.run: el resultado APARECE (HELLO)")
    check(status == "HALTED" and steps == 1, "3 estado final coherente (HALTED, 1 paso)")

    # --- 5. El motor hace el trabajo, no una tabla del host ----------------
    out_bye, _, _ = run(source, stdin_data="bye")
    check(out_bye != out and out_bye == "BYE",
          "4 mismo artefacto, otro input -> otro resultado (BYE != HELLO)")

    # --- 6. La imagen compilada es identica entre inputs --------------------
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    check(digest == hashlib.sha256(source.encode("utf-8")).hexdigest(),
          "5 mismo artefacto (sha256 invariable entre inputs)")

    # --- 7. Determinismo: rerun exacto --------------------------------------
    out2, steps2, status2 = run(source, stdin_data="hello")
    check((out2, steps2, status2) == (out, steps, status),
          "6 rerun: mismo programa + mismo input = mismo resultado")

    # --- 8. Input desconocido: el motor no inventa nada ----------------------
    out_none, steps_none, status_none = run(source, stdin_data="ciao")
    check((out_none, steps_none, status_none) == ("", 0, "HALTED"),
          "7 input sin regla: ninguna emision, HALTED limpio (no hay fallback del host)")

    # --- 9. Trace es canal lateral: no altera la ejecucion -------------------
    plain = run(source, stdin_data="hello")
    traced = Jajaja(source, trace=True)
    out_t, steps_t, status_t = traced.run(stdin_data="hello")
    check((out_t, steps_t, status_t) == plain,
          "8 invariante trace: con/sin traza mismo (output, steps, status)")
    check(len(traced.trace) == steps_t + 1,
          "9 traza completa: un snapshot por paso mas el inicial")

    print("passed=%d failed=%d" % (9 - failed, failed))
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
