# Python como oráculo / LOLCODE como runtime principal

Decisión: **NO se elimina el intérprete Python.** La relación entre ambos:

```
Python (jajaja_interpreter.py)  = oracle de referencia + generadores
                                  (tm_to_jajaja, ja_encoding) + host.py
                                  (capability broker, protocolo EFFECT/RESULT)
LOLCODE (src/jajaja.lol)        = runtime del LENGUAJE JAJAJA, ejecutado
                                  por un runtime lolcode externo (lci)
```

`tools/run_jajaja_lol.py` es transporte puro: serializa el programa como
stream 1-char/línea y recoge la tupla `(output, steps, status)`. No contiene
ninguna regla del lenguaje. Está demostrado porque `tools/parity_check.py`
produce 24/24 exacto incluyendo caso-límite CRLF, stdin, MAX_STEPS y
semánticas tramposas.

## Frontera host / lenguaje (P08)

`LANGUAGE_RUNTIME != HOST_ENVIRONMENT`:

- El lenguaje JAJAJA (algoritmo Markov) vive enteramente en LOLCODE.
- Las capacidades de host (`kv`, `fs`, `http`, reloj) son externas; en esta
  port son un host mínimo aparte, NO reproducción en LOLCODE *(nota: el
  protocolo EFFECT/RESULT correría en cualquier lenguaje con I/O de stream;
  LOLCODE lo soporta en principio, pero el file/socket I/O lo provee el
  exterior, y eso es por especificación, no por carencia).*

El host original `host.py` se conserva para los ejemplos de capacidades.

## Línea de complementos

| Función | Implementación | Estado |
|---|---|---|
| Ejecución `.jaja` de usuarios | `src/jajaja.lol` via lci | PRINCIPAL |
| Verificación diferencial | `tools/parity_check.py` + oracle | tests |
| Generadores de programas | `proofs/tm_to_jajaja.py`, `ja_encoding.py` | Python (codificación estática) |
| Host de capabilities | `host.py` | Python (externo) |

La adopción de LOLCODE no borra al oráculo: precisamente porque existe, la
paridad permanece chequeable en cualquier momento.
