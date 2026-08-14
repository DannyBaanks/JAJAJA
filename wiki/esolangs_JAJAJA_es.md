# JAJAJA

**JAJAJA** es un lenguaje de programación esotérico creado por
[DannyBaanks](https://esolangs.org/wiki/User:DannyBaanks) en 2026, basado en
**reescritura de cadenas determinista**. Su alfabeto semántico son repeticiones
del token `ja`, y
el número de risas contiguas *es* la identidad del símbolo. Un programa JAJAJA
se lee como una carcajada para cualquier hispanohablante y al mismo tiempo es un
sistema formal de reescritura.

Es pariente determinista de [Thue](https://esolangs.org/wiki/Thue), de quien
hereda la sintaxis de superficie.

> Esta es la versión en español del artículo. La versión publicada en
> esolangs.org está en inglés (`esolangs_JAJAJA.wiki`) porque ese wiki es
> anglófono de facto: su política pide *"read the articles to absorb our
> style"*, y los cientos de artículos existentes están en inglés. Un artículo
> íntegro en español sería traducido o revertido, no por hostilidad sino por
> convención. Lo que sí viaja al inglés intacto es el lenguaje mismo: los
> programas siguen siendo risas en español, y eso ningún editor lo traduce.

## Relación con Thue

JAJAJA usa el formato de programa de Thue y su notación de salida, pero no su
estrategia de evaluación. Thue es **no determinista**: en cada paso puede
aplicarse *cualquier* regla aplicable en *cualquier* posición que matchee.
JAJAJA no. Recorre las reglas en el orden en que fueron escritas, aplica la
primera cuyo lado izquierdo aparezca en el estado, y la aplica en la ocurrencia
más a la izquierda.

Lista ordenada de reglas · primera regla aplicable · ocurrencia más a la
izquierda · parar cuando ninguna aplica. Eso es exactamente un **algoritmo
normal de Markov**, no un sistema semi-Thue. Es un modelo de computación
distinto, no uno más débil: los algoritmos de Markov son Turing completos.

JAJAJA tampoco tiene entrada. La regla `::=:::` de Thue no existe.

## Descripción del lenguaje

Un programa es una lista de reglas de la forma

```
<lado izquierdo>::=<lado derecho>
```

terminada por una línea que contiene solo `::=` (se tolera whitespace
alrededor), seguida de una sola línea con el estado inicial, llamado **base**:

```
jajaja::=~JAJAJA-OK
j::=~
::=
jajaja j
```

Solo la primera línea no vacía y no comentada después del separador se vuelve la
base; las siguientes se ignoran en silencio. A diferencia de Thue, la base no
puede ocupar varias líneas.

Una línea cuyo **primer carácter** sea `#` es un comentario. La prueba se hace
sobre la línea cruda, así que un `#` *indentado* es un error de sintaxis, no un
comentario, mientras se leen reglas. Después del separador la prueba se aplica a
la línea recortada, así que ahí sí se saltan comentarios indentados y líneas en
blanco. Una línea en posición de regla que no contenga `::=` es error de
sintaxis.

El whitespace dentro de una regla es significativo: forma parte del lado
izquierdo o derecho. Solo el primer `::=` de la línea separa ambos lados; los
`::=` posteriores pertenecen al lado derecho.

## Semántica

La ejecución repite este paso:

1. Recorrer las reglas en el orden en que fueron escritas.
2. Tomar la primera cuyo lado izquierdo aparezca en la base, en su ocurrencia
   más a la izquierda. Las reglas con lado izquierdo vacío se saltan.
3. Si el lado derecho empieza con `~`, emitir el resto y **borrar** el match de
   la base. Un `~` solo emite un salto de línea.
4. Si no, reemplazar el match por el lado derecho.

El programa termina cuando ninguna regla aplica. Como la reescritura puede no
terminar, los intérpretes imponen un presupuesto de pasos.

Como la selección es por orden de regla y no por longitud del match, **el orden
en que se escriben las reglas es semántico**. Las risas largas van antes que las
cortas que son su prefijo; si no, la regla corta reescribe dentro de su propio
resultado y el programa no termina nunca:

```
jajaja::=~TRES
jaja::=jajaja
::=
jaja
```

emite `TRES` y termina en dos pasos. Con las dos reglas invertidas, en cambio,
se cuelga: `jaja` sigue matcheando dentro del `jajaja` que acaba de producir.

## Ejemplos

### ¡Hola, mundo!

El lenguaje es español, y su primer programa también:

```
# hola_mundo.jaja
jaja::=~¡Hola, mundo!
j::=~
::=
jaja j
```

La risa de dos emite el saludo y se borra; la risa de uno que queda emite el
salto de línea. Termina en dos pasos.

### Hello, world!

El mismo programa con el saludo en inglés, que al final el fuente son risas
igual:

```
# hola.jaja
jaja::=~Hello, world!
j::=~
::=
jaja j
```

### Amplificación

Una risa de dos se amplifica a tres antes de emitirse:

```
jajaja::=~jajaja!
jaja::=jajaja
::=
jaja
```

La base se reescribe primero a `jajaja`, que la primera regla entonces emite,
dejando nada que matchear. Emite `jajaja!` en dos pasos. Ojo con el orden de las
reglas, según la sección anterior.

### Eco

```
jajaja::=~jajaja jajaja
j::=~
::=
jajaja j
```

Emite `jajaja jajaja` seguido de un salto de línea.

## Clase computacional

JAJAJA es **Turing completo**. La implementación de referencia incluye un
compilador uniforme de máquina de Turing de una cinta a programa JAJAJA, junto
con una prueba diferencial que corre siete máquinas contra un simulador de
referencia y compara las cintas resultantes. La traducción es *uniforme* —toma
una máquina como dato—, así que los tests verifican la traducción, no sustituyen
a la afirmación. Como es habitual en estos argumentos, el resultado supone cinta
ilimitada; toda corrida real está acotada por el presupuesto de pasos.

Un matiz que conviene decir, porque es fácil equivocarse: el **alfabeto de risas
puro** es Turing completo **solo con delimitador**. La codificación unaria sin
delimitador es ambigua, porque `jaja` es substring de `jajaja`, y entonces las
reglas se muerden entre sí. El espacio en `jaja j` —presente en todos los
ejemplos— es estructural, no cosmético. Con delimitador la ambigüedad
desaparece.

El motor en sí acepta tokens arbitrarios: `Hola::=mundo` es una regla válida y
ejecutable. Restringir los programas a risas es una convención estilística del
lenguaje, no una restricción que imponga el intérprete, y eso hace el argumento
de completitud más fácil, no más difícil.

## Implementaciones

- [Intérprete de referencia en Python](https://github.com/DannyBaanks/ISyCo),
  con la especificación y la prueba de Turing completitud.
- Implementación en JavaScript que corre en el navegador dentro de
  [Interpret Esolangs Online](https://github.com/none-None1/Interpret-Esolangs-Online),
  portada desde el intérprete de referencia y verificada contra él sobre un
  corpus de conformidad compartido.
