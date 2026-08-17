# tests/test_mcd_lexer.py
import pytest

from miststar.mcd_analyzer.mcd_lexer import (
    MCDLexerV1,
    MCDLexerV2,
    DocumentTokenKind,
    DocumentToken,
)


# ---------- 辅助函数 ----------
def tokens_of(lexer, document: str) -> list[DocumentToken]:
    """将 Lexer 生成器转换为 Token 列表，便于断言"""
    return list(lexer.tokenize(document))


# ---------- V1 词法分析器测试 ----------
class TestMCDLexerV1:
    @pytest.fixture
    def lexer(self):
        return MCDLexerV1()

    def test_empty_document(self, lexer):
        assert tokens_of(lexer, "") == []
        assert tokens_of(lexer, "\n\n   \n") == []

    def test_label(self, lexer):
        # 标准 Label
        result = tokens_of(lexer, "###Function###")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.Label
        assert result[0].data == "Function"

        # 带空格的 Label
        result = tokens_of(lexer, "###  End  ###")
        assert result[0].kind == DocumentTokenKind.Label
        assert result[0].data == "End"

        # 空 Label（边界情况）
        result = tokens_of(lexer, "######")
        assert result[0].kind == DocumentTokenKind.Label
        assert result[0].data == ""

    def test_comment(self, lexer):
        result = tokens_of(lexer, "# 这是一条注释")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.Comment
        assert result[0].data == "这是一条注释"

        # 无空格注释
        result = tokens_of(lexer, "#nospace")
        assert result[0].data == "nospace"

        # 空注释
        result = tokens_of(lexer, "#")
        assert result[0].data == ""

    def test_meta(self, lexer):
        # 标准 Meta
        result = tokens_of(lexer, "@author = lesomras")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.Meta
        assert result[0].data == "author"
        assert result[0].extra_data == "lesomras"

        # 无空格 Meta
        result = tokens_of(lexer, "@version=2")
        assert result[0].data == "version"
        assert result[0].extra_data == "2"

        # 空值（value 为空）
        result = tokens_of(lexer, "@key=")
        assert result[0].data == "key"
        assert result[0].extra_data == ""

        # 空键（key 为空）—— Lexer 会识别但不会报错
        result = tokens_of(lexer, "@=value")
        assert result[0].data == ""
        assert result[0].extra_data == "value"

    def test_text_command(self, lexer):
        # 以 / 开头的命令
        result = tokens_of(lexer, "/say hello")
        assert result[0].kind == DocumentTokenKind.TextCommand
        assert result[0].data == "/say hello"

        # 以英文字母开头的命令
        result = tokens_of(lexer, "say hello")
        assert result[0].kind == DocumentTokenKind.TextCommand
        assert result[0].data == "say hello"

        # 大写字母开头
        result = tokens_of(lexer, "SayHello")
        assert result[0].kind == DocumentTokenKind.TextCommand

    def test_unmatch_line(self, lexer):
        # 非 ASCII 字母开头的行 → UnmatchLine
        result = tokens_of(lexer, "你好世界")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.UnmatchLine
        assert result[0].data == "你好世界"

        # 特殊符号开头
        result = tokens_of(lexer, "!!!danger!!!")
        assert result[0].kind == DocumentTokenKind.UnmatchLine

        # 数字开头（不是字母也不是 /）
        result = tokens_of(lexer, "123command")
        assert result[0].kind == DocumentTokenKind.UnmatchLine

    def test_mixed_document(self, lexer):
        doc = """
        @author = test
        ###Function###
        # 注释
        /say hello
        乱码行
        ###End###
        """
        result = tokens_of(lexer, doc)
        kinds = [t.kind for t in result]
        assert kinds == [
            DocumentTokenKind.Meta,
            DocumentTokenKind.Label,
            DocumentTokenKind.Comment,
            DocumentTokenKind.TextCommand,
            DocumentTokenKind.UnmatchLine,
            DocumentTokenKind.Label,
        ]
        # 验证最后一个 Label 是 End
        assert result[-1].data == "End"


