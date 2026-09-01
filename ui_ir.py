"""ui_ir.py — Declarative UI intermediate representation for JAJAJA.

JAJAJA produces UI IR. Adapters render to HTML, terminal, or SwiftUI.
This is the protocol, not a specific rendering.

UI IR format (one element per line):
    VIEW <id> <parent_id>
    TEXT <id> <parent_id> <content>
    BUTTON <id> <parent_id> <label> <event>
    INPUT <id> <parent_id> <placeholder> <event>
    ROW <id> <parent_id>
    COLUMN <id> <parent_id>
    IMAGE <id> <parent_id> <src>
    EVENT <event_id> <event_type> <target_id>

Example (from JAJAJA output):
    VIEW root -1
    COLUMN root_col -1
    TEXT t1 root_col Welcome to the store
    ROW products_row root_col
    BUTTON btn1 products_row Add to Cart add_cart
    INPUT search products_row Search... search_input
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class UIElement:
    kind: str       # VIEW, TEXT, BUTTON, INPUT, ROW, COLUMN, IMAGE
    id: str
    parent: str     # parent id, or "-1" for root
    content: str = ""
    event: str = ""


@dataclass
class UIIR:
    """Declarative UI tree produced by JAJAJA."""
    elements: list[UIElement] = field(default_factory=list)

    def add(self, kind: str, id: str, parent: str, content: str = "", event: str = ""):
        self.elements.append(UIElement(kind, id, parent, content, event))

    def to_lines(self) -> list[str]:
        lines = []
        for e in self.elements:
            parts = [e.kind, e.id, e.parent]
            if e.content:
                parts.append(e.content)
            if e.event:
                parts.append(e.event)
            lines.append(" ".join(parts))
        return lines

    def render_html(self) -> str:
        """Render to minimal HTML."""
        children: dict[str, list[UIElement]] = {}
        for e in self.elements:
            children.setdefault(e.parent, []).append(e)

        def render_node(parent_id: str, indent: int = 0) -> str:
            parts = []
            for e in children.get(parent_id, []):
                tag = {
                    "VIEW": "div",
                    "TEXT": "p",
                    "BUTTON": "button",
                    "INPUT": "input",
                    "ROW": "div",
                    "COLUMN": "div",
                    "IMAGE": "img",
                }.get(e.kind, "div")

                cls = f' class="{e.kind.lower()}"'
                attrs = ""
                if e.kind == "INPUT":
                    attrs = f' placeholder="{e.content}"'
                elif e.kind == "IMAGE":
                    attrs = f' src="{e.content}"'

                inner = render_node(e.id, indent + 1) if e.kind in ("VIEW", "ROW", "COLUMN") else ""

                if inner:
                    parts.append(f'{"  " * indent}<{tag}{cls}{attrs}>{e.content}{inner}</{tag}>')
                elif e.kind == "INPUT":
                    parts.append(f'{"  " * indent}<{tag}{cls}{attrs}>')
                else:
                    parts.append(f'{"  " * indent}<{tag}{cls}{attrs}>{e.content}</{tag}>')

            return "\n".join(parts)

        body = render_node("-1")
        return f"<!DOCTYPE html>\n<html><body>\n{body}\n</body></html>"

    def render_terminal(self) -> str:
        """Render to terminal-friendly text."""
        lines = []
        for e in self.elements:
            indent = "  "
            if e.kind == "TEXT":
                lines.append(f"{indent}{e.content}")
            elif e.kind == "BUTTON":
                lines.append(f"{indent}[{e.content}]")
            elif e.kind == "INPUT":
                lines.append(f"{indent}__{e.content}__")
            elif e.kind in ("ROW", "COLUMN"):
                lines.append(f"{indent}--- {e.kind} ---")
        return "\n".join(lines)
