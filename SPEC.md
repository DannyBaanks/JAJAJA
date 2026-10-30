# JAJAJA — Especificación v1.0 (FROZEN)

> **Estado del contrato: GOLDEN v1.0** (ver `GOLDEN.md`).
> Este documento define la semántica congelada del núcleo del lenguaje.
> Cualquier cambio en lo aquí declarado es un **cambio de contrato**: exige
> versión nueva, entrada en `CHANGELOG.md` y re-ejecución del corpus de
> conformidad (`conformance/`). Nunca un ajuste silencioso.
>
> Documento narrativo y de diseño: `JAJAJA_LANG.md`.
> En caso de conflicto entre ambos, **gana este documento**.

---

## 1. Nombre, formato y extensión

- Nombre del lenguaje: **JAJAJA**.
- Extensión canónica: `.jaja`.
- Un archivo `.jaja` ES el artefacto ejecutable del lenguaje; no hay etapa de
  compilación obligatoria.
- Encoding: **UTF-8** (sin BOM). El comportamiento con BOM u otro encoding no
  forma parte del contrato.
- Terminadores de línea: LF y CRLF son equivalentes; un `\r` residual al final
  de cualquier línea se descarta antes de procesar.

## 2. Gramática del archivo

Un programa `.jaja` tiene dos secciones: reglas y base.

```
[# comentario]
<lhs1>::=<rhs1>
<lhs2>::=<rhs2>
...
::=
[<base inicial>]
```

Reglas de parseo, en orden:

1. **Modo reglas** (inicial). Para cada línea, primero se aplica `rstrip('\r')`:
   1. Línea completamente vacía: se ignora.
   2. Línea cuyo primer carácter es `#`: comentario, se ignora.
      **No hay comentarios inline**: un `#` a mitad de línea es carácter normal.
   3. Línea cuyo contenido, ignorando espacios a ambos lados, es `::=`: pasa a
      **modo base**. Se tolera whitespace (`   ::=   ` es válido).
   4. Línea que contiene `::=`: se divide en el primer `::=` en
      `(lhs, rhs)` y se agrega como regla, **en orden de aparición**.
   5. Línea que NO contiene `::=`: **error de sintaxis**
      (`SYNTAX_ERROR: regla sin '::=' en linea N`).
2. **Modo base**: la base del programa es la **primera línea posterior al
   separador que no sea vacía ni comentario** (se compara con `strip()`). Las
   líneas posteriores se descartan en silencio. Si ninguna línea califica, la
   base es la cadena vacía `""`.

Propiedades derivadas del parseo (parte del contrato):

- Una regla con `lhs` vacío (`::=rhs`) es **válida pero inerte**: el motor la
  salta en cada paso. No es error ni produce reescritura infinita.
- El `rhs` puede ser la cadena vacía (`lhs::=`): borra el match sin emitir.
- El orden de las reglas es **semántica** (ver §4): reordenar reglas puede
  cambiar el resultado o la terminación de un programa.

## 3. Modelo de máquina

JAJAJA es un **algoritmo normal de Markov con emisión de texto** (no un
sistema Thue: ver `proofs/TURING.md` §1).

Estado observable de una ejecución:

| campo | tipo | descripción |
|---|---|---|
| `rules` | lista ordenada `(lhs, rhs)` | programa cargado |
| `base` | cadena | cinta de reescritura |
| `output` | cadena | concatenación de emisiones |
| `steps` | entero | pasos ejecutados |
| `status` | enum | `RUNNING`, `HALTED`, `MAX_STEPS`, `SYNTAX_ERROR: <msg>` |

## 4. Paso de reescritura (semántica congelada)

Dado el estado en `RUNNING`, un paso funciona así:

```
para cada (lhs, rhs) en rules, EN ORDEN:
    si lhs == ""  ->  saltar regla
    idx = base.find(lhs)              # ocurrencia MÁS A LA IZQUIERDA
    si idx >= 0:
        si rhs empieza con "~":
            tail = rhs[1:]
            si tail == "":  emitir "\n"
            si tail != "":  emitir tail
            base = base sin el match          # el match SALE de la base
        si no:
            base = base[:idx] + rhs + base[idx+len(lhs):]
        steps += 1
        fin del paso
si ninguna regla aplicó:  status = HALTED
```

Consecuencias contractuales:

- **Primera regla aplicable, no mejor regla.** Dos reglas con lhs aplicable se
  resuelven por orden de lista, no por posición.
