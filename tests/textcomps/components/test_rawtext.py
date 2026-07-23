"""
测试 Rawtext 容器
（不包含 TranslateBuilder 相关测试）
"""
import pytest
from miststar.textcomps_refactor import Rawtext, Text, Score, Selector, Translate
from miststar.textcomps_refactor.exceptions import InvalidValueException


# ============================================================================
# Test Rawtext 构造方法
# ============================================================================

class TestRawtextConstruction:
    """测试 Rawtext 的多种构造方式"""

    def test_empty(self):
        r = Rawtext()
        assert len(r) == 0
        assert r.data == []

    def test_from_list(self):
        r = Rawtext([Text("a"), Selector("@p")])
        assert len(r) == 2
        assert r[0].content == "a"
        assert r[1].selector == "@p"

    def test_from_iterable(self):
        r = Rawtext.from_iterable([Text("x"), Text("y")])
        assert len(r) == 2
        assert r[0].content == "x"
        assert r[1].content == "y"

    def test_from_iterable_generator(self):
        """生成器应被正确物化，不会被耗尽"""
        def gen():
            yield Text("a")
            yield Text("b")
        r = Rawtext.from_iterable(gen())
        assert len(r) == 2

    def test_from_component(self):
        r = Rawtext.from_component(Text("a"), Score("Steve", "kills"))
        assert len(r) == 2
        assert isinstance(r[0], Text)
        assert isinstance(r[1], Score)

    def test_from_component_empty(self):
        r = Rawtext.from_component()
        assert len(r) == 0

    def test_from_template(self):
        r = Rawtext.from_template("Hello {@p}")
        assert len(r) == 2
        assert isinstance(r[0], Text)
        assert isinstance(r[1], Selector)

    def test_from_dictionary(self):
        d = {"rawtext": [{"text": "Hi"}, {"selector": "@p"}]}
        r = Rawtext.from_dictionary(d)
        assert len(r) == 2
        assert r[0].content == "Hi"
        assert r[1].selector == "@p"

    def test_from_dictionary_with_translate(self):
        d = {"rawtext": [{"translate": "gui.done"}]}
        r = Rawtext.from_dictionary(d)
        assert len(r) == 1
        assert isinstance(r[0], Translate)
        assert r[0].translate == "gui.done"


# ============================================================================
# Test Rawtext 添加方法
# ============================================================================

class TestRawtextAddMethods:
    """测试 Rawtext 的各种添加方法"""

    def test_add(self):
        r = Rawtext()
        r.add(Text("a"), Selector("@p"))
        assert len(r) == 2
        assert r[0].content == "a"

    def test_add_empty(self):
        r = Rawtext([Text("a")])
        r.add()
        assert len(r) == 1

    def test_add_invalid_type(self):
        r = Rawtext()
        with pytest.raises(InvalidValueException) as exc:
            r.add(123)  # type: ignore
        assert "args" in str(exc.value)

    def test_add_iterable(self):
        r = Rawtext()
        r.add_iterable([Text("a"), Text("b")])
        assert len(r) == 2

    def test_add_iterable_generator(self):
        """生成器应被正确物化"""
        def gen():
            yield Text("a")
            yield Text("b")
        r = Rawtext()
        r.add_iterable(gen())
        assert len(r) == 2

    def test_add_iterable_invalid_element(self):
        r = Rawtext()
        with pytest.raises(InvalidValueException) as exc:
            r.add_iterable([Text("a"), 123])  # type: ignore
        assert "iterable" in str(exc.value)

    # ---------- asc 智能添加 ----------
    def test_asc_selector(self):
        r = Rawtext()
        r.asc("@p")
        assert len(r) == 1
        assert isinstance(r[0], Selector)
        assert r[0].selector == "@p"

    def test_asc_score(self):
        r = Rawtext()
        r.asc("money[].Steve")
        assert len(r) == 1
        assert isinstance(r[0], Score)
        assert r[0].name == "Steve"
        assert r[0].objective == "money"

    def test_asc_text(self):
        r = Rawtext()
        r.asc("plain text")
        assert len(r) == 1
        assert isinstance(r[0], Text)
        assert r[0].content == "plain text"

    def test_asc_mixed(self):
        r = Rawtext()
        r.asc("Hello", "@p", "money[].Steve", "!")
        assert len(r) == 4
        assert isinstance(r[0], Text)
        assert isinstance(r[1], Selector)
        assert isinstance(r[2], Score)
        assert isinstance(r[3], Text)

    def test_asc_with_textcomponent(self):
        r = Rawtext()
        r.asc(Text("prefix"), "@p")
        assert len(r) == 2
        assert r[0].content == "prefix"
        assert isinstance(r[1], Selector)

    def test_asc_invalid_type(self):
        r = Rawtext()
        with pytest.raises(InvalidValueException) as exc:
            r.asc(123)  # type: ignore
        assert "sentence" in str(exc.value)

    # ---------- 快捷方法 ----------
    def test_text_shortcut(self):
        r = Rawtext().text("Hello")
        assert len(r) == 1
        assert r[0].content == "Hello"

    def test_score_shortcut(self):
        r = Rawtext().score("@s", "kills")
        assert len(r) == 1
        assert r[0].name == "@s"
        assert r[0].objective == "kills"

    def test_selector_shortcut(self):
        r = Rawtext().selector("@a[tag=admin]")
        assert len(r) == 1
        assert r[0].selector == "@a[tag=admin]"

    def test_chain_shortcuts(self):
        r = (Rawtext()
             .text("Hello ")
             .selector("@p")
             .score("@s", "kills")
             .text("!"))
        assert len(r) == 4
        assert isinstance(r[0], Text)
        assert isinstance(r[1], Selector)
        assert isinstance(r[2], Score)
        assert isinstance(r[3], Text)

    # ---------- template 方法 ----------
    def test_template_method(self):
        r = Rawtext()
        r.template("Hello {@p}")
        assert len(r) == 2
        assert isinstance(r[0], Text)
        assert isinstance(r[1], Selector)

    def test_template_method_chain(self):
        r = Rawtext().template("Hello {@p}").template(" 再见 {@a}")
        assert len(r) == 4


