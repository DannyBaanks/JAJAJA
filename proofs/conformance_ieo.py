"""Conformance: the IEO JavaScript port vs the JAJAJA reference interpreter.

The browser interpreter contributed to Interpret Esolangs Online is a port,
not a reimplementation. This runs both engines over the same corpus and fails
on any divergence in output, step count, termination status or error text.

The Python side is the oracle. Nothing here hardcodes an expected value: every
expectation is whatever `jajaja_interpreter.run()` produces.

Run:
    python proofs/conformance_ieo.py \
        --js "../Interpret-Esolangs-Online/jajaja.js"

Requires Node.js on PATH. Exit code 0 means the port is faithful.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(REPO))

from jajaja_interpreter import run as reference_run  # noqa: E402

# Cases the spec, the proofs and the reference test-suite already exercise,
# plus the rule-ordering and edge behaviour the port could plausibly get wrong.
INLINE_CASES: list[tuple[str, str]] = [
    ("minimal: single emitting rule", "jajaja::=~X\n::=\njajaja\n"),
    ("no rule matches: immediate halt", "jaja::=~X\n::=\nnope\n"),
    ("empty base after separator", "jaja::=~X\n::=\n"),
    ("basic rewrite, no output", "Hola::=mundo\n::=\nHola\n"),
    ("rewrite then emit", "jaja::=jajaja\njajaja::=~TRES\n::=\njaja\n"),
    # Rule order is semantic: the first *listed* applicable rule wins, not the
    # longest or leftmost match across rules.
    ("rule priority: first listed wins", "ja::=~A\njaja::=~B\n::=\njaja\n"),
    ("rule priority: reversed order flips result", "jaja::=~B\nja::=~A\n::=\njaja\n"),
    ("leftmost occurrence within base", "ja::=~L\n::=\nXjaYja\n"),
    ("repetition until exhausted", "ja::=~.\n::=\njajajajaja\n"),
    ("bare tilde emits newline", "ja::=~\n::=\njaja\n"),
    ("emitting rule deletes its match", "ja::=~E\n::=\naajabb\n"),
    ("empty lhs rule is skipped", "::=~SKIP\nja::=~OK\n::=\nja\n"),
    # Parser edge cases that differ between rule position and base position.
    ("comment in rule position", "# c\nja::=~OK\n::=\nja\n"),
    ("indented comment is a syntax error in rule position", "  # c\nja::=~OK\n::=\nja\n"),
    ("blank lines skipped before base", "ja::=~OK\n::=\n\n\nja\n"),
    ("comment skipped before base", "ja::=~OK\n::=\n# not the base\nja\n"),
    ("separator tolerates trailing whitespace", "jajaja::=~X\n::=   \njajaja j\n"),
    ("rule without ::= is a syntax error", "jaja no es regla\n::=\njaja\n"),
    ("::~ is a syntax error, not an emit", "ja::~X\n::=\nja\n"),
    ("first ::= splits, later ones are rhs", "a::=b::=c\n::=\na\n"),
    ("whitespace in lhs and rhs is significant", "ja ::= X \n::=\nja \n"),
    ("CRLF source parses like LF", "ja::=~OK\r\n::=\r\nja\r\n"),
    ("lines after the base are ignored", "ja::=~OK\n::=\nja\nIGNORED\n"),
    ("non-terminating program hits the budget", "ja::=jaja\n::=\nja\n"),
]

JS_DRIVER = """
const path = process.argv[2];
const cases = JSON.parse(require('fs').readFileSync(process.argv[3], 'utf8'));
const mod = require(path);
const out = cases.map(function (c) {
  try {
    const r = mod.jajajaCore(c.source, c.maxSteps);
    return { output: r.output, steps: r.steps, status: r.status };
  } catch (e) {
    return { error: String(e && e.message) };
  }
});
process.stdout.write(JSON.stringify(out));
"""


# Both engines are given the same budget, which is what conformance requires;
# the value only has to exceed what the terminating programs need. Every
# terminating example here halts in single-digit steps, while grow.jaja and
# simple_counter.jaja grow their base every step and cost O(n^2) to run out --
# at the reference default of 200000 this suite takes minutes to prove nothing
# extra.
DEFAULT_BUDGET = 20000


def load_corpus() -> list[dict]:
    cases: list[dict] = []
    for name, source in INLINE_CASES:
        cases.append({"name": name, "source": source, "maxSteps": DEFAULT_BUDGET})

    for jaja in sorted((REPO / "examples").glob("*.jaja")):
        cases.append({
            "name": f"example: {jaja.name}",
            "source": jaja.read_text(encoding="utf-8"),
            "maxSteps": DEFAULT_BUDGET,
        })

    bootstrap = REPO / "bootstrap.jaja"
    if bootstrap.is_file():
        cases.append({
            "name": "bootstrap.jaja (canonical signature)",
            "source": bootstrap.read_text(encoding="utf-8"),
            "maxSteps": DEFAULT_BUDGET,
        })
    return cases


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--js", required=True, help="path to jajaja.js")
    args = parser.parse_args()

    js_path = Path(args.js).resolve()
    if not js_path.is_file():
        print(f"interpreter not found: {js_path}")
        return 2

    cases = load_corpus()

    tmp_cases = HERE / "_conformance_cases.json"
    tmp_driver = HERE / "_conformance_driver.js"
    try:
        tmp_cases.write_text(json.dumps(cases), encoding="utf-8")
        tmp_driver.write_text(JS_DRIVER, encoding="utf-8")
        proc = subprocess.run(
            ["node", str(tmp_driver), str(js_path), str(tmp_cases)],
            capture_output=True, text=True,
            # Node writes UTF-8; without this, Python decodes it with the
            # console codepage (cp1252 on Windows) and a program emitting
            # "¡Hola, mundo!" fails conformance against itself.
            encoding="utf-8",
        )
        if proc.returncode != 0:
            print("node failed:\n" + proc.stderr)
            return 2
        js_results = json.loads(proc.stdout)
    finally:
        for tmp in (tmp_cases, tmp_driver):
            if tmp.exists():
                tmp.unlink()

    passed = failed = 0
    for case, js in zip(cases, js_results):
        text, steps, status = reference_run(case["source"], max_steps=case["maxSteps"])
        want = {"output": text, "steps": steps, "status": status}

        if "error" in js:
            print(f"FAIL {case['name']}\n     js threw: {js['error']}\n     want: {want}")
            failed += 1
            continue

        if js == want:
            print(f"OK   {case['name']}")
            passed += 1
        else:
            print(f"FAIL {case['name']}")
            for key in ("output", "steps", "status"):
                if js[key] != want[key]:
                    print(f"     {key}: js={js[key]!r} reference={want[key]!r}")
            failed += 1

    print(f"\npassed={passed} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
