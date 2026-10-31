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

## Estado del contrato: núcleo GOLDEN v1.0

El **núcleo** del lenguaje (formato `.jaja`, paso de reescritura, estados
`HALTED`/`MAX_STEPS`/`SYNTAX_ERROR`, input, traza) tiene su semántica
**congelada**: [`SPEC.md`](SPEC.md) v1.0 + [`GOLDEN.md`](GOLDEN.md). El
contrato se verifica con un corpus declarativo:

```bash
python tools/conformance_run.py      # corpus 20/20 (un claim por caso)
python tools/collect_evidence.py     # regenera evidence/golden_v1/
```

### Tabla de claims (núcleo)

| Claim | Status | Evidencia |
|---|---|---|
| Parser acepta el formato canónico (.jaja, CRLF, comentarios) | VERIFIED | corpus c007-c012 + `test_jajaja.py` |
| Paso de reescritura (orden de reglas, leftmost, `~` emite y borra) | GOLDEN | SPEC §4 + corpus c001-c005/c015 |
| `HALTED`, `MAX_STEPS` y `SYNTAX_ERROR` son estados distintos | GOLDEN | SPEC §6 + corpus c006/c013/c014 |
| Runtime input: mismo artefacto, distintos inputs, distintos resultados | GOLDEN | corpus c010a/b + `test_engine_does_the_work.py` |
| El host NO hace el trabajo del lenguaje | VERIFIED | `test_engine_does_the_work.py` (§9) |
| Traza observable sin alterar la ejecución | GOLDEN | SPEC §8 + test de invariante trace |
| Motor Turing completo (algoritmo de Markov) | VERIFIED | `proofs/tm_to_jajaja.py` + segundo runtime |
| Alfabeto de risas TC **con delimitador** | VERIFIED | `proofs/ja_encoding.py` + corpus c017/c018 |
| Paridad Python-oráculo vs runtime LOLCODE | VERIFIED (histórico) | `evidence/lolcode_port/` (24/24, 7/7; rerun hoy: `lci` ausente en este host) |

### NO demostrado

| Claim | Status | Razón |
|---|---|---|
| Persistencia real (KV duradero) | NOT_DEMONSTRATED | KV del host es solo in-memory |
| Concurrencia | NOT_DEMONSTRATED | motor single-threaded |
| Código nativo (JIT/AOT) | NOT_DEMONSTRATED | no existe |
| "LOLCODE es el lenguaje menos usado de GitHub" | NOT_DEMONSTRATED | medido: Befunge tiene menos archivos indexados (`evidence/lolcode_backend/LINGUIST_AUDIT.md`) |

### Límites conocidos

`max_steps` por defecto 200 000 (configurable); sin timeout de wall-clock en el
motor; memoria sin cota en el motor (acotada por el host). Detalle y tabla en
`SPEC.md` §7. `MAX_STEPS` nunca se reporta como `HALTED`.

---

## Runtime

JAJAJA tiene dos runtimes con la MISMA semántica:

| runtime | ejecutor | papel |
|---|---|---|
| `src/jajaja.lol` (armado desde `src/parts/*.lol`) | un runtime LOLCODE externo (`lci`) | implementación en LOLCODE |
| `jajaja_interpreter.py` | Python | oráculo de referencia y herramientas |

Además de correr programas, el repo ya incluye en **LOLCODE** los generadores
que lo construyen: `src/proofs_lol/tm_compile.lol` compila màquinas de Turing
a JAJAJA (byte-idéntico al generador Python, verificado por
`tools/compare_tm_compile.py`) y `src/proofs_lol/ja_encoding.lol` hace la
versión en risas puras (verificado con `tools/compare_ja_compile.py` y
`tools/compare_ja_run.py`). La suite nativa `tests/runtime_tests.lol`
corre 22 aserciones dentro de lci vía `test_lolcode_native.py`.

Guía operativa (en español, con salidas reales): `docs/GUIA_LOLCODE.md`.

