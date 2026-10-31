"""test_pytest_bridge.py — puente pytest -> las suites standalone del repo.

Cada suite corre en su PROPIO proceso, igual que si se lanzara a mano
(`python3 test_xxx.py`). Eso da aislamiento real entre suites: ninguna puede
contaminar el entorno de otra (p. ej. LOLCODE_CMD, que un test negativo
sobreescribe temporalmente) ni dejar estado en modulo compartido.

    python3 -m pytest -q   ->  5 suites + el corpus de conformidad,
                               y sale 0 solo si ninguna falla.

No duplica ninguna verificacion: reutiliza los mismos scripts que se ejecutan
directamente y respeta su codigo de salida (non-zero si algun check fallo).
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent

SUITES = [
    "test_jajaja.py",
    "test_host.py",
    "test_backend_lolcode.py",
    "test_lolcode_emit.py",
    "test_lolcode_native.py",
]


@pytest.mark.parametrize("script", SUITES, ids=[s.removesuffix(".py") for s in SUITES])
def test_suite_runs_isolated(script):
    proc = subprocess.run(
        [sys.executable, str(REPO / script)],
        capture_output=True,
        text=True,
        timeout=900,
        cwd=REPO,
    )
    assert proc.returncode == 0, (
        f"{script}: rc={proc.returncode}\n"
        f"--- stdout ---\n{proc.stdout[-2000:]}\n--- stderr ---\n{proc.stderr[-2000:]}"
    )
    assert proc.stdout.strip(), f"{script}: no imprimio nada"


def test_conformance_corpus_passed():
    proc = subprocess.run(
        [sys.executable, str(REPO / "tools" / "conformance_run.py")],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert proc.returncode == 0, f"rc={proc.returncode}\n{proc.stdout}\n{proc.stderr}"
