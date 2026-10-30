# GOLDEN.md — Declaración de contrato GOLDEN

> Fecha: 2026-09-05. Marco: ISyCo Language Engine Standard v1.0 §1.6.

El **núcleo de JAJAJA v1.0** (semántica §4 de `SPEC.md`, formato §2, estados
§6) se declara **GOLDEN**. Fuera de ese núcleo (host de capabilities, UI IR,
stdlib, port LOLCODE) el estado es el de sus propias evidencias — no heredan
esta etiqueta.

Escala de la norma y dónde está JAJAJA:

```
IDEA -> EXAMPLE -> EXECUTABLE -> DEMONSTRATED -> VERIFIED -> GOLDEN
                                                         ^^^^^^ núcleo
```

## Las 7 condiciones de §1.6 y su respaldo

| # | Condición | Respaldo |
|---|---|---|
| 1 | Semántica congelada | `SPEC.md` v1.0 (FROZEN); política de cambio en §10 |
| 2 | Representación canónica | `.jaja` definido en `SPEC.md` §1-2 (UTF-8, gramática, comentarios, separador, terminación) |
| 3 | Corpus de conformidad pasa | `conformance/` (20 casos, claim por caso): `python tools/conformance_run.py` → 20/20 PASS |
| 4 | Evidencia reproducible | `evidence/golden_v1/` regenerable con `python tools/collect_evidence.py` |
| 5 | Límites conocidos documentados | `SPEC.md` §7 (`max_steps`, memoria, sin timeout); §6 distingue `HALTED`/`MAX_STEPS`/`SYNTAX_ERROR` |
| 6 | Rerun reproduce el comportamiento | el colector corre el corpus dos veces y exige veredictos byte-idénticos: `rerun_identical=true` en `evidence/golden_v1/manifest.json` |
| 7 | Rupturas = cambio de contrato | esta declaración + `CHANGELOG.md` + tests del corpus como referencia |

Además, sobre el principio "el host no hace el trabajo" (§9 de la norma):
`test_engine_does_the_work.py` prueba que el resultado no existe antes de
correr el motor, que aparece solo después, y que el mismo artefacto con inputs
distintos da resultados distintos — sin fallback del host.

## Qué significa esto

Significa: **este comportamiento es parte del contrato y ya no puede cambiar
accidentalmente.** Si mañana el intérprete se reescribe, el corpus debe seguir
pasando byte a byte; si alguien "arregla" un comportamiento del corpus,
está haciendo un cambio de contrato y paga el costo completo: versión nueva,
changelog, evidencia nueva.

No significa que el lenguaje sea perfecto, ni que el motor sea el único
posible, ni que las extensiones estén congeladas.

## Verificación cruzada (VERIFIED, norma §1.5)

ENGINE ≠ VERIFIER: el motor Python (`jajaja_interpreter.py`) tiene un segundo
runtime independiente en LOLCODE (`src/jajaja.lol`, runtime externo `lci`),
con paridad medida: 24/24 en corpus de paridad y 7/7 en los fixtures de
Turing (`evidence/lolcode_port/`, 2026-09-03/04). Esa evidencia es histórica
válida; hoy esta máquina no tiene `lci` instalado y los pasos de paridad del
colector se registran como `SKIPPED`, no como PASS simulado.
