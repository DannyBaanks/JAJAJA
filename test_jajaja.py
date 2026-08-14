"""test_jajaja.py - Tests para Jajaja (intérprete + ejemplos).

Cubre:
  1. import/startup
  2. hola.jaja -> output exacto
  3. amplificacion.jaja -> reescritura real, output exacto
  4. eco.jaja -> regla que emite dos copias
  5. bootstrap.jaja -> firma canónica
  6. invalid-input: regla sin ::= -> SYNTAX_ERROR
  7. loop.jaja -> MAX_STEPS (limite de ejecucion, no crash)
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from jajaja_interpreter import run  # noqa: E402

passed = 0
failed = 0


def check(name, got, want):
    global passed, failed
    ok = got == want
    print(("OK   " if ok else "FAIL ") + name)
    if not ok:
        print("    got =", repr(got))
        print("   want =", repr(want))
        failed += 1
    else:
        passed += 1


# 1. import/startup
check("1 import/startup",
      bool(callable(run)), True)

# 2. hola.jaja -> output exacto
src = (HERE / "examples" / "hola.jaja").read_text(encoding="utf-8")
got = run(src, max_steps=200000)
check("2 hola.jaja output",
      got, ("Hello, world!\n", 2, "HALTED"))

# 3. amplificacion.jaja -> reescritura real, output exacto
src = (HERE / "examples" / "amplificacion.jaja").read_text(encoding="utf-8")
got = run(src, max_steps=200000)
check("3 amplificacion.jaja output",
      got, ("jajaja! \n", 3, "HALTED"))

# 4. eco.jaja -> regla que emite dos copias
src = (HERE / "examples" / "eco.jaja").read_text(encoding="utf-8")
got = run(src, max_steps=200000)
check("4 eco.jaja output",
      got, ("jajaja jajaja\n", 2, "HALTED"))

# 5. bootstrap.jaja -> firma canonica
src = (HERE / "bootstrap.jaja").read_text(encoding="utf-8")
got = run(src, max_steps=200000)
check("5 bootstrap signature",
      got, ("JAJAJA-OK\n", 2, "HALTED"))

# 6. invalid-input: regla sin ::=
src = "jaja no es regla\n::=\njaja\n"
got = run(src, max_steps=200000)
check("6 invalid-input syntax error",
      got, ("", 0, "SYNTAX_ERROR: regla sin '::=' en linea 1: 'jaja no es regla'"))

# 7. loop.jaja -> MAX_STEPS
src = (HERE / "examples" / "loop.jaja").read_text(encoding="utf-8")
got = run(src, max_steps=1000)
check("7 loop.jaja MAX_STEPS at 1000", got[1], 1000)
check("7b loop.jaja status MAX_STEPS", got[2], "MAX_STEPS")

# 8. CRLF regression: .jaja con \r\n debe parsear igual que \n
src = (HERE / "examples" / "bootstrap_crlf.jaja").read_bytes().decode("utf-8")
got = run(src, max_steps=200000)
check("8 CRLF bootstrap signature", got, ("JAJAJA-OK\n", 2, "HALTED"))

# 9. separador con whitespace tolerate: "::= " con trailing spaces
src = "jajaja::=~X\n::=   \njajaja j\n"
got = run(src, max_steps=200000)
check("9 separador tolerante a whitespace",
      got, ("X", 1, "HALTED"))

# 10. alfabeto: acepta tokens no-ja (Thue-completo), convencion no restriccion
# La regla reescribe Hola -> mundo en base; no emitir (rhs no empieza con ~)
src = "Hola::=mundo\n::=\nHola\n"
got = run(src, max_steps=200000)
check("10 Thue-completo: tokens arbitrarios",
      got, ("", 1, "HALTED"))

# ---------------------------------------------------------------------------
# 11-16. Los ejemplos de JAJAJA_LANG.md se EJECUTAN, no se leen.
#
# Motivo: la spec afirmaba que el ejemplo §5.3 "termina en un solo ciclo".
# Corrido de verdad no terminaba nunca y no emitía nada -- la regla `jaja`
# rematcheaba dentro de su propio resultado. Nadie lo notó porque ningún test
# ejecutaba los ejemplos documentados; los 10 tests de arriba pasaban en verde
# con la spec rota.
#
# Cada caso comprueba DOS cosas: que el programa haga lo documentado, y que ese
# programa siga literalmente presente en la spec. Si alguien edita el ejemplo
# en el .md, el segundo assert falla y la doc no puede desincronizarse en
# silencio otra vez.
# ---------------------------------------------------------------------------
SPEC = (HERE / "JAJAJA_LANG.md").read_text(encoding="utf-8")


def check_spec_example(name, source, want):
    """Ejecuta un ejemplo y verifica que siga textualmente en la spec."""
    check(name + " (ejecuta)", run(source, max_steps=2000), want)
    check(name + " (está en la spec)", source.strip() in SPEC, True)


# 11. §5.1 Hello, world!
check_spec_example(
    "11 spec §5.1 hola",
    "jaja::=~Hello, world!\nj::=~\n::=\njaja j",
    ("Hello, world!\n", 2, "HALTED"))

# 12. §5.2 amplificación
check_spec_example(
    "12 spec §5.2 amplificacion",
    "jajaja::=~jajaja! \njaja::=jajaja\nj::=~\n::=\njaja j",
    ("jajaja! \n", 3, "HALTED"))

# 13. §5.3 amplificación por etapas (orden correcto: lhs más largo primero)
check_spec_example(
    "13 spec §5.3 orden correcto",
    "jajajaja::=~jajajaja!\njaja::=jajajaja\nj::=~\n::=\njaja j",
    ("jajajaja!\n", 3, "HALTED"))

# 14. §5.3 anti-ejemplo: el orden invertido NO termina. La spec lo documenta
#     como trampa; acá se fija que siga siendo cierto lo que se documenta.
check_spec_example(
    "14 spec §5.3 anti-ejemplo no termina",
    "jaja::=jajajaja\njajajaja::=~jajajaja!\nj::=~\n::=\njaja j",
    ("", 2000, "MAX_STEPS"))

# 15. §3 base = primera línea NO-VACÍA tras el separador (lo que la spec dice).
#     Antes se tomaba la primera línea a secas y una línea en blanco dejaba la
#     cinta vacía: HALT sin salida y sin error.
check("15 base salta lineas en blanco",
      run("jaja::=~X\n::=\n\njaja\n"), ("X", 1, "HALTED"))

# 16. ...y salta comentarios, que en modo reglas ya se saltaban.
check("16 base salta comentarios",
      run("jaja::=~X\n::=\n# esto es un comentario\njaja\n"), ("X", 1, "HALTED"))

# 17. Notación de salida: `::=~` emite; `::~` no es una regla válida.
#     Las tablas §2 y §7 documentaban `::~text`, que no parsea.
check("17a notacion ::=~ emite",
      run("jajaja::=~Hola\n::=\njajaja\n"), ("Hola", 1, "HALTED"))
check("17b notacion ::~ es error de sintaxis",
      run("jajaja::~Hola\n::=\njajaja\n")[2].startswith("SYNTAX_ERROR"), True)
check("17c la spec ya no documenta ::~",
      "`::~" in SPEC, False)

# 18. §7.1 la codificación unaria sin delimitador es ambigua: la regla del
#     símbolo 2 muerde dentro del símbolo 3. Es el ejemplo que documenta por qué
#     el espacio de `jaja j` es estructural. Prueba completa en proofs/TURING.md.
check_spec_example(
    "18 spec §7.1 ambiguedad sin delimitador",
    "jaja::=~MORDIO\n::=\njajaja",
    ("MORDIO", 1, "HALTED"))

# 19. ...y con delimitador deja de morder: ` jaja ` no ocurre en ` jajaja `.
check("19 delimitador desambigua",
      " jaja " in " jajaja ", False)

print()
print("passed=%d failed=%d" % (passed, failed))
sys.exit(0 if failed == 0 else 1)
