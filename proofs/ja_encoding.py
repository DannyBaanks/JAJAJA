"""ja_encoding.py — ¿el alfabeto `ja` alcanza, o hace falta un delimitador?

`tm_to_jajaja.py` demuestra que el MOTOR de JAJAJA simula cualquier máquina de
Turing, usando tokens arbitrarios (`<q0>`, `0`, `1`, `|`, `$`).

Pero la §7 de la spec afirma algo más fuerte: que el conteo de `ja` es una
codificación unaria del alfabeto, o sea que el lenguaje sigue siendo Turing
completo **usando solamente risas**. Eso no es automático, y este script lo
somete a prueba.

EL PROBLEMA
-----------
La codificación unaria sin delimitador es AMBIGUA por construcción:

    símbolo 2  ->  "jaja"
    símbolo 3  ->  "jajaja"

y `"jaja"` es un substring de `"jajaja"`. Peor: concatenar el símbolo 2 con el
3 da `"jajajajaja"`, que es indistinguible del símbolo 5. Como las reglas de
JAJAJA matchean por substring, una regla para el símbolo 2 se dispara en medio
del símbolo 3 y la máquina se corrompe.

LA SOLUCIÓN
-----------
Un delimitador. Los ejemplos de la spec ya usan espacios entre risas
(`jaja j`), pero la spec nunca dice que ese espacio sostiene la codificación.
Con delimitador, ` jaja ` no es substring de ` jajaja `, la ambigüedad
desaparece y la traducción del script hermano se transporta tal cual.

Conclusión: el alfabeto de risas es Turing completo **con delimitador**, y no
lo es sin él.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from jajaja_interpreter import Jajaja, run  # noqa: E402
from tm_to_jajaja import (  # noqa: E402
    BLANK, TM, run_tm, tm_binary_increment, tm_bit_flip,
)

SEP = " "


# --------------------------------------------------------------------------
# 1. La ambigüedad, demostrada
# --------------------------------------------------------------------------
def demo_ambiguity() -> bool:
    print("1. SIN delimitador la codificación unaria es ambigua")
    print("-" * 66)

    dos, tres, cinco = "ja" * 2, "ja" * 3, "ja" * 5
    print(f"   símbolo 2      = {dos!r}")
    print(f"   símbolo 3      = {tres!r}")
    print(f"   ¿2 es substring de 3?        {dos in tres}")
    print(f"   símbolo2 + símbolo3          = {dos + tres!r}")
    print(f"   símbolo 5                    = {cinco!r}")
    print(f"   ¿son la misma cadena?        {dos + tres == cinco}")

    # Consecuencia operativa: una regla del símbolo 2 muerde dentro del 3.
    source = f"{dos}::=~MORDIO\n::=\n{tres}\n"
    output, steps, status = run(source)
    print(f"\n   programa: regla sobre el símbolo 2, base = sólo el símbolo 3")
    print(f"   resultado: output={output!r} steps={steps} status={status}")
    corrupted = output == "MORDIO"
    print(f"   -> la regla del símbolo 2 se disparó dentro del 3: {corrupted}")

    print("\n   CON delimitador:")
    d_dos, d_tres = f"{SEP}{dos}{SEP}", f"{SEP}{tres}{SEP}"
    print(f"   ¿{d_dos!r} es substring de {d_tres!r}?  {d_dos in d_tres}")
    ok = corrupted and (d_dos not in d_tres)
    print(f"\n   {'OK' if ok else 'FAIL'}: el delimitador es el que sostiene la codificación")
    return ok


# --------------------------------------------------------------------------
# 2. Una MT real, corrida en risas puras
# --------------------------------------------------------------------------
class JaAlphabet:
    """Asigna a cada símbolo/estado una risa distinta: `ja` repetido k veces."""

    def __init__(self, tm: TM):
        # 1 se reserva para el tope izquierdo, 2 para el derecho.
        self.code: dict[str, str] = {"|": "ja" * 1, "$": "ja" * 2}
        nxt = 3
        for sym in tm.tape_symbols():
            self.code[sym] = "ja" * nxt
            nxt += 1
        for q in tm.states:
            self.code[f"<{q}>"] = "ja" * nxt
            nxt += 1
        self.decode = {v: k for k, v in self.code.items()}

    def tok(self, symbol: str) -> str:
        return self.code[symbol]

    def word(self, *symbols: str) -> str:
        """Secuencia delimitada, con separador a ambos lados."""
        return SEP + SEP.join(self.tok(s) for s in symbols) + SEP


def compile_tm_ja(tm: TM, tape: str) -> tuple[str, JaAlphabet]:
    a = JaAlphabet(tm)
    rules: list[str] = []

    for q in tm.states:
        if q != tm.halt:
            rules.append(f"{a.word(f'<{q}>', '$')}::={a.word(f'<{q}>', BLANK, '$')}")

    for (q, s), (q2, s2, move) in tm.transitions.items():
        if move == "R":
            rules.append(f"{a.word(f'<{q}>', s)}::={a.word(s2, f'<{q2}>')}")
        else:
            for x in tm.tape_symbols():
                rules.append(f"{a.word(x, f'<{q}>', s)}::={a.word(f'<{q2}>', x, s2)}")
            rules.append(f"{a.word('|', f'<{q}>', s)}::={a.word('|', f'<{q2}>', BLANK, s2)}")

    # OJO: acá NO va una regla emisora de firma, a diferencia de la versión con
    # tokens arbitrarios. Una regla `~` borra el match ENTERO, delimitadores
    # incluidos, así que al consumir ` <halt> ` fusiona a sus dos vecinos en un
    # solo token y corrompe la cinta. Medido: la cinta salía como '100' en vez
    # de '1100', y en bit_flip la firma se emitía tres veces mientras la cinta
    # se deshacía.
    #
    # Es una incompatibilidad real entre las reglas de salida de JAJAJA y
    # cualquier codificación que dependa de delimitadores: se computa en la
    # cinta, no en el output. La máquina para sola cuando el estado final no
    # tiene transiciones, que es el criterio de parada correcto igual.
    base = a.word("|", f"<{tm.start}>", *(tape or BLANK), "$")
    return "\n".join(rules) + "\n::=\n" + base + "\n", a


def decode_tape(base: str, a: JaAlphabet, tm: TM) -> str:
    out = []
    for token in base.strip().split(SEP):
        if not token:
            continue
        sym = a.decode.get(token, "?")
        if sym in ("|", "$") or sym.startswith("<"):
            continue
        out.append(sym)
    return "".join(out)


def demo_pure_ja() -> bool:
    print("\n\n2. Una máquina de Turing corriendo en risas puras")
    print("-" * 66)
    failures = 0

    for tm, tape in [(tm_binary_increment(), "1011"), (tm_bit_flip(), "1011")]:
        source, a = compile_tm_ja(tm, tape)
        machine = Jajaja(source)
        output, steps, status = machine.run(max_steps=200000)
        got = decode_tape(machine.base, a, tm).strip(BLANK)
        want = run_tm(tm, tape)[0].strip(BLANK)

        ok = got == want and status == "HALTED" and output == ""
        failures += not ok
        print(f"\n   {'OK  ' if ok else 'FAIL'} {tm.name}({tape!r})")
        print(f"        esperado : {want!r}")
        print(f"        en risas : {got!r}  ({steps} pasos, {status}, output={output!r})")
        print(f"        el resultado vive en la cinta, no en el output (ver compile_tm_ja)")

        if tm.name == "binary_increment":
            # Todo el programa menos la única regla emisora (`::=~HALT`, cuyo
            # texto de salida es ASCII por necesidad): reglas, cinta y estados
            # tienen que ser exclusivamente risas.
            laughs_only = "\n".join(
                ln for ln in source.splitlines() if not ln.endswith("~HALT"))
            alphabet = {c for c in laughs_only if c not in " \n:=~"}
            print(f"        alfabeto de reglas y cinta: {sorted(alphabet)}")
            print(f"        (sólo 'j' y 'a' -> risa pura)")

    return failures == 0


def main() -> int:
    print("¿El alfabeto `ja` alcanza para Turing completitud?")
    print("=" * 66 + "\n")
    ok = demo_ambiguity()
    ok = demo_pure_ja() and ok
    print("\n" + "=" * 66)
    print("VEREDICTO: el alfabeto `ja` es Turing completo CON delimitador.")
    print("           Sin delimitador la codificación unaria es ambigua y")
    print("           las reglas se muerden entre sí.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