# ---------- V2 词法分析器测试 ----------
class TestMCDLexerV2:
    @pytest.fixture
    def lexer(self):
        return MCDLexerV2()

    def test_empty_document(self, lexer):
        assert tokens_of(lexer, "") == []
        assert tokens_of(lexer, "\n\n   \n") == []

    def test_label(self, lexer):
        result = tokens_of(lexer, "###Function###")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.Label
        assert result[0].data == "Function"

    def test_chain_label(self, lexer):
        # 标准链标签
        result = tokens_of(lexer, "---Chain 1---")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.ChainLabel
        assert result[0].data == "Chain 1"

        # 空链名（边界情况）
        result = tokens_of(lexer, "------")
        assert result[0].kind == DocumentTokenKind.ChainLabel
        assert result[0].data == ""

        # 带空格的链名
        result = tokens_of(lexer, "---  Hello World  ---")
        assert result[0].data == "Hello World"  # 保留中间空格，strip 由 parser 处理

    def test_comment(self, lexer):
        result = tokens_of(lexer, "# 注释")
        assert result[0].kind == DocumentTokenKind.Comment
        assert result[0].data == "注释"

    def test_state(self, lexer):
        result = tokens_of(lexer, ">I?t5")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.State
        assert result[0].data == "I?t5"

        # 带前导空格的 State
        result = tokens_of(lexer, ">  I?t5")
        assert result[0].data == "I?t5"

        # 空 State（只有 >）
        result = tokens_of(lexer, ">")
        assert result[0].data == ""

    def test_meta(self, lexer):
        result = tokens_of(lexer, "@key=value")
        assert result[0].kind == DocumentTokenKind.Meta
        assert result[0].data == "key"
        assert result[0].extra_data == "value"

        # Meta 中有空格
        result = tokens_of(lexer, "@author = lesomras")
        assert result[0].data == "author"
        assert result[0].extra_data == "lesomras"

    def test_marked_command(self, lexer):
        # 以 / 开头
        result = tokens_of(lexer, "/say hello")
        assert result[0].kind == DocumentTokenKind.MarkedCommand
        assert result[0].data == "/say hello"

        # 以字母开头
        result = tokens_of(lexer, "say hello")
        assert result[0].kind == DocumentTokenKind.MarkedCommand

        # 大写字母
        result = tokens_of(lexer, "SayHello")
        assert result[0].kind == DocumentTokenKind.MarkedCommand

    def test_unmatch_line(self, lexer):
        # 非字母、非 /、非特殊前缀
        result = tokens_of(lexer, "!!!invalid!!!")
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.UnmatchLine
        assert result[0].data == "!!!invalid!!!"

        # 数字开头
        result = tokens_of(lexer, "123command")
        assert result[0].kind == DocumentTokenKind.UnmatchLine

        # 中文字符
        result = tokens_of(lexer, "你好世界")
        assert result[0].kind == DocumentTokenKind.UnmatchLine

    def test_v2_full_document(self, lexer):
        doc = """
        @version=2
        ###Function###
        ---Main---
        # 注释
        >I?t5
        /say hello
        ---Sub---
        >R!t10
        /say loop
        ###End###
        """
        result = tokens_of(lexer, doc)
        kinds = [t.kind for t in result]
        expected_kinds = [
            DocumentTokenKind.Meta,
            DocumentTokenKind.Label,
            DocumentTokenKind.ChainLabel,  # Main
            DocumentTokenKind.Comment,
            DocumentTokenKind.State,
            DocumentTokenKind.MarkedCommand,
            DocumentTokenKind.ChainLabel,  # Sub
            DocumentTokenKind.State,
            DocumentTokenKind.MarkedCommand,
            DocumentTokenKind.Label,  # End
        ]
        assert kinds == expected_kinds
        # 验证链名
        assert result[2].data == "Main"
        assert result[6].data == "Sub"

    def test_trailing_spaces_handling(self, lexer):
        """确保前导/尾随空格不会影响 Token 识别"""
        doc = "  /say hello  "
        result = tokens_of(lexer, doc)
        assert len(result) == 1
        assert result[0].kind == DocumentTokenKind.MarkedCommand
        assert result[0].data == "/say hello"  # strip 去掉了首尾空格

    def test_multiple_tokens(self, lexer):
        doc = "# comment\n/say hi\n---chain---"
        result = tokens_of(lexer, doc)
        assert len(result) == 3
        assert result[0].kind == DocumentTokenKind.Comment
        assert result[1].kind == DocumentTokenKind.MarkedCommand
        assert result[2].kind == DocumentTokenKind.ChainLabel
