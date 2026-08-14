# JAJAJA — lenguaje de programación por risa

> "El chiste no se cuenta, se reescribe."

Jajaja es un esolang de **reescritura de cadenas** (familia Thue) cuyo
alfabeto son repeticiones del token `ja`. La "longevidad" de la risa
(cuántas veces se repite `ja` contiguamente) determina cada palabra
semántica: ese conteo **es** el identificador del símbolo.

## 1. Filosofía

En la mayoría de los esolangs, los tokens son símbolos arbitrarios
(`>`, `«`, `MOO`...). Jajaja impone una sola unidad semántica — la risa
`ja` — y construye todo el lenguaje a partir de cuántas veces se ríe el
programa en cada punto. Resultado: el programa fuente **es legible por
cualquier hispanohablante** y al mismo tiempo es un sistema de
reescritura formal completo (puede simular Thue y por ende máquinas de
Turing).

**Importante (convención vs. restricción):** el motor acepta tokens
arbitrarios (`Hola::=mundo` es válido y se ejecuta). Eso NO debilita el
lenguaje, al contrario: el motor es Thue-completo irrestricto. La risa
`ja`+N es una **convención estilística** que el programador sigue por
legibilidad hispano-parlante, no una restricción semántica forzada por el
intérprete. (Esto hace el claim de Turing-completitud *más* sólido, no
menos.)

## 2. Estado / Regla / Evaluación / Memoria

| Concepto | Jajaja |
|----------|--------|
| **State** | una cadena `base` (la risa acumulada) |
| **Rule model** | `lhs ::= rhs`: reemplaza la primera ocurrencia de `lhs` por `rhs` |
| **Evaluation** | leftmost match, primera regla que aplica (determinista en esta implementación; el spec Thue permite no determinismo) |
| **Memory** | solo `base` + `output buffer` (sin heap, sin stack) |
| **Control flow** | implícito en la reescritura; *no hay jumps* |
| **Termination** | HALTED = ninguna regla matchea; MAX_STEPS = presupuesto agotado |
| **Input** | ningún input intrínseco |
| **Output** | reglas con rhs `::=~<text>` emiten `<text>`; `::=~` solo = newline |

## 3. Formato del programa

```
# comentarios opcionales (línea empieza con #)

<lhs1>::=<rhs1>
<lhs2>::=<rhs2>
...

::=

<base inicial>
```

- Cada línea que contenga `::=` antes del separador es una regla.
- Los comentarios son de **línea completa**: sólo se ignora una línea cuyo
  primer carácter no-blanco sea `#`. **No hay comentarios inline** —
  un `#` a mitad de una regla se vuelve parte del `rhs`, en silencio.
- El separador `::=` debe aparecer solo en una línea (se tolera whitespace
  alrededor: `   ::=   ` también es válido). Indica fin de reglas e inicio
  de la base.
- La **base** es la primera línea no-vacía tras el separador. Las líneas
  posteriores se descartan en silencio (el spec v1 no soporta base
  multilínea).
- El parser es tolerante a CRLF (`\r\n`) y LF (`\n`) indistintamente;
  cualquier `\r` residual al final de línea se descarta antes de procesar.

### 3.1 Sintaxis de salida

```
jajaja::=~Hola        # al reescribir jajaja, emite "Hola" y borra el match
jajaja::=~            # rhs = "~" solo -> emite newline
jajaja::=~Hola mundo  # emite "Hola mundo" (incluyendo el espacio)
```

### 3.2 Tipos de regla

| rhs | comportamiento |
|-----|-----------------|
| `~<text>` | emite `<text>` al output, **elimina el match de base** |
| `~`       | emite `\n`, elimina el match |
| `<otra risa>` | reemplaza el match en base por esta nueva risa |

## 4. Simbología de la risa

El conteo de `ja` define cada "palabra":

| Token | Risas (`ja` repetido) | Caracteres | Ejemplo |
|-------|----------------------:|-----------:|---------|
| `ja`        | 1 | 2  | risa corta |
| `jaja`      | 2 | 4  | risa social |
| `jajaja`    | 3 | 6  | risa cómplice |
| `jajajaja`  | 4 | 8  | risa de carcajada |
| `jajajajaja`| 5 | 10 | risa incontrolable |
| `jajajajajaja` | 6 | 12 | idem pero más |

La columna que importa es **Risas**: es la que codifica el símbolo. La de
caracteres está sólo para evitar la confusión de leer `jaja` como "4".

> **`j` está fuera de esta serie.** Una jota sola contiene **cero**
> repeticiones de `ja`, así que no es "la risa más corta": es un token aparte,
> usado por convención como marcador de newline. La codificación unaria de la
> §7 se define sobre `ja`⁺ (una o más risas); `j` no participa en ella.

> Nota: la gramática no fija N, así que el programador es libre de inventar
> la "risa" con el conteo que represente mejor su intención.

## 5. Programa básico

### 5.1 Hello, world!

```
# hola.jaja — primer programa
jaja::=~Hello, world!
j::=~
::=
jaja j
```

Ejecución:
1. `jaja` matchea primera regla, emite `"Hello, world!"`, eliminando el match.
2. base queda como `" j"`.
3. `j` matchea segunda regla, emite `"\n"`.
4. base queda `" "`. Ninguna regla matchea -> HALT.

Salida: `Hello, world!\n`

### 5.2 Amplificación de risa

Un programa donde la risa más corta se amplifica a risas más largas antes de
ser emitida:

```
jajaja::=~jajaja! 
jaja::=jajaja
j::=~
::=
jaja j
```

