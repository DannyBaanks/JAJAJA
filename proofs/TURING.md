# ¿JAJAJA es Turing completo?

**Sí, el motor lo es.** El alfabeto de risas también, pero sólo con
delimitador — y eso la spec no lo decía.

Este documento no pide que le creas: hay dos scripts que se corren y verifican
solos.

```bash
python proofs/tm_to_jajaja.py    # 7 casos, 0 fallos
python proofs/ja_encoding.py     # ambigüedad + MT en risas puras
```

---

## 1. Qué es JAJAJA, en realidad

La spec dice "familia Thue". Es más preciso que eso, y la precisión importa.

Thue es **no determinista**: en cada paso se puede aplicar cualquier regla
aplicable, en cualquier posición. JAJAJA no. Mirando `step()`:

```python
def step(self) -> bool:
    for lhs, rhs in self.rules:          # las reglas, EN ORDEN
        idx = self.base.find(lhs)        # la ocurrencia MÁS A LA IZQUIERDA
        if idx >= 0:
            ...                          # aplica y termina el paso
            return True
    return False                          # ninguna aplica -> HALT
```

Lista ordenada de reglas · primera regla aplicable · ocurrencia más a la
izquierda · parar cuando ninguna aplica. Eso es exactamente un **algoritmo
normal de Markov** (Markov, 1951), no un sistema Thue.

Y eso es una buena noticia, porque los algoritmos normales de Markov son uno de
los modelos clásicos de computación, equivalente a las máquinas de Turing. La
determinización no debilita el modelo: lo vuelve un modelo distinto, igual de
potente.

> **Detalle:** los algoritmos de Markov clásicos tienen *reglas terminales*
> (`→·`) que detienen la ejecución. JAJAJA no las tiene, sólo para cuando
> ninguna regla matchea. No hace falta: alcanza con que la configuración final
> no matchee nada, y la construcción de abajo lo consigue así.

## 2. La prueba constructiva

No nos apoyamos en el teorema. `proofs/tm_to_jajaja.py` implementa una
**traducción mecánica y uniforme**: recibe una MT arbitraria como datos y
escupe un programa JAJAJA. No hay nada hecho a mano por máquina.

### Codificación

Una configuración entera vive en una sola cadena:

```
| izquierda <q> símbolo derecha $
```

`|` y `$` son topes de cinta. `<q>` es el estado, puesto justo a la izquierda
de la celda bajo el cabezal.

**El marcador de estado aparece exactamente una vez.** De ahí sale todo: como
sólo hay una ocurrencia, "la más a la izquierda" no es una elección, es *la*
posición del cabezal. El no determinismo posicional desaparece sin pedirle nada
al lenguaje.

### Las reglas

```
δ(q,s) = (q', s', R)   ->   <q>s   ::= s'<q'>
δ(q,s) = (q', s', L)   ->   x<q>s  ::= <q'>xs'      (una regla por cada x)
                            |<q>s  ::= |<q'>_s'     (extiende por la izquierda)
cinta infinita a la derecha ->   <q>$  ::= <q>_$
```

El movimiento a la izquierda necesita una regla por cada símbolo posible de
cinta, porque el `rhs` tiene que reponer lo que había a la izquierda y el
sistema de reescritura no tiene variables. Es finito: |Γ| reglas por
transición.

### El orden de las reglas es parte de la construcción

Las reglas de extensión de cinta van **primero**. `<q>$` sólo matchea cuando el
cabezal se salió de la parte escrita, así que no le roba el turno a ninguna
transición real. Si fueran al final, nunca se alcanzarían.

Esto no es un detalle de implementación: en un modelo de prioridad por orden,
**el orden es semántica**. Es la misma trampa que documenta la §5.3 de la spec.

### Verificación

Cada caso corre en dos motores independientes —un simulador de MT en Python y
el intérprete JAJAJA real— y se comparan las cintas finales:

```
OK    binary_increment('1011')   ref '1100'  ->  jajaja '1100'   (10 pasos, HALTED)
OK    binary_increment('111')    ref '1000'  ->  jajaja '1000'
OK    binary_increment('0')      ref '1'     ->  jajaja '1'
OK    bit_flip('1011')           ref '0100'  ->  jajaja '0100'
OK    bit_flip('0000')           ref '1111'  ->  jajaja '1111'
OK    parity('1111')             ref '1111P' ->  jajaja '1111P'
OK    parity('11111')            ref '11111I'->  jajaja '11111I'

casos=7 fallos=0
```

Las máquinas ejercitan movimiento a derecha, a izquierda, propagación de
acarreo, extensión de cinta en ambos extremos, y alternancia de estados.

## 3. El alfabeto de risas: acá está el matiz

Lo anterior usa tokens arbitrarios (`<seek>`, `0`, `1`, `|`, `$`). El motor los
acepta —el alfabeto `ja` es convención, no restricción— así que **el motor es
Turing completo**, sin discusión.

