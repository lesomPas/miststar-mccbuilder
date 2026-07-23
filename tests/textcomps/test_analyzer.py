# tests/test_analyzer.py
"""
测试 analyzer 模块：SemanticComponentAnalyzer 和 TemplateLexer
"""
import pytest
from miststar.textcomps_refactor.analyzer import SemanticComponentAnalyzer, TemplateLexer
from miststar.textcomps_refactor.exceptions import InvalidValueException


# ============================================================================
# 测试 SemanticComponentAnalyzer.analyze
# ============================================================================

class TestSemanticComponentAnalyzer:
    """测试语义分析器的类型推断功能"""

    # ---------- 选择器识别 ----------
    @pytest.mark.parametrize("input_str, expected", [
        # 标准选择器（无参数）
        ("@p", ("selector", ["@p"])),
        ("@a", ("selector", ["@a"])),
        ("@e", ("selector", ["@e"])),
        ("@r", ("selector", ["@r"])),
        ("@s", ("selector", ["@s"])),
        ("@n", ("selector", ["@n"])),
        # 带参数的选择器
        ("@a[tag=admin]", ("selector", ["@a[tag=admin]"])),
        ("@e[type=zombie,c=5]", ("selector", ["@e[type=zombie,c=5]"])),
        ("@p[tag=!admin]", ("selector", ["@p[tag=!admin]"])),
        # @initiator
        ("@initiator", ("selector", ["@initiator"])),
        ("@initiator[tag=foo]", ("selector", ["@initiator[tag=foo]"])),
        # 带空格的合法选择器（被规范化）
        ("@a[ tag = admin ]", ("selector", ["@a[ tag = admin ]"])),
    ])
    def test_selector_detection(self, input_str, expected):
        """测试各种选择器格式能否正确识别"""
        assert SemanticComponentAnalyzer.analyze(input_str) == expected

    # ---------- 计分板识别 ----------
    @pytest.mark.parametrize("input_str, expected", [
        ("money[].Steve", ("score", ["Steve", "money"])),
        ("kills[].@p", ("score", ["@p", "kills"])),
        ("points[].@a[tag=admin]", ("score", ["@a[tag=admin]", "points"])),
        ("level[].@s", ("score", ["@s", "level"])),
    ])
    def test_score_detection(self, input_str, expected):
        """测试计分板格式 objective[].name 是否正确解析"""
        assert SemanticComponentAnalyzer.analyze(input_str) == expected

    # ---------- 文本识别 ----------
    @pytest.mark.parametrize("input_str", [
        "hello world",
        "plain text",
        "@invalid",        # 不是有效选择器
        "moneySteve",      # 缺少 [].
        "[]",              # 只有分隔符，没有实际内容
        "@p[",             # 不完整的括号，不应识别为选择器
        "@initiatorx",     # 不完整 @initiator，应为文本
        "Steve[]",         # objective 为空？实际上会被当作 text 因为 format 是 "[]."，但这里写 "[]" 后无内容，不会匹配计分板（需要后面有名字）
        "[]Steve",         # 前面为空，不会被识别为计分板
    ])
    def test_text_detection(self, input_str):
        """测试这些输入应被归类为普通文本"""
        result = SemanticComponentAnalyzer.analyze(input_str)
        assert result[0] == "text"
        assert result[1] == [input_str]

    # ---------- 边界情况 ----------
    def test_empty_string(self):
        """空字符串应视为文本"""
        result = SemanticComponentAnalyzer.analyze("")
        assert result == ("text", [""])

    def test_single_character(self):
        """单字符，不是选择器，应视为文本"""
        assert SemanticComponentAnalyzer.analyze("@") == ("text", ["@"])
        assert SemanticComponentAnalyzer.analyze("a") == ("text", ["a"])

    def test_selector_with_extra_text(self):
        """选择器后跟文本应整体作为文本（我们的分词器会先拆开，但此处 analyzer 只判断单个 token）"""
        # 注意：analyze 只处理单个 token，所以 "@p hello" 不会被当作选择器
        assert SemanticComponentAnalyzer.analyze("@p hello") == ("text", ["@p hello"])


# ============================================================================
# 测试 TemplateLexer.tokenize
# ============================================================================

