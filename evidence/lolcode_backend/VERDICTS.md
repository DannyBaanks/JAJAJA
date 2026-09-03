# VERDICTS — demo JAJAJA -> LOLCODE (2026-09-03)

Evidencia asociada: `TRANSCRIPT.txt` (salida cruda, capturada completa),
`LINGUIST_AUDIT.md`, `RUNTIME.md`, `hashes.json`. Python 3.12.4,
lci v1.3 externo (ver RUNTIME.md).

| Verdict | Estado | Evidencia |
|---|---|---|
| JAJAJA_IN_EXECUTION_PATH | DEMONSTRATED | receipts existen solo si `route.jaja` reescribió (`steps>=2`); input `DIV 1 2` no genera efecto ni llamada al backend (TRANSCRIPT, control negativo) |
| LOLCODE_CODE_SELECTION | DEMONSTRATED | la regla que matchea decide el op (`ADD`→sum.lol, `MAX`→max.lol...); host solo despacha lo que JAJAJA pidió |
| LOLCODE_BACKEND_EXECUTION | DEMONSTRATED | proceso externo `lci.exe` ejecuta programs/*.lol; TRANSCRIPT muestra stdout del runtime |
| BACKEND_COMPUTES_SEMANTICS | DEMONSTRATED | `ADD 17 25` -> `42` (input nunca usado en development), MAX ambos lados del branch, COUNT loop 3→0; outputs vienen de `VISIBLE` de lci |
| PYTHON_FRONTEND_ONLY | DEMONSTRATED | Python: parsea argv, lee archivos, lanza el proceso, imprime; ninguna suma/comparación/loop en Python |
| NO_PYTHON_SEMANTIC_FALLBACK | DEMONSTRATED | con runtime ausente: `LolcodeRuntimeNotFound`, receipt != OK, payload distinto de `5`, demo exit=1 (TRANSCRIPT) |
| CAPABILITY_GATE | DEMONSTRATED | `lolcode` fuera del allowlist → DENY (test) |
| PRIVATE_ENGINE_NOT_EXPOSED | DEMONSTRATED | grep: 0 referencias a rutas/módulos privados del workspace (ver siguiente sección) |
| PUBLIC_PRIVATE_DEPENDENCY | **NO** (respuesta deseada) | `py test_backend_lolcode.py` corre solo con este repo + runtime externo |
| END_TO_END_JAJAJA_TO_LOLCODE | DEMONSTRATED | TRANSCRIPT: ADD/MAX/ECHO/COUNT end-to-end |
| LOLCODE_IN_LINGUIST_CATALOG | DEMONSTRATED | LINGUIST_AUDIT.md §1 |
| LINGUIST_ABSOLUTE_LEAST_USED | NOT_DEMONSTRATED | LINGUIST_AUDIT.md §3 — no existe ranking oficial; Befunge midió menos en nuestra shortlist |

## Privacy grep (público no depende de nada privado)

Comando (PowerShell, raíz del repo JAJAJA, excluyendo .git y evidence de
documentación):

```powershell
git grep -I -n -i -E "workspace[\\/]assembly|ISyCo\\\\workspace|security_sentinel|security_authority|bootstrap_runtime|C:\\\\Development\\\\ISyCo[^ ]"
```

Resultado: 0 coincidencias en código (este propio VERDICTS.md describe el
comando; `demo_lolcode.py`/`adapter.py`/`route.jaja`/tests: 0 matches).

### Limitaciones conocidas

- Operandos: enteros no negativos (LOLCODE GIMMEH lee YARN; los programas
  .lol castean vía operaciones LOLCODE).
- El conteo `extension:` de GitHub Search no es un censo: Search no indexa
  todo el código público. Es una aproximación consistente, no un ranking.
