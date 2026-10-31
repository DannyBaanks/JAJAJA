# LOLCODE backend

JAJAJA compone peticiones que ejecuta un runtime **LOLCODE externo**.

```
python demo_lolcode.py "ADD 2 3"
```

Pipeline:

```
Python frontend (demo_lolcode.py)
  -> route.jaja (JAJAJA reescribe la petición y elige la op)
  -> host.py capability "lolcode"
  -> backends/lolcode/adapter.py (transporte ONLY)
  -> runtime LOLCODE externo (lci) ejecuta programs/<op>.lol
  -> stdout vuelve como RESULT
  -> JAJAJA confirma recepción
  -> Python imprime
```

Python nunca calcula el resultado. La prueba negativa está en los tests:
sin runtime externo, el sistema falla ruidosamente en lugar de inventar
la suma.

## Runtime externo requerido

No distribuimos ningún intérprete ni runtime LOLCODE con este repo.
El runtime referencia es **lci** (GPL-3.0, Justin Meza), compilado desde
su fuente pública:

```bash
# Linux/macOS:
git clone --depth 1 --branch v1.3 https://github.com/justinmeza/lci
cd lci && cmake . && make            # produce ./lci

# Windows (MinGW):
gcc -O2 -o lci.exe main.c error.c interpreter.c lexer.c parser.c tokenizer.c unicode.c
```

Luego apúntale al adapter:

```bash
export LOLCODE_CMD=/ruta/al/lci        # Linux/macOS
$env:LOLCODE_CMD="C:\ruta\a\lci.exe"   # PowerShell
```

O simplemente deja `lci` en tu `PATH`.

Verificado el 2026-10-31 en Ubuntu 24.04 con las dos fuentes, y las dos sin SKIP:

| runtime | binario | e2e |
|---|---|---|
| `v1.3` (la referencia de arriba, se reporta `v0.10.5`) | `~/.local/bin/lci` | 30 + 22 + 4 OK, 0 SKIP |
| `master` `a0a3767` (se reporta `v0.11.2`) | `~/.local/bin/lci-v0.11.2-master` | 30 + 22 + 4 OK, 0 SKIP |

`v1.3` pide CMake 3.31 y este host trae 3.28.3, así que el build se hace con

```bash
sh tools/build_lci.sh            # v1.3  (rebaja cmake_minimum_required en su copia local)
sh tools/build_lci.sh --master   # master
```

que instala en `~/.local/bin/lci` sin sudo y termina con un smoke (`HAI 1.2`).

## Ops

| petición    | programa .lol | semántica LOLCODE demostrada          |
|-------------|---------------|---------------------------------------|
| `ADD 2 3`   | `sum.lol`     | `GIMMEH` + `SUM OF ... AN ...`        |
| `MAX 9 4`   | `max.lol`     | `BIGGR OF`, `BOTH SAEM`, `O RLY?` branch |
| `ECHO hola` | `echo.lol`    | strings: `GIMMEH` + `VISIBLE`         |
| `COUNT 3`   | `count.lol`   | loop `IM IN YR` + estado + `GTFO`     |

Cualquier otra op: JAJAJA no agarra ninguna regla, no hay EFFECT, y el
frontend falla limpio. Las peticiones que sí agarran pero llegan con un
operando inválido son rechazadas por el propio runtime (lci).

## Limitaciones honestas

- Operandos: enteros no-negativos de una sola línea (LOLCODE GIMMEH).
- El token `READY` es interno; si lo usas como texto de `ECHO`, se lo
  come la reescritura. No lo hagas.
- `lci` es GPL-3.0: se ejecuta como proceso separado, no se enlaza ni
  se distribuye con este repo (licencia limpia para JAJAJA).
