# ¿Cómo corro el runtime JAJAJA en LOLCODE?

## El comando que buscas

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/run_jajaja_lol.py bootstrap.jaja
```

Eso es todo. `run_jajaja_lol.py` lee tu `.jaja`, lo empaqueta, llama a lci, y
te devuelve output, steps y status idénticos al intérprete Python.

## La golden rule

Python ya no es la referencia: es *un oráculo más*. Si tienes que elegir entre
lo que dice el intérprete Python y lo que dice `tests/runtime_tests.lol`
corriendo en lci, gana **lci + la suite nativa**.

## Comandos, uno por uno

### 1. Ejecutar cualquier .jaja en lci

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/run_jajaja_lol.py <ruta_a_programa.jaja>
# opcional: py tools/run_jajaja_lol.py <prog.jaja> --input "stdin" --max-steps 500000
```

Salida:

```
output="jaja"
steps=1
status=HALTED
```

También puedes no usar env var si `lci.exe` está en PATH.

### 2. Paridad de la suite de 24 programas (`src/jajaja.lol` vs oráculo)

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/parity_check.py --check-only
```

Debe imprimir:

```
24 cases, 24 identical, 0 mismatches
```

### 3. Paridad Turing (7 fixtures de proofs/tm_to_jajaja.py)

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/turing_parity_lol.py
```

Imprime una línea por caso y un resumen final:

```
7/N cases, 7 identical, 0 mismatches
```

### 4. Tests nativos en lci (sin host Python)

```powershell
py tools/build_lol.py jajaja_tests.cfg      # ensambla tests/runtime_tests.lol
C:\Development\runtimes\lolcode\lci.exe tests\runtime_tests.lol
```

Resultado:

```
====
PASS 22
FAILURES 0
```

### 5. Wrapper Python de ese test (los llama todos)

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py test_lolcode_native.py
```

```
4 OK, 0 FAILED
```

### 6. Compilador TM→JAJAJA (LOLCODE vs Python)

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/compare_tm_compile.py
```

```
3/3 byte-identical
```

### 7. Compilador al alfabeto de risas (`ja` puras)

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/compare_ja_compile.py
```

```
2/2 byte-identical
```

### 8. Ejecución completa del programa de risas

```powershell
$env:LOLCODE_CMD="C:\Development\runtimes\lolcode\lci.exe"
py tools/compare_ja_run.py
```

```
PASS binary_increment('1011')
PASS bit_flip('1011')
```

## Cómo leer lo que ves

| Salida | Qué significa | Qué hacer |
|---|---|---|
| `N/N byte-identical`, todos PASS | Las dos implementaciones coinciden | nada |
| `FAIL <caso>` | Hay regresión | corre `py tools/compare_*` con `-v` si existe, mira la línea dif reportada |
| `run_jajaja_lol.TransportError` | No encuentra lci | exportar `$env:LOLCODE_CMD` o poner `lci` en PATH |
| `lci.exe : file.lol:NN: ...` | Error de lci | revisar que `tests/runtime_tests.lol` está regenerado (`py tools/build_lol.py jajaja_tests.cfg`) |
| salida truncada, pasos grandes | El programa cuelga | `--max-steps` más alto |

## Errores reales que me he llevado (T-locales)

- **No grites al terminal sin `$env:LOLCODE_CMD`**: todas las herramientas
  fallan con un `TransportError` que se parece a "no está instalado"; lo está,
  pero en `C:\Development\runtimes\lolcode\lci.exe` no en PATH.
- **Sólo Python puedes usar sin env var**: `jajaja_interpreter.run()` es lo
  `run_lol()` fallback a un oráculo; lo hicimos *no silencioso* — `resolve_lci()`
  levanta si no está `lci`.
- **"zebras failing" por un uno/menos**: todos los `byte-identical` son justos
  sobre `\n`; no hacemos normalización `.replace("\r\n","\n")` — eso escondería
  diferencias reales.
- **lci quiso decir ":..." pero no dijo**: los literales `":(` y `"::"` se
  confunden en el lexer. El compilador LOLCODE los evita usando escapes hex
  `:(3A)` y emitiendo por `VISIBLE` en streaming (no pasando por `SMOOSH`).
  No pongas `":"` como último argumento de una función: dispara un lexer bug
  en lci (documentado en `tools/run_jajaja_lol.py` y en el bloque PUSHCH del
  runtime LOLCODE). Ver evidencia en `evidence/lolcode_port/VERDICTS.md`.

## Qué NO está verificado (NO_DEMONSTRATED)

- Parity en programas **largos** (miles de reglas y >100k pasos).
- Rendimiento absoluto: tiempo de ejecución en lci vs el intérprete Python
  se ve similar en tests cortos, no hay benchmark demostrativo.
- El path de entrada stdin *recibe* input correctamente para todos los
  fixtures Python (`--input` está cubierto en los 24 casos, pero no en todos
  los modos).

## En resumen

quedo útil para:

```powershell
py tools/parity_check.py --check-only
py test_lolcode_native.py
py tools/compare_tm_compile.py
py tools/compare_ja_run.py
```

y nada más correron todas esas cuatro cosas: tengo el repo funcional en
LOLCODE sin todavía dejar Python en el camino.