Pero la §7 de la spec afirma algo más fuerte: que el conteo de `ja` es una
codificación unaria del alfabeto de Thue, o sea que el lenguaje sigue siendo
Turing completo **usando sólo risas**. Eso **no es automático**.

### El problema: la unaria sin delimitador es ambigua

```
símbolo 2  =  "jaja"
símbolo 3  =  "jajaja"

¿"jaja" es substring de "jajaja"?          True
símbolo2 + símbolo3  =  "jajajajaja"
símbolo 5            =  "jajajajaja"       ← la misma cadena
```

Y como JAJAJA matchea por substring, no es teórico. Medido:

```
programa:  jaja::=~MORDIO
           ::=
           jajaja                    ← la base es SÓLO el símbolo 3

resultado: output='MORDIO'  steps=1  status=HALTED
```

La regla del símbolo 2 se disparó **dentro** del símbolo 3. Con esa codificación
una máquina se corrompe sola.

### La solución, que la spec ya usaba sin decirlo

Un delimitador. `' jaja '` **no** es substring de `' jajaja '`, y la ambigüedad
desaparece.

Los ejemplos de la spec siempre escribieron `jaja j`, con espacio. **Ese espacio
es estructural, no cosmético**, y en ningún lado se decía.

### Una MT corriendo en risas puras

`proofs/ja_encoding.py` reencodea toda la construcción de la §2 a risas:

```
OK   binary_increment('1011')    esperado '1100'  ->  en risas '1100'  (9 pasos, HALTED)
OK   bit_flip('1011')            esperado '0100'  ->  en risas '0100'  (6 pasos, HALTED)

alfabeto de reglas y cinta: ['a', 'j']
```

Reglas, cinta y estados: **sólo `j` y `a`**.

## 4. Lo que encontramos construyendo la prueba

Tres cosas reales, ninguna fatal, todas nuevas para la spec:

**Las reglas de salida son incompatibles con codificaciones delimitadas.** Una
regla `~` borra el match **entero, delimitadores incluidos**, y al hacerlo
fusiona a sus dos vecinos en un solo token. En la versión en risas puras, una
regla emisora de firma corrompía la cinta: salía `'100'` en vez de `'1100'`, y
en `bit_flip` la firma se emitía tres veces mientras la cinta se deshacía. Por
eso ahí se computa **en la cinta, no en el output**.

Consecuencia general: una regla `~` puede emitir o puede preservar estructura,
nunca las dos. El `rhs` de una regla emisora es texto plano, así que no puede
reponer un cursor ni un delimitador.

**La base no puede empezar con `#`.** Una línea que arranca con `#` es un
comentario, así que ese carácter no sirve como tope izquierdo de cinta.
Descubierto compilando esto mismo: la base salía comentada entera y la máquina
"terminaba" en 0 pasos con la cinta vacía. Por eso el tope es `|`.

**JAJAJA es Markov, no Thue.** Ver §1. La spec lo llama Thue y aclara
"determinista en v1"; la identificación precisa es más útil, porque explica de
dónde sale la potencia sin depender del no determinismo.

## 5. Qué NO prueba esto

- **No prueba nada sobre terminación.** Turing completo implica, por
  construcción, que el problema de la parada de JAJAJA es indecidible. El
  `max_steps` del intérprete es una cota práctica, no un resultado.
- **Asume cinta ilimitada.** Toda corrida real está acotada por `max_steps` y
  por la memoria. Es el supuesto estándar de cualquier argumento de este tipo.
- **Es una prueba por simulación en un sentido.** Muestra que JAJAJA simula
  cualquier MT. Que el intérprete de JAJAJA es a su vez simulable por una MT es
  evidente —son 128 líneas de Python determinista— pero no está formalizado acá.
- **7 máquinas no son todas las máquinas.** Lo que hace de esto una prueba y no
  siete anécdotas es que la traducción es **uniforme**: `compile_tm` toma una MT
  arbitraria como datos. Los 7 casos verifican la traducción, no la afirmación.

## Veredicto

| Pregunta | Respuesta |
|---|---|
| ¿El motor de JAJAJA es Turing completo? | **Sí** — es un algoritmo normal de Markov, y hay traducción MT→JAJAJA uniforme y verificada |
| ¿El alfabeto `ja` solo es Turing completo? | **Sí, con delimitador.** Sin delimitador la codificación unaria es ambigua y las reglas se muerden |
| ¿La spec lo decía bien? | No. Afirmaba la completitud del alfabeto sin mencionar que el espacio de sus propios ejemplos la sostiene |

---

*Otras rutas llegan al mismo lugar: simular una máquina de registros de Minsky
(dos contadores alcanzan) es una construcción alternativa y perfectamente
válida. Acá se eligió la MT porque la codificación de configuración en una sola
cadena hace visible por qué el marcador de estado único elimina la ambigüedad
posicional — que es la parte no obvia.*