- **Leftmost**: dentro de la regla elegida se reescribe la ocurrencia más a la
  izquierda.
- **`~` borra, no reemplaza**: el rhs emisor no se vuelve a inyectar en la
  base. Una regla emisora no puede preservar delimitadores (ver
  `proofs/TURING.md` §4).

## 5. Entrada

Una invocación puede proveer `input` (cadena). Si `input` es no vacía, antes
del primer paso la base inicial pasa a ser:

```
base_0 = input + " " + base_archivo
```

Si `input` es vacía, la base queda intacta. No existe lectura interactiva;
toda la entrada se consume como prefijo de la cinta.

La misma fuente compilada + distintos inputs producen distintas ejecuciones
porque **las reglas procesan el input** (el host no lo interpreta).

## 6. Terminación y estados finales

```
status = HALTED      ninguna regla aplicó          (terminación normal)
status = MAX_STEPS   se agotó el presupuesto        (NO es terminación)
status = SYNTAX_ERROR:…  el archivo viola §2        (programa inválido)
```

Contractualmente: **`HALTED`, `MAX_STEPS` y `SYNTAX_ERROR` son valores
distintos y no intercambiables.** En particular, cortar por presupuesto no
equivale a terminar (`MAX_STEPS => HALTED` está prohibido).

Sobre terminación: JAJAJA es Turing completo (ver `proofs/TURING.md`), así que
su problema de parada es indecidible; `MAX_STEPS` es una cota práctica, no un
resultado semántico.

## 7. Límites (parte de la semántica)

| límite | valor por defecto | naturaleza |
|---|---|---|
| `max_steps` | 200 000 pasos | presupuesto de ejecución, configurable por parámetro |
| memoria de `base` | sin cota en el motor | acotada en la práctica por la memoria del host |
| `output` | sin cota en el motor | idem |
| recursión | no aplica | el motor es iterativo |
| timeout de wall-clock | ninguno en el motor | el host que lo necesite debe medirlo fuera |

Los límites existentes son los de esta tabla. No hay más cotas ocultas.

## 8. Traza observable

El motor puede registrar una traza opcional (flag `trace`):

```
snapshot = { step, base, output, status }   # tras CADA paso aplicado,
                                            # más un snapshot inicial (step=0)
```

Contrato de la traza:

- **Invariante trace**: ejecutar con y sin traza produce el mismo
  `(output, steps, status)`. La traza es un canal lateral observacional;
  **no modifica la ejecución**.
- La traza es completa: un snapshot por paso, en orden.

## 9. Alfabeto `ja` (convención, no restricción)

El motor acepta cualquier token. El alfabeto de risas (`ja`⁺, con el conteo de
`ja` como símbolo) es una **convención estilística** del programador.

Declaración formal (con evidencia en `proofs/ja_encoding.py`):

- Con **delimitador** (espacio), el alfabeto de risas es una codificación
  unaria válida y Turing completa.
- Sin delimitador es **ambigua por construcción** (`jaja` es substring de
  `jajaja`) y una regla de un símbolo puede morder dentro de otro. Esto está
  medido y fijado como caso del corpus de conformidad (`c017`).
- `j` solo (una jota) no pertenece a la serie `ja`⁺; por convención se usa
  como marcador (típicamente newline).

## 10. Versionado y cambios de contrato

- Versión de esta especificación: **1.0**.
- La semántica §4, el formato §2 y los estados §6 forman el **núcleo
  congelado**. Inmutables sin nueva versión mayor.
- El conjunto de referencia de comportamiento es el corpus de
  `conformance/`; un cambio que lo ponga en rojo sin actualizar la versión es
  una regresión.
- Fuera del núcleo (quedan explícitamente FUERA de este contrato):
  el host de capabilities (`host.py`, protocolo EFFECT/RESULT), la UI IR,
  la stdlib y el backend/port a LOLCODE. Son extensiones con su propio
  estado de madurez (ver README §"Estado de madurez").

## 11. Implementaciones de referencia

| rol | implementación | notas |
|---|---|---|
| Motor/oráculo | `jajaja_interpreter.py` (Python 3.10+, cero dependencias) | ejecuta la semántica de este documento |
| Segunda implementación | `src/jajaja.lol` (LOLCODE 1.3, runtime externo `lci`) | paridad medida en `evidence/lolcode_port/` |

El host de capabilities está en `host.py` y **no** forma parte de la
semántica del núcleo.
