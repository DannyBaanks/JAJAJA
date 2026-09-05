# ZERO PYTHON — inventario inicial (M5.1)

Clasificación de los 26 `.py` tracked del repo (bytes on disk, 2026-09-04).
Clases:
- A: semántica activa (si se va, el repo deja de funcionar)
- B: oracle/reference (debe seguir existiendo como evidencia o apagarse)
- C: test harness (todos los que verifican cosas)
- D: generador/compiler (produce artefactos)
- E: host/adapter (transporte vs JAJAJA real)
- F: demo
- G: tooling/build
- H: evidencia histórica/obsoleto

| bytes | archivo | clase | nota |
|---:|---|---|---|
| 11,272 | test_jajaja.py | C | 49 aserciones, herma del runtime Python |
| 8,698 | proofs/tm_to_jajaja.py | D/B | generador, vive como ORÁCULO |
| 8,196 | host.py | E | transporte entre JAJAJA y capacidades del host |
| 8,075 | proofs/ja_encoding.py | D/B | generador, vive como ORÁCULO |
| 7,383 | test_host.py | C | 51 aserciones del host |
| 7,172 | jajaja_stdlib.py | A | cómputos de la librería estándar (matemáticas, strings) |
| 6,638 | proofs/conformance_ieo.py | C/B | conformidad IEO |
| 6,599 | tools/parity_check.py | C | 24 casos, oráculo |
| 6,425 | test_backend_lolcode.py | C | 30 aserciones del backend |
| 6,250 | jajaja_interpreter.py | A | runtime Python de referencia |
| 5,842 | tools/run_jajaja_lol.py | C | transporte a lci; lógica de framing + timeouts |
| 4,904 | test_lolcode_emit.py | C | 22 aserciones del emitter |
| 4,388 | backends/lolcode/emit.py | A | genera .lol desde instrucciones abstractas |
| 3,938 | backends/lolcode/adapter.py | E | front-end para ejecutar .jaja vía lci |
| 3,762 | ui_ir.py | F/B | IR de UI no-gui; no entra en runtime |
| 3,132 | tools/build_lol.py | G | ← ENSAMBLA src/jajaja.lol (necesario) |
| 2,805 | tools/compare_tm_compile.py | C | nuevo en M3 |
| 2,654 | demo_lolcode.py | F | demo backend con programs .lol |
| 2,360 | tools/compare_ja_compile.py | C | nuevo en M4 |
| 2,354 | tools/turing_parity_lol.py | C | 7 casos Turing |
| 2,008 | test_lolcode_native.py | C | 4 aserciones + invoca suite .lol |
| 2,008 | evidence/lolcode_flip/collect_stats.py | G | medidor |
| 1,860 | tools/compare_ja_run.py | C | corre el .jaja en ambos motores |
| 693 | check_bootstrap.py | C | smoke test canónico |
| 473 | run_examples.py | F | loop por examples/*.jaja |
| 0 | backends/__init__.py | A | vacío |
| 0 | backends/lolcode/__init__.py | A | vacío |

## Decisión por pieza

| pieza | acción | por qué |
|---|---|---|
| jajaja_interpreter.py | CONSERVAR COMO ORÁCULO + re-generar fixtures; ya es .py<0.1% del repo des-historial=0 |
| jajaja_stdlib.py | PORTAR. Es semántica activa (objetos, matemáticas, acceso a propiedades). Toca `src/parts/60_stdlib.lol` |
| host.py | PORTAR a LOLCODE si las capacidades son expresables; stdin/stdout se apoya en el runtime |
| ui_ir.py + demo_lolcode.py | MANTENER como UI-abstracta con evidencia, PYTHON-based (sin related code): reducir a herramienta de documentación |
| proofs/tm_to_jajaja.py | MANTENER COMO ORÁCULO: "TM válido" se compara contra esto |
| proofs/ja_encoding.py | MANTENER COMO ORÁCULO |
| proofs/conformance_ieo.py | MANTENER COMO ORÁCULO |
| tools/build_lol.py | REEMPLAZAR por `build.ps1`/`build.sh` sin Python |
| tools/run_jajaja_lol.py | REEMPLAZAR por `run.ps1`/`run.sh` (ya es sólo transporte, sin lógica calculadora) |
| tools/parity_check.py, turing_parity_lol.py, compare_*.py | RETIRAR como requerimiento; la paridad ya fue DEMOSTRADA y puede reproducirse re-invocándolos con despliegue manual del runtime |
| test_*.py | PORTAR a tests/runtime_tests.lol (aumentar cobertura) |
| backends/lolcode/emit.py, adapter.py | REEMPLAZAR por LOLCODE que cubra el emisor y por la llamada nativa lci |
| run_examples.py, demo_lolcode.py, check_bootstrap.py, collect_stats.py | RETIRAR de la superficie activa; son frágiles a PYTHON anyway |
| backends/{__init__}.py (2 vacíos) | BORRAR (ninguno tiene semántica; un `__init__` vacío sólo existe por convención Python) |
| test_lolcode_native.py | REEMPLAZAR por un comando directo que corra lci sobre tests (sin wrapper) |

## Meta

El retenido Python final:
- **ninguno activo** (no hay código que el usuario necesite para `run`)
- **oráculos preservados** sólo como referencias para auditar qué se copió

## Riesgo identificado

`tools/build_lol.py` y `tools/run_jajaja_lol.py` son los dos archivos cuya
remoción NO se puede postergar; ambos entran en el pipeline diario. Kyle hay
que cubrirlos primero.
