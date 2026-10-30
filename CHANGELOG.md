# CHANGELOG

## 1.0.0 — 2026-09-05 (GOLDEN)

Primer contrato congelado del **núcleo** del lenguaje.

- `SPEC.md` v1.0 FROZEN: formato `.jaja`, paso de reescritura, estados
  `HALTED` / `MAX_STEPS` / `SYNTAX_ERROR`, input como prefijo de base,
  límites, traza observable.
- Corpus de conformidad declarativo `conformance/` (20 casos, un claim por
  caso) + runner `tools/conformance_run.py`.
- Prueba adversarial §9: `test_engine_does_the_work.py`.
- Evidencia canonical regenerable: `tools/collect_evidence.py` →
  `evidence/golden_v1/` (doble pasada del corpus, byte-idéntica).
- `GOLDEN.md` declara el núcleo GOLDEN; host/UI/stdlib/LOLCODE son
  extensiones con su propio estado.

Historia previa (pre-contrato, orden cronológico de git): bootstrap del
intérprete, ejemplos, prueba de Turing ejecutable (`proofs/`), host de
capabilities, port a LOLCODE con paridad 24/24 y generadores TM→JAJAJA en
LOLCODE. Ver `CURRENT_STATE.md`.
