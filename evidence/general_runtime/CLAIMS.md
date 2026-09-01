# CLAIMS.md — Evidence-backed claims

## DEMONSTRATED

| Claim | Evidence | Status |
|---|---|---|
| TURING_COMPLETENESS | 7 MTs + ja_encoding proof | DEMONSTRATED |
| DETERMINISTIC_STEP | step() is first-match leftmost | DEMONSTRATED |
| REWRITE_SEMANTICS | Parser + 49 tests | DEMONSTRATED |
| RUNTIME_INPUT | stdin_data injection, 5 unique outputs | DEMONSTRATED |
| COMPILE_ONCE_TEST_MANY | Same SHA256 + 5 inputs → 5 outputs | DEMONSTRATED |
| STRUCTURED_OUTPUT | Compute in base, emit at end | DEMONSTRATED |
| TRACE_INVARIANT | trace_disabled output == trace_enabled output | DEMONSTRATED |
| TRACE_DETERMINISM | Same input → same trace | DEMONSTRATED |
| DATA_MODEL | Unary, decimal, list, record encodings | DEMONSTRATED |
| HOST_ABI | EFFECT/RESULT protocol | DEMONSTRATED |
| HOST_RUNTIME | host.py with capability allowlist | DEMONSTRATED |
| CALCULATOR | JAJAJA rules compute, Python prints | DEMONSTRATED |
| FS_SANDBOX | fs-read, fs-write, path traversal blocked | DEMONSTRATED |
| UI_IR | Declarative UI → HTML/terminal | DEMONSTRATED |
| CAPABILITY_DENY | Unknown capability rejected | DEMONSTRATED |

## POSSIBLE_BY_CONSTRUCTION

| Claim | Reason |
|---|---|
| HTTP_CLIENT | http-get effect defined, fixture mode |
| HTTP_SERVER | Can be built on EFFECT protocol |
| PERSISTENCE | KV store could be backed by filesystem |
| CONCURRENCY | Multiple machines could run in parallel |

## NOT_DEMONSTRATED

| Claim | Reason |
|---|---|
| PERSISTENCE | KV store is in-memory only |
| CONCURRENCY | Single-threaded execution |
| NATIVE_CODEGEN | No JIT or AOT compilation |
| BARE_METAL | Requires OS/hardware |

## OUT_OF_SCOPE

| Claim | Reason |
|---|---|
| BOOT | Requires hardware/ABI |
| INTERRUPTS | Requires hardware |
| MMU | Requires hardware |
| DRIVERS | Requires hardware |
