"""
测试打印机模块：StructuredPrinter 和 printraw
匹配 printer.py 优化后的格式
"""
import pytest
from miststar.textcomps import (
    Rawtext, Text, Score, Selector, Translate,
    StructuredPrinter, default_printer, printraw
)


class TestStructuredPrinter:
    """测试 StructuredPrinter 的格式化功能"""

    # ---------- Text ----------
    def test_format_text_single_line(self):
        printer = StructuredPrinter()
        t = Text("Hello")
        result = printer.format(t)
        assert result == "text  | Hello"

    def test_format_text_multi_line(self):
        printer = StructuredPrinter()
        t = Text("Hello\nWorld")
        result = printer.format(t)
        expected = "text  | Hello\n      | World"
        assert result == expected

    def test_format_text_with_offset(self):
        printer = StructuredPrinter()
        t = Text("Hello\nWorld")
        result = printer.format(t, offset=2)
        expected = "  text  | Hello\n        | World"
        assert result == expected

    # ---------- Score ----------
    def test_format_score(self):
        printer = StructuredPrinter()
        s = Score("Steve", "kills")
        result = printer.format(s)
        assert result == "score | Steve scoreboard :kills"

    # ---------- Selector ----------
    def test_format_selector(self):
        printer = StructuredPrinter()
        sel = Selector("@p")
        result = printer.format(sel)
        assert result == "selec | @p"

    # ---------- Rawtext ----------
    def test_format_rawtext_empty(self):
        printer = StructuredPrinter()
        r = Rawtext()
        result = printer.format(r)
        expected = "raw > {\n}"
        assert result == expected

    def test_format_rawtext_with_children(self):
        printer = StructuredPrinter()
        r = Rawtext([Text("Hello"), Selector("@p")])
        result = printer.format(r)
        expected = (
            "raw > {\n"
            "    text  | Hello\n"
            "    selec | @p\n"
            "}"
        )
        assert result == expected

    def test_format_rawtext_nested(self):
        printer = StructuredPrinter()
        inner = Rawtext([Text("inner")])
        r = Rawtext([Text("outer"), inner])
        result = printer.format(r)
        expected = (
            "raw > {\n"
            "    text  | outer\n"
            "    raw > {\n"
            "        text  | inner\n"
            "    }\n"
            "}"
        )
        assert result == expected

    # ---------- Translate ----------
    def test_format_translate_pure(self):
        printer = StructuredPrinter()
        t = Translate("gui.done")
        result = printer.format(t)
        assert result == "trans | gui.done"

    def test_format_translate_with_string_list(self):
        printer = StructuredPrinter()
        t = Translate("key", with_content=["a", "b"])
        result = printer.format(t)
        expected = (
            "trans > {\n"
            "    trans | key\n"
            "    with  | sequence => (\n"
            "        a\n"
            "        b\n"
            "    )\n"
            "}"
        )
        assert result == expected

    def test_format_translate_with_rawtext(self):
        printer = StructuredPrinter()
        with_content = Rawtext([Text("Hello"), Selector("@p")])
        t = Translate("key", with_content=with_content)
        result = printer.format(t)
        # _format_translate 中嵌套 Rawtext 时，第一行被重新对齐为 "with  | raw > {"
        expected = (
            "trans > {\n"
            "    trans | key\n"
            "    with  | raw > {\n"
            "        text  | Hello\n"
            "        selec | @p\n"
            "    }\n"
            "}"
        )
        assert result == expected

    def test_format_translate_with_none(self):
        printer = StructuredPrinter()
        # 强制 with_content 为 None 以外的类型（但走 else 分支）
        t = Translate("key")
        object.__setattr__(t, 'with_content', 123)  # 强制设为 int
        result = printer.format(t)
        expected = (
            "trans > {\n"
            "    trans | key\n"
            "    with  | None\n"
            "}"
        )
        assert result == expected

    # ---------- 未知组件 ----------
    def test_format_unknown_component(self):
        printer = StructuredPrinter()

        class Unknown:
            def __str__(self):
                return "unknown_str"
            def __repr__(self):
                return "unknown_repr"

        comp = Unknown()
        result = printer.format(comp)  # type: ignore
        assert result == "unknown_repr"

        # 自定义 extra_formatter
        result = printer.format(comp, extra_formatter=lambda c: "custom")
        assert result == "custom"

    # ---------- 自定义缩进 ----------
    def test_custom_indent(self):
        printer = StructuredPrinter(indent=2)
        r = Rawtext([Text("Hello")])
        result = printer.format(r)
        expected = "raw > {\n  text  | Hello\n}"
        assert result == expected

    def test_format_with_offset_affects_all_lines(self):
        printer = StructuredPrinter()
        t = Text("Hello\nWorld")
        result = printer.format(t, offset=4)
        expected = "    text  | Hello\n          | World"
        assert result == expected


class TestPrintraw:
    """测试 printraw 函数"""

    def test_printraw_single(self, capsys):
        r = Rawtext([Text("Hello")])
        printraw(r)
        captured = capsys.readouterr()
        expected = "raw > {\n    text  | Hello\n}\n"
        assert captured.out == expected

    def test_printraw_multiple(self, capsys):
        r1 = Rawtext([Text("A")])
        r2 = Rawtext([Text("B")])
        printraw(r1, r2)
        captured = capsys.readouterr()
        expected = "raw > {\n    text  | A\n}\nraw > {\n    text  | B\n}\n"
        assert captured.out == expected

    def test_printraw_custom_formatter(self, capsys):
        r = Rawtext([Text("Hello")])
        def custom_formatter(comp):
            return "CUSTOM"
        printraw(r, formatter=custom_formatter)
        captured = capsys.readouterr()
        assert captured.out.strip() == "CUSTOM"

    def test_printraw_accepts_any_textcomponent(self, capsys):
        t = Text("Hello")
        printraw(t)
        captured = capsys.readouterr()
        expected = "text  | Hello\n"
        assert captured.out == expected


class TestDefaultPrinter:
    """测试全局 default_printer"""

    def test_default_printer_instance(self):
        assert isinstance(default_printer, StructuredPrinter)
        assert default_printer.indent == 4

    def test_default_printer_format(self):
        t = Text("Hello")
        result = default_printer.format(t)
        assert result == "text  | Hello"

    def test_printraw_uses_default_formatter(self, capsys):
        r = Rawtext([Text("Hello")])
        printraw(r)
        captured = capsys.readouterr()
        expected = "raw > {\n    text  | Hello\n}\n"
        assert captured.out == expected
