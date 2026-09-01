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
python test_jajaja.py            # 49 tests del intérprete
python test_host.py              # 51 tests del host runtime
python proofs/tm_to_jajaja.py    # simula máquinas de Turing (7 casos)
python proofs/ja_encoding.py     # ¿el alfabeto de risas alcanza?

# Host runtime
python host.py examples/calculator.jaja --input "ADD 1 2"
python host.py examples/echo.jaja --input "hello" --allow stdin,stdout
python host.py examples/calculator.jaja --input "MUL 3 3" --trace
```

```python
from jajaja_interpreter import run, Jajaja

# Básico
output, steps, status = run(source, max_steps=200000)

# Runtime input (COMPILE_ONCE_TEST_MANY)
output, steps, status = run(source, stdin_data="hello")

# Con trace (no afecta output)
j = Jajaja(source, trace=True)
output, steps, status = j.run(stdin_data="hello")
for snapshot in j.trace:
    print(snapshot.step, snapshot.base)
```

## El lenguaje

Especificación completa en **[JAJAJA_LANG.md](JAJAJA_LANG.md)**. Lo mínimo:

| | |
|---|---|
| **Estado** | una cadena (`base`) más un buffer de salida |
| **Regla** | `lhs::=rhs` — reemplaza la primera ocurrencia de `lhs` por `rhs` |
| **Salida** | `lhs::=~texto` emite `texto` y borra el match; `::=~` solo emite newline |
| **Evaluación** | primera regla que matchea, ocurrencia más a la izquierda |
| **Input** | `stdin_data` se inyecta como prefijo de la base |
| **Fin** | `HALTED` cuando ninguna regla matchea; `MAX_STEPS` al agotar presupuesto |

El alfabeto `ja`⁺ es una **convención estilística, no una restricción**: el
motor acepta tokens arbitrarios.

## Runtime input

El mismo archivo `.jaja` responde a diferentes inputs en runtime:

```
# command.jaja
bye::=~BYE
hello::=~HELLO
::=
```

```python
from jajaja_interpreter import Jajaja

src = open("examples/command.jaja").read()
Jajaja(src).run(stdin_data="hello")  # → ("HELLO", 1, "HALTED")
Jajaja(src).run(stdin_data="bye")    # → ("BYE", 1, "HALTED")
Jajaja(src).run(stdin_data="")       # → ("", 0, "HALTED")
```

Mismo SHA256, diferentes inputs, diferentes outputs. Python no calcula nada —
las reglas JAJAJA procesan el input directamente.

## Host runtime

`host.py` ejecuta programas JAJAJA con un protocolo de capabilities:

```bash
python host.py program.jaja --input "data" --allow stdin,stdout,kv
python host.py program.jaja --allow fs-read,fs-write --root ./sandbox
```

JAJAJA genera peticiones `EFFECT` via reglas de output. host.py las ejecuta,
inyecta los `RESULT` de vuelta en la base, y JAJAJA continúa computando.

```
JAJAJA → EFFECT stdout {"text":"hello"}
host.py → ejecuta, inyecta RESULT OK ""
JAJAJA → continua...
```

### Capabilities disponibles

| Capability | Grupo | Descripción |
|---|---|---|
| `stdin` | `io` | Lee del input buffer |
| `stdout` | `io` | Escribe a stdout |
| `kv-get` | `kv` | Lee del key-value store |
| `kv-set` | `kv` | Escribe al key-value store |
| `fs-read` | filesystem | Lee archivo (sandboxed) |
| `fs-write` | filesystem | Escribe archivo (sandboxed) |
| `clock` | — | Timestamp actual |
| `http-get` | `http` | GET request (fixture mode) |

### Sandbox

El filesystem está sandboxed — path traversal bloqueado:

```bash
python host.py app.jaja --allow fs-read,fs-write --root ./sandbox
# app.jaja NO puede leer fuera de ./sandbox
```

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

## Ejemplos

| Archivo | Qué hace |
|---|---|
| `hola.jaja` | Hello, world! |
| `amplificacion.jaja` | Amplificación de risa por etapas |
| `eco.jaja` | Emite dos copias |
| `loop.jaja` | Bucle infinito (MAX_STEPS) |
| `calculator.jaja` | `ADD 1 2` → `3` (JAJAJA computa, Python imprime) |
| `echo.jaja` | Mismo archivo, 5 inputs diferentes → 5 outputs diferentes |
| `command.jaja` | Router de comandos (hello→HELLO, bye→BYE) |
| `structured.jaja` | Compute en base, emit al final |

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

100 tests, sin framework:

```bash
python test_jajaja.py            # 49 tests: intérprete + examples + runtime input + trace
python test_host.py              # 51 tests: data model + host ABI + calculator + UI IR + FS
```

Cubren el intérprete, los ejemplos, CRLF, tolerancia del separador, runtime
input, trace equivalence, structured output, host capabilities, filesystem
sandbox, y UI IR. Los ejemplos de la spec se ejecutan y verifican contra el
`.md` — si alguien edita un ejemplo sin actualizar su salida documentada, el
suite se pone en rojo.

## Arquitectura

```
JAJAJA Program (.jaja)
    ↓
Jajaja (Markov rewriter)
    ↓ rules produce EFFECT lines
Host IR (EFFECT/RESULT protocol)
    ↓
host.py (capability dispatcher)
    ↓
Capability adapters (stdin, stdout, kv, fs, http)
    ↓
RESULT injected back into base
    ↓
JAJAJA continues computing
```

JAJAJA decide **qué** effects requestear. host.py los ejecuta. Python no calcula
la lógica de aplicación.

## Licencia

MIT.
