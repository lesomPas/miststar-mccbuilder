"""
测试模板系统：template_analysis 函数
"""
import pytest
from miststar.textcomps_refactor import template_analysis, Text, Score, Selector
from miststar.textcomps_refactor.exceptions import InvalidValueException


# ============================================================================
# Test template_analysis
# ============================================================================

class TestTemplateAnalysis:
    """测试 template_analysis 函数"""

    # ---------- 基础功能 ----------
    def test_plain_text(self):
        """纯文本模板，无插值"""
        result = template_analysis("Hello world")
        assert len(result) == 1
        assert isinstance(result[0], Text)
        assert result[0].content == "Hello world"

    def test_single_selector(self):
        """单个选择器插值"""
        result = template_analysis("Hello {@p}")
        assert len(result) == 2
        assert isinstance(result[0], Text)
        assert result[0].content == "Hello "
        assert isinstance(result[1], Selector)
        assert result[1].selector == "@p"

    def test_single_score(self):
        """单个计分板插值"""
        result = template_analysis("你有 {money[].Steve} 金币")
        assert len(result) == 3
        assert result[0].content == "你有 "
        assert isinstance(result[1], Score)
        assert result[1].name == "Steve"
        assert result[1].objective == "money"
        assert result[2].content == " 金币"

    def test_multiple_interpolations(self):
        """多个插值混合"""
        result = template_analysis("玩家 {@p} 的分数是 {kills[].@s}")
        assert len(result) == 4
        assert result[0].content == "玩家 "
        assert isinstance(result[1], Selector)
        assert result[1].selector == "@p"
        assert result[2].content == " 的分数是 "
        assert isinstance(result[3], Score)
        assert result[3].name == "@s"
        assert result[3].objective == "kills"

    # ---------- 边界情况 ----------
    def test_empty_template(self):
        """空模板"""
        result = template_analysis("")
        assert result == []

    def test_template_with_interpolation_at_start(self):
        """插值在开头"""
        result = template_analysis("{@p} 你好")
        assert len(result) == 2
        assert isinstance(result[0], Selector)
        assert result[0].selector == "@p"
        assert result[1].content == " 你好"

    def test_template_with_interpolation_at_end(self):
        """插值在结尾"""
        result = template_analysis("你好 {@p}")
        assert len(result) == 2
        assert result[0].content == "你好 "
        assert isinstance(result[1], Selector)
        assert result[1].selector == "@p"

    def test_template_only_interpolation(self):
        """整个模板只有一个插值"""
        result = template_analysis("{@p}")
        assert len(result) == 1
        assert isinstance(result[0], Selector)
        assert result[0].selector == "@p"

    # ---------- 混合复杂场景 ----------
    def test_complex_template(self):
        """复杂模板：多种插值混合 + 转义"""
        template = "玩家 {@p} 有 {money[].@s} 金币，等级 {level[].@s}。{{这是普通文本}}"
        result = template_analysis(template)
        # 预期: [Text, Selector, Text, Score, Text, Score, Text]
        assert len(result) == 7
        assert result[0].content == "玩家 "
        assert isinstance(result[1], Selector)
        assert result[2].content == " 有 "
        assert isinstance(result[3], Score)
        assert result[3].objective == "money"
        assert result[4].content == " 金币，等级 "
        assert isinstance(result[5], Score)
        assert result[5].objective == "level"
        assert result[6].content == "。{这是普通文本}"

    # ---------- 真实场景模拟 ----------
    def test_realistic_template(self):
        """模拟真实 Minecraft 消息"""
        template = "§l欢迎 {@p} 回来！你有 {money[].@s} 个金币，排名 {rank[].@s}"
        result = template_analysis(template)
        assert len(result) == 6
        assert result[0].content == "§l欢迎 "
        assert isinstance(result[1], Selector)
        assert result[2].content == " 回来！你有 "
        assert isinstance(result[3], Score)
        assert result[3].objective == "money"
        assert result[4].content == " 个金币，排名 "
        assert isinstance(result[5], Score)
        assert result[5].objective == "rank"

    # ---------- 错误处理 ----------
    def test_invalid_template_type(self):
        """template 必须是字符串"""
        with pytest.raises(InvalidValueException) as exc:
            template_analysis(123)  # type: ignore
        assert "template" in str(exc.value)
        assert "str" in str(exc.value)