Para correr sobre LOLCODE (requiere un intérprete `lci` disponible; ver
`backends/lolcode/README.md`):

```bash
python tools/run_jajaja_lol.py examples/hola.jaja
python tools/run_jajaja_lol.py examples/echo.jaja --input "hello"
```

Paridad demostrada: `python tools/parity_check.py` corre un corpus y compara
(output, steps, status) entre ambos runtimes. `python tools/turing_parity_lol.py`
verifica que los fixtures de Turing producidos por `proofs/tm_to_jajaja.py`
dan el mismo resultado en ambos runtimes. Evidencia en `evidence/lolcode_port/`.
El rol de Python: ver `docs/PYTHON_ORACLE_AND_LOLCODE.md`.

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

Contrato formal congelado en **[SPEC.md](SPEC.md)** (gana en caso de
conflicto); narrativa y diseño en **[JAJAJA_LANG.md](JAJAJA_LANG.md)**. Lo mínimo:

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

## Backend LOLCODE (demo de composición)

JAJAJA puede *targetear* otros lenguajes. Demo: Python como único frontend,
JAJAJA componiendo la petición, y **LOLCODE** (un lenguaje de bajo uso
soportado por GitHub Linguist) como backend ejecutando la semántica con un
runtime externo real (lci).

```bash
python demo_lolcode.py "ADD 2 3"     # 5   (SUM OF lo calcula LOLCODE)
python demo_lolcode.py "MAX 9 4"     # 9   (BIGGR OF + O RLY? branch)
python demo_lolcode.py "ECHO hola"   # hola (string real)
python demo_lolcode.py "COUNT 3"     # 3 2 1 0 (loop IM IN YR)
```

**Why this backend?** Para demostrar que la arquitectura no depende de un
backend convencional, esta demo conecta el frontend Python con *a low-usage
language supported by GitHub Linguist*: LOLCODE (19,904 archivos `.lol`
indexados vs ~360 millones de `.py`, medido 2026-09-03 vía GitHub Search
API; ver `evidence/lolcode_backend/LINGUIST_AUDIT.md`). No afirmamos que sea
"el menos usado de GitHub" — no existe ranking oficial y nuestra medición
encontró lenguajes con menos archivos (Befunge, 228). El punto es la
composición, no el récord.

Firma de honestidad del diseño:

- La regla de `route.jaja` que matchea decide qué op corre. Sin esa
  reescritura no hay llamada al backend (prueba: `"DIV 1 2"` no emite nada).
- Python nunca calcula el resultado: transporta y presenta.
- Sin runtime externo instalado, el sistema **falla ruidosamente** — no hay
  fallback secreto que calcule en Python.
- Docs y requisitos del runtime: `backends/lolcode/README.md`.

## Tests

159 comprobaciones, sin framework:

```bash
python test_jajaja.py                # 49 tests: intérprete + examples + runtime input + trace
python test_host.py                  # 51 tests: data model + host ABI + calculator + UI IR + FS
python test_backend_lolcode.py       # 30 tests: backend LOLCODE (e2e requiere runtime externo; sin él se omite el e2e y se prueba el fallo limpio)
python test_engine_does_the_work.py  # 9 checks adversariales: el host no roba el trabajo del lenguaje
python tools/conformance_run.py      # 20 casos del corpus de conformidad (un claim por caso)
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

## Archivos añadidos al repositorio (2026-10-31)

El commit `bd0f9b7` versiona el material que estaba sin control de versiones y que
sostiene la sección anterior: `SPEC.md`, `GOLDEN.md`, `CHANGELOG.md`,
`conformance/` (19 casos en `conformance/cases/` + `cases.json`),
`tools/conformance_run.py`, `tools/collect_evidence.py`,
`evidence/golden_v1/` (manifest, hashes y corridas en `runs/`) y
`test_engine_does_the_work.py`.


## Licencia

MIT.
