# lolcode_flip — antes vs después

Medición sobre archivos **tracked** (no incluye `.pyc` ni basura de git):

## Antes (commit 7454aa7 demo backend, antes de M1-M4)

| ext | files | bytes |
|---|---|---|
| .py | 25 | 105,716 | (47.3%) |
| .md | 16 | 64,084 | (28.7%) |
| **.lol** | **4** | **13,821** | (6.2%) |
| .json | 4 | 15,834 | (7.1%) |
| .jaja | 19 | 7,062 | (3.2%) |
| resto | 6 | 16,956 | (7.6%) |

## Después (M1-M4 completos)

| ext | files | bytes |
|---|---|---|
| .py | 26 | 117,881 | (42.6%) |
| .md | 16 | 64,084 | (23.1%) |
| **.lol** | **20** | **56,402** | (20.4%) |
| .json | 4 | 15,838 | (5.7%) |
| .jaja | 19 | 7,062 | (2.5%) |
| resto | 7 | 15,696 | (5.7%) |

Cambios en LOLCODE: +16 archivos, +42,581 bytes (4.3x en bytes, 5x en archivos).

## Cómo interpretar

- Python sigue siendo el más grande (tooling + oráculo). El flip es
  representacional (LOLCODE ya ejecuta especificaciones completas y tiene
  tests nativos corren en lci), no una espectativa de superar a .py en
  bytes. El trabajo real es dialectal: dejar de necesitar Python para
  *generar* y *validar* los artefactos JAJAJA.
- `.lol` pasó de cuarto a tercer lugar; de ~6% a ~20% del repositorio.
- La parte importante: 3 nuevas suites (`test_lolcode_native.py`,
  `compare_tm_compile.py`, `compare_ja_compile.py`) verifican los artefactos
  LOLCODE con oráculo Python, y no sólo meramente existen.

## Comandos de verificación

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/parity_check.py --check-only    # 24/24 MATCH
py tools/turing_parity_lol.py            # 7/7 MATCH
py tools/compare_tm_compile.py           # 3/3 byte-identical
py tools/compare_ja_compile.py           # 2/2 byte-identical (risas)
py tools/compare_ja_run.py               # 2/2 runtime parity, tape correcta
py test_lolcode_native.py                # 4 OK, 0 FAILED (suite LOLCODE)
```