class TestTemplateLexer:
    """测试模板词法分析器"""

    # ---------- 基本功能 ----------
    def test_no_braces(self):
        """没有任何花括号的纯文本"""
        result = TemplateLexer.tokenize("Hello world")
        assert result == [("Hello world", False)]

    def test_single_interpolation(self):
        """单个插值域"""
        result = TemplateLexer.tokenize("Hello {@p}!")
        assert result == [
            ("Hello ", False),
            ("@p", True),
            ("!", False),
        ]

    def test_multiple_interpolations(self):
        """多个插值域"""
        result = TemplateLexer.tokenize("A {@p} B {kills[]Steve} C")
        assert result == [
            ("A ", False),
            ("@p", True),
            (" B ", False),
            ("kills[]Steve", True),
            (" C", False),
        ]

    def test_interpolation_at_start_and_end(self):
        result = TemplateLexer.tokenize("{@p} hello {kills[]Steve}")
        assert result == [
            ("@p", True),
            (" hello ", False),
            ("kills[]Steve", True),
        ]

    # ---------- 转义花括号 ----------
    def test_escaped_braces(self):
        """{{ 和 }} 应转为字面量 { 和 }，且标记为 False"""
        result = TemplateLexer.tokenize("{{escaped}}")
        # 实际输出：先是 "{" (False)，然后是 "escaped" (False)，最后是 "}" (False)
        # 它们会被合并为一个包？在 push_sentence 之前，pacakge 积累：遇到第一个 '{' 检测到 {{ 时直接 append '{'，
        # 然后检测到 "escaped" 时 append，然后检测到 }} 时 append '}'，最后 push_sentence(False)
        assert result == [("{escaped}", False)]  # 因为 package 在 push_sentence 时合并了

    def test_escaped_braces_with_interpolation(self):
        """转义花括号包围的文本不应被识别为插值域"""
        result = TemplateLexer.tokenize("{{@p}}")
        # 应该全部作为普通文本 "{@p}"
        assert result == [("{@p}", False)]

    # ---------- 嵌套花括号 ----------
    def test_nested_braces(self):
        """嵌套花括号应作为一个整体插值域被捕获"""
        result = TemplateLexer.tokenize("{outer {inner}}")
        # 整个 {outer {inner}} 是一个插值域，其内容为 "outer {inner}"
        assert result == [("outer {inner}", True)]

    def test_nested_with_escaped_inside(self):
        """插值域内部包含转义花括号"""
        result = TemplateLexer.tokenize("{outer {{inner}} }")
        # 插值域内容是 "outer {{inner}} "，其中的 {{inner}} 会被转义为 {inner}
        # 但因为是插值域内部，转义逻辑不会执行，内容中会保留字面量花括号
        # 我们只关心它是否被正确识别为一个插值域
        assert result[0][1] is True
        assert result[0][0] == "outer {{inner}} "  # 注意转义后的结果

    # ---------- 不匹配的花括号 ----------
    def test_unmatched_opening_brace(self):
        """左花括号没有匹配的右花括号，应忽略"""
        result = TemplateLexer.tokenize("Hello {world")
        # 按照当前实现，遇到 '{' 后寻找匹配，找不到则丢弃 package，继续
        # 所以结果应为 [("Hello ", False)]，因为 "world" 在寻找匹配时被收集到 package，匹配失败后清空，没有回退
        # 实际上可能会丢失 "world"，因为匹配失败后清空了 package 但并没有再处理 "world"
        # 我们测试实际行为以锁定当前逻辑
        # 预期：因为匹配失败，所以最后一个部分的world在程序退出前被被记录，所以为 "Hello ", "world"，相当于忽略掉左括号
        assert result == [("Hello ", False), ("world", False)]

    def test_unmatched_closing_brace(self):
        """多余的右花括号，应忽略"""
        result = TemplateLexer.tokenize("Hello }world")
        # 单独的 '}' 会被跳过，所以结果为 [("Hello world", False)]
        # 因为在处理 '}' 时，直接 p += 1，不 append 任何内容
        assert result == [("Hello world", False)]

    def test_multiple_unmatched(self):
        result = TemplateLexer.tokenize("{unmatched} still")
        # 第一个 {unmatched} 匹配成功，所以是插值域，后面 " still" 是文本
        assert result == [("unmatched", True), (" still", False)]

    # ---------- 空插值域 ----------
    def test_empty_interpolation(self):
        """空插值域 {}"""
        result = TemplateLexer.tokenize("Hello {} world")
        # 内容为空，会被 push 空字符串，但 push_sentence 会跳过空 package，所以插值域消失
        # 实际结果可能为 [("Hello ", False), (" world", False)]
        assert result == [("Hello ", False), (" world", False)]

    # ---------- 边界情况 ----------
    def test_only_braces(self):
        result = TemplateLexer.tokenize("{}")
        assert result == []  # 空插值域被跳过

    def test_whitespace_only(self):
        result = TemplateLexer.tokenize("   ")
        assert result == [("   ", False)]

    def test_empty_string(self):
        result = TemplateLexer.tokenize("")
        assert result == []

    # ---------- 与其他模块的集成 ----------
    def test_tokenize_realistic_template(self):
        """模拟真实使用场景的模板"""
        template = "玩家 {@p} 的分数是 {kills[]@s}，等级 {level[]@s}。"
        result = TemplateLexer.tokenize(template)
        expected = [
            ("玩家 ", False),
            ("@p", True),
            (" 的分数是 ", False),
            ("kills[]@s", True),
            ("，等级 ", False),
            ("level[]@s", True),
            ("。", False),
        ]
        assert result == expected