"""tm_to_jajaja.py — traduce cualquier máquina de Turing a un programa JAJAJA.

La pregunta "¿JAJAJA es Turing completo?" se contesta con una traducción
mecánica, no con un argumento. Este script:

  1. define una MT como diccionario de transiciones;
  2. la compila a reglas JAJAJA (`compile_tm`);
  3. la corre en un simulador de MT de referencia (`run_tm`);
  4. corre el programa JAJAJA compilado en el intérprete real;
  5. compara las dos cintas finales.

Si coinciden para toda MT que probemos, la traducción es correcta y JAJAJA
puede simular cualquier MT.

CODIFICACIÓN
------------
Una configuración se representa como una sola cadena:

    | izquierda <q> símbolo derecha $

`|` y `$` son topes de cinta; `<q>` es el estado, colocado inmediatamente a la
izquierda de la celda bajo el cabezal. El marcador de estado aparece
exactamente una vez, así que "la ocurrencia más a la izquierda" nunca es
ambigua: la regla se aplica donde está el cabezal y en ningún otro lado.

    δ(q,s) = (q', s', R)   ->   <q>s        ::= s'<q'>
    δ(q,s) = (q', s', L)   ->   x<q>s       ::= <q'>xs'     (una por cada x)
                                #<q>s       ::= #<q'>_s'    (extiende a la izq.)
    cinta infinita a la derecha ->   <q>$   ::= <q>_$

ORDEN DE LAS REGLAS
-------------------
JAJAJA aplica la primera regla que matchea. Las reglas de extensión de cinta
van primero: `<q>$` sólo matchea cuando el cabezal cayó fuera de la cinta
escrita, así que no le roba el turno a ninguna transición real.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from jajaja_interpreter import Jajaja  # noqa: E402

BLANK = "_"
# Tope izquierdo: NO puede ser "#". Una línea que empieza con "#" es un
# comentario, así que la base nunca puede arrancar con ese carácter. Se
# descubrió compilando esta misma traducción: la base salía comentada entera y
# la máquina "terminaba" en 0 pasos con la cinta vacía.
LEFT_END = "|"
RIGHT_END = "$"


class TM:
    """Máquina de Turing determinista de una cinta."""

    def __init__(self, name, states, alphabet, transitions, start, halt):
        self.name = name
        self.states = states
        self.alphabet = alphabet          # sin contar BLANK
        self.transitions = transitions    # (q, s) -> (q', s', 'L'|'R')
        self.start = start
        self.halt = halt

    def tape_symbols(self):
        return list(self.alphabet) + [BLANK]


# --------------------------------------------------------------------------
# 1. Simulador de referencia (independiente de JAJAJA)
# --------------------------------------------------------------------------
def run_tm(tm: TM, tape: str, max_steps: int = 10000):
    cells = list(tape) if tape else [BLANK]
    head, state, steps = 0, tm.start, 0

    while state != tm.halt and steps < max_steps:
        if head < 0:
            cells.insert(0, BLANK)
            head = 0
        while head >= len(cells):
            cells.append(BLANK)

        key = (state, cells[head])
        if key not in tm.transitions:
            break
        state, cells[head], move = tm.transitions[key]
        head += 1 if move == "R" else -1
        steps += 1

    return "".join(cells), state, steps


# --------------------------------------------------------------------------
# 2. Compilador MT -> JAJAJA
# --------------------------------------------------------------------------
def compile_tm(tm: TM, tape: str) -> str:
    rules: list[str] = []

    # Extensión de cinta: el cabezal se salió por la derecha -> materializa un
    # blanco. Va primero porque `<q>$` sólo matchea en ese caso exacto.
    for q in tm.states:
        if q != tm.halt:
            rules.append(f"<{q}>{RIGHT_END}::=<{q}>{BLANK}{RIGHT_END}")

    # Transiciones.
    for (q, s), (q2, s2, move) in tm.transitions.items():
        if move == "R":
            rules.append(f"<{q}>{s}::={s2}<{q2}>")
        else:
            # Movimiento a la izquierda: hay que saber qué había a la izquierda,
            # así que se emite una regla por cada símbolo posible de cinta.
            for x in tm.tape_symbols():
                rules.append(f"{x}<{q}>{s}::=<{q2}>{x}{s2}")
            # ...y el caso de estar pegado al tope izquierdo: extiende la cinta.
            rules.append(f"{LEFT_END}<{q}>{s}::={LEFT_END}<{q2}>{BLANK}{s2}")

    # Al llegar al estado final, emite una firma observable y borra el marcador.
    # Después de esto ninguna regla matchea -> HALTED.
    rules.append(f"<{tm.halt}>::=~HALT")

    base = f"{LEFT_END}<{tm.start}>{tape or BLANK}{RIGHT_END}"
    return "\n".join(rules) + "\n::=\n" + base + "\n"


def jajaja_tape(final_base: str) -> str:
    """Extrae la cinta de la base final de JAJAJA (quita topes y estado)."""
    body = final_base
    if body.startswith(LEFT_END):
        body = body[len(LEFT_END):]
    if body.endswith(RIGHT_END):
        body = body[: -len(RIGHT_END)]
    while "<" in body:                      # borra el marcador de estado
        i = body.index("<")
        j = body.index(">", i)
        body = body[:i] + body[j + 1:]
    return body


def run_compiled(tm: TM, tape: str, max_steps: int = 200000):
    machine = Jajaja(compile_tm(tm, tape))
    output, steps, status = machine.run(max_steps=max_steps)
    return jajaja_tape(machine.base), output, steps, status


# --------------------------------------------------------------------------
# 3. Máquinas de prueba
# --------------------------------------------------------------------------
def tm_binary_increment() -> TM:
    """Suma 1 a un binario. Va al final, vuelve propagando el acarreo."""
    return TM(
        name="binary_increment",
        states=["seek", "carry", "done"],
        alphabet=["0", "1"],
        transitions={
            ("seek", "0"): ("seek", "0", "R"),
            ("seek", "1"): ("seek", "1", "R"),
            ("seek", BLANK): ("carry", BLANK, "L"),
            ("carry", "1"): ("carry", "0", "L"),
            ("carry", "0"): ("done", "1", "L"),
            ("carry", BLANK): ("done", "1", "L"),
        },
        start="seek",
        halt="done",
    )


def tm_bit_flip() -> TM:
    """Complementa cada bit y vuelve una celda. Ejercita sólo movimientos R."""
    return TM(
        name="bit_flip",
        states=["flip", "done"],
        alphabet=["0", "1"],
        transitions={
            ("flip", "0"): ("flip", "1", "R"),
            ("flip", "1"): ("flip", "0", "R"),
            ("flip", BLANK): ("done", BLANK, "L"),
        },
        start="flip",
        halt="done",
    )


def tm_unary_to_binary_parity() -> TM:
    """Recorre unos y termina; el estado final codifica la paridad.

    Ejercita alternancia de estados, que es lo que distingue una MT de un
    simple reemplazo de símbolos.
    """
    return TM(
        name="parity",
        states=["even", "odd", "done"],
        alphabet=["1"],
        transitions={
            ("even", "1"): ("odd", "1", "R"),
            ("odd", "1"): ("even", "1", "R"),
            ("even", BLANK): ("done", "P", "L"),   # par   -> marca P
            ("odd", BLANK): ("done", "I", "L"),    # impar -> marca I
        },
        start="even",
        halt="done",
    )


CASES = [
    (tm_binary_increment(), "1011"),
    (tm_binary_increment(), "111"),
    (tm_binary_increment(), "0"),
    (tm_bit_flip(), "1011"),
    (tm_bit_flip(), "0000"),
    (tm_unary_to_binary_parity(), "1111"),
    (tm_unary_to_binary_parity(), "11111"),
]


def main() -> int:
    print("Traducción mecánica MT -> JAJAJA, verificada contra un simulador")
    print("=" * 68)
    failures = 0

    for tm, tape in CASES:
        ref_tape, ref_state, ref_steps = run_tm(tm, tape)
        got_tape, output, steps, status = run_compiled(tm, tape)

        ref_clean = ref_tape.strip(BLANK)
        got_clean = got_tape.strip(BLANK)
        ok = ref_clean == got_clean and status == "HALTED" and output == "HALT"

        failures += not ok
        print(f"\n{'OK  ' if ok else 'FAIL'}  {tm.name}({tape!r})")
        print(f"        MT de referencia : {ref_clean!r}  ({ref_steps} pasos, estado {ref_state})")
        print(f"        JAJAJA compilado : {got_clean!r}  ({steps} pasos, {status}, output={output!r})")

    print("\n" + "=" * 68)
    print(f"casos={len(CASES)} fallos={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
