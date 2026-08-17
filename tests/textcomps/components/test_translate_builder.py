"""
测试 TranslateBuilder
"""
import pytest
from miststar.textcomps import (
    Rawtext, Text, Score, Selector, Translate,
    TranslateBuilder, TranslateKind
)
from miststar.exceptions import InvalidValueException


# ============================================================================
# Test TranslateBuilder
# ============================================================================

class TestTranslateBuilder:
    """测试 TranslateBuilder 的所有功能"""

    # ---------- 构造 ----------
    def test_constructor(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        assert builder.translate is t
        assert builder.raw is None

    def test_constructor_with_rawtext(self):
        raw = Rawtext()
        t = Translate("key")
        builder = TranslateBuilder(t, raw)
        assert builder.raw is raw
        assert builder.translate is t

    # ---------- include 系列 ----------
    def test_include(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include(Text("Hello"), Selector("@p"))
        assert t.kind == TranslateKind.RawtextTranslate
        assert isinstance(t.with_content, Rawtext)
        assert len(t.with_content) == 2
        assert t.with_content[0].content == "Hello"
        assert t.with_content[1].selector == "@p"

    def test_include_asc(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_asc("@p", "money[].Steve")
        assert t.kind == TranslateKind.RawtextTranslate
        assert isinstance(t.with_content, Rawtext)
        assert len(t.with_content) == 2
        assert isinstance(t.with_content[0], Selector)
        assert t.with_content[0].selector == "@p"
        assert isinstance(t.with_content[1], Score)
        assert t.with_content[1].name == "Steve"
        assert t.with_content[1].objective == "money"

    def test_include_string(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("Hello", "World")
        assert t.kind == TranslateKind.StringTranslate
        assert t.with_content == ["Hello", "World"]

    def test_include_string_multiple(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("a").include_string("b")
        assert t.with_content == ["a", "b"]

    # ---------- build 系列 ----------
    def test_build(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        raw = builder.build(Text("Hello"), Selector("@p"))
        assert t.kind == TranslateKind.RawtextTranslate
        assert isinstance(t.with_content, Rawtext)
        assert len(t.with_content) == 2
        # 返回的 Rawtext 包含 Translate
        assert len(raw) == 1
        assert raw[0] is t

    def test_build_asc(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        raw = builder.build_asc("@p", "money[].Steve")
        assert t.kind == TranslateKind.RawtextTranslate
        assert isinstance(t.with_content, Rawtext)
        assert len(t.with_content) == 2
        assert len(raw) == 1
        assert raw[0] is t

    def test_build_string(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        raw = builder.build_string("Hello", "World")
        assert t.kind == TranslateKind.StringTranslate
        assert t.with_content == ["Hello", "World"]
        assert len(raw) == 1
        assert raw[0] is t

    def test_build_without_args(self):
        """build 无参数时应保持纯翻译，不创建 with"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        raw = builder.build()
        assert t.kind == TranslateKind.PureTranslate
        assert t.with_content is None
        assert len(raw) == 1
        assert raw[0] is t

    def test_build_asc_without_args(self):
        """build_asc 无参数时也应保持纯翻译"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        raw = builder.build_asc()
        assert t.kind == TranslateKind.PureTranslate
        assert t.with_content is None
        assert len(raw) == 1

    def test_build_string_without_args(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        raw = builder.build_string()
        assert t.kind == TranslateKind.PureTranslate
        assert t.with_content is None
        assert len(raw) == 1

    # ---------- end() ----------
    def test_end(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        result = builder.end()
        assert result is t
        # end() 不修改 builder 状态，可以继续添加
        builder.include_string("Hello")
        assert t.with_content == ["Hello"]

    def test_end_after_include(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("Hello")
        result = builder.end()
        assert result is t
        assert t.with_content == ["Hello"]

    # ---------- rawtext() ----------
    def test_rawtext_without_raw(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        raw = builder.rawtext()
        # 应返回新建的 Rawtext，包含 Translate
        assert isinstance(raw, Rawtext)
        assert len(raw) == 1
        assert raw[0] is t
        # builder 的 raw 仍为 None
        assert builder.raw is None

    def test_rawtext_with_raw(self):
        raw = Rawtext()
        t = Translate("key")
        builder = TranslateBuilder(t, raw)
        result = builder.rawtext()
        # 应返回同一个 Rawtext，且 Translate 已追加
        assert result is raw
        assert len(raw) == 1
        assert raw[0] is t
        # builder 的 raw 不变
        assert builder.raw is raw

    # ---------- 冲突检查（状态锁） ----------
    def test_conflict_include_after_string(self):
        """先 include_string，后 include 应抛出异常"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("Hello")
        with pytest.raises(InvalidValueException) as exc:
            builder.include(Text("World"))
        assert "string" in str(exc.value).lower() or "TextComponent" in str(exc.value)

    def test_conflict_string_after_include(self):
        """先 include，后 include_string 应抛出异常"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include(Text("Hello"))
        with pytest.raises(InvalidValueException) as exc:
            builder.include_string("World")
        assert "rawtext" in str(exc.value).lower() or "component" in str(exc.value)

    def test_conflict_build_after_string(self):
        """先 include_string，后 build（含参数）应抛出异常"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("Hello")
        with pytest.raises(InvalidValueException):
            builder.build(Text("World"))

    def test_conflict_build_string_after_include(self):
        """先 include，后 build_string 应抛出异常"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include(Text("Hello"))
        with pytest.raises(InvalidValueException):
            builder.build_string("World")

    def test_conflict_asc_after_string(self):
        """先 include_string，后 include_asc 应抛出异常"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("Hello")
        with pytest.raises(InvalidValueException):
            builder.include_asc("@p")

    def test_conflict_string_after_asc(self):
        """先 include_asc，后 include_string 应抛出异常"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_asc("Hello")
        with pytest.raises(InvalidValueException):
            builder.include_string("World")

    # ---------- 多参数累积 ----------
    def test_multiple_includes(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include(Text("A")).include(Text("B"))
        assert t.kind == TranslateKind.RawtextTranslate
        assert len(t.with_content) == 2  # type: ignore
        assert t.with_content[0].content == "A"  # type: ignore
        assert t.with_content[1].content == "B"  # type: ignore

    def test_multiple_include_strings(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("a").include_string("b")
        assert t.with_content == ["a", "b"]

    def test_mixed_valid_within_same_kind(self):
        """同一个 kind 内可以多次添加"""
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include(Text("A")).include(Selector("@p"))
        assert len(t.with_content) == 2  # type: ignore

    # ---------- 错误处理 ----------
    def test_include_string_with_non_string(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        with pytest.raises(InvalidValueException):
            builder.include_string(123)  # type: ignore

    def test_build_string_with_non_string(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        with pytest.raises(InvalidValueException):
            builder.build_string(123)  # type: ignore

    def test_include_with_non_textcomponent(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        with pytest.raises(InvalidValueException):
            builder.include("not a component")  # type: ignore

    # ---------- 状态转换 ----------
    def test_pure_to_string(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include_string("Hello")
        assert t.kind == TranslateKind.StringTranslate

    def test_pure_to_rawtext(self):
        t = Translate("key")
        builder = TranslateBuilder(t)
        builder.include(Text("Hello"))
        assert t.kind == TranslateKind.RawtextTranslate

    # ---------- 与 Rawtext 的集成 ----------
    def test_build_with_rawtext(self):
        raw = Rawtext()
        t = Translate("key")
        builder = TranslateBuilder(t, raw)
        result = builder.build_string("Hello")
        assert result is raw
        assert len(raw) == 1
        assert raw[0] is t
        assert t.with_content == ["Hello"]

    def test_chain_translate_from_rawtext(self):
        """测试 raw.translate(...).build_asc(...) 这种常用链式调用"""
        raw = Rawtext()
        raw.translate("key").build_asc("@p")
        assert len(raw) == 1
        t = raw[0]
        assert isinstance(t, Translate)
        assert t.kind == TranslateKind.RawtextTranslate
        assert len(t.with_content) == 1  # type: ignore
        assert t.with_content[0].selector == "@p"  # type: ignore

    def test_chain_translate_from_rawtext_string(self):
        raw = Rawtext()
        raw.translate("key").build_string("Hello")
        assert len(raw) == 1
        t = raw[0]
        assert t.kind == TranslateKind.StringTranslate
        assert t.with_content == ["Hello"]
