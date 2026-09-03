"""backends/lolcode/emit.py — LOLCODE source emitter.

Navigation, pas syntaxe magique: fonctions qui renvoient des chaînes de
LOLCODE 1.3 idiomatique (lci-compatible), pensées pour composer des
programmes cibles. Aucune de ces fonctions n'évalue la sémantique JAJAJA
ou du backend — elles produisent juste du texte source bien formé.

API minimale:

    declare(name, value=None)      'I HAS A n ITZ <v>' ou 'I HAS A n'
    assign(name, expr)             'n R <expr>'
    visible(expr, bang=False)      'VISIBLE <expr>' / 'VISIBLE <expr>!'
    gimmeh(var)                    'GIMMEH <var>'
    call(name, *args)              'I IZ name YR a AN YR b MKAY'
    funcdec(name, params, body)    bloc HOW IZ I ... IF U SAY SO
    cmp_eq(a, b)                   'BOTH SAEM a AN b'
    cmp_ne(a, b)                   'DIFFRINT a AN b'
    and_(*xs) / or_(*xs) / not_(x) 'BOTH OF ...' / 'EITHER OF ...' / 'NOT x'
    orly(cond, true_lines, false_lines=None)  'cond, O RLY? ... OIC'
    iminyr(label, body_lines)      'IM IN YR lbl ... IM OUTTA YR lbl'
    wile(cond) inline dans iminyr  'WILE <cond>' (como primera línea)
    program(body_lines)            'HAI 1.3' + body + 'KTHXBYE'

Convención: `value` puede ser:
    - int/float -> literal numérico
    - str crudo -> YA ES LOLCODE (se inserta verbatim)
    - str entre comillas explícitas -> se autodetecta si empieza/termina en '"'
    - el wrapper str_lit("hola") para una literal YARN escapada.
"""
from __future__ import annotations


def str_lit(s: str) -> str:
    """Cita una LOLCODE yarn, escapando los especiales de lci."""
    out = []
    for ch in s:
        if ch == '"':
            out.append(':"')
        elif ch == "\n":
            out.append(":)")
        elif ch == "\t":
            out.append(":>")
        elif ch == ":":
            out.append("::")
        else:
            out.append(ch)
    return '"' + "".join(out) + '"'


def _v(x) -> str:
    if isinstance(x, (int, float)):
        return repr(x)
    return x  # raw LOLCODE expression


def declare(name: str, value=None) -> str:
    if value is None:
        return f"I HAS A {name}"
    return f"I HAS A {name} ITZ {_v(value)}"


def assign(name: str, expr) -> str:
    return f"{name} R {_v(expr)}"


def visible(expr, bang: bool = False) -> str:
    return f"VISIBLE {_v(expr)}" + ("!" if bang else "")


def gimmeh(var: str) -> str:
    return f"GIMMEH {var}"


def call(name: str, *args) -> str:
    if args:
        joined = " AN YR ".join(_v(a) for a in args)
        return f"I IZ {name} YR {joined} MKAY"
    return f"I IZ {name} MKAY"


def funcdec(name: str, params: list[str], body: list[str]) -> list[str]:
    hdr = f"HOW IZ I {name}"
    if params:
        hdr += " YR " + " AN YR ".join(params)
    return [hdr, *body, "IF U SAY SO"]


def cmp_eq(a, b) -> str:
    return f"BOTH SAEM {_v(a)} AN {_v(b)}"


def cmp_ne(a, b) -> str:
    return f"DIFFRINT {_v(a)} AN {_v(b)}"


def and_(*xs) -> str:
    return "BOTH OF " + " AN ".join(_v(x) for x in xs)


def or_(*xs) -> str:
    return "EITHER OF " + " AN ".join(_v(x) for x in xs)


def not_(x) -> str:
    return f"NOT {_v(x)}"


def orly(cond: str, true_lines: list[str], false_lines: list[str] | None = None) -> list[str]:
    lines = [f"{cond}, O RLY?", "  YA RLY"]
    lines.extend("    " + l if l else "" for l in true_lines)
    if false_lines is not None:
        lines.append("  NO WAI")
        lines.extend("    " + l if l else "" for l in false_lines)
    lines.append("OIC")
    return lines


def iminyr(label: str, body: list[str], wile: str | None = None) -> list[str]:
    lines = [f"IM IN YR {label}"]
    if wile is not None:
        lines.append(f"  WILE {wile}")
    lines.extend("  " + l if l else "" for l in body)
    lines.append(f"IM OUTTA YR {label}")
    return lines


def program(body: list[str], hai: str = "1.3") -> str:
    return "\n".join([f"HAI {hai}", *body, "KTHXBYE"]) + "\n"


class Emitter:
    """Mini buildeur fluide: acumula líneas, produce programa completo."""

    def __init__(self, hai: str = "1.3"):
        self.hai = hai
        self.lines: list[str] = []

    def emit(self, *lines: str) -> "Emitter":
        self.lines.extend(lines)
        return self

    def block(self, lines: list[str]) -> "Emitter":
        return self.emit(*lines)

    def source(self) -> str:
        return program(self.lines, hai=self.hai)
