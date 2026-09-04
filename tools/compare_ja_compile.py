"""compare_ja_compile.py — compara src/proofs_lol/ja_encoding.lol (salida)
contra proofs/ja_encoding.py::compile_tm_ja, byte a byte.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "proofs"))
sys.path.insert(0, str(REPO / "tools"))

import ja_encoding as pyenc  # noqa: E402
import tm_to_jajaja as pygen  # noqa: E402
from run_jajaja_lol import resolve_lci  # noqa: E402

SRC = REPO / "src" / "proofs_lol" / "ja_encoding.lol"


def lolcode_all() -> dict[tuple[str, str], str]:
    lci = resolve_lci()
    proc = subprocess.run([lci, str(SRC)], capture_output=True, text=True,
                          encoding="utf-8", timeout=120)
    if proc.returncode != 0:
        raise SystemExit(f"lci failed: {proc.stderr}")
    sections: dict[tuple[str, str], str] = {}
    cur = None
    buf: list[str] = []
    for line in proc.stdout.splitlines(keepends=True):
        m = re.match(r"^==== (\S+) (\S+) ====\s*$", line)
        if m:
            if cur is not None:
                sections[cur] = "".join(buf)
            cur = (m.group(1), m.group(2))
            buf = []
            continue
        buf.append(line)
    if cur is not None:
        sections[cur] = "".join(buf)
    return sections


def main() -> int:
    got = lolcode_all()
    cases = [
        ("binary_increment", pygen.tm_binary_increment()),
        ("bit_flip", pygen.tm_bit_flip()),
    ]
    failures = 0
    for name, tm in cases:
        expected, _ = pyenc.compile_tm_ja(tm, "1011")
        actual = got.get((name, "1011"), "")
        ok = actual == expected
        print(("PASS" if ok else "FAIL") + f"  {name}('1011')")
        if not ok:
            failures += 1
            el, al = expected.splitlines(), actual.splitlines()
            for i in range(max(len(el), len(al))):
                a = el[i] if i < len(el) else None
                b = al[i] if i < len(al) else None
                if a != b:
                    print(f"   linea {i}: oracle={a!r}  lolcode={b!r}")
                    break
            print(f"   longitudes: oracle={len(expected)} lolcode={len(actual)}")
    print(f"{len(cases) - failures}/{len(cases)} byte-identical")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
