"""demo_lolcode.py — Python-only frontend -> JAJAJA -> LOLCODE backend.

Usage:
    python demo_lolcode.py "ADD 2 3"
    python demo_lolcode.py "MAX 9 4"
    python demo_lolcode.py "ECHO Bolgang dice hola"
    python demo_lolcode.py "COUNT 3"

Pipeline (all of it happens on every run):

    Python (this frontend)
      -> JAJAJA program (backends/lolcode/route.jaja) rewrites the
         request and emits an EFFECT selecting WHICH op runs
      -> host capability "lolcode" -> backends/lolcode/adapter.py
      -> external LOLCODE runtime executes a real .lol program
         (lci: SUM OF / BIGGR OF + O RLY? / IM IN YR / GIMMEH)
      -> RESULT travels back through the host into the JAJAJA base
      -> JAJAJA confirms reception
      -> Python prints the receipt. Python never computes the value.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from host import run_host  # noqa: E402
from backends.lolcode.adapter import resolve_runtime, LolcodeRuntimeNotFound  # noqa: E402

ROUTE = HERE / "backends" / "lolcode" / "route.jaja"


def main() -> int:
    if len(sys.argv) < 2 or not sys.argv[1].strip():
        print(__doc__)
        return 2
    request = " ".join(sys.argv[1:]).strip()

    print(f'[frontend] python request: "{request}"')

    source = ROUTE.read_text(encoding="utf-8")

    try:
        runtime = resolve_runtime()
        print(f"[backend]  runtime: {runtime} (external LOLCODE runtime)")
    except LolcodeRuntimeNotFound as e:
        # NO fallback: if the backend cannot run, the demo fails loudly.
        print(f"[backend]  FAIL: {e}")
        return 1

    output, steps, status, receipts = run_host(
        source,
        stdin_data=request,
        allow=["lolcode"],
    )

    print(f"[jajaja]   rewrite steps={steps} status={status}")

    lolcode_receipts = [r for r in receipts if r["capability"] == "lolcode"]
    if not lolcode_receipts:
        print("[jajaja]   no rule matched the request -> no backend call")
        print(f'[jajaja]   (ops soportadas: ADD, MAX, ECHO, COUNT)')
        return 1

    receipt = lolcode_receipts[0]
    print(f'[jajaja]   EFFECT -> host -> backend (receipt {receipt["request_id"]})')

    if receipt["status"] != "OK":
        print(f'[backend]  FAIL: {receipt["payload"]}')
        return 1

    if output.strip():
        print(f"[jajaja]   confirmacion: {output.strip()}")

    payload = receipt["payload"]
    print(f"[backend]  LOLCODE stdout: {payload!r}")
    print(f"[result]   {payload.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
