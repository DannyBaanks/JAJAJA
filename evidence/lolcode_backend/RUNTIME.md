# RUNTIME — runtime LOLCODE externo usado en las pruebas

- Runtime: **lci** (LOLCODE interpreter), https://github.com/justinmeza/lci
- Tag: `v1.3` (annotated tag object `04702308...`, commit `0b32ed1cc52abd1971d199db9bd77c387316cae1` — exact commit
  obtenido con `git clone --branch v1.3 --depth 1` + `git log -1 --format=%H`
  el 2026-09-03
- Licencia: GPL-3.0 (`COPYING` en el repo de lci). El runtime se ejecuta como
  proceso separado; NO se distribuye con este repositorio.
- Compilación (MinGW-w64 gcc 16.1.0 ucrt):

```
gcc -O2 -o lci.exe main.c error.c interpreter.c lexer.c parser.c tokenizer.c unicode.c
```

- SHA-256 del binario usado en las pruebas:

```
53200EEAD0D8FED7BF8D05CF7C124EA1484D5C2025217FAE195EBBC1E752DAC6  lci.exe
```

- Ubicación durante las pruebas: fuera de este repo (se accedía vía
  `LOLCODE_CMD`, que apuntaba al `lci.exe` compilado).

## Smoke probes (pre-demo)

| probe | comando | salida |
|---|---|---|
| aritmética | programa con `GIMMEH XVAR`/`GIMMEH YVAR` + `SUM OF XVAR AN YVAR`, stdin `2\n3` | `5` |
| comparación+rama | `BIGGR OF` + `BOTH SAEM` + `O RLY?`, stdin `9\n4` | `9` |
| loop | `IM IN YR` + `DIFF OF N AN 1`, stdin `3` | `3 2 1 0` |
| echo | `GIMMEH MSG` + `VISIBLE MSG`, stdin `Bolgang dice hola` | `Bolgang dice hola` |

Hallazgo documentado en el camino: `GIMMEH` lee YARN y `BOTH SAEM` compara
por tipo, así que `SAEM "9" 9` es FAIL; los programas .lol que comparan
hacen `MAEK <var> NUMBR` primero (ver comentarios en `programs/max.lol`).