Ejecución:
1. base = `"jaja j"`; primera regla (`jajaja`) no matchea; segunda regla
   (`jaja`) matchea en pos 0 -> reemplaza por `"jajaja"`. base = `"jajaja j"`.
2. `jajaja` ahora matchea primera regla -> emite `"jajaja! "`, borra.
   base = `" j"`.
3. `j` matchea última regla -> emite `"\n"`. base = `" "`.
4. HALT.

Salida: `jajaja! \n`

### 5.3 Amplificación por etapas, y el orden de las reglas

```
jajajaja::=~jajajaja!
jaja::=jajajaja
j::=~
::=
jaja j
```

Ejecución:
1. base = `"jaja j"`; la regla 1 (`jajajaja`) no matchea; la regla 2 sí ->
   base = `"jajajaja j"`.
2. Ahora la regla 1 matchea -> emite `"jajajaja!"`, borra. base = `" j"`.
3. `j` -> emite `"\n"`. base = `" "`. HALT.

Salida: `jajajaja!\n` (3 pasos).

#### El orden importa, y no es cosmético

Estas mismas tres reglas **con las dos primeras invertidas no terminan nunca**:

```
jaja::=jajajaja
jajajaja::=~jajajaja!
j::=~
::=
jaja j
```

`jaja` se reescribe a `jajajaja`, que **contiene `jaja`**. Como la evaluación
toma la primera regla que matchea, la regla 1 vuelve a dispararse sobre su
propio resultado y la regla 2 nunca se alcanza: la base crece 4 caracteres por
paso y el programa termina en `MAX_STEPS` **sin emitir nada**.

```
('', 2000, 'MAX_STEPS')
```

Regla práctica en toda la familia Thue: **si el rhs de una regla contiene su
propio lhs, poné antes las reglas de lhs más largo.** Aquí, `jajajaja` antes
que `jaja`.

## 6. Semántica formal

Mutación de estado:
```
base_0       = base literal del archivo
base_{i+1}  = base_i[:idx] + rhs + base_i[idx + len(lhs):]
              para_lhs ::= rhs = primera regla con idx = base_i.find(lhs) >= 0
              si rhs es "~<text>": output += text, base = base_i sin el match
              si lhs no aparece en base_i: HALT
```

Esto corresponde a un **sistema de reescritura de cadenas semi-Thue** con
emisión de texto, equivalente en poder computacional a Thue y por ende a
máquinas de Turing.

## 7. Jajaja vs. Thue

|              | Thue                  | Jajaja                       |
|--------------|-----------------------|-----------------------------|
| Alphabet     | arbitrario            | `ja` con longevidad variable |
| Source looks | imperativo obscure   | risa en español               |
| Nondeterminism | parte del spec       | determinista en v1 (próx)     |
| Output       | `::=~text`            | idéntico                      |
| Power        | Turing-complete       | Turing-complete               |

Jajaja es un Thue restringido sintácticamente a un alfabeto legible por
hispanohablantes; la restricción NO reduce el poder (el conteo de `ja` es
una codificación unaria del alfabeto de Thue).

### 7.1 Precisiones que salieron de probarlo

La afirmación de arriba es cierta, pero incompleta en dos puntos. La prueba
ejecutable está en **[`proofs/TURING.md`](proofs/TURING.md)**.

**Jajaja es un algoritmo normal de Markov, no un Thue.** Thue es no
determinista; Jajaja aplica la primera regla de la lista sobre la ocurrencia
más a la izquierda y para cuando ninguna matchea. Eso es exactamente el modelo
de Markov (1951), que también es Turing completo. La identificación precisa
explica de dónde sale la potencia sin depender del no determinismo.

**La codificación unaria necesita un delimitador.** Sin él es ambigua por
construcción: `jaja` (2 risas) es substring de `jajaja` (3 risas), y el símbolo
2 concatenado con el 3 es indistinguible del símbolo 5. Como las reglas matchean
por substring, una regla del símbolo 2 se dispara **dentro** del 3:

```
jaja::=~MORDIO
::=
jajaja                 <- la base es sólo el símbolo 3

-> output='MORDIO'     la regla mordió adentro del otro símbolo
```

Con delimitador (` jaja ` no es substring de ` jajaja `) la ambigüedad
desaparece y la codificación se sostiene. **Los ejemplos de este documento ya
usaban el espacio** (`jaja j`) — pero era estructural, no cosmético, y no estaba
dicho. Si escribís risas pegadas, no tenés una codificación unaria: tenés una
ambigüedad.

## 8. Runtime

Este repo trae un intérprete Python puro en
`jajaja_interpreter.py`.

API pública:
```python
def run(source: str, max_steps: int = 200000, stdin_data: str = "")
        -> tuple[str, int, str]:
    """
    Devuelve (output, steps, status).
    status ∈ {"HALTED", "MAX_STEPS", "SYNTAX_ERROR: <msg>"}
    """
```

Smoke check canónico:
```
python check_bootstrap.py
# -> Jajaja_COMPILE_OK status=HALTED steps=2 signature='JAJAJA-OK\n'
```

## 9. Diseño futuro (abierto)

- **Jajaja-N nondeterminista**: añadir selección aleatoria de regla
  aplicable (más fiel al spec Thue).
- **Jajaja-2**: combinar `jajaja` (reescritura) con `jeje` (stack push)
  como tipo compuesto — concatenación de familias.
- **Jajaja-V**: versión visual al estilo Piet, donde el color de cada
  pixel indica risas contiguas.

Cualquier prolongación mantiene el mismo modelo de reescritura; el
lenguaje crece sin cambiar su semántica base.
