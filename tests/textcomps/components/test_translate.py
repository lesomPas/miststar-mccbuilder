"""
测试 Translate 组件
"""
import pytest
from miststar.textcomps_refactor import Translate, Rawtext, Text, TranslateKind
from miststar.textcomps_refactor.exceptions import InvalidValueException


# ============================================================================
# Test Translate
# ============================================================================

class TestTranslate:
    """测试 Translate 组件"""

    # ---------- 三种状态 ----------
    def test_pure_translate(self):
        """纯翻译：无 with 参数"""
        t = Translate("gui.done")
        assert t.kind == TranslateKind.PureTranslate
        assert t.translate == "gui.done"
        assert t.with_content is None
        assert t.to_dictionary() == {"translate": "gui.done"}

    def test_string_translate(self):
        """字符串列表模式：with 为 list[str]"""
        t = Translate("chat.type.text", with_content=["Steve", "Hello"])
        assert t.kind == TranslateKind.StringTranslate
        assert t.with_content == ["Steve", "Hello"]
        assert t.to_dictionary() == {
            "translate": "chat.type.text",
            "with": ["Steve", "Hello"]
        }

    def test_rawtext_translate(self):
        """Rawtext 模式：with 为 Rawtext 对象"""
        raw = Rawtext([Text("Hello"), Text("World")])
        t = Translate("key", with_content=raw)
        assert t.kind == TranslateKind.RawtextTranslate
        assert isinstance(t.with_content, Rawtext)
        assert t.to_dictionary() == {
            "translate": "key",
            "with": {"rawtext": [{"text": "Hello"}, {"text": "World"}]}
        }

    # ---------- from_dictionary 反序列化 ----------
    def test_from_dictionary_pure(self):
        """从字典反序列化纯翻译"""
        d = {"translate": "gui.done"}
        t = Translate.from_dictionary(d)
        assert t.kind == TranslateKind.PureTranslate
        assert t.translate == "gui.done"
        assert t.with_content is None

    def test_from_dictionary_string_list(self):
        """从字典反序列化字符串列表模式"""
        d = {"translate": "chat.type.text", "with": ["Steve", "Hello"]}
        t = Translate.from_dictionary(d)
        assert t.kind == TranslateKind.StringTranslate
        assert t.with_content == ["Steve", "Hello"]

    def test_from_dictionary_rawtext(self):
        """从字典反序列化 Rawtext 模式（with 为 dict）"""
        d = {
            "translate": "key",
            "with": {"rawtext": [{"text": "Hello"}, {"text": "World"}]}
        }
        t = Translate.from_dictionary(d)
        assert t.kind == TranslateKind.RawtextTranslate
        assert isinstance(t.with_content, Rawtext)
        assert len(t.with_content) == 2
        assert t.with_content[0].content == "Hello"

    def test_from_dictionary_with_empty_rawtext(self):
        """with 为空 Rawtext"""
        d = {"translate": "key", "with": {"rawtext": []}}
        t = Translate.from_dictionary(d)
        assert t.kind == TranslateKind.RawtextTranslate
        assert isinstance(t.with_content, Rawtext)
        assert len(t.with_content) == 0

    def test_from_dictionary_with_empty_list(self):
        """with 为空列表"""
        d = {"translate": "key", "with": []}
        t = Translate.from_dictionary(d)
        assert t.kind == TranslateKind.StringTranslate
        assert t.with_content == []

    # ---------- 序列化 roundtrip ----------
    def test_roundtrip_pure(self):
        original = Translate("gui.done")
        d = original.to_dictionary()
        restored = Translate.from_dictionary(d)
        assert restored.translate == original.translate
        assert restored.with_content == original.with_content

    def test_roundtrip_string(self):
        original = Translate("chat.type.text", with_content=["Steve", "Hello"])
        d = original.to_dictionary()
        restored = Translate.from_dictionary(d)
        assert restored.kind == TranslateKind.StringTranslate
        assert restored.with_content == ["Steve", "Hello"]

    def test_roundtrip_rawtext(self):
        raw = Rawtext([Text("Hello")])
        original = Translate("key", with_content=raw)
        d = original.to_dictionary()
        restored = Translate.from_dictionary(d)
        assert restored.kind == TranslateKind.RawtextTranslate
        assert isinstance(restored.with_content, Rawtext)
        assert restored.with_content[0].content == "Hello"

    # ---------- into_builder 方法 ----------
    def test_into_builder(self):
        """测试 Translate 转换为 Builder"""
        t = Translate("key")
        builder = t.into_builder()
        assert builder.translate is t
        builder.include_string("Hello")
        assert t.with_content == ["Hello"]

    def test_into_builder_modify_existing(self):
        """已有 with 内容的 Translate 进入 Builder 后可以追加"""
        raw = Rawtext([Text("Hello")])
        t = Translate("key", with_content=raw)
        builder = t.into_builder()
        builder.include(Text("World"))
        assert len(t.with_content) == 2  # type: ignore
        assert t.with_content[1].content == "World"  # type: ignore

    # ---------- 错误处理 ----------
    def test_invalid_translate_type(self):
        with pytest.raises(InvalidValueException) as exc:
            Translate(123)  # type: ignore
        assert "translate" in str(exc.value)
        assert "str" in str(exc.value)

    def test_invalid_with_content_list(self):
        """with_content 列表中包含非字符串元素"""
        with pytest.raises(InvalidValueException) as exc:
            Translate("key", with_content=["a", 123])  # type: ignore
        assert "with_content" in str(exc.value)

    def test_from_dictionary_extra_keys(self):
        # 这个测试取决于实际行为。如果 from_dictionary 会忽略额外键，则不会报错
        d = {"translate": "key", "with": ["a"], "extra": "ignored"}
        t = Translate.from_dictionary(d)
        assert t.translate == "key"
        assert t.with_content == ["a"]

    def test_from_dictionary_missing_translate(self):
        """缺少 translate 键"""
        with pytest.raises(KeyError):
            Translate.from_dictionary({})

    # ---------- kind 属性 ----------
    @pytest.mark.parametrize("with_content, expected_kind", [
        (None, TranslateKind.PureTranslate),
        ([], TranslateKind.StringTranslate),
        (["a"], TranslateKind.StringTranslate),
        (Rawtext(), TranslateKind.RawtextTranslate),
    ])
    def test_kind_property(self, with_content, expected_kind):
        t = Translate("key", with_content=with_content)
        assert t.kind == expected_kind

    # ---------- build_dictionary 静态方法 ----------
    def test_build_dictionary_pure(self):
        d = Translate.build_dictionary("key")
        assert d == {"translate": "key"}

    def test_build_dictionary_string(self):
        d = Translate.build_dictionary("key", with_content=["a", "b"])
        assert d == {"translate": "key", "with": ["a", "b"]}

    def test_build_dictionary_rawtext(self):
        raw = Rawtext([Text("Hello")])
        d = Translate.build_dictionary("key", with_content=raw)
        assert d == {"translate": "key", "with": {"rawtext": [{"text": "Hello"}]}}
