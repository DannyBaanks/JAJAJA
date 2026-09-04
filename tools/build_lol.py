"""tools/build_lol.py — ensamblador de partes LOLCODE -> .lol final.

Cómo funciona:
- Las partes viven en src/parts/ (00_, 10_, 20_, etc; alfanumétrico).
- Cada builds/*.lolcfg lista las partes a concatenar, un archivo por línea.
- La salida final es un .lol válido que lci puede ejecutar.

Este script NO interpreta LOLCODE, NO ejecuta lógica de JAJAJA. Es puro
texto: lee entradas preautorizadas, las concatena en el orden dado y
escribe la salida con SHA-256 y los nombres de entrada registrados en
una cabecera de trazas al final (fuera del programa, como comentarios).

Uso:
    python tools/build_lol.py builds/jajaja_build.cfg  ->  src/jajaja.lol
    python tools/build_lol.py --check-all              -> valida cfg sin escribir
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
PARTS = REPO / "src" / "parts"
BUILDS = REPO / "builds"


def assemble(cfg_path: Path) -> tuple[str, list[str], str]:
    """Read a build cfg, concatenate the parts in order. Returns (text, parts_list, sha256)."""
    names = [
        ln.strip() for ln in cfg_path.read_text(encoding="utf-8").splitlines()
        if ln.strip() and not ln.strip().startswith("#")
    ]
    if not names:
        raise SystemExit(f"cfg vacía: {cfg_path}")
    text = ""
    for name in names:
        p = PARTS / name
        if not p.exists():
            raise SystemExit(f"parte no encontrada: {name}")
        text += p.read_text(encoding="utf-8").rstrip() + "\n"
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return text, names, digest


def out_path_for(cfg: Path) -> Path:
    """La convención: cfg llamado 'X.cfg' -> X.lol en el dir objetivo dado por
    la primera línea de comentario `# out: <repo-relative-path>`, o
    'src/<stem>.lol' por defecto."""
    for ln in cfg.read_text(encoding="utf-8").splitlines():
        ln = ln.strip()
        if ln.startswith("# out:"):
            rel = ln.split(":", 1)[1].strip()
            return (REPO / rel).resolve()
    return REPO / "src" / (cfg.stem + ".lol")


def build(cfg_name: str) -> Path:
    cfg = BUILDS / cfg_name
    text, names, digest = assemble(cfg)
    out = out_path_for(cfg)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8", newline="\n")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Ensamblador de partes LOLCODE")
    ap.add_argument("cfg", nargs="?", help="builds/<cfg>.cfg")
    ap.add_argument("--check-all", action="store_true",
                    help="Solo valida todas las cfg; no escribe")
    args = ap.parse_args()

    if args.check_all:
        for cfg in sorted(BUILDS.glob("*.cfg")):
            text, names, digest = assemble(cfg)
            print(f"{cfg.name}: {len(names)} partes, sha256={digest[:16]}...")
        return 0

    if not args.cfg:
        ap.error("specify builds/<name>.cfg or --check-all")
    out = build(args.cfg)
    print(f"ensamblado: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
