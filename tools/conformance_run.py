"""conformance_run.py — corre el corpus de conformidad de JAJAJA.

Para cada caso de conformance/cases.json:

    Engine(programa_i, input_i, max_steps_i) == expected_i

Uso:
    python tools/conformance_run.py                 # corre y reporta en consola
    python tools/conformance_run.py --report out.json  # ademas guarda JSON

Exit code: 0 si todos los casos pasan, 1 si alguno falla.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jajaja_interpreter import run  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_corpus(cases_path: Path) -> list[dict]:
    cases = json.loads(cases_path.read_text(encoding="utf-8"))["cases"]
    results = []
    for case in cases:
        program_path = ROOT / case["program"]
        source = program_path.read_text(encoding="utf-8")
        max_steps = case.get("max_steps", 200000)
        stdin_data = case.get("stdin_data", "")
        output, steps, status = run(source, max_steps=max_steps, stdin_data=stdin_data)

        exp = case["expected"]
        failures = []
        if output != exp.get("output", ""):
            failures.append("output=%r expected=%r" % (output, exp.get("output", "")))
        if "status_prefix" in exp:
            if not status.startswith(exp["status_prefix"]):
                failures.append("status=%r expected prefix=%r" % (status, exp["status_prefix"]))
        elif status != exp.get("status"):
            failures.append("status=%r expected=%r" % (status, exp.get("status")))
        if "steps" in exp and steps != exp["steps"]:
            failures.append("steps=%r expected=%r" % (steps, exp["steps"]))

        results.append({
            "id": case["id"],
            "name": case["name"],
            "claim": case["claim"],
            "program": case["program"],
            "program_sha256": sha256_file(program_path),
            "observed": {"output": output, "steps": steps, "status": status},
            "expected": exp,
            "verdict": "PASS" if not failures else "FAIL",
            "failures": failures,
        })
    return results


def main() -> int:
    ap = argparse.ArgumentParser(description="JAJAJA conformance corpus runner")
    ap.add_argument("--report", default=None, help="ruta opcional para el reporte JSON")
    args = ap.parse_args()

    cases_path = ROOT / "conformance" / "cases.json"
    engine_path = ROOT / "jajaja_interpreter.py"
    results = run_corpus(cases_path)

    passed = sum(1 for r in results if r["verdict"] == "PASS")
    failed = len(results) - passed

    for r in results:
        if r["verdict"] == "PASS":
            print("PASS %-5s %s" % (r["id"], r["name"]))
        else:
            print("FAIL %-5s %s" % (r["id"], r["name"]))
            for f in r["failures"]:
                print("       %s" % f)
    print("conformance: %d passed, %d failed, %d total" % (passed, failed, len(results)))

    if args.report:
        report = {
            "report": "jajaja-conformance-report/1",
            "spec_version": "1.0",
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "environment": {
                "python": sys.version.split()[0],
                "platform": platform.platform(),
            },
            "engine": {
                "file": "jajaja_interpreter.py",
                "sha256": sha256_file(engine_path),
            },
            "corpus": {
                "file": "conformance/cases.json",
                "sha256": sha256_file(cases_path),
            },
            "totals": {"passed": passed, "failed": failed, "total": len(results)},
            "verdict": "PASS" if failed == 0 else "FAIL",
            "cases": results,
        }
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        print("report written: %s" % report_path)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
