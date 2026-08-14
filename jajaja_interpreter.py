r"""Jajaja interpreter (rewriting system over the laugh alphabet).

Jajaja es un esolang mexicano basado en Thue. La idea: el alfabeto
semantico son repeticiones del token "ja".

    "ja"     = 1 risa        (token unidad)
    "jaja"   = 2 risas
    "jajaja" = 3 risas
    ... y asi. La "longevidad" de la risa (conteo de `ja`s) forma cada
    "palabra" del programa.

State model:
    base :: str                  (la cinta de reescritura; risa acumulada)
    rules :: list[(lhs, rhs)]    (reglas lhs ::= rhs)
    output :: list[str]          (emisiones recogidas)

Rule model:
    En cada paso recorremos las reglas en orden. La PRIMERA regla cuyo lhs
    aparece en base se aplica en su primera ocurrencia (leftmost).
    - Si rhs comienza con `~`, el resto del rhs se emite como texto y se
      quita el match de base. `::~` solo (rhs="~") emite newline.
    - Si rhs no comienza con `~`, se reemplaza el match lhs por rhs en base.
    Si ninguna regla matchea -> HALT.

Termination behavior:
    HALTED: ningun lhs matchea en base.
    MAX_STEPS: presupuesto agotado (la risa puede no terminar).

Output: texto emitido via reglas `::~...`.

Source format (identico a Thue):

    # comentarios opcionales
    <lhs1>::=<rhs1>
    <lhs2>::=<rhs2>
    ...
    ::=
    <base inicial>

Convencion de Jajaja: lhs y rhs son tipicamente secuencias de `ja` contiguas
separadas por espacios (palabras).

    jajaja::=~JAJAJA-OK    # 3-risas emite "JAJAJA-OK"
    jaja::=jajaja          # 2-risas -> 3-risas (amplifica risa)
    j::=~                  # 1-risa silenciosa emite newline
    ::=
    jajaja j               # base: 3-risas seguidas de 1-risa

El motor es fiel a la semantica de reescritura; no convierte Thue en maquina
de registros. La diversidad semantica (reescritura no determinista) vive
aqui igual que en Thue.
"""
from __future__ import annotations


class JajajaError(Exception):
    pass


class Jajaja:
    def __init__(self, source: str):
        self.rules: list[tuple[str, str]] = []
        self.base = ""
        self.output: list[str] = []
        self._parse(source)

    def _parse(self, source: str) -> None:
        lines = source.splitlines()
        mode = "rules"
        i = 0
        for ln in lines:
            i += 1
            ln = ln.rstrip("\r")
            if mode == "rules":
                if ln == "":
                    continue
                if ln.startswith("#"):
                    continue
                if ln.strip() == "::=":
                    mode = "base"
                    continue
                if "::=" not in ln:
                    raise JajajaError(f"regla sin '::=' en linea {i}: {ln!r}")
                lhs, rhs = ln.split("::=", 1)
                self.rules.append((lhs, rhs))
            elif mode == "base":
                # La base es la primera linea NO-VACIA y no-comentario tras el
                # separador, igual que la spec §3 declara. Antes se tomaba la
                # primera linea a secas: una linea en blanco o un comentario
                # despues de `::=` se volvia la base, el programa arrancaba con
                # una cinta vacia y terminaba en HALT sin emitir nada ni
                # reportar error. Fallaba en silencio, que es la peor forma de
                # fallar en un lenguaje de juguete.
                if ln.strip() == "" or ln.strip().startswith("#"):
                    continue
                self.base = ln
                break

    def step(self) -> bool:
        for lhs, rhs in self.rules:
            if lhs == "":
                continue
            idx = self.base.find(lhs)
            if idx >= 0:
                if rhs.startswith("~"):
                    tail = rhs[1:]
                    self.output.append("\n" if tail == "" else tail)
                    self.base = self.base[:idx] + self.base[idx + len(lhs):]
                else:
                    self.base = self.base[:idx] + rhs + self.base[idx + len(lhs):]
                return True
        return False

    def run(self, max_steps: int = 200000, stdin_data: str = "") -> tuple[str, int, str]:
        self.output = []
        steps = 0
        while steps < max_steps:
            if not self.step():
                return "".join(self.output), steps, "HALTED"
            steps += 1
        return "".join(self.output), steps, "MAX_STEPS"


def run(source: str, max_steps: int = 200000, stdin_data: str = "") -> tuple[str, int, str]:
    try:
        return Jajaja(source).run(max_steps=max_steps, stdin_data=stdin_data)
    except JajajaError as e:
        return "", 0, "SYNTAX_ERROR: %s" % e
