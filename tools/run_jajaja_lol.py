"""tools/run_jajaja_lol.py — launcher/transporte para el runtime LOLCODE.

Este modulo NO ejecuta semantica JAJAJA. Solo:

1. encode_stream: serializa un programa .jaja + stdin al stream de
   transporte `src/jajaja.lol` (un caracter por linea, escapes de los
   caracteres de control, marcadores de seccion).
2. decode_out: separa el output del programa del frame final
   `<|JAJAJA|status=...|steps=N|>`.

Correr:

    python tools/run_jajaja_lol.py examples/hola.jaja
    python tools/run_jajaja_lol.py examples/echo.jaja --input "hola"
    python tools/run_jajaja_lol.py prog.jaja --max-steps 50

Requiere un runtime LOLCODE externo (`LOLCODE_CMD` o `lci` en PATH).

La invariante de transporte: `decode_out ∘ encode_stream ∘ jajaja.lol`
debe ser identidad respecto a (output, steps, status); ninguna regla
del lenguaje vive aqui. Comprobacion de paridad: tools/parity_check.py.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
RUNTIME_SRC = REPO / "src" / "jajaja.lol"

FRAME_PREFIX = "<|JAJAJA|status="


class TransportError(RuntimeError):
    """Fallo de transporte (nunca semantico)."""


def resolve_lci() -> str:
    env = os.environ.get("LOLCODE_CMD", "").strip()
    if env:
        if Path(env).exists():
            return env
        raise TransportError(f"LOLCODE_CMD apunta a un archivo inexistente: {env!r}")
    found = shutil.which("lci") or shutil.which("lci.exe")
    if found:
        return found
    raise TransportError(
        "no external LOLCODE runtime (set LOLCODE_CMD or put lci on PATH)"
    )


def encode_stream(source: str, stdin_data: str = "", max_steps: int = 200000) -> str:
    """Serialize (source, stdin_data, max_steps) as the lci stream protocol.

    One unit per line. Raw characters pass through; the two control chars
    that cannot survive line transport are escaped. Section markers are
    tokens that cannot be confused with raw chars because raw chars are
    serialised alone on their line.
    """
    stream = []

    def emit_text(text: str) -> None:
        for ch in text:
            if ch == "\n":
                stream.append("<<N>>")
            elif ch == "\t":
                stream.append("<<T>>")
            else:
                stream.append(ch)

    emit_text(source)
    # The protocol frames lines by <<N>>. A source missing its trailing
    # newline must still terminate the last program line; <<N>> here is
    # a frame terminator, not program content.
    stream.append("<<N>>")
    stream.append("<<S1>>")
    emit_text(stdin_data)
    stream.append("<<S2>>")
    emit_text(str(int(max_steps)))
    stream.append("<<EOF>>")
    return "\n".join(stream) + "\n"


def decode_out(stdout_text: str) -> tuple[str, int, str]:
    """Split lci stdout into (program_output, steps, status).

    The frame is the last line; everything before it plus the one newline
    the runtime prints before the frame forms the program output. That
    newline is a framing artifact of the LOLCODE emission (there is no
    way to emit "chars then newline" without printing it), so the decoder
    removes exactly one trailing '\n' before the frame; the parity check
    verifies the reconstructed output matches the oracle exactly.
    """
    # The frame is the last line; the runtime puts it on its own line by
    # printing "\n" before it. Program output may itself end with "\n";
    # the leading "\n" of the frame is exactly one char, stripped once.
    marker = "\n" + FRAME_PREFIX
    cut = stdout_text.rfind(marker)
    if cut < 0:
        raise TransportError(
            f"frame not found in runtime stdout: {stdout_text[-200:]!r}"
        )
    before, frame = stdout_text[:cut], stdout_text[cut + 1:]
    frame = frame.split("\n", 1)[0]
    # parse frame
    try:
        body = frame[len(FRAME_PREFIX):]
        status_part, rest = body.split("|steps=", 1)
        steps_str = rest.split("|>", 1)[0]
        steps = int(steps_str)
        status = status_part
    except (ValueError, IndexError) as e:
        raise TransportError(f"unparseable frame {frame!r}: {e}")
    return before, steps, status


def run_lol(source: str, stdin_data: str = "", max_steps: int = 200000,
            lci: str | None = None,
            timeout: float = 120.0) -> tuple[str, int, str]:
    """Run the LOLCODE runtime on source. Returns (output, steps, status)."""
    lci = lci or resolve_lci()
    stream = encode_stream(source, stdin_data, max_steps)
    proc = subprocess.run(
        [lci, str(RUNTIME_SRC)],
        input=stream,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if proc.returncode != 0:
        raise TransportError(
            f"lci exited {proc.returncode}: {(proc.stderr or '').strip()[:300]}"
        )
    return decode_out(proc.stdout)


def main() -> int:
    ap = argparse.ArgumentParser(description="JAJAJA on LOLCODE (transport launcher)")
    ap.add_argument("program", help=".jaja source file")
    ap.add_argument("--input", "-i", default="", help="runtime stdin_data")
    ap.add_argument("--max-steps", "-n", type=int, default=200000)
    args = ap.parse_args()

    source = Path(args.program).read_text(encoding="utf-8")
    try:
        output, steps, status = run_lol(source, stdin_data=args.input,
                                        max_steps=args.max_steps)
    except TransportError as e:
        print(f"TRANSPORT_ERROR: {e}", file=sys.stderr)
        return 2

    sys.stdout.write(output)
    if output and not output.endswith("\n"):
        print()
    print(f"status={status} steps={steps}")
    return 0 if status == "HALTED" else 1


if __name__ == "__main__":
    sys.exit(main())
