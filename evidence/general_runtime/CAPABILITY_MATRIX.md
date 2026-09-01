# CAPABILITY_MATRIX.md — What JAJAJA can and cannot do

## Language Level

| Capability | Status | Evidence |
|---|---|---|
| Arbitrary computation | DEMONSTRATED | 7 MTs, Turing proof |
| State machines | DEMONSTRATED | Markov normal algorithm |
| Structured data | DEMONSTRATED | Data model (unary, decimal, list, record) |
| Control flow | POSSIBLE_BY_CONSTRUCTION | Rules = implicit control flow |
| I/O requests | DEMONSTRATED | EFFECT/RESULT protocol |
| Filesystem model | DEMONSTRATED | host.py fs-read, fs-write (sandboxed) |
| Networking model | POSSIBLE_BY_CONSTRUCTION | http-get effect (fixture mode) |
| UI model | DEMONSTRATED | UI IR → HTML/terminal renderer |

## Hosted Runtime Level

| Capability | Status | Evidence |
|---|---|---|
| Files | DEMONSTRATED | fs-read, fs-write with sandbox |
| Network | POSSIBLE_BY_CONSTRUCTION | http-get effect defined |
| Display | DEMONSTRATED | UI IR renders to HTML |
| Input | DEMONSTRATED | stdin_data injection |
| Persistence | NOT_DEMONSTRATED | KV store is in-memory only |
| Concurrency | NOT_DEMONSTRATED | Single-threaded execution |

## Bare Metal Level

| Capability | Status | Evidence |
|---|---|---|
| Boot | OUT_OF_SCOPE | Requires OS/hardware |
| Interrupts | OUT_OF_SCOPE | Requires hardware |
| MMU | OUT_OF_SCOPE | Requires hardware |
| Drivers | OUT_OF_SCOPE | Requires hardware |
| Hardware access | OUT_OF_SCOPE | Requires hardware |
| Scheduler | OUT_OF_SCOPE | Requires OS |
| Executable codegen | NOT_DEMONSTRATED | No native code generation |

## Summary

JAJAJA's language semantics are not the limiting factor for general hosted software construction. The language can express arbitrary computation, state machines, structured data, and I/O requests. The host runtime materializes capabilities. What's missing is persistence, concurrency, and bare metal access — which are host capabilities, not language capabilities.
