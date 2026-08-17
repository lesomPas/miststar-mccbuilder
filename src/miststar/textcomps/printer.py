# created by lesomras on 2026-7-22

from __future__ import annotations
from typing import Union, Callable

from .components import (
    TextComponent,
    TranslateKind,
    Text,
    Score,
    Selector,
    Translate,
    Rawtext,
)

class StructuredPrinter:
    """
    结构化字符串打印机，用于生成美观的树形缩进文本。
    """

    def __init__(self, indent: int = 4):
        self.indent = indent

    def format(self, component: TextComponent, offset: int = 0, extra_formatter: Callable[[TextComponent], str] = repr) -> str:
        """
        将任意 TextComponent 格式化为树形字符串。
        """
        match component:
            case Rawtext():
                return self._format_rawtext(component, offset)
            case Translate():
                return self._format_translate(component, offset)
            case Text(content=content):
                return self._format_text(content, offset)
            case Score(name=name, objective=objective):
                return f"{' ' * offset}score | {name} scoreboard :{objective}"
            case Selector(selector=selector):
                return f"{' ' * offset}selec | {selector}"
            case _:
                return f"{' ' * offset}{extra_formatter(component)}"

    def _format_text(self, content: str, offset: int) -> str:
        prefix = ' ' * offset
        lines = []
        for i, ln in enumerate(content.splitlines()):
            if i == 0:
                lines.append(f"{prefix}text  | {ln}")
            else:
                lines.append(f"{prefix}      | {ln}")
        return "\n".join(lines)

    def _format_rawtext(self, raw: Rawtext, offset: int) -> str:
        prefix = " " * offset
        lines = [f"{prefix}raw > {{"]
        for comp in raw.data:
            lines.append(self.format(comp, offset + self.indent))
        lines.append(f"{prefix}}}")
        return "\n".join(lines)

    def _format_translate(self, trans: Translate, offset: int) -> str:
        prefix = " " * offset
        kind = trans.kind

        if kind == TranslateKind.PureTranslate:
            return f"{prefix}trans | {trans.translate}"

        lines = [f"{prefix}trans > {{"]
        lines.append(f"{' ' * (offset + self.indent)}trans | {trans.translate}")

        with_content = trans.with_content
        if isinstance(with_content, Rawtext):
            sub = self.format(with_content)

            sub_lines = sub.split("\n")
            for i, line in enumerate(sub_lines):
                if i == 0:
                    # 第一行去掉原有缩进，重新对齐
                    stripped = line.lstrip()
                    sub_lines[i] = f"{' ' * (offset + self.indent)}with  | {stripped}"
                else:
                    sub_lines[i] = f"{' ' * (offset + self.indent)}{line}"
            lines.extend(sub_lines)
        elif isinstance(with_content, list):
            lines.append(f"{' ' * (offset + self.indent)}with  | sequence => (")
            for item in with_content:
                lines.append(f"{' ' * (offset + 2 * self.indent)}{item}")
            lines.append(f"{' ' * (offset + self.indent)})")
        else:
            lines.append(f"{' ' * (offset + self.indent)}with  | None")

        lines.append(f"{prefix}}}")
        return "\n".join(lines)


default_printer = StructuredPrinter(indent=4)

def printraw(*args, formatter: Callable[[TextComponent], str] = default_printer.format) -> None:
    output = []
    for i in args:
        assert isinstance(i, TextComponent)
        output.append(formatter(i))
    print("\n".join(output))
