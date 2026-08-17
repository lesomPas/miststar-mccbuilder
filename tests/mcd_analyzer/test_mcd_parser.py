"""
MCD Parser 测试套件 (pytest)

基于 mcd_parser(3).py 的完整测试覆盖。

请根据实际项目结构调整导入路径。
"""

import pytest

# 根据实际包结构调整这些导入
from miststar.mcd_analyzer.mcd_parser import (
    detect_version,
    MCDParserV1,
    MCDParserV2,
    MCDParserConfig,
    MCDParsingException,
    DocumentCursor,
    ChainState,
    STATE_SECTIONS,
    STATE_CHARS,
)
from miststar.mcd_analyzer.mcd_lexer import MCDLexerV1, MCDLexerV2, DocumentTokenKind, DocumentToken
from miststar.mcd_analyzer.mcd import BlockKind, ChainItem, MCDMeta, MCDChain, CommandState


# ============================================================================
# detect_version
# ============================================================================

class TestDetectVersion:
    """@mcd_version 检测逻辑"""

    def test_no_version_defaults_to_1(self):
        assert detect_version("some content") == 1
        assert detect_version("") == 1

    def test_v1_explicit(self):
        assert detect_version("@mcd_version = 1") == 1

    def test_v2_explicit(self):
        assert detect_version("@mcd_version = 2") == 2

    def test_v2_with_leading_whitespace(self):
        assert detect_version("  @mcd_version = 2") == 2

    def test_v2_with_extra_spaces(self):
        assert detect_version("@mcd_version  =  2") == 2

    def test_invalid_version_returns_negative(self):
        assert detect_version("@mcd_version = 3") == -1
        assert detect_version("@mcd_version = abc") == -1

    def test_last_version_wins(self):
        doc = "@mcd_version = 1\n@mcd_version = 2"
        assert detect_version(doc) == 1

    def test_last_version_wins_even_if_invalid(self):
        doc = "@mcd_version = 2\n@mcd_version = 3"
        assert detect_version(doc) == 2

    def test_version_with_trailing_content(self):
        assert detect_version("@mcd_version = 2 # comment") == 2


# ============================================================================
# DocumentCursor
# ============================================================================

class TestDocumentCursor:
    """DocumentCursor 游标行为"""

    def test_empty_document_raises(self):
        lexer = MCDLexerV1()
        with pytest.raises(MCDParsingException, match="Empty document"):
            DocumentCursor("", lexer)

    def test_single_token_eof(self):
        lexer = MCDLexerV1()
        cursor = DocumentCursor("###Function###", lexer)
        assert cursor.current is not None
        assert cursor.current.kind == DocumentTokenKind.Label
        assert cursor.peek is None
        assert cursor.is_eof() is False

    def test_bump_advances(self):
        lexer = MCDLexerV1()
        cursor = DocumentCursor("###Function###\n/say hi", lexer)
        assert cursor.current.kind == DocumentTokenKind.Label
        assert cursor.peek.kind == DocumentTokenKind.TextCommand

        old = cursor.bump()
        assert old.kind == DocumentTokenKind.Label
        assert cursor.current.kind == DocumentTokenKind.TextCommand
        assert cursor.peek is None

        old = cursor.bump()
        assert old.kind == DocumentTokenKind.TextCommand
        assert cursor.current is None
        assert cursor.is_eof() is True

    def test_bump_returns_none_on_eof(self):
        lexer = MCDLexerV1()
        cursor = DocumentCursor("/say hi", lexer)
        cursor.bump()  # 消费掉唯一 token
        assert cursor.current is None
        assert cursor.is_eof() is True


# ============================================================================
# MCDParserConfig
# ============================================================================

class TestMCDParserConfig:
    """配置对象默认值"""

    def test_default_values(self):
        cfg = MCDParserConfig()
        assert cfg.unmatch_mode == "comment"
        assert cfg.extra_mode == "ignore"
        assert cfg.label_mode == "ignore"
        assert cfg.chain_label_mode == "auto"
        assert cfg.state_generator == "simple"
        assert cfg.unused_state == "ignore"

    def test_custom_values(self):
        cfg = MCDParserConfig(
            unmatch_mode="forbid",
            extra_mode="forbid",
            label_mode="strict",
            chain_label_mode="strict",
            state_generator="strict",
            unused_state="forbid",
        )
        assert cfg.unmatch_mode == "forbid"
        assert cfg.label_mode == "strict"


