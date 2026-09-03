# LINGUIST_AUDIT — por qué LOLCODE y qué NO afirmamos

Fecha de medición: 2026-09-03.

## 1. ¿LOLCODE está en el catálogo de GitHub Linguist?

Sí. Fuente: `github-linguist/linguist`, rama `main`,
commit `d5214e1612c858ba14bf98edeca57e1683276f1d` (consultado 2026-09-03),
archivo `lib/linguist/languages.yml` (descarga vía raw.githubusercontent.com),
entrada:

```yaml
LOLCODE:
  type: programming
  extensions:
  - ".lol"
  color: "#cc9900"
  tm_scope: source.lolcode
  ace_mode: text
  language_id: 192
```

Veredicto: `LOLCODE_IN_LINGUIST_CATALOG = DEMONSTRATED`.

## 2. Método de medición

GitHub Search API (autenticada), una sola query por lenguaje con la forma
`extension:<ext>` (per_page=1, se lee `total_count`). Misma query, mismo
día, misma cuenta. Lenguajes cuya extensión canónica es compartida
(.bf también es Beef, .i también es C) se marcan como "shared-extension"
porque el conteo no los aísla.

| language   | ext canonical | in Linguist catalog | observed files | note |
|---|---|---|---|---|
| Lagoon     | .lagoon     | NOT in catalog | 8          | excluded: not recognized by Linguist |
| INTERCAL   | .i (shared) | NOT in catalog     | 23         | excluded on both grounds |
| Malbolge   | .malbolge   | NOT in catalog     | 38         | excluded: not recognized by Linguist |
| Piet       | .piet       | NOT in catalog     | 51         | excluded: not recognized by Linguist |
| Befunge    | .befunge    | yes (id 30)        | 228        | in-catalog, lowest measured |
| Unary      | .unl?       | yes? not verified  | 1,708      | not isolated |
| BQN        | .bqn        | yes (id 327207808) | 5,600      | not an esolang, measured as scale |
| Dylan      | .dylan      | yes (id 91)        | 8,976      | scale reference |
| **LOLCODE**| **.lol**    | **yes (id 192)**   | **19,904** | **selected backend** |
| Brainfuck  | .bf (shared)| yes (id 38)        | 62,208     | shared-extension caveat |
| Python     | .py         | yes                | 359,661,568| scale reference |

## 3. Veredictos

```
LINGUIST_ABSOLUTE_LEAST_USED = NOT_DEMONSTRATED
```

Razones: GitHub no publica un ranking oficial de "least used"; el count de
`extension:` es una aproximación (Search indexa un subconjunto del código
público), y nuestra shortlist no es exhaustiva.

```
LOWEST_MEASURED_IN_SHORTLIST = Befunge (228 archivos .befunge)
```

LOLCODE NO es el menor medido. Fue **elegido por decisión del autor del
proyecto** (chiste de la demo), no por salir ganador de la métrica.
Lo que sí se puede afirmar con evidencia:

```
LOLCODE_LOW_USAGE_VS_MAINSTREAM = DEMONSTRATED
  19,904 archivos .lol vs 359,661,568 .py (~0.0055%)
```

Redacción permitida: *"a low-usage language supported by GitHub Linguist"*.
Redacción prohibida: "the least-used language on GitHub".
