# HOST_BOUNDARY.md — Language vs Host separation

## Language Capabilities (JAJAJA)
- String rewriting (Markov normal algorithm)
- Rule priority (first-rule, leftmost-match)
- Emission via `~` rules
- Runtime input via stdin_data injection
- Structured computation via in-base transformation

## Host Capabilities (host.py)
- Effect dispatch (EFFECT/RESULT protocol)
- Capability allowlist
- Filesystem sandbox
- Standard I/O (stdin, stdout)
- Key-value store
- HTTP client (fixture mode)
- Clock

## The Boundary
- JAJAJA decides WHAT effects to request
- host.py executes them
- JAJAJA does NOT know about Python, files, network, or OS
- host.py does NOT contain program-specific logic

## Evidence
- calculator.jaja: JAJAJA rules match patterns, host prints result
- host.py dispatch: generic effect handler, no program-specific code
- FS sandbox: path traversal blocked at host level
- Capability deny: unknown capabilities rejected by host