# ============================================================================
# MCDParserV1
# ============================================================================

class TestMCDParserV1:
    """V1 解析器测试"""

    @pytest.fixture
    def lexer(self):
        return MCDLexerV1()

    @pytest.fixture
    def default_config(self):
        return MCDParserConfig()

    # ------------------------------------------------------------------
    # 基础解析
    # ------------------------------------------------------------------

    def test_basic_parse(self, lexer, default_config):
        doc = "###Function###\n/say hello\n###End###"
        parser = MCDParserV1(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert mcd.version == 1
        assert len(mcd.chains) == 1
        assert mcd.chains[0].name == "分离的命令"
        assert len(mcd.chains[0].items) == 1
        assert isinstance(mcd.chains[0].items[0], ChainItem.TextCommand)
        assert mcd.chains[0].items[0].command == "/say hello"

    def test_comments_and_commands_mixed(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "# comment 1\n"
            "/say hello\n"
            "# comment 2\n"
            "/give @a dirt\n"
            "###End###"
        )
        parser = MCDParserV1(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        items = mcd.chains[0].items
        assert len(items) == 4
        assert isinstance(items[0], ChainItem.Comment)
        assert items[0].text == "comment 1"
        assert isinstance(items[1], ChainItem.TextCommand)
        assert isinstance(items[2], ChainItem.Comment)
        assert isinstance(items[3], ChainItem.TextCommand)

    def test_only_comments(self, lexer, default_config):
        doc = "###Function###\n# only comments\n###End###"
        parser = MCDParserV1(lexer, default_config)
        mcd = parser.generate_mcd(doc)
        assert len(mcd.chains[0].items) == 1
        assert isinstance(mcd.chains[0].items[0], ChainItem.Comment)

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def test_meta_parsing(self, lexer, default_config):
        doc = "@author = test\n###Function###\n/say hi\n###End###"
        parser = MCDParserV1(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.meta_info) == 1
        assert mcd.meta_info[0].key == "author"
        assert mcd.meta_info[0].value == "test"

    def test_multiple_meta(self, lexer, default_config):
        doc = (
            "@author = test\n"
            "@version = 1.0\n"
            "###Function###\n"
            "/say hi\n"
            "###End###"
        )
        parser = MCDParserV1(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.meta_info) == 2
        assert mcd.meta_info[0].key == "author"
        assert mcd.meta_info[1].key == "version"

    # ------------------------------------------------------------------
    # 严格标签模式
    # ------------------------------------------------------------------

    def test_strict_missing_end(self, lexer):
        config = MCDParserConfig(label_mode="strict")
        doc = "###Function###\n/say hello"
        parser = MCDParserV1(lexer, config)

        with pytest.raises(MCDParsingException, match="Missing \'End\' label"):
            parser.generate_mcd(doc)

    def test_strict_missing_function(self, lexer):
        config = MCDParserConfig(label_mode="strict")
        doc = "/say hello\n###End###"
        parser = MCDParserV1(lexer, config)

        # 没有 Function，但 End 存在；结束时 matched_start=False, matched_end=True
        # 但当前代码只在结尾检查 matched_end，不检查 matched_start
        # 所以这里不会报错（除非后续增加检查）
        mcd = parser.generate_mcd(doc)
        assert mcd.version == 1

    def test_strict_duplicate_function(self, lexer):
        config = MCDParserConfig(label_mode="strict")
        doc = "###Function###\n###Function###\n###End###"
        parser = MCDParserV1(lexer, config)

        with pytest.raises(MCDParsingException, match="Duplicate label \'Function\'"):
            parser.generate_mcd(doc)

    def test_strict_end_not_last(self, lexer):
        config = MCDParserConfig(label_mode="strict")
        doc = "###Function###\n###End###\n/say hello"
        parser = MCDParserV1(lexer, config)

        with pytest.raises(MCDParsingException, match="Label \'End\' must be the last token"):
            parser.generate_mcd(doc)

    def test_strict_invalid_label(self, lexer):
        config = MCDParserConfig(label_mode="strict")
        doc = "###Function###\n###Invalid###\n###End###"
        parser = MCDParserV1(lexer, config)

        with pytest.raises(MCDParsingException, match="Invalid label"):
            parser.generate_mcd(doc)

    # ------------------------------------------------------------------
    # 忽略标签模式
    # ------------------------------------------------------------------

    def test_label_mode_ignore_allows_anything(self, lexer):
        config = MCDParserConfig(label_mode="ignore")
        doc = "/say hello"
        parser = MCDParserV1(lexer, config)
        mcd = parser.generate_mcd(doc)

        assert mcd.version == 1
        assert len(mcd.chains[0].items) == 1

    def test_label_mode_ignore_with_labels(self, lexer):
        config = MCDParserConfig(label_mode="ignore")
        doc = "###Function###\n/say hello\n###End###\n/say extra"
        parser = MCDParserV1(lexer, config)
        mcd = parser.generate_mcd(doc)

        # End 后面的内容也会被解析
        assert len(mcd.chains[0].items) == 2

    # ------------------------------------------------------------------
    # UnmatchLine 模式
    # ------------------------------------------------------------------

    def test_unmatch_mode_forbid(self, lexer):
        config = MCDParserConfig(unmatch_mode="forbid")
        doc = "###Function###\n$ invalid\n###End###"
        parser = MCDParserV1(lexer, config)

        with pytest.raises(Exception):  # InvalidValueException
            parser.generate_mcd(doc)

    def test_unmatch_mode_ignore(self, lexer):
        config = MCDParserConfig(unmatch_mode="ignore")
        doc = "###Function###\n$ invalid\n###End###"
        parser = MCDParserV1(lexer, config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains[0].items) == 0

    def test_unmatch_mode_comment(self, lexer):
        config = MCDParserConfig(unmatch_mode="comment")
        doc = "###Function###\n$ invalid\n###End###"
        parser = MCDParserV1(lexer, config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains[0].items) == 1
        assert isinstance(mcd.chains[0].items[0], ChainItem.Comment)
        assert mcd.chains[0].items[0].text == "$ invalid"

    def test_unmatch_mode_text_command(self, lexer):
        config = MCDParserConfig(unmatch_mode="text_command")
        doc = "###Function###\n$ invalid\n###End###"
        parser = MCDParserV1(lexer, config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains[0].items) == 1
        assert isinstance(mcd.chains[0].items[0], ChainItem.TextCommand)

    # ------------------------------------------------------------------
    # Extra 模式
    # ------------------------------------------------------------------

    def test_extra_mode_forbid(self, lexer):
        config = MCDParserConfig(extra_mode="forbid")
        doc = "###Function###\n/say hello\n###End###"
        parser = MCDParserV1(lexer, config)
        # V1 Lexer 不会产出 extra token，所以正常文档不会触发
        mcd = parser.generate_mcd(doc)
        assert mcd.version == 1

    def test_extra_mode_ignore(self, lexer):
        config = MCDParserConfig(extra_mode="ignore")
        doc = "###Function###\n/say hello\n###End###"
        parser = MCDParserV1(lexer, config)
        mcd = parser.generate_mcd(doc)
        assert mcd.version == 1

    # ------------------------------------------------------------------
    # 边界
    # ------------------------------------------------------------------

    def test_empty_document(self, lexer, default_config):
        parser = MCDParserV1(lexer, default_config)
        with pytest.raises(MCDParsingException, match="Empty document"):
            parser.generate_mcd("")

    def test_only_labels(self, lexer, default_config):
        doc = "###Function###\n###End###"
        parser = MCDParserV1(lexer, default_config)
        mcd = parser.generate_mcd(doc)
        assert len(mcd.chains[0].items) == 0


# ============================================================================
# MCDParserV2
# ============================================================================

class TestMCDParserV2:
    """V2 解析器测试"""

    @pytest.fixture
    def lexer(self):
        return MCDLexerV2()

    @pytest.fixture
    def default_config(self):
        return MCDParserConfig()

    # ------------------------------------------------------------------
    # 基础链解析
    # ------------------------------------------------------------------

    def test_basic_chain(self, lexer, default_config):
        doc = "###Function###\n---Main---\n/say hello\n###End###"
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert mcd.version == 2
        assert len(mcd.chains) == 1
        assert mcd.chains[0].name == "Main"
        assert len(mcd.chains[0].items) == 1

    def test_multiple_chains(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Chain A---\n/say a\n"
            "---Chain B---\n/say b\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains) == 2
        assert mcd.chains[0].name == "Chain A"
        assert mcd.chains[1].name == "Chain B"

    def test_empty_chain(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Empty---\n"
            "---Next---\n/say hi\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains) == 2
        assert mcd.chains[0].name == "Empty"
        assert len(mcd.chains[0].items) == 0
        assert mcd.chains[1].name == "Next"

    # ------------------------------------------------------------------
    # 自动命名
    # ------------------------------------------------------------------

    def test_auto_chain_naming(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Named---\n/say 1\n"
            "---\n/say 2\n"
            "---\n/say 3\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert mcd.chains[0].name == "Named"

    def test_auto_chain_naming_all_empty(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---\n/say 1\n"
            "---\n/say 2\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert mcd.chains[0].name == "Chain 1"

    # ------------------------------------------------------------------
    # 前缀链 (root_comments)
    # ------------------------------------------------------------------

    def test_root_comments_before_first_chain(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "# root comment 1\n"
            "# root comment 2\n"
            "---Main---\n"
            "/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains) == 1
        assert mcd.chains[0].name == "Main"
        assert len(mcd.chains[0].items) == 3
        assert isinstance(mcd.chains[0].items[0], ChainItem.Comment)
        assert isinstance(mcd.chains[0].items[1], ChainItem.Comment)
        assert isinstance(mcd.chains[0].items[2], ChainItem.MarkedCommand)

    def test_root_comments_only_no_chains(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "# comment 1\n"
            "# comment 2\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains) == 1
        assert mcd.chains[0].name == "分离的命令"
        assert len(mcd.chains[0].items) == 2

    def test_no_root_comments(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Main---\n"
            "/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains) == 1
        assert mcd.chains[0].name == "Main"
        assert len(mcd.chains[0].items) == 1

    # ------------------------------------------------------------------
    # chain_label_mode 严格
    # ------------------------------------------------------------------

    def test_chain_label_mode_strict_no_label(self, lexer):
        config = MCDParserConfig(chain_label_mode="strict")
        doc = "###Function###\n/say no chain label\n###End###"
        parser = MCDParserV2(lexer, config)

        with pytest.raises(MCDParsingException, match="chain_label_mode is strict"):
            parser.generate_mcd(doc)

    def test_chain_label_mode_strict_with_label_ok(self, lexer):
        config = MCDParserConfig(chain_label_mode="strict")
        doc = "###Function###\n---Main---\n/say hello\n###End###"
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)
        assert mcd.chains[0].name == "Main"

    # ------------------------------------------------------------------
    # 状态解析 - Simple 模式
    # ------------------------------------------------------------------

    def test_state_simple_impulse(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I\n/say impulse\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert isinstance(item, ChainItem.MarkedCommand)
        assert item.state.kind == BlockKind.Impulse
        assert item.state.conditional is False
        assert item.state.always_active is True

    def test_state_simple_repeat_conditional_redstone(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> R?!\n/say complex\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Repeat
        assert item.state.conditional is True
        assert item.state.always_active is False

    def test_state_simple_chat(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> H\n/say chat mode\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Chat

    def test_state_simple_tick(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> Ct5\n/say tick 5\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.tick_delay == 5

    def test_state_simple_tick_underscore(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> Ct_\n/say tick 0\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.tick_delay == 0

    def test_state_simple_no_tick(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> C\n/say default\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.tick_delay == 0

    def test_state_simple_default_chain(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> \n/say default state\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Chain
        assert item.state.conditional is False
        assert item.state.always_active is True

    # ------------------------------------------------------------------
    # 状态解析 - Strict 模式
    # ------------------------------------------------------------------

    def test_state_strict_full(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> C_!t10\n/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Chain
        assert item.state.conditional is False
        assert item.state.always_active is False
        assert item.state.tick_delay == 10

    def test_state_strict_omit_sections(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I!\n/say omit conditional\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Impulse
        assert item.state.conditional is False  # 省略，默认 False
        assert item.state.always_active is False

    def test_state_strict_underscore_skip(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> C_t5\n/say skip conditional\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Chain
        assert item.state.conditional is False
        assert item.state.always_active is True
        assert item.state.tick_delay == 5

    def test_state_strict_chat_only(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> H\n/say chat\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Chat

    def test_state_strict_chat_with_extra_fails(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> Ht5\n/say chat\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)

        with pytest.raises(MCDParsingException, match="Chat Mode"):
            parser.generate_mcd(doc)

    def test_state_strict_invalid_char(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> X\n/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)

        with pytest.raises(MCDParsingException, match="Invalid char"):
            parser.generate_mcd(doc)

    def test_state_strict_invalid_tick(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> C_!tx\n/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)

        with pytest.raises(MCDParsingException, match="Invalid tick"):
            parser.generate_mcd(doc)

    def test_state_strict_tick_only_t(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> C_!t\n/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)

        with pytest.raises(MCDParsingException, match="Invalid tick"):
            parser.generate_mcd(doc)

    def test_state_strict_empty_state(self, lexer):
        config = MCDParserConfig(state_generator="strict")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> \n/say default\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)

        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Chain
        assert item.state.tick_delay == 0

    # ------------------------------------------------------------------
    # unused_state
    # ------------------------------------------------------------------

    def test_unused_state_forbid(self, lexer):
        config = MCDParserConfig(unused_state="forbid")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I?\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)

        with pytest.raises(MCDParsingException, match="Unused state"):
            parser.generate_mcd(doc)

    def test_unused_state_ignore(self, lexer):
        config = MCDParserConfig(unused_state="ignore")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I?\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains[0].items) == 0

    def test_unused_state_ignore_with_following_command(self, lexer):
        config = MCDParserConfig(unused_state="ignore")
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I?\n"
            "/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)

        # State 后面是 Command，会被正常配对
        assert len(mcd.chains[0].items) == 1
        assert isinstance(mcd.chains[0].items[0], ChainItem.MarkedCommand)

    # ------------------------------------------------------------------
    # State-Command 前瞻配对
    # ------------------------------------------------------------------

    def test_state_pairs_with_next_command(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I?\n/say paired\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains[0].items) == 1
        item = mcd.chains[0].items[0]
        assert isinstance(item, ChainItem.MarkedCommand)
        assert item.state.kind == BlockKind.Impulse
        assert item.command == "/say paired"

    def test_state_hangs_without_command(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I?\n"
            "> R\n/say next state\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        # 第一个 State (I?) 没有配对，被丢弃
        # 第二个 State (R) 与 /say next state 配对
        assert len(mcd.chains[0].items) == 1
        item = mcd.chains[0].items[0]
        assert item.state.kind == BlockKind.Repeat

    # ------------------------------------------------------------------
    # Label 清空 pending_state
    # ------------------------------------------------------------------

    def test_label_resets_pending_state(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---A---\n"
            "> I?\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        # Label 应该清空 pending_state，不会触发 unused_state 错误
        mcd = parser.generate_mcd(doc)
        assert len(mcd.chains) == 1

    def test_chainlabel_resets_pending_state(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---A---\n"
            "> I?\n"
            "---B---\n"
            "/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        # ChainLabel 清空 pending_state，I? 被丢弃
        # B 链的 /say 用默认状态
        assert len(mcd.chains) == 2
        assert mcd.chains[1].items[0].state.kind == BlockKind.Chain

    # ------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------

    def test_meta_parsing_v2(self, lexer, default_config):
        doc = (
            "@version = 2\n"
            "###Function###\n"
            "---Main---\n"
            "/say hi\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert any(m.key == "version" and m.value == "2" for m in mcd.meta_info)

    def test_meta_in_chain(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Main---\n"
            "@inline = meta\n"
            "/say hi\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert any(m.key == "inline" for m in mcd.meta_info)

    # ------------------------------------------------------------------
    # Comment 在链内
    # ------------------------------------------------------------------

    def test_comments_in_chain(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "# before\n"
            "/say hello\n"
            "# after\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        items = mcd.chains[0].items
        assert isinstance(items[0], ChainItem.Comment)
        assert isinstance(items[1], ChainItem.MarkedCommand)
        assert isinstance(items[2], ChainItem.Comment)

    def test_comments_between_states(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "---Test---\n"
            "> I?\n"
            "# middle comment\n"
            "/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        # State 前瞻看到 Comment 不是 MarkedCommand，所以 State 挂起
        # Comment 被追加到链
        # 然后 /say 用挂起的 State 配对
        items = mcd.chains[0].items
        assert isinstance(items[0], ChainItem.Comment)
        assert isinstance(items[1], ChainItem.MarkedCommand)
        assert items[1].state.kind == BlockKind.Impulse

    # ------------------------------------------------------------------
    # 边界
    # ------------------------------------------------------------------

    def test_empty_document(self, lexer, default_config):
        parser = MCDParserV2(lexer, default_config)
        with pytest.raises(MCDParsingException, match="Empty document"):
            parser.generate_mcd("")

    def test_only_labels_no_chains(self, lexer, default_config):
        doc = "###Function###\n###End###"
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains) == 1
        assert mcd.chains[0].name == "分离的命令"
        assert len(mcd.chains[0].items) == 0

    def test_only_labels_with_root_comments(self, lexer, default_config):
        doc = (
            "###Function###\n"
            "# comment\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, default_config)
        mcd = parser.generate_mcd(doc)

        assert len(mcd.chains) == 1
        assert mcd.chains[0].name == "分离的命令"
        assert len(mcd.chains[0].items) == 1

    def test_strict_label_mode_v2(self, lexer):
        config = MCDParserConfig(label_mode="strict")
        doc = (
            "###Function###\n"
            "---Main---\n"
            "/say hello\n"
            "###End###"
        )
        parser = MCDParserV2(lexer, config)
        mcd = parser.generate_mcd(doc)
        assert mcd.version == 2

    def test_strict_label_mode_missing_end_v2(self, lexer):
        config = MCDParserConfig(label_mode="strict")
        doc = (
            "###Function###\n"
            "---Main---\n"
            "/say hello\n"
        )
        parser = MCDParserV2(lexer, config)

        with pytest.raises(MCDParsingException, match="Missing \'End\' label"):
            parser.generate_mcd(doc)


# ============================================================================
# 静态方法独立测试
# ============================================================================

class TestGenerateStateSimply:
    """generate_state_simply 静态方法"""

    def test_empty(self):
        state = MCDParserV2.generate_state_simply("")
        assert state.kind == BlockKind.Chain
        assert state.conditional is False
        assert state.always_active is True
        assert state.tick_delay == 0

    def test_impulse(self):
        state = MCDParserV2.generate_state_simply("I")
        assert state.kind == BlockKind.Impulse
        assert state.conditional is False
        assert state.always_active is True

    def test_repeat(self):
        state = MCDParserV2.generate_state_simply("R")
        assert state.kind == BlockKind.Repeat

    def test_chat(self):
        state = MCDParserV2.generate_state_simply("H")
        assert state.kind == BlockKind.Chat

    def test_chain_default(self):
        state = MCDParserV2.generate_state_simply("C")
        assert state.kind == BlockKind.Chain

    def test_no_explicit_type_defaults_chain(self):
        state = MCDParserV2.generate_state_simply("?")
        assert state.kind == BlockKind.Chain
        assert state.conditional is True

    def test_complex_combination(self):
        state = MCDParserV2.generate_state_simply("R?!t5")
        assert state.kind == BlockKind.Repeat
        assert state.conditional is True
        assert state.always_active is False
        assert state.tick_delay == 5

    def test_tick_underscore(self):
        state = MCDParserV2.generate_state_simply("Ct_")
        assert state.tick_delay == 0

    def test_no_tick_match(self):
        state = MCDParserV2.generate_state_simply("C")
        assert state.tick_delay == 0

    def test_conditional_only(self):
        state = MCDParserV2.generate_state_simply("?")
        assert state.conditional is True
        assert state.kind == BlockKind.Chain

    def test_redstone_only(self):
        state = MCDParserV2.generate_state_simply("!")
        assert state.always_active is False
        assert state.kind == BlockKind.Chain


class TestGenerateStateStrictly:
    """generate_state_strictly 静态方法"""

    def test_empty(self):
        state = MCDParserV2.generate_state_strictly("")
        assert state.kind == BlockKind.Chain
        assert state.tick_delay == 0

    def test_full_explicit(self):
        state = MCDParserV2.generate_state_strictly("C?!t10")
        assert state.kind == BlockKind.Chain
        assert state.conditional is True
        assert state.always_active is False
        assert state.tick_delay == 10

    def test_omit_conditional(self):
        # 残留值复用: I 后面直接跟 !，省略 conditional
        state = MCDParserV2.generate_state_strictly("I!")
        assert state.kind == BlockKind.Impulse
        assert state.conditional is False
        assert state.always_active is False

    def test_underscore_skip_conditional(self):
        state = MCDParserV2.generate_state_strictly("C_t5")
        assert state.kind == BlockKind.Chain
        assert state.conditional is False
        assert state.always_active is True
        assert state.tick_delay == 5

    def test_chat_only(self):
        state = MCDParserV2.generate_state_strictly("H")
        assert state.kind == BlockKind.Chat
        assert state.tick_delay == 0

    def test_chat_with_extra_fails(self):
        with pytest.raises(MCDParsingException, match="Chat Mode"):
            MCDParserV2.generate_state_strictly("Ht5")

    def test_chat_with_any_extra_fails(self):
        with pytest.raises(MCDParsingException, match="Chat Mode"):
            MCDParserV2.generate_state_strictly("H_")

    def test_invalid_first_char(self):
        with pytest.raises(MCDParsingException, match="Invalid char"):
            MCDParserV2.generate_state_strictly("X")

    def test_invalid_second_char(self):
        with pytest.raises(MCDParsingException, match="Invalid char"):
            MCDParserV2.generate_state_strictly("CX")

    def test_invalid_third_char(self):
        with pytest.raises(MCDParsingException, match="Invalid char"):
            MCDParserV2.generate_state_strictly("C?X")

    def test_invalid_tick_letter(self):
        with pytest.raises(MCDParsingException, match="Invalid tick"):
            MCDParserV2.generate_state_strictly("C_!tx")

    def test_tick_only_t_no_value(self):
        with pytest.raises(MCDParsingException, match="Invalid tick"):
            MCDParserV2.generate_state_strictly("C_!t")

    def test_tick_wrong_prefix(self):
        with pytest.raises(MCDParsingException, match="Invalid tick"):
            MCDParserV2.generate_state_strictly("C_!x5")

    def test_all_defaults(self):
        state = MCDParserV2.generate_state_strictly("___")
        assert state.kind == BlockKind.Chain
        assert state.conditional is False
        assert state.always_active is True
        assert state.tick_delay == 0

    def test_all_defaults_with_tick(self):
        state = MCDParserV2.generate_state_strictly("___t5")
        assert state.kind == BlockKind.Chain
        assert state.conditional is False
        assert state.always_active is True
        assert state.tick_delay == 5

    def test_impulse_conditional_redstone_tick(self):
        state = MCDParserV2.generate_state_strictly("I?!t99")
        assert state.kind == BlockKind.Impulse
        assert state.conditional is True
        assert state.always_active is False
        assert state.tick_delay == 99

