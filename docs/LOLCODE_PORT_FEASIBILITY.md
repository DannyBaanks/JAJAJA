# LOLCODE_PORT_FEASIBILITY — P0 audit of lci v1.3

Date: 2026-09-03. Runtime under audit: **lci v1.3** (justinmeza/lci, commit
`0b32ed1cc52abd1971d199db9bd77c387316cae1`), compiled locally from source
(MinGW gcc 16.1.0). All verdicts below come from executable probes
(`lci.exe <probe.lol>`), not from docs. Probe transcripts are summarized
inline; the strategic ones are reproduced.

Question: can a real JAJAJA (Markov rewriter) be written in LOLCODE for
lci, or are storage/string primitives missing?

## Verdicts per primitive

| Primitive | Verdict | Evidence |
|---|---|---|
| STRING equality (`BOTH SAEM`) | DEMONSTRATED | base in all probes |
| STRING concatenation (`SMOOSH ... MKAY`) | DEMONSTRATED | `p_smoosh.lol` -> `jajline` |
| Functions (`HOW IZ I / FOUND YR / IF U SAY SO`) | DEMONSTRATED | `p_func.lol` factorial(5)=120 |
| Recursion | DEMONSTRATED | same probe |
| Loops (`IM IN YR / IM OUTTA YR / GTFO`) | DEMONSTRATED | countdown probes |
| Branch (`O RLY? YA RLY / NO WAI / OIC`) | DEMONSTRATED | max/count probes |
| Stdin (`GIMMEH`) | DEMONSTRATED | sum/max/echo probes |
| EOF behavior of GIMMEH | DEMONSTRATED | EOF yields empty line, exit 0 -> protocol must use explicit sentinels |
| Stdout without newline (`VISIBLE x!`) | DEMONSTRATED | `p_eof.lol` output `linea uno|end` |
| Arrays / associative storage | DEMONSTRATED via BUKKIT | `B'Z slot` per lci's own test suite 12-Arrays |
| Dynamic slot names (`B'Z SRS <expr>`, `B HAS A SRS <expr> ITZ v`) | DEMONSTRATED | probes p_dyn2/p_dyn3; creation AND assignment work |
| Nested BUKKITs | DEMONSTRATED | probe p_nest2: `OUTER'Z SRS 0` -> inner bukkit read OK |
| Static var via SRS (`I HAS A SRS name`, `SRS name R ...` top level) | DEMONSTRATED | p_srs.lol |
| Block scoping | DEMONSTRATED (it is REAL) | probe p_perf2: a variable declared inside `O RLY?` does NOT exist after `OIC`. Structures must persist state on an outer-scope BUKKIT, which DOES survive blocks. |
| Assignment of an existing slot across blocks | DEMONSTRATED | perf probes write `B'Z ... R` inside loops |
| String indexing / substring search (native) | NOT_DEMONSTRATED | no such builtin in LOLCODE 1.3 or lci source |
| char->code / code->char (ord/chr) | NOT_DEMONSTRATED | no builtin |
| File I/O | NOT_DEMONSTRATED | no file ops in the language |
| Sockets / argv | NOT_DEMONSTRATED | lci CLI runs a single file only |

## Consequence for design (evidence-driven)

LOLCODE has arrays (BUKKIT with dynamic slots, incl. numeric) and
recursion, but **no string indexing**. Therefore:

1. The base is stored as a BUKKIT of characters (index -> 1-char string).
2. Rules keep lhs/rhs as BUKKITs of characters too.
3. Match = character-by-character leftmost scan (`find` hand-implemented),
   which is exactly the Python reference semantics (`base.find(lhs)`,
   first rule in order, leftmost occurrence).
4. Input arrives as a LINE STREAM (one character per line; control
   characters escaped) because GIMMEH cannot read a lone `\n`. The
   launcher that produces this stream does transport only (no parsing,
   no rules knowledge).
5. Output is emitted character by character with `VISIBLE ...!`.

## Performance measurement (matters for parity runs)

100k BUKKIT slot writes + 100k dynamic reads (numeric SRS keys):
~10.5 s locally (~9.5k slot-ops/s). Markov steps for the repo's fixture
corpus are in the hundreds-to-thousands range with bases under ~200
chars: estimated seconds-to-minutes per fixture. Feasible; if a specific
fixture gets too slow that will be recorded per-fixture in parity.json,
and the parity table will never claim parity for fixtures not run.

## What Python keeps doing during the port

Python = oracle reference (`jajaja_interpreter.py`) + transport launcher
(GIMMEH stream producer). Nothing semantic.

## Known NOT-portable edges (documented before coding)

- Python `str.splitlines()` splits on Unicode line-boundaries
  (`\x85`, `\u2028`...). The launcher normalizes newlines; parity is
  claimed for \n and \r\n sources (which is what the repo fixtures use).
- Control characters other than CR/LF/TAB would need ord encoding that
  LOLCODE cannot materialize back into output strings; not present in the
  current corpus. Recorded as a limitation, not patched over.
