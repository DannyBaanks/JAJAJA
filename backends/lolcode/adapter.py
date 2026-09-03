"""backends/lolcode/adapter.py — LOLCODE backend adapter.

Boundary contract:

- Python in this file TRANSPORTS ONLY. It never computes `sum`, never
  compares, never branches, never loops. All computation happens inside
  an external LOLCODE runtime executing a real `.lol` program.
- The JAJAJA host decides WHICH op to request (the rule that fires).
  This adapter receives `op` plus the raw operand text left in the
  JAJAJA base, feeds operands to the LOLCODE program via its stdin,
  and returns the program's stdout as the RESULT payload.

Runtime resolution (external, required):

- `LOLCODE_CMD` env var (absolute path to a working `lci`), else
- `lci` / `lci.exe` found on PATH.

If none is available we raise LolcodeRuntimeNotFound. There is NO
silent fallback to Python: without an external LOLCODE runtime, the
backend fails loudly.

Reference runtime used during development: `lci` v1.3 (GPL-3.0),
https://github.com/justinmeza/lci — see backends/lolcode/README.md.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROGRAMS_DIR = HERE / "programs"

# op -> canonical .lol program. These are real LOLCODE 1.3 sources that
# consume operands from stdin (GIMMEH) and compute with LOLCODE
# semantics (SUM OF / BIGGR OF / O RLY? / IM IN YR).
PROGRAMS = {
    "sum":   "sum.lol",
    "max":   "max.lol",
    "echo":  "echo.lol",
    "count": "count.lol",
}


class LolcodeRuntimeNotFound(RuntimeError):
    """No external LOLCODE runtime available. Fails LOUDLY."""


class LolcodeExecutionError(RuntimeError):
    """The external runtime failed to execute the program."""


def resolve_runtime() -> str:
    """Return the path of an external LOLCODE runtime, or raise."""
    env = os.environ.get("LOLCODE_CMD", "").strip()
    if env:
        if Path(env).exists():
            return env
        raise LolcodeRuntimeNotFound(
            f"LOLCODE_CMD points to a missing file: {env!r}. "
            "Install lci (see backends/lolcode/README.md) or fix the env var."
        )
    found = shutil.which("lci") or shutil.which("lci.exe")
    if found:
        return found
    raise LolcodeRuntimeNotFound(
        "no external LOLCODE runtime found on PATH (looked for: lci). "
        "Install lci (see backends/lolcode/README.md) or set LOLCODE_CMD."
    )


def run(op: str, operands: str, timeout: float = 10.0) -> dict:
    """Execute a backend op.

    op:       operation selected by the JAJAJA program ("sum", "max", ...).
    operands: raw operand text from the JAJAJA base ("2 3", "hola").

    Returns {"op", "program", "runtime", "stdout", "exit_code"}.
    Raises LolcodeRuntimeNotFound / LolcodeExecutionError.
    """
    if op not in PROGRAMS:
        raise LolcodeExecutionError(f"unknown op {op!r}; known: {sorted(PROGRAMS)}")

    runtime = resolve_runtime()
    program = PROGRAMS_DIR / PROGRAMS[op]
    if not program.exists():
        raise LolcodeExecutionError(f"missing LOLCODE program: {program}")

    # Operands travel as stdin lines to the LOLCODE program (GIMMEH).
    # Splitting text into lines is transport, not semantics: GIMMEH and
    # LOLCODE's own casting (YARN -> NUMBR) do the parsing.
    stdin_data = "\n".join(operands.split()) + "\n" if operands else ""
    if op == "echo":
        # echo is string semantics: the whole operand text is one value.
        stdin_data = operands.strip() + "\n"

    proc = subprocess.run(
        [runtime, str(program)],
        input=stdin_data,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise LolcodeExecutionError(
            f"runtime exited {proc.returncode}: {proc.stderr.strip()[:300]}"
        )
    return {
        "op": op,
        "program": program.name,
        "runtime": runtime,
        "stdout": proc.stdout,
        "exit_code": proc.returncode,
    }
