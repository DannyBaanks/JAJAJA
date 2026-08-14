"""run_examples.py - corre todos los ejemplos .jaja y muestra resultado."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from jajaja_interpreter import run

ex = HERE / "examples"
for f in sorted(ex.glob("*.jaja")):
    src = f.read_text(encoding="utf-8")
    out, steps, status = run(src, max_steps=1000)
    print(f"\n=== {f.name} ===")
    print(f"status={status} steps={steps}")
    print(f"output={out!r}")
