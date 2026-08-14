# JAJAJA

> *"El chiste no se cuenta, se reescribe."*

Un esolang de **reescritura de cadenas** cuyo alfabeto son repeticiones del
token `ja`. Cuántas veces se ríe el programa en cada punto **es** el símbolo.

El resultado: un sistema de reescritura formal, Turing completo, cuyo código
fuente lo lee cualquier hispanohablante.

```
jaja::=~Hello, world!
j::=~
::=
jaja j
```

```
$ python check_bootstrap.py
Jajaja_COMPILE_OK status=HALTED steps=2 signature='JAJAJA-OK\n'
```

Sin dependencias. Python 3 y nada más.

---

## Correr

```bash
python check_bootstrap.py        # smoke test canónico
python run_examples.py           # todos los examples/*.jaja
python test_jajaja.py            # 27 tests
python proofs/tm_to_jajaja.py    # simula máquinas de Turing (7 casos)
python proofs/ja_encoding.py     # ¿el alfabeto de risas alcanza?
```

```python
from jajaja_interpreter import run

output, steps, status = run(source, max_steps=200000)
# status ∈ {"HALTED", "MAX_STEPS", "SYNTAX_ERROR: <msg>"}
```

## El lenguaje

Especificación completa en **[JAJAJA_LANG.md](JAJAJA_LANG.md)**. Lo mínimo:

| | |
|---|---|
| **Estado** | una cadena (`base`) más un buffer de salida |
| **Regla** | `lhs::=rhs` — reemplaza la primera ocurrencia de `lhs` por `rhs` |
| **Salida** | `lhs::=~texto` emite `texto` y borra el match; `::=~` solo emite newline |
| **Evaluación** | primera regla que matchea, ocurrencia más a la izquierda |
| **Fin** | `HALTED` cuando ninguna regla matchea; `MAX_STEPS` al agotar presupuesto |

El alfabeto `ja`⁺ es una **convención estilística, no una restricción**: el
motor acepta tokens arbitrarios.

## ¿Es Turing completo?

**Sí.** Y la prueba se corre, no se cree: **[proofs/TURING.md](proofs/TURING.md)**.

Resumen:

- **JAJAJA es un algoritmo normal de Markov**, no un sistema Thue. Lista
  ordenada de reglas, primera aplicable, ocurrencia más a la izquierda, parar
  cuando ninguna aplica. Ese modelo es Turing completo desde 1951.
- **Traducción mecánica MT → JAJAJA**, uniforme: `compile_tm` toma una máquina
  de Turing arbitraria *como datos*. Verificada contra un simulador
  independiente en 7 casos, 0 fallos.
- **El alfabeto de risas también alcanza — pero con delimitador.** Sin él la
  codificación unaria es ambigua: `jaja` es substring de `jajaja`, y el símbolo
  2 concatenado con el 3 es indistinguible del 5. Medido: una regla del símbolo
  2 se dispara *dentro* del símbolo 3.

```
$ python proofs/ja_encoding.py
OK   binary_increment('1011')   esperado '1100'  ->  en risas '1100'
OK   bit_flip('1011')           esperado '0100'  ->  en risas '0100'
     alfabeto de reglas y cinta: ['a', 'j']
```

Una máquina de Turing corriendo en risas puras: reglas, cinta y estados, sólo
`j` y `a`.

Los ejemplos de la spec siempre escribieron `jaja j`, con espacio. Ese espacio
es estructural, no cosmético — y hasta ahora no estaba dicho en ningún lado.

## La trampa que vas a pisar

Si el `rhs` de una regla contiene su propio `lhs`, esa regla se dispara sobre su
propio resultado para siempre:

```
jaja::=jajajaja          # jajajaja CONTIENE jaja -> bucle infinito
jajajaja::=~jajajaja!    # nunca se alcanza
```

Poné antes las reglas de `lhs` más largo. La §5.3 de la spec lo documenta con
los dos casos, y el suite fija los dos como test — incluido el anti-ejemplo.

## Tests

27 tests, sin framework: `python test_jajaja.py`.

Cubren el intérprete, los ejemplos, CRLF, tolerancia del separador, y
—lo importante— **ejecutan los ejemplos de la especificación** verificando que
sigan textualmente en el `.md`. Si alguien edita un ejemplo de la spec sin
actualizar su salida documentada, el suite se pone en rojo.

Eso no es paranoia. La spec afirmaba que un ejemplo *"termina en un solo
ciclo"* cuando en realidad no terminaba nunca ni emitía nada; su tabla de
conteo contradecía al intérprete; y dos de sus tablas documentaban una
notación que ni siquiera parsea. Diez tests pasaban en verde con todo eso roto,
porque ninguno ejecutaba lo que la documentación prometía.

## Licencia

MIT.
