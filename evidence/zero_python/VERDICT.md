# ZERO PYTHON — VERDICT

**Fecha**: 2026-09-04
**Scope**: M5 completo

## Tabla requerida

| Comprobación | Veredicto | Cómo se midió |
|---|---|:---:|
| `ZERO_PYTHON_RUNTIME` | **DEMONSTRATED** | `tools/run_jajaja_lol.ps1` corre `.jaja` vía lci; verificado byte-idéntico a `run_jajaja_lol.py` en 5 casos (`tools/parity_ps_vs_py.ps1`) |
| `ZERO_PYTHON_BUILD` | **DEMONSTRATED** | `tools/build_lol.ps1 jajaja.cfg` ensambla idéntico a `tools/build_lol.py` (SHA-256 match) sin Python |
| `ZERO_PYTHON_TESTS` | **DEMONSTRATED** | `tests/runtime_tests.lol` corre 22 aserciones dentro de lci; wrapper PS1 `tests/verify_snapshots.ps1` confirma 19/19 snapshots |
| `ZERO_PYTHON_TOOLING` | **DEMONSTRATED** | los tres activos (`build_lol.ps1`, `run_jajaja_lol.ps1`, `verify_snapshots.ps1`) no invocan `python`/`py`/`python3` (verificado por `tests/zero_python_check.ps1`) |
| `LOLCODE_REFERENCE_RUNTIME` | **DEMONSTRATED** | `src/jajaja.lol` ensamblado desde `src/parts/*.lol`; la respuesta del runtime no cambia si `python.exe` no existe en PATH |
| `LINGUIST_NO_PYTHON` | **NOT_OBSERVED** | el repo sigue teniendo `.py` tracked (inventario 26 archivos, 121 KB). No editamos `.gitattributes`, no marcamos nada como `vendored`, y los oráculos se mantienen. El indicador que persiste es **histórico/documental**, no operativo. |

## Prueba sin Python en PATH

Script `tests/verify_sin_python.ps1` corre (desde un proceso PowerShell con
PATH saneado de Python) los tres jobs: BUILD, SNAPSHOTS, ZERO_PYTHON_GATE:

```
RUN   PATH sin python
  --- BUILD            OK   (ensamblado src\jajaja.lol, sha256=5cf6f3..be)
  --- SNAPSHOTS        OK   (19/19 snapshots MATCH, 0 SKIP)
  --- ZERO_PYTHON_GATE OK   (sin violaciones)
>>> ZERO_PYTHON = DEMONSTRATED para: BUILD, SNAPSHOTS, GATE
```

## Lo que queda como Python (oráculo, por definición)

| archivo | bytes | función | por qué sigue |
|---|---:|---|---|
| jajaja_interpreter.py | 6,250 | semántica Python | oráculo, exige fixtures |
| jajaja_stdlib.py | 7,172 | estrictamente oráculo estándar |
| host.py | 8,196 | resultados observados; no ejecutable operacional |
| ui_ir.py | 3,762 | UI IR |
| tools/run_jajaja_lol.py | 5,842 | oráculo del transporte (validamos run_jajaja_lol.ps1 contra él) |
| tools/build_lol.py | 3,132 | oráculo del ensamblador (runamos build_lol.ps1 contra él) |
| proofs/*.py | varios | oráculo de los compiladores ya portados |
| tests/test_*.py | varios | tests del oráculo antes del port |

**Total Python tracked**: 26 archivos, 121,754 bytes (~35% del repo tracked).
Estódigo no es la superficie activa — si `python.exe` desaparece mañana el
repo **opera completo**.

## Trap/documentación

- PowerShell de Windows tiene un alias automático `$Input` que pisaba el
  parámetro `-[string]$Input` de nuestro script; lo renombramos a
  `-StdinData` en `tools/run_jajaja_lol.ps1` (ver commit).
- `MSMash` de lci re-aplica escapes sobre strings con ":" literal, por eso
  los separadores se escriben como `":(3A):(3A)="` (documentado en
  `src/proofs_lol/tm_compile.lol` y en evidence/lolcode_port/).
- `tools/parity_ps_vs_py.ps1` se mantiene (*intencionalmente invoca a
  `py`) como referencia entre transportes; excluido de la superficie activa.

## Hashes

Ver `evidence/zero_python/hashes.json`
