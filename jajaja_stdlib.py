"""jajaja_stdlib.py — Data model and host ABI protocol for JAJAJA.

This module defines:
1. Data encodings (bool, int, string, list, record)
2. Effect protocol (EFFECT/RESULT IR)
3. Compiler helpers for control flow macros

All computation happens in the JAJAJA base (no Python calculation).
Python only encodes/decodes representations and executes host effects.
"""
from __future__ import annotations

import json

# ─── Data Encodings ────────────────────────────────────────────────
# These are CONVENTIONS, not language changes.
# Rules process these representations; Python verifies them.

# Boolean: literal tokens
BOOL_TRUE = "TRUE"
BOOL_FALSE = "FALSE"

# Integer: unary (ja repeated N times, space-delimited)
# 0 = empty, 1 = ja, 2 = jaja, 3 = jajaja, etc.
def int_to_unary(n: int) -> str:
    if n < 0:
        raise ValueError("unary encoding is for non-negative integers only")
    if n == 0:
        return "_ZERO"
    return "ja" * n

def unary_to_int(s: str) -> int:
    s = s.strip()
    if s == "_ZERO":
        return 0
    if not s or "ja" not in s:
        raise ValueError(f"not a unary integer: {s!r}")
    # Must be all 'ja' repeated
    count = len(s) // 2
    if "ja" * count != s:
        raise ValueError(f"not a unary integer: {s!r}")
    return count

# Integer: positional decimal (digits 0-9 as single chars)
def int_to_decimal(n: int) -> str:
    return str(n)

def decimal_to_int(s: str) -> int:
    return int(s.strip())

# String: literal characters in base, delimited by quotes for clarity
# In base: "hello" — rules can match individual chars
def string_encode(s: str) -> str:
    return s

def string_decode(b: str) -> str:
    return b

# List: space-delimited items with bracket markers
# [item1 item2 item3]
def list_encode(items: list[str]) -> str:
    if not items:
        return "[]"
    return "[" + " ".join(items) + "]"

def list_decode(s: str) -> list[str]:
    s = s.strip()
    if s == "[]":
        return []
    if s.startswith("[") and s.endswith("]"):
        return s[1:-1].split(" ")
    return [s]

# Record: key:value pairs separated by spaces
# name:Danny age:30 city:CDMX
def record_encode(pairs: dict[str, str]) -> str:
    return " ".join(f"{k}:{v}" for k, v in pairs.items())

def record_decode(s: str) -> dict[str, str]:
    result = {}
    for pair in s.strip().split(" "):
        if ":" in pair:
            k, v = pair.split(":", 1)
            result[k] = v
    return result


# ─── Host ABI Protocol ─────────────────────────────────────────────
# Effect/Result IR for host communication.
#
# JAJAJA emits EFFECT requests via output rules:
#   EFFECT <request_id> <capability> <arguments_json>
#
# host.py parses these, executes capabilities, injects results:
#   RESULT <request_id> <status> <payload_json>
#
# The result is prepended to the base, so JAJAJA rules can process it.

EFFECT_PREFIX = "EFFECT "
RESULT_PREFIX = "RESULT "

def make_effect(request_id: str, capability: str, **args) -> str:
    """Generate an EFFECT output line for JAJAJA to emit."""
    return f"{EFFECT_PREFIX}{request_id} {capability} {json.dumps(args)}"

def parse_effect(line: str) -> dict | None:
    """Parse an EFFECT line from JAJAJA output."""
    line = line.strip()
    if not line.startswith(EFFECT_PREFIX):
        return None
    rest = line[len(EFFECT_PREFIX):]
    parts = rest.split(" ", 2)
    if len(parts) < 2:
        return None
    request_id = parts[0]
    capability = parts[1]
    args = {}
    if len(parts) == 3:
        try:
            args = json.loads(parts[2])
        except json.JSONDecodeError:
            pass
    return {"request_id": request_id, "capability": capability, **args}

def make_result(request_id: str, status: str, payload: str = "") -> str:
    """Generate a RESULT to inject back into the base."""
    return f"{RESULT_PREFIX}{request_id} {status} {json.dumps(payload)}"

def parse_result(line: str) -> dict | None:
    """Parse a RESULT line from injected base content."""
    line = line.strip()
    if not line.startswith(RESULT_PREFIX):
        return None
    rest = line[len(RESULT_PREFIX):]
    parts = rest.split(" ", 2)
    if len(parts) < 2:
        return None
    request_id = parts[0]
    status = parts[1]
    payload = ""
    if len(parts) == 3:
        try:
            payload = json.loads(parts[2])
        except json.JSONDecodeError:
            payload = parts[2]
    return {"request_id": request_id, "status": status, "payload": payload}


# ─── Effect Handlers (host side) ──────────────────────────────────

def handle_stdin(args: dict, stdin_data: str = "") -> str:
    """Read from input buffer. Returns the next line."""
    if not stdin_data:
        return ""
    lines = stdin_data.split("\n", 1)
    return lines[0]

def handle_stdout(args: dict) -> str:
    """Write to stdout. Returns empty (side effect only)."""
    text = args.get("text", "")
    print(text, end="")
    return ""

def handle_kv_get(args: dict, store: dict) -> str:
    """Get value from key-value store."""
    key = args.get("key", "")
    return store.get(key, "")

def handle_kv_set(args: dict, store: dict) -> str:
    """Set value in key-value store."""
    key = args.get("key", "")
    value = args.get("value", "")
    store[key] = value
    return "OK"

def handle_fs_read(args: dict, root: str = ".") -> str:
    """Read file from sandbox."""
    import os
    path = args.get("path", "")
    full = os.path.normpath(os.path.join(root, path))
    if not full.startswith(os.path.normpath(root)):
        return "DENY:path_traversal"
    try:
        with open(full, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "DENY:not_found"
    except Exception as e:
        return f"DENY:{e}"

def handle_fs_write(args: dict, root: str = ".") -> str:
    """Write file to sandbox."""
    import os
    path = args.get("path", "")
    data = args.get("data", "")
    full = os.path.normpath(os.path.join(root, path))
    if not full.startswith(os.path.normpath(root)):
        return "DENY:path_traversal"
    try:
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(data)
        return "OK"
    except Exception as e:
        return f"DENY:{e}"

def handle_clock(args: dict) -> str:
    """Get current timestamp."""
    import time
    return str(time.time())

def handle_http_get(args: dict) -> str:
    """HTTP GET request (fixture mode — returns mock)."""
    url = args.get("url", "")
    # Fixture responses for demo
    if "/hello" in url:
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        name = params.get("name", ["World"])[0]
        return json.dumps({"status": 200, "body": f"Hello, {name}!"})
    return json.dumps({"status": 404, "body": "Not found"})
