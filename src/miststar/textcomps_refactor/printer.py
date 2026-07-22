# created by lesomras on 2026-7-22

from __future__ import annotations
from typing import Union, TYPE_CHECKING

from .components.base import TextComponent, TranslateKind
from .components.text import Text

class StructuredPrinter:
    """
    结构化字符串打印机，用于生成美观的树形缩进文本。
    """

    def __init__(self, indent: int = 4):
        self.indent = indent

    def format(self, component: TextComponent, offset: int = 0) -> str:
        """
        将任意 TextComponent 格式化为树形字符串。
        """
        from .components.rawtext import Rawtext
        from .components.translate import Translate

        if isinstance(component, Rawtext):
            return self._format_rawtext(component, offset)
        elif isinstance(component, Translate):
            return self._format_translate(component, offset)
        elif isinstance(component, Text):
            lines = [f"{' ' * offset}{ln}" for ln in component._str_sequence()]
            return "\n".join(lines)
        else:
            return f"{' ' * offset}{str(component)}"

    def _format_rawtext(self, raw: Rawtext, offset: int) -> str:
        prefix = " " * offset
        lines = [f"{prefix}rawtext => {{"]
        for comp in raw.data:
            lines.append(self.format(comp, offset + self.indent))
        lines.append(f"{prefix}}}")
        return "\n".join(lines)

    def _format_translate(self, trans: Translate, offset: int) -> str:
        from .components.rawtext import Rawtext

        prefix = " " * offset
        kind = trans.kind

        if kind == TranslateKind.PureTranslate:
            return f"{prefix}translate | {trans.translate}"

        lines = [f"{prefix}translate* => {{"]
        lines.append(f"{' ' * (offset + self.indent)}translate | {trans.translate}")

        with_content = trans.with_content
        if isinstance(with_content, Rawtext):
            sub = self.format(with_content)

            sub_lines = sub.split("\n")
            for i, line in enumerate(sub_lines):
                if i == 0:
                    # 第一行去掉原有缩进，重新对齐
                    stripped = line.lstrip()
                    sub_lines[i] = f"{' ' * (offset + self.indent)}{stripped}"
                else:
                    sub_lines[i] = f"{' ' * (offset + self.indent)}{line}"
            lines.extend(sub_lines)
        elif isinstance(with_content, list):
            lines.append(f"{' ' * (offset + self.indent)}with | sequence => (")
            for item in with_content:
                lines.append(f"{' ' * (offset + 2 * self.indent)}{item}")
            lines.append(f"{' ' * (offset + self.indent)})")
        else:
            lines.append(f"{' ' * (offset + self.indent)}with | None")

        lines.append(f"{prefix}}} end*")
        return "\n".join(lines)


# ---------- 全局默认实例（兼容旧版 get_structured_str） ----------
default_printer = StructuredPrinter(indent=4)

def set_default_indent(indent: int) -> None:
    """设置全局默认缩进"""
    global _default_printer
    default_printer = StructuredPrinter(indent=indent)
