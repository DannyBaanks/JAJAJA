"""collect_stats.py — mide la composición real del repo (bytes, líneas,
archivos) por extensión, ignorando .git. Sirve de evidencia para el flip
a LOLCODE como lenguaje de primera plana.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent


def walk() -> dict[str, dict[str, int]]:
    by_ext: dict[str, dict[str, int]] = {}
    for p in REPO.rglob("*"):
        if not p.is_file():
            continue
        if ".git" in p.parts:
            continue
        ext = p.suffix.lower()
        try:
            b = p.read_bytes()
            n_lines = b.count(b"\n")
        except Exception:
            continue
        d = by_ext.setdefault(ext, {"files": 0, "bytes": 0, "lines": 0})
        d["files"] += 1
        d["bytes"] += len(b)
        d["lines"] += n_lines
    return by_ext


def main() -> int:
    stats = walk()
    out = dict(sorted(stats.items(), key=lambda kv: -kv[1]["bytes"]))
    for ext, d in list(out.items())[:40]:
        print(f"{ext or '(none)':10s} files={d['files']:5d}  bytes={d['bytes']:9d}  lines={d['lines']:7d}")
    Path(__file__).with_name("composition.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
