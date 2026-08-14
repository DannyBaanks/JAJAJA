import sys
from pathlib import Path

from jajaja_interpreter import run

HERE = Path(__file__).resolve().parent
SIGNATURE = 'JAJAJA-OK\n'


def main() -> int:
    src = (HERE / "bootstrap.jaja").read_text(encoding="utf-8")
    text, steps, status = run(src, max_steps=200000)
    if status != "HALTED":
        print("Jajaja_COMPILE_FAIL status=%s steps=%s" % (status, steps))
        return 1
    if text != SIGNATURE:
        print("Jajaja_COMPILE_FAIL signature=%r expected=%r" % (text, SIGNATURE))
        return 1
    print("Jajaja_COMPILE_OK status=%s steps=%s signature=%r" % (status, steps, text))
    return 0


if __name__ == "__main__":
    sys.exit(main())
