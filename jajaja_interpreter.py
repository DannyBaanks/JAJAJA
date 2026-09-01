r"""Jajaja interpreter (rewriting system over the laugh alphabet).

Jajaja es un esolang mexicano basado en Markov normal algorithm.
La idea: el alfabeto semantico son repeticiones del token "ja".

    "ja"     = 1 risa        (token unidad)
    "jaja"   = 2 risas
    "jajaja" = 3 risas
    ... y asi. La "longevidad" de la risa (conteo de `ja`s) forma cada
    "palabra" del programa.

State model (JajajaMachineState):
    rules       :: list[(lhs, rhs)]    reglas lhs ::= rhs
    base        :: str                 cinta de reescritura
    output      :: list[str]           emisiones recogidas
    steps       :: int                 pasos ejecutados
    status      :: str                 RUNNING | HALTED | MAX_STEPS
    trace_log   :: list[dict] | None   snapshots opcionales

Step:
    En cada paso recorremos las reglas en orden. La PRIMERA regla cuyo lhs
    aparece en base se aplica en su primera ocurrencia (leftmost).
    - Si rhs comienza con `~`, el resto del rhs se emite como texto y se
      quita el match de base. `::~` solo (rhs="~") emite newline.
    - Si rhs no comienza con `~`, se reemplaza el match lhs por rhs en base.
    Si ninguna regla matchea -> HALT.

    S_n+1 = step(S_n):
      for (lhs, rhs) in rules:
        if lhs == "": continue
        idx = base.find(lhs)
        if idx >= 0:
          if rhs starts with "~":
            output += [tail or "\n"]
            base = base[:idx] + base[idx+len(lhs):]
          else:
            base = base[:idx] + rhs + base[idx+len(lhs):]
          steps += 1
          record trace if enabled
          return True
      status = HALTED
      return False

Input:
    stdin_data se inyecta como prefijo delimitado de la base.
    La misma imagen SHA256 del .jaja + diferentes inputs = diferentes resultados.
    COMPILE_ONCE_TEST_MANY: las reglas JAJAJA procesan el input directamente.

Output:
    Texto emitido via reglas `::~...`.

Source format (identico a Thue):

    # comentarios opcionales
    <lhs1>::=<rhs1>
    <lhs2>::=<rhs2>
    ...
    ::=
    <base inicial>

Trace invariant:
    run(trace=False) produces identical (output, steps, status)
    as run(trace=True). The trace log is a side-channel only.
"""
from __future__ import annotations

from dataclasses import dataclass, field


class JajajaError(Exception):
    pass


@dataclass
class StateSnapshot:
    """Captura completa del estado en un instante dado."""
    step: int
    base: str
    output: list[str]
    status: str


class Jajaja:
    """Motor de reescritura Markov para JAJAJA.

    Invariante: step() no cambia output si status != RUNNING.
    Trace invariante: trace_disabled output == trace_enabled output.
    """

    def __init__(self, source: str, *, trace: bool = False):
        self.rules: list[tuple[str, str]] = []
        self.base = ""
        self.output: list[str] = []
        self.steps = 0
        self.status = "RUNNING"
        self._trace_enabled = trace
        self._trace_log: list[StateSnapshot] = [] if trace else []
        self._parse(source)

    def _snapshot(self) -> StateSnapshot:
        return StateSnapshot(
            step=self.steps,
            base=self.base,
            output=list(self.output),
            status=self.status,
        )

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
                if ln.strip() == "" or ln.strip().startswith("#"):
                    continue
                self.base = ln
                break

    def step(self) -> bool:
        """Aplica un paso de reescritura. Retorna True si se aplicó, False si HALT."""
        if self.status != "RUNNING":
            return False
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
                self.steps += 1
                if self._trace_enabled:
                    self._trace_log.append(self._snapshot())
                return True
        self.status = "HALTED"
        return False

    def run(self, max_steps: int = 200000, stdin_data: str = "") -> tuple[str, int, str]:
        """Ejecuta el programa. stdin_data se inyecta como prefijo de la base.

        COMPILE_ONCE_TEST_MANY: la misma fuente + diferentes inputs = diferentes
        resultados, porque las reglas JAJAJA procesan el input directamente.
        """
        self.output = []
        self.steps = 0
        self.status = "RUNNING"
        if stdin_data:
            self.base = stdin_data + " " + self.base
        if self._trace_enabled:
            self._trace_log.append(self._snapshot())
        while self.steps < max_steps:
            if not self.step():
                break
        if self.status == "RUNNING":
            self.status = "MAX_STEPS"
        return "".join(self.output), self.steps, self.status

    @property
    def trace(self) -> list[StateSnapshot]:
        """Log de snapshots (solo si trace=True en constructor)."""
        return list(self._trace_log)


def run(source: str, max_steps: int = 200000, stdin_data: str = "") -> tuple[str, int, str]:
    """Funcion wrapper con manejo de errores de sintaxis."""
    try:
        return Jajaja(source).run(max_steps=max_steps, stdin_data=stdin_data)
    except JajajaError as e:
        return "", 0, "SYNTAX_ERROR: %s" % e
