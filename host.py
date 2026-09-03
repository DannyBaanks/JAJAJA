"""host.py — Minimal JAJAJA host runtime.

Runs a .jaja program with:
- Effect dispatch (EFFECT/RESULT protocol)
- Explicit capability allowlist
- Sandboxed filesystem
- Receipt logging

Usage:
    python host.py program.jaja
    python host.py program.jaja --input "hello"
    python host.py program.jaja --max-steps 10000
    python host.py program.jaja --allow stdin,stdout,kv
    python host.py program.jaja --allow fs-read,fs-write --root ./sandbox
    python host.py program.jaja --trace

Rules:
    host.py does NOT contain program-specific logic.
    JAJAJA decides what effects to request.
    host.py only validates, authorizes, executes, returns.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jajaja_interpreter import Jajaja
from jajaja_stdlib import (
    EFFECT_PREFIX, RESULT_PREFIX,
    parse_effect, make_result,
    handle_stdin, handle_stdout,
    handle_kv_get, handle_kv_set,
    handle_fs_read, handle_fs_write,
    handle_clock, handle_http_get,
)

# ─── Capability Registry ───────────────────────────────────────────

CAPABILITIES = {
    "stdin":     {"handler": "stdin",     "needs": []},
    "stdout":    {"handler": "stdout",    "needs": []},
    "kv-get":    {"handler": "kv-get",    "needs": ["kv"]},
    "kv-set":    {"handler": "kv-set",    "needs": ["kv"]},
    "fs-read":   {"handler": "fs-read",   "needs": ["fs-read"]},
    "fs-write":  {"handler": "fs-write",  "needs": ["fs-write"]},
    "clock":     {"handler": "clock",     "needs": []},
    "http-get":  {"handler": "http-get",  "needs": ["http"]},
    "lolcode":   {"handler": "lolcode",   "needs": ["lolcode"]},
}

DEPENDENCY_MAP = {
    "kv":       ["kv-get", "kv-set"],
    "fs-read":  ["fs-read"],
    "fs-write": ["fs-write"],
    "http":     ["http-get"],
    "io":       ["stdin", "stdout"],
}


def expand_allow(allow: list[str]) -> set[str]:
    """Expand shorthand capability groups into individual capabilities."""
    result = set()
    for cap in allow:
        if cap in DEPENDENCY_MAP:
            result.update(DEPENDENCY_MAP[cap])
        else:
            result.add(cap)
    return result


def dispatch_effect(
    effect: dict,
    allowed: set[str],
    state: dict,
) -> tuple[str, str]:
    """Dispatch a single effect. Returns (status, payload)."""
    cap = effect.get("capability", "")
    if cap not in allowed:
        return "DENY", f"capability {cap!r} not in allowlist"
    if cap not in CAPABILITIES:
        return "DENY", f"unknown capability {cap!r}"

    req_id = effect.get("request_id", "0")
    args = {k: v for k, v in effect.items() if k not in ("request_id", "capability")}

    try:
        if cap == "stdin":
            payload = handle_stdin(args, state.get("stdin_data", ""))
            return "OK", payload
        elif cap == "stdout":
            handle_stdout(args)
            return "OK", ""
        elif cap == "kv-get":
            return "OK", handle_kv_get(args, state["kv"])
        elif cap == "kv-set":
            return "OK", handle_kv_set(args, state["kv"])
        elif cap == "fs-read":
            return "OK", handle_fs_read(args, state.get("fs_root", "."))
        elif cap == "fs-write":
            return "OK", handle_fs_write(args, state.get("fs_root", "."))
        elif cap == "clock":
            return "OK", handle_clock(args)
        elif cap == "http-get":
            return "OK", handle_http_get(args)
        elif cap == "lolcode":
            from backends.lolcode.adapter import run as lolcode_run
            op = effect.get("op", "")
            # The operands are whatever the JAJAJA program left in its
            # base. This is transport: the adapter feeds them to the
            # external LOLCODE runtime, which does the actual parsing
            # and computation.
            operands = state.get("base", "").strip()
            result = lolcode_run(op, operands)
            return "OK", result["stdout"]
        else:
            return "DENY", f"unimplemented capability {cap!r}"
    except Exception as e:
        return "ERROR", str(e)


def run_host(
    source: str,
    stdin_data: str = "",
    max_steps: int = 100000,
    allow: list[str] | None = None,
    trace: bool = False,
    fs_root: str = ".",
) -> tuple[str, int, str, list[dict]]:
    """Run a JAJAJA program with host effect dispatch.

    Returns (output, steps, status, receipts).
    """
    if allow is None:
        allow = ["stdin", "stdout"]
    allowed = expand_allow(allow)

    state = {
        "stdin_data": stdin_data,
        "kv": {},
        "fs_root": fs_root,
    }
    receipts = []
    machine = Jajaja(source, trace=trace)
    machine.output = []
    machine.steps = 0
    machine.status = "RUNNING"

    # Inject stdin as base prefix
    if stdin_data:
        machine.base = stdin_data + " " + machine.base

    total_steps = 0
    while total_steps < max_steps:
        # Run until HALT or output contains an EFFECT
        while total_steps < max_steps:
            if not machine.step():
                break
            total_steps += 1

        # Check if any EFFECT lines were emitted
        effects_found = False
        new_output = []
        # Expose the remaining base as effect input data. This is pure
        # transport: handlers may read it (e.g. the lolcode adapter
        # forwards it as the backend program's stdin) but the host
        # never computes on it.
        state["base"] = machine.base.strip()
        for line in machine.output:
            parsed = parse_effect(line)
            if parsed:
                status, payload = dispatch_effect(parsed, allowed, state)
                receipt = {
                    "request_id": parsed["request_id"],
                    "capability": parsed["capability"],
                    "status": status,
                    "payload": payload,
                }
                receipts.append(receipt)
                # Inject result back into base
                result_str = make_result(parsed["request_id"], status, payload)
                machine.base = result_str + " " + machine.base
                effects_found = True
            else:
                new_output.append(line)

        if not effects_found:
            break

        # Clear output and continue with results injected
        machine.output = []
        machine.steps = 0
        machine.status = "RUNNING"

    if machine.status == "RUNNING":
        machine.status = "MAX_STEPS"

    # Filter EFFECT lines from final output
    final_output = [l for l in machine.output if not l.strip().startswith(EFFECT_PREFIX)]
    return "".join(final_output), total_steps, machine.status, receipts


def main() -> int:
    parser = argparse.ArgumentParser(description="JAJAJA host runtime")
    parser.add_argument("program", help="Path to .jaja file")
    parser.add_argument("--input", "-i", default="", help="Runtime input")
    parser.add_argument("--max-steps", "-n", type=int, default=100000)
    parser.add_argument("--allow", "-a", default="stdin,stdout",
                        help="Comma-separated capabilities or groups")
    parser.add_argument("--trace", "-t", action="store_true")
    parser.add_argument("--root", "-r", default=".",
                        help="Sandbox root for filesystem")
    args = parser.parse_args()

    source = Path(args.program).read_text(encoding="utf-8")
    allow_list = [a.strip() for a in args.allow.split(",") if a.strip()]

    output, steps, status, receipts = run_host(
        source,
        stdin_data=args.input,
        max_steps=args.max_steps,
        allow=allow_list,
        trace=args.trace,
        fs_root=args.root,
    )

    print(f"status={status} steps={steps}")
    if output:
        print(f"output={output!r}")
    if receipts:
        print("receipts:")
        for r in receipts:
            print(f"  {r['request_id']}: {r['capability']} -> {r['status']}: {r['payload']!r}")

    return 0 if status in ("HALTED",) else 1


if __name__ == "__main__":
    sys.exit(main())
