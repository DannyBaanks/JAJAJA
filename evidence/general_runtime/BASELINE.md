# BASELINE.md — Fase 0 snapshot

## Date: 2026-09-01

## Interpreter
- `jajaja_interpreter.py` — 128 lines, Markov normal algorithm
- State: rules[], base, output[], steps, status, trace
- Deterministic: first-rule, leftmost-match, halt-when-none

## Tests
- `test_jajaja.py`: 49 tests (27 original + 22 new for Fase 1-2)
- `test_host.py`: 51 tests (data model, host ABI, calculator, UI IR, FS sandbox)
- Proofs: 7/7 MTs, ja_encoding OK
- Bootstrap: JAJAJA-OK, steps=2

## Bug Fixed
- `stdin_data` was accepted but ignored → NOW injects into base as prefix
- COMPILE_ONCE_TEST_MANY: same SHA256, different inputs → different outputs

## New Capabilities
- Formal machine state with trace (optional,不影响output)
- Runtime input injection
- Host ABI (EFFECT/RESULT protocol)
- host.py with capability allowlist
- Data model (unary, decimal, list, record)
- UI IR (declarative, renders to HTML/terminal)
- Filesystem sandbox with path traversal prevention

## Test Counts
- Total: 100 tests, 0 failures
- Original: 49/49 pass
- Host: 51/51 pass
- Proofs: 7/7 + ja_encoding OK