# ============================================================================
# Test Rawtext 序列化与反序列化
# ============================================================================

class TestRawtextSerialization:
    """测试 Rawtext 的序列化"""

    def test_to_dictionary(self):
        r = Rawtext([Text("Hi"), Selector("@p")])
        expected = {
            "rawtext": [
                {"text": "Hi"},
                {"selector": "@p"}
            ]
        }
        assert r.to_dictionary() == expected

    def test_to_dictionary_empty(self):
        r = Rawtext()
        assert r.to_dictionary() == {"rawtext": []}

    def test_to_dictionary_nested(self):
        inner = Rawtext([Text("inner")])
        r = Rawtext([Text("outer"), inner])
        expected = {
            "rawtext": [
                {"text": "outer"},
                {"rawtext": [{"text": "inner"}]}
            ]
        }
        assert r.to_dictionary() == expected

    def test_roundtrip(self):
        original = Rawtext([
            Text("Hi"),
            Selector("@p"),
            Score("Steve", "kills"),
            Translate("gui.done")
        ])
        d = original.to_dictionary()
        restored = Rawtext.from_dictionary(d)
        assert restored.to_dictionary() == d

    def test_roundtrip_with_nested(self):
        inner = Rawtext([Text("inner")])
        original = Rawtext([Text("outer"), inner])
        d = original.to_dictionary()
        restored = Rawtext.from_dictionary(d)
        assert restored.to_dictionary() == d


# ============================================================================
# Test Rawtext 序列协议
# ============================================================================

class TestRawtextSequenceProtocol:
    """测试 Rawtext 作为序列的行为"""

    def test_len(self):
        r = Rawtext([Text("a"), Text("b")])
        assert len(r) == 2

    def test_getitem(self):
        r = Rawtext([Text("a"), Text("b")])
        assert r[0].content == "a"
        assert r[1].content == "b"

    def test_getitem_negative_index(self):
        r = Rawtext([Text("a"), Text("b")])
        assert r[-1].content == "b"

    def test_getitem_out_of_range(self):
        r = Rawtext([Text("a")])
        with pytest.raises(IndexError):
            _ = r[1]

    def test_iteration(self):
        r = Rawtext([Text("a"), Text("b")])
        contents = [comp.content for comp in r]
        assert contents == ["a", "b"]

    def test_iteration_empty(self):
        r = Rawtext()
        contents = [comp for comp in r]
        assert contents == []


# ============================================================================
# Test Rawtext 错误处理
# ============================================================================

class TestRawtextErrorHandling:
    """测试 Rawtext 的错误处理"""

    def test_post_init_invalid_data(self):
        """__post_init__ 应检测 data 中非 TextComponent 的元素"""
        with pytest.raises(InvalidValueException) as exc:
            Rawtext(data=[Text("a"), 123])  # type: ignore
        assert "data" in str(exc.value)

    def test_from_component_invalid(self):
        with pytest.raises(InvalidValueException) as exc:
            Rawtext.from_component(Text("a"), 123)  # type: ignore
        assert "args" in str(exc.value)

    def test_from_dictionary_missing_rawtext(self):
        with pytest.raises(KeyError):
            Rawtext.from_dictionary({})

    def test_from_dictionary_invalid_rawtext(self):
        d = {"rawtext": "not a list"}
        with pytest.raises(InvalidValueException):
            Rawtext.from_dictionary(d)
