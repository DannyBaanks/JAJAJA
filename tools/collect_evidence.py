"""collect_evidence.py — recolector canonico de evidencia de JAJAJA.

Ejecuta los comandos de verificacion del repo, guarda salidas crudas,
corre el corpus de conformidad DOS veces y compara (reproducibilidad),
y emite:

    evidence/golden_v1/
    ├── manifest.json            # registro §6: comandos, entorno, verdicts
    ├── runs/                    # salida cruda por comando (stdout+stderr+exit)
    │   ├── conformance_report_a.json
    │   └── conformance_report_b.json   # segunda pasada (debe decidir igual)
    └── hashes.json              # sha256 de artefactos del contrato

Si falta el runtime externo de LOLCODE (lci), los pasos de paridad se registran
como SKIPPED con razon — no se simulan ni se omiten a escondidas.

Uso:  python tools/collect_evidence.py
Exit code: 0 si todo PASS (los SKIPPED por falta de lci no cuentan como fallo).
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "evidence" / "golden_v1"
RUNS = OUT / "runs"

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

PY = sys.executable


COMMANDS = [
    ("check_bootstrap", [PY, str(ROOT / "check_bootstrap.py")]),
    ("test_jajaja", [PY, str(ROOT / "test_jajaja.py")]),
    ("test_host", [PY, str(ROOT / "test_host.py")]),
    ("test_engine_does_the_work", [PY, str(ROOT / "test_engine_does_the_work.py")]),
    ("test_backend_lolcode", [PY, str(ROOT / "test_backend_lolcode.py")]),
    ("run_examples", [PY, str(ROOT / "run_examples.py")]),
    ("proof_tm", [PY, str(ROOT / "proofs" / "tm_to_jajaja.py")]),
    ("proof_ja_encoding", [PY, str(ROOT / "proofs" / "ja_encoding.py")]),
]

# Comandos que requieren lci (runtime LOLCODE externo)
LOLCODE_COMMANDS = [
    ("parity_check_lolcode", [PY, str(ROOT / "tools" / "parity_check.py"), "--check-only"]),
    ("turing_parity_lolcode", [PY, str(ROOT / "tools" / "turing_parity_lol.py")]),
    ("test_lolcode_native", [PY, str(ROOT / "test_lolcode_native.py")]),
]


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(name: str, cmd: list[str]) -> dict:
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    raw = {
        "command": " ".join(os.fspath(c) for c in cmd),
        "stdout": p.stdout,
        "stderr": p.stderr,
        "exit_code": p.returncode,
    }
    (RUNS / f"{name}.txt").write_text(
        "command: %s\nexit_code: %s\n--- stdout ---\n%s\n--- stderr ---\n%s\n"
        % (raw["command"], raw["exit_code"], raw["stdout"], raw["stderr"]),
        encoding="utf-8",
    )
    return {"name": name, "exit_code": p.returncode, "status": "PASS" if p.returncode == 0 else "FAIL"}


def conformance_report(dest: Path) -> dict:
    p = subprocess.run(
        [PY, str(ROOT / "tools" / "conformance_run.py"), "--report", str(dest)],
        capture_output=True, text=True, cwd=ROOT,
    )
    return {"exit_code": p.returncode, "stdout": p.stdout[-400:], "dest": str(dest)}


def main() -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    started = datetime.now(timezone.utc).isoformat()

    runs = [run_command(name, cmd) for name, cmd in COMMANDS]

    # Corpus de conformidad: DOS pasadas; el veredicto por caso debe ser identico.
    rep_a = RUNS / "conformance_report_a.json"
    rep_b = RUNS / "conformance_report_b.json"
    ra = conformance_report(rep_a)
    rb = conformance_report(rep_b)
    (RUNS / "conformance_console.txt").write_text(
        "--- run A (cola) ---\n%s\n--- run B (cola) ---\n%s\n" % (ra["stdout"], rb["stdout"]),
        encoding="utf-8",
    )
    ja = json.loads(rep_a.read_text(encoding="utf-8"))
    jb = json.loads(rep_b.read_text(encoding="utf-8"))
    repeat_ok = (ja["cases"] == jb["cases"]) and (ja["totals"] == jb["totals"])
    runs.append({
        "name": "conformance_corpus",
        "exit_code": ra["exit_code"],
        "status": "PASS" if ra["exit_code"] == 0 else "FAIL",
    })
    runs.append({
        "name": "conformance_rerun_identical",
        "exit_code": 0 if repeat_ok else 1,
        "status": "PASS" if repeat_ok else "FAIL",
    })

    # Parte LOLCODE: solo si existe un runtime externo; si no, SKIPPED explicito.
    lci = os.environ.get("LOLCODE_CMD") or shutil.which("lci")
    lolcode_note = None
    if lci:
        runs.extend(run_command(name, cmd) for name, cmd in LOLCODE_COMMANDS)
    else:
        lolcode_note = (
            "no external LOLCODE runtime (lci not on PATH, LOLCODE_CMD unset): "
            "parity/native runs SKIPPED en esta maquina. La evidencia historica "
            "2026-09-03/04 en evidence/lolcode_port y evidence/lolcode_backend "
            "sigue siendo valida historicamente."
        )
        for name, _ in LOLCODE_COMMANDS:
            runs.append({"name": name, "exit_code": None, "status": "SKIPPED", "reason": "lci absent"})

    artifacts = [
        "jajaja_interpreter.py",
        "SPEC.md",
        "conformance/cases.json",
        "tools/conformance_run.py",
        "test_engine_does_the_work.py",
        "check_bootstrap.py",
        "bootstrap.jaja",
        str(Path("runs/conformance_report_a.json")),
        str(Path("runs/conformance_report_b.json")),
    ]
    for f in sorted((ROOT / "conformance" / "cases").glob("*.jaja")):
        artifacts.append(str(f.relative_to(ROOT)))

    hashes = {}
    missing = []
    for rel in artifacts:
        rel = str(rel).replace("\\", "/")
        p = OUT / rel if rel.startswith("runs/") else ROOT / rel
        if p.exists():
            hashes[rel] = sha256_path(p)
        else:
            missing.append(rel)

    overall_fail = [r for r in runs if r["status"] == "FAIL"]
    manifest = {
        "pack": "jajaja-golden-evidence/1",
        "spec_version": "1.0",
        "collected_utc": started,
        "environment": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "cwd": str(ROOT),
        },
        "runs": runs,
        "conformance": {
            "totals": ja["totals"],
            "verdict": ja["verdict"],
            "rerun_identical": repeat_ok,
        },
        "lolcode_note": lolcode_note,
        "missing_artifacts": missing,
        "verdict": "PASS" if not overall_fail and repeat_ok else "FAIL",
    }

    (OUT / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    (OUT / "hashes.json").write_text(
        json.dumps({k: v for k, v in sorted(hashes.items())}, indent=2) + "\n",
        encoding="utf-8",
    )

    print("== evidence pack evidence/golden_v1 ==")
    for r in runs:
        extra = " (%s)" % r.get("reason", "") if r["status"] == "SKIPPED" else ""
        print("%-7s %s%s" % (r["status"], r["name"], extra))
    print("conformance: %s (rerun_identical=%s)" % (ja["verdict"], repeat_ok))
    print("verdict: %s" % manifest["verdict"])
    if missing:
        print("MISSING artifacts: %s" % ", ".join(missing))
    return 0 if manifest["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
