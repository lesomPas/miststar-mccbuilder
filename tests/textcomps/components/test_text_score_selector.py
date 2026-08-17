"""
测试基础组件：Text, Score, Selector
"""
import pytest
from miststar.textcomps import Text, Score, Selector
from miststar.exceptions import InvalidValueException


# ============================================================================
# Test Text
# ============================================================================

class TestText:
    """测试 Text 组件"""

    def test_creation(self):
        t = Text("hello")
        assert t.content == "hello"

    def test_to_dictionary(self):
        t = Text("world")
        assert t.to_dictionary() == {"text": "world"}

    def test_from_dictionary(self):
        t = Text.from_dictionary({"text": "foo"})
        assert t.content == "foo"

    def test_roundtrip(self):
        original = Text("roundtrip")
        d = original.to_dictionary()
        restored = Text.from_dictionary(d)
        assert restored.content == original.content

    def test_empty_string(self):
        t = Text("")
        assert t.content == ""
        assert t.to_dictionary() == {"text": ""}
        t2 = Text.from_dictionary({"text": ""})
        assert t2.content == ""

    def test_invalid_content_type(self):
        with pytest.raises(InvalidValueException) as exc:
            Text(123)  # type: ignore
        assert "content" in str(exc.value)
        assert "str" in str(exc.value)

    def test_from_dictionary_missing_key(self):
        with pytest.raises(KeyError):
            Text.from_dictionary({})


# ============================================================================
# Test Score
# ============================================================================

class TestScore:
    """测试 Score 组件"""

    def test_creation(self):
        s = Score("Steve", "kills")
        assert s.name == "Steve"
        assert s.objective == "kills"

    def test_to_dictionary(self):
        s = Score("Steve", "kills")
        assert s.to_dictionary() == {
            "score": {"name": "Steve", "objective": "kills"}
        }

    def test_from_dictionary(self):
        d = {"score": {"name": "@p", "objective": "points"}}
        s = Score.from_dictionary(d)
        assert s.name == "@p"
        assert s.objective == "points"

    def test_roundtrip(self):
        original = Score("Alex", "level")
        d = original.to_dictionary()
        restored = Score.from_dictionary(d)
        assert restored.name == original.name
        assert restored.objective == original.objective

    # ---------- 快捷构造方法 ----------
    @pytest.mark.parametrize("method, expected_name", [
        (Score.p, "@p"),
        (Score.r, "@r"),
        (Score.a, "@a"),
        (Score.e, "@e"),
        (Score.s, "@s"),
        (Score.n, "@n"),
        (Score.initiator, "@initiator"),
    ])
    def test_shortcuts(self, method, expected_name):
        s = method("test_objective")
        assert s.name == expected_name
        assert s.objective == "test_objective"

    # ---------- 错误处理 ----------
    def test_invalid_name_type(self):
        with pytest.raises(InvalidValueException) as exc:
            Score(123, "kills")  # type: ignore
        assert "name" in str(exc.value)

    def test_invalid_objective_type(self):
        with pytest.raises(InvalidValueException) as exc:
            Score("Steve", 123)  # type: ignore
        assert "objective" in str(exc.value)

    def test_from_dictionary_missing_key(self):
        with pytest.raises(KeyError):
            Score.from_dictionary({})


# ============================================================================
# Test Selector
# ============================================================================

class TestSelector:
    """测试 Selector 组件"""

    def test_creation(self):
        s = Selector("@p")
        assert s.selector == "@p"

    def test_to_dictionary(self):
        s = Selector("@a[tag=admin]")
        assert s.to_dictionary() == {"selector": "@a[tag=admin]"}

    def test_from_dictionary(self):
        s = Selector.from_dictionary({"selector": "@e[type=zombie]"})
        assert s.selector == "@e[type=zombie]"

    def test_roundtrip(self):
        original = Selector("@p[tag=!admin]")
        d = original.to_dictionary()
        restored = Selector.from_dictionary(d)
        assert restored.selector == original.selector

    def test_empty_selector(self):
        s = Selector("")
        assert s.selector == ""
        assert s.to_dictionary() == {"selector": ""}

    def test_invalid_selector_type(self):
        with pytest.raises(InvalidValueException) as exc:
            Selector(123)  # type: ignore
        assert "selector" in str(exc.value)

    def test_from_dictionary_missing_key(self):
        with pytest.raises(KeyError):
            Selector.from_dictionary({})
