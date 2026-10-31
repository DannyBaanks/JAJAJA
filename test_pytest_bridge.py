"""test_pytest_bridge.py — puente pytest -> las suites standalone del repo.

Los tests de JAJAJA son scripts con dos patrones:

  * corren todos sus checks al importarse y publican `passed` / `failed` como
    variables de modulo (test_jajaja, test_host, test_backend_lolcode,
    test_lolcode_emit);
  * o exponen un main() que hay que llamar (test_lolcode_native).

Este puente es lo unico que necesita pytest para ejecutarlos de verdad:

    python3 -m pytest -q   ->  corre las 5 suites + el corpus de conformidad
                               y sale 0 solo si ningun check fallo.

No duplica ninguna verificacion: reutiliza los mismos modulos que se ejecutan
directamente (python3 test_jajaja.py, etc.).
"""

import importlib
import subprocess
import sys

import pytest

# Suites que ejecutan sus checks al importarse.
SUITES_IMPORT_RUN = [
    "test_jajaja",
    "test_host",
    "test_backend_lolcode",
    "test_lolcode_emit",
]

# Suites que exponen main() y solo se ejecutan al invocarla.
SUITES_MAIN_CALL = [
    "test_lolcode_native",
]


@pytest.mark.parametrize("name", SUITES_IMPORT_RUN, ids=SUITES_IMPORT_RUN)
def test_suite_standalone_passed(name):
    mod = importlib.import_module(name)
    assert mod.failed == 0, f"{name}: {mod.failed} checks fallaron"
    assert mod.passed > 0, f"{name}: no ejecuto ningun check"


@pytest.mark.parametrize("name", SUITES_MAIN_CALL, ids=SUITES_MAIN_CALL)
def test_suite_main_returned_zero(name):
    mod = importlib.import_module(name)
    assert mod.main() == 0, f"{name}: main() devolvio distinto de 0"


def test_conformance_corpus_passed():
    proc = subprocess.run(
        [sys.executable, "tools/conformance_run.py"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert proc.returncode == 0, f"rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}"
