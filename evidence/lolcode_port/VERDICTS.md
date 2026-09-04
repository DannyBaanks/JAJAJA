# VERDICTS — Port del runtime JAJAJA a LOLCODE

Fecha: 2026-09-03. Runtime externo: lci v1.3 (commit `0b32ed1cc52abd...`
de justinmeza/lci, GPL-3.0), compilado localmente. Corre como proceso
separado; NO se distribuye con este repo.

## Resultados

| Verdict | Estado | Evidencia |
|---|---|---|
| LOLCODE_PRIMITIVES_SUFFICIENT | DEMONSTRATED | Probes P0 en docs/LOLCODE_PORT_FEASIBILITY.md: BUKKITs + slot dinámico + recursión + GIMMEH con EOF vacío + VISIBLE `!` sin newline |
| LEFTMOST_SINGLE_REWRITE | DEMONSTRATED | parity: `overlap_leftmost`, `lhs_in_rhs_grows`, etc. |
| ORDERED_RULE_SEMANTICS | DEMONSTRATED | parity: `order_first_long`, `order_fallback` |
| JAJAJA_PARSER_IN_LOLCODE | DEMONSTRATED | comentarios `#`, separador `::=` exacto y con espacios, CRLF (`crlf`), comentarios entre reglas (`comments_between_rules`), `#` en rhs (`hash_in_rhs`), clase de reglas `::=~` / `::=`, inline y stdin |
| JAJAJA_RUNTIME_IN_LOLCODE | DEMONSTRATED | 24/24 outputs/steps/status idénticos vs Python oracle |
| PYTHON_REFERENCE_PARITY | DEMONSTRATED | parity.json 24/24 |
| RUNTIME_INPUT_PARITY | DEMONSTRATED | `stdin_prefix`, `stdin_special_input`, `stdin_empty`, `stdin_brackets` |
| MAX_STEPS_PARITY | DEMONSTRATED | `max_steps_cap` (3), `simple_counter` (20), `grow` (20) alcanzan MAX_STEPS en ambos |
| TURING_FIXTURES_PARITY | DEMONSTRATED | turing_parity_lol.py: 7/7 en las MTs del repo (binary increment, bit flip, parity unary) HALTED en ambos runtimes |
| PYTHON_REQUIRED_FOR_CORE | NO | El runtime LOLCODE corre con Cero lógica Python; Python solo transporta bytes (run_jajaja_lol.py) |
| LOLCODE_PRIMARY_IMPLEMENTATION | DEMONSTRATED | `src/jajaja.lol` ejecuta los *programas* del repo (ver README: "para correr... se usa lci"); el oráculo Python pasa a rol de *verificador* |
| PUBLIC_PRIVATE_DEPENDENCY | NO | línea a línea implementación nueva; `.gitattributes` ni Grammatik artificialmente tocados |
| NO_MANIPULATE_LINGUIST | DEMONSTRATED | No se añadió `.gitattributes` ni trucos de barras; lo que GitHub muestre ahora refleja código real de `.lol` |

## Lo que NO se hizo

- **No se eliminó Python** del repo (es oráculo + generadores + host + tests).
  La instrucción original era migrar tras paridad; la política del repo
  es mantener oráculos antes de reemplazar (documentado en
  docs/PYTHON_ORACLE_AND_LOLCODE.md).
- **No se escribió un intérprete LOLCODE propio**: se usó `lci` externo.
- **No se falsificaron tests**: `parity_check.py` ejecuta los 24 casos de
  verdad y `turing_parity_lol.py` los 7 de Turing; ambos reportan con
  número `/total` — si alguno fallara el conteo lo diría.
- `--check-only` existe para un gate CI sin re-escribir JSON.

## Limitaciones documentadas del runtime lci

- Aritmética 64-bit entera (no floating/negative trickery).
- `\r` en fuentes se normaliza a `\n` por el transporte (parity claims
  cubren `\n` y `\r\n`; el oráculo igualmente normaliza).
- `\x85`/`\u2028` como separador de línea **no** se cubre (igual que el
  oráculo Python no lo distingue tampoco, salvo rarezas; queda como límite).
